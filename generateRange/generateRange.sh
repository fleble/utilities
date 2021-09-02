#!/bin/bash

# Example use
# $ ./generateRange.sh 3 root://cms-xrd-global.cern.ch//store/user/some/path/nano_mc2018_ .root > files.txt
# $ cat files.txt
# root://cms-xrd-global.cern.ch//store/user/some/path/nano_mc2018_1.root
# root://cms-xrd-global.cern.ch//store/user/some/path/nano_mc2018_2.root
# root://cms-xrd-global.cern.ch//store/user/some/path/nano_mc2018_3.root


# Defaults
n1=1
prefix=''
suffix=''

# Parse arguments
if [ $# -eq 1 ]; then
    n2=$1  
elif [ $# -eq 2 ]; then
    n1=$1
    n2=$2
elif [ $# -eq 3 ]; then
    n2=$1
    prefix=$2
    suffix=$3
elif [ $# -eq 4 ]; then
    n1=$1
    n2=$2
    prefix=$3
    suffix=$4
else
    echo "ERROR: 2 arguments expected!"
fi

# Print the range
for ((i=$n1; i<($n2+1); i++)); do
    echo ${prefix}$i${suffix}
done
