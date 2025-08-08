VERSION="250730_Run25CD_renano"
ERA=25CD

python3 make_condor_sh.py --era ${ERA} --version ${VERSION}

condor_submit sub_condor_${ERA}_${VERSION}.sub

#python3 make_condor_sh.py --era Winter24 --version ${VERSION}
#condor_submit sub_condor_Winter24_${VERSION}.sub
