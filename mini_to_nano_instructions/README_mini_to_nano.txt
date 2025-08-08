cmsrel CMSSW_15_0_X
cd CMSSW_15_0_X/src; cmsenv;
git cms-addpkg PhysicsTools/NanoAOD
cp triggerObjects_cff.py PhysicsTools/NanoAOD/python/triggerObjects_cff.py
mkdir filterbit_testing; cd filterbit_testing; echo 'you want a directory to contain output configs because one will be generated per input file';
cp make_condor_sh_improved.py ./
.... some file editing (changing settings at top of file, and making directory on EOS for output)
python3 make_condor_sh_improved.py
.... test the output by running one of the generated commands in condor_jobs.sh (change leading file input to [root://cms-xrd-global.cern.ch/](root://cms-xrd-global.cern.ch/) and use -n 100 just for the test)
if testing works well, then submit to condor. Should be relatively fast (~4hrs?), you may need to submit a second time to catch files with indeterminate errors.
