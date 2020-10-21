#!/usr/bin/env python

import os
import sys
from distutils.core import setup, Extension

def main():
    if not float(sys.version[:3])>=3:
        sys.stderr.write("CRITICAL: Python 3 is required!\n")
        sys.exit(1)
    setup(name="CEAS-Package",
          version="1.1.2",
          description="CEAS -- Cis-regulatory Element Annotation System Package",
          author='H. Gene Shin',
          author_email='shin@jimmy.harvard.edu',
          url='http://liulab.dfci.harvard.edu/CEAS/',
          package_dir={'CEAS' : 'lib'},
          packages=['CEAS'],
          scripts=['bin/ceas', 'bin/ceasBW', 'bin/sitepro', 'bin/siteproBW', 'bin/gca', 'bin/build_genomeBG', 'bin/ChIPAssoc'],

          classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Artistic License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Topic :: Database',
            ],
          )

if __name__ == '__main__':
    main()

