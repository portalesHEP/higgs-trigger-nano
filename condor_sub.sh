#!/bin/bash

# read arguments
WORKDIR=$1
SAMPLE=$2
TRIGGER=$3
ERA=$4
ID=$5

# create directories if not existing
cd $WORKDIR
mkdir -p ./ntuples_out/${ERA}
mkdir -p ./ntuples_out/${ERA}/goodfiles/

# setup
export X509_USER_PROXY=~/.t3/my_proxy.cert
source /cvmfs/cms.cern.ch/cmsset_default.sh
export XRD_NETWORKSTACK=IPv4
cd ../
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
eval `scram r -sh`
cd $WORKDIR
ls -lrth $X509_USER_PROXY
voms-proxy-info -all

# run cmd
echo "python vbf_ntuples.py --era ${ERA} --version ${TRIGGER} --input ${SAMPLE} --outdir ./ntuples_out/${ERA} --id ${ID}"

python vbf_ntuples.py --era ${ERA} --version ${TRIGGER} --input ${SAMPLE} --outdir ./ntuples_out/${ERA} --id ${ID}

mv ./histoFiles_all/tmp/${ERA}/*_${ID}.*root ./ntuples_out/${ERA}/goodfiles/
