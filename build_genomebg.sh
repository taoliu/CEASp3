## this script prepare meta information for regulatory potential score and ceas 

ORG=$1

## for ceas bedannotate script
mysql -N -B --user=genome --host=genome-mysql.cse.ucsc.edu -A -D $ORG -e "SELECT * from refGene;"  > ${ORG}.refGene
