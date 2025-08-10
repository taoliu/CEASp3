#!/usr/bin/env python3

"""Module Description

Copyright (c) 2009 H. Gene Shin <shin@jimmy.harvard.edu>

This code is free software; you can redistribute it and/or modify it
under the terms of the BSD License (see the file COPYING included with
the distribution).

site.py gives an average enrichment profile of given regions of interest (eg, binding sites or motifs).

@status:  experimental
@version: $Revision$
@author:  H. Gene Shin
@contact: shin@jimmy.harvard.edu
"""

# ------------------------------------
# python modules
# ------------------------------------
import os
import sys
import time
import subprocess
import string
import math
import logging
import re

import CEAS.corelib as corelib
import CEAS.R as R
import CEAS.inout as inout
#from numpy import seterr

from CEAS.bigwig_utils import open_bigwig, summarize_bigwig
from CEAS import sitepro as sitepro_parser

# ------------------------------------
# constants
# ------------------------------------
#seterr(invalid='ignore')
logging.basicConfig(level=20,
                    format='%(levelname)-5s @ %(asctime)s: %(message)s ',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    stream=sys.stderr,
                    filemode="w"
                    )

error   = logging.critical        # function alias
warn    = logging.warning
debug   = logging.debug
info    = logging.info


def opt_validate (parser):
    """Validate options from an ArgumentParser object.

    Ret: Validated options object.
    """
    options = parser.parse_args()
    
    # input BED file and GDB must be given 
    if not (options.wig and options.bed):
        parser.print_help()
        sys.exit(1)
    else:
        if len(options.wig) > 1 and len(options.bed) > 1:
            error("Either a single BED file and multiple bigWIG files or multiple BED files and a single bigWIG file are allowed.")
            sys.exit(1)

    if options.wig:
        for wig in options.wig:
            if not os.path.isfile(wig):
                error("Check -w (--bw). No such file as '%s'" %wig)
                sys.exit(1)
    
    if options.bed:
        for bed in options.bed:
            if not os.path.isfile(bed):
                error('Check -b (--bed). No such file exists:%s' %bed)
                sys.exit(1)
            
    # get namename
    if not options.name:
        #options.name=os.path.split(options.bed)[-1].rsplit('.bed',2)[0]
        options.name="sitepro_%s" %(time.strftime("%Y.%b.%d.%H-%M-%S", time.localtime()))
        
    # get the aliases
    if len(options.wig) > 1:
        if options.label:
            if len(options.label) != len(options.wig):
                error("The number and order of the labels must be the same as the bigWIG files. Check -w and -l options.")
                sys.exit(1)
        else:
            options.label = [os.path.split(x)[1].rsplit('.bw')[0] for x in options.wig]    
    elif len(options.bed) > 1:
        if options.label:
            if len(options.label) != len(options.bed):
                error("The number and order of the labels must be the same as the BED files. Check -b and -l options.")
                sys.exit(1)
        else:
            options.label = [os.path.split(x)[1].rsplit('.bed')[0] for x in options.bed]
    else:  # when given very standard inputs, one bed and one wig
        if options.label:
            if len(options.label) != 1:
                error("Only one label must be given with one BED and one bigWIG. Check -l option.")
                sys.exit(1)
        else:
            options.label = [os.path.split(options.wig[0])[1].rsplit('.bw')[0]]
            
    # print arguments 
    options.argtxt = \
    "# ARGUMENTS:\n" +\
    "# name: %s\n" %options.name +\
    "# BED file(s): %s\n" %(', '.join(options.bed),) +\
    "# WIG file(s): %s\n" %(', '.join(options.wig),) +\
    "# span: %d bp\n" %options.span +\
    "# resolution: %d bp\n" %options.pf_res +\
    "# direction (+/-): %s\n" %{True:'ON', False:'OFF'}[options.dir]
        
    return options

def draw_siteprofiles(sitebreaks, avg_siteprof, confid_interval):
    """Return a R script that draws the average profile on the given sites"""
    
    if avg_siteprof == None:
        avg_siteprof = [0]*len(sitebreaks)
    
    if confid_interval:
        str_breaks = ','.join([str(t) for t in sitebreaks])
        str_avg_siteprof = ','.join([str(t) for t in avg_siteprof])
        str_lower = ','.join([str(t[0]) for t in confid_interval])
        str_higher = ','.join([str(t[1]) for t in confid_interval])
        rscript = 'plotCI(x=c(%s),y=c(%s),ui=c(%s),li=c(%s),type="l",col="#C8524D", \
            barcol="#C8524D",gap=0, lwd=2, main="Average Profile around the Center of Sites", \
            xlab="Relative Distance from the Center (bp)",ylab="Average Profile",)\n' \
            %(str_breaks, str_avg_siteprof, str_higher, str_lower,)
    else:
        rscript=R.plot(sitebreaks,avg_siteprof,col=["#C8524D"],main="Average Profile around the Center of Sites",xlab="Relative Distance from the Center (bp)",ylab="Average Profile",lwd=2)
    rscript += R.abline(v=0,lty=2,col=['black'])

    return rscript
    
def draw_multiple_siteprofiles(sitebreaks, avg_siteprofs, confid_interval, legends):
    """Return a R script that draws multiple average profiles on the given sites"""
    
    n_prfls = len(avg_siteprofs)
    ylim=[min([min(t) for t in avg_siteprofs]),max([max(t) for t in avg_siteprofs])]
    
    rscript = ''
    rscript += 'cr <- colorRampPalette(col=c("#C8524D", "#BDD791", "#447CBE", "#775A9C"), bias=1)\n'
    rscript += 'linecols <- cr(%d)\n' %(n_prfls-1)
    rscript += 'linecols <- c(linecols, "black")\n'

    if confid_interval[0]:
        for i in range(n_prfls):
            str_breaks = ','.join([str(t) for t in sitebreaks])
            str_ylim = ','.join([str(t) for t in ylim])
            str_avg_siteprof = ','.join([str(t) for t in avg_siteprofs[i]])
            str_lower = ','.join([str(t[0]) for t in confid_interval[i]])
            str_higher = ','.join([str(t[1]) for t in confid_interval[i]])
            if i == 0:
                rscript += 'plotCI(x=c(%s),y=c(%s),ui=c(%s),li=c(%s),type="l",col=linecols[%d], \
                    barcol=linecols[%d],gap=0, lwd=2, main="Average Profile around the Center of Sites", \
                    xlab="Relative Distance from the Center (bp)",ylab="Average Profile",ylim=c(%s))\n' \
                    %(str_breaks, str_avg_siteprof, str_higher, str_lower, i+1, i+1, str_ylim)
            else:
                rscript += 'plotCI(x=c(%s),y=c(%s),ui=c(%s),li=c(%s),type="l",col=linecols[%d], \
                    barcol=linecols[%d],gap=0, lwd=2, main="Average Profile around the Center of Sites", \
                    xlab="Relative Distance from the Center (bp)",ylab="Average Profile",ylim=c(%s),add=TRUE)\n' \
                    %(str_breaks, str_avg_siteprof, str_higher, str_lower, i+1, i+1, str_ylim)
            
    else:
        rscript +=R.plot(sitebreaks,avg_siteprofs[0],col='linecols[1]', main='Average Profiles around the Center of Sites',xlab='Relative Distance from the Center (bp)',ylab='Average Profile', ylim=ylim, lwd=2) 
        for i in range(1, n_prfls):
            rscript += R.lines(sitebreaks, avg_siteprofs[i], col='linecols[%d]' %(i+1), lwd=2)
    if not legends:
        legends=['Group %d' %i for i in range(1,len(avg_siteprofs)+1)]
    rscript+=R.legend(x='topleft', legend=legends, pch=15, col='linecols', bty='o')
        
    rscript+=R.abline(v=0,lty=2,col=['black'])
    
    return rscript
    
def dump(dumpfn, bedlist, siteprofs):
    """Dump the sites and their profiles in a long string
    
    """
    dfhd = open(dumpfn, 'w')
    #if len(bedlist[0]) < 4:
    #    nameCol = None

    for i in range(len(bedlist)):
        chrom = bedlist[i][0]
        start = bedlist[i][1]
        end = bedlist[i][2]    
        s = ','.join(map(str, siteprofs[i]))
    
        if len(bedlist[0]) < 4:
            txt = "%s\t%s\t%s\t%s\n" %(chrom, start, end, s)
        else:
            txt = "%s\t%s\t%s\t\t%s\t%s\n" %(chrom, start, end, bedlist[i][3], s)
        dfhd.write(txt)
    dfhd.close()

def BedInput(fn=''):
    """Read a bed file
    
    Parameters:
    1. fn: file name
    """
    f=open(fn,'r')
    standard_chroms={'I':'chrI','II':'chrII','III':'chrIII','IV':'chrIV','V':'chrV','M':'chrM','X':'chrX'}
    bedlist = []
    for line in f:
        if line.startswith('track') or line.startswith('#') or line.startswith('browser') or not line.strip():
            continue
        l=line.strip().split()
        
        try:
            l[0]=standard_chroms[l[0]]
        except KeyError:
            pass
        bedlist.append(l)
    
    f.close()
    return bedlist
    
def CalcConfidInterval(lx): #threadhold: 0.95
    z = 1.96 #95% confid interval for normal dist, 2 side
    E = float(sum(lx))/len(lx)
    S2 = sum((t-E)**2 for t in lx) / len(lx)
    lower = E - z*math.sqrt(S2/len(lx))
    higher = E + z*math.sqrt(S2/len(lx))
    return (lower, higher)

# ------------------------------------
# Main function
# ------------------------------------
def main():
    parser = sitepro_parser.get_parser()
    opts = opt_validate(parser)
    info("\n" + opts.argtxt)

    sitebreaks = list(range(-opts.span, opts.span+opts.pf_res , opts.pf_res))
    
    super_avg_siteprofs = []
    super_confid_interval = []
    
    for iw in range(len(opts.wig)):
        info('processing wig %s %s', iw, os.path.split(opts.wig[iw])[1])
        bw = open_bigwig(opts.wig[iw])
        #avg_siteprofs = []
        ibed = 0
        for ib in range(len(opts.bed)):
            bedlist = BedInput(opts.bed[ib]) #read bed file
            valid_bedlist = [] #used for dump file
            siteprofs = []
            for line in bedlist:
                center = (int(line[1])+int(line[2]))/2
                prange = (center-opts.span-opts.pf_res/2, center+opts.span-opts.pf_res/2+opts.pf_res)
                if prange[0] <= 0 or prange[1] <= 0:
                    continue
                summarize = summarize_bigwig(
                    bw,
                    line[0],
                    int(prange[0]),
                    int(prange[1]),
                    int(2 * opts.span / opts.pf_res + 1),
                )
                if not summarize:
                    continue
                valid_bedlist.append(line)
                siteprof = summarize
                if len(line) >5: #if set --dir, reverse the profile.
                    if opts.dir and line[5] == '-':
                        siteprof = siteprof[::-1]
                siteprofs.append(siteprof)
            if opts.dump:
                dumpfn = opts.label[iw + ib] + '_dump.txt'
                dump(dumpfn, valid_bedlist, siteprofs)
            siteprofs_t = list(map(list, list(zip(*siteprofs))))
            siteprofs_t = [[t2 for t2 in t if not math.isnan(t2)] for t in siteprofs_t] #filter out NaN
            if opts.confidence:
                super_confid_interval.append([CalcConfidInterval(t) for t in siteprofs_t])
            else:
                super_confid_interval.append(None)
            kk = []
            for t in siteprofs_t:
                if len(t):
                    kk.append(sum(t)/len(t))
                else:
                    kk.append(0)
            super_avg_siteprofs.append(kk)

    # write the R script
    info('# writing R script of profiling...')
    rscript = ''
    rscript += 'library(gplots)\n'
    rscript += R.pdf(opts.name+'.pdf', height=6, width=8.5)
    
    # if single profile; otherwise multiple profiles
    if len(opts.wig) == 1 and len(opts.bed) == 1:
        rscript += draw_siteprofiles(sitebreaks, super_avg_siteprofs[0], super_confid_interval[0])
    else:
        rscript += draw_multiple_siteprofiles(sitebreaks, super_avg_siteprofs, super_confid_interval, opts.label)
    rscript += R.devoff()
    
    outf=open(opts.name+'.R','w')
    outf.write(rscript)
    outf.close()
    
    # Run R directly - if any exceptions, just pass
    try:
        p = subprocess.Popen("R" + " --vanilla < %s"  %(opts.name+'.R'), shell=True)
        sts = os.waitpid(p.pid, 0)
    except:       
        info ('#... cong! Run %s using R for the graphical result of sitepro! sitepro could not run R directly.' %(opts.name+'.R'))
        
# program running
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        warn("User interrupts me! ;-) See you!")
        sys.exit(0)
