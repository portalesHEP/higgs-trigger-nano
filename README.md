# higgs-trigger-nano

Framework to run on PromptNanoAOD for trigger efficiency evaluation

# Setting up
Setup CMSSW
```
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH="slc7_amd64_gcc700"
cmsrel CMSSW_10_6_18
cd CMSSW_10_6_18/src
cmsenv
git clone git@github.com:portalesHEP/higgs-trigger-nano.git
```

# Get NanoAOD tools
```
cd $CMSSW_BASE/src
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
cd PhysicsTools/NanoAODTools
scram b -j 4
cd $CMSSW_BASE/src/higgs-trigger-nanoaod
```

# Get samples list
Currently framework is using `cmsxrootd.fnal.gov` to access the samples from remote on `/store/`. To get the file list:
```
python get_sample_list.py
```

This will store the list of available samples in `data/dataset_lists`

# Run ntuplizing
```
python vbf_ntuples.py \
       --era 24ABC \
       --version VBFincl \
       --input /store/data/Run2024C/Muon1/NANOAOD/PromptReco-v1/000/379/420/00000/425b1aa1-059b-4661-956c-fd1ac61ff8e4.root \
        --outdir ./ \
	--id 0

```

The script saves the HLT decision for VBF paths only for now, as well as minimal object information to evaluate their efficiencies

Efficiencies are then evaluated & plotted in notebooks, e.g.
```
notebooks/Efficiency_plotting_VBFincl_2024.ipynb
```



