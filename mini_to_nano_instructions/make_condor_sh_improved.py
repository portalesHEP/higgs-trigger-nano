# Braden Allmond Jun 26, 2024
# usage #
# python3 make_condor_sh.py
# open {job_file_name}.sh, copy one command from any IF-FI block, and test (takes < 10 minutes if you change nEvents to 100)
# if successful, submit
# condor_submit condor_sub.sub
# # # # #
# If you're not familiar with condor or python, probably ping Braden (braden.allmond@gmail.com) to get some help using this.
# This script makes two other files.
# {job_file_name}.sh   - a chain of IF-FI statements to take advantage of condor's queue-ing submission style
# {sub_file_name}.sub  - configures the condor environment
# This script also automatically makes a jobs directory to contain logs/errors/outputs from condor jobs
# By default, files are stored on /eos space. If you don't configure this to your space, your output files will be lost.
# There is some handling provided to help catch HLT errors, like submitting data era tags on MC samples or vice versa.
# However, this file is provided as is and it is assumed the input files, cffs, and re-HLT/Nano commands have been
# thoroughly checked by the current user for correctness.

# note: if you need to make a new filelist, you want a command like this
# dasgoclient --query "file dataset=/DYto2Tau-4Jets_Bin-MLL-50_Fil-MuTauh_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM " >> MiniAOD_DYMuTauh_PAG_2024.txt

# note: if you need to make a new cff to include for reHLTing, the command to make that should look something like this
# hltGetConfiguration /dev/CMSSW_15_0_0/GRun \
# --globaltag 142X_mcRun3_2025_realistic_v7 \
# --process HLTX --mc --eras Run3_2025 \
# --max-events -1 --cff
# > HLT_MYCUSTOMIZATION_cff.py

# this cff should then be placed in the HLTrigger/Configuration/python directory
# after the usual cmsrel CMSSW_X_Y_Z; cd CMSSW_X_Y_Z/src; cmsenv;
# git cms-addpkg HLTrigger/Configuration
# then cp HLT_MYCUSTOMIZATION_cff.py HLTrigger/Configuration/python
# to access this cff in your reHLT commands, call it in the HLT step by name like "HLT:MYCUSTOMIZATION"

# note: you might want to hadd your files after they're made
# to do that, copy this file to your working dir
# (you may need to go to github and search for haddnano.py to ensure you have the most up to date version)
# wget https://raw.githubusercontent.com/cms-sw/cmssw/bc453a7b38ef87d29c87a4b5cb73919cd7b3ff8c/PhysicsTools/NanoAOD/scripts/haddnano.py
# and give a command like this to hadd files onto an eos space
# python3 haddnano.py /eos/user/b/ballmond/Tau_Trigger/reNanoed_samples/DYMuTauh_PAG_2024_partial.root /eos/user/b/ballmond/Tau_Trigger/reNano/DYMuTauh_2024_PAG_extrabits/*.root

# note: if you want to adjust filterbits, you'll need the following setup commands
# git cms-addpkg PhysicsTools/NanoAOD
# there, you can freely modify this file PhysicsTools/NanoAOD/python/triggerObjects_cff.py 
# after changes, remember to rebuild your library links
# scram b -j 8
# you can check if your changes took place by investigating the branch "Trig_filterbits" of an output file

# The only fields you should have to change in this file are
# input_filelist, output_dir, command_reHLT, and command_reNano

# Happy HLTing!

import os

def trim_dir(indir, searchword, splitter="/"):
  temp = indir.split(splitter)
  end  = temp.index(searchword)
  temp = splitter.join(temp[:end+1])
  return temp

cwd = os.getcwd() #current working directory (place script is executed from)
work_dir   = cwd
input_filelist = work_dir + "/MINIAOD_Muon1_Run25D.txt"
CMSSW_dir      = trim_dir(cwd, "src")
output_dir     = "/eos/user/l/lportale/STEAM/MINItoNANO/25D/" # put backslash on the end please :)
batch_name     = output_dir.split('/')[-2]
job_info_dir   = batch_name + "_Jobs"
# if you have intermediate files used during the same job, always store them on the local condor machine
# for testing before submission, copy and paste the command from condor_jobs.sh and manually change the temp file location
temp_dir   = "${_CONDOR_SCRATCH_DIR}"
OnlyReNano = True

print()
print('\033[94m',end="") # set terminal lilac
print("@#$%^&*(*&^%$#@!     did you set your VOMS proxy?    !@#$%^&*(*&^%$#@!")
print('\033[0m',end="") # reset
print()
print(f"work dir:   {work_dir}")
print(f"CMSSW top:  {CMSSW_dir}")
print('\033[31m',end="") # set terminal red
print(f"output dir: {output_dir}")
print('\033[0m',end="") # reset
print(f"temp dir:   {temp_dir}")
print(f"input filelist: {input_filelist}")
if OnlyReNano: 
    print('\033[31m',end="") # set terminal red
    print("ONLY MAKING JOBS FOR RE-NANOING")
    print('\033[0m',end="") # reset
print()

### # note that "conditions" variable are in general DIFFERENT for the HLT and Nano steps in DATA
### # the "conditions" refer to a global tag or "GT"
### # FOR MC
### # it's possible you need to repack L1
### # --step L1REPACK:FullMC,HLT \
### command_reHLT = '''cmsDriver.py reHLT \
### --conditions 142X_mcRun3_2025_realistic_v7 \
### --step HLT \
### --eventcontent RAWSIM \
### --processName HLTX \
### --mc --era Run3_2025 \
### --custom_conditions 'L1Menu_Collisions2025_v1_1_1_xml,L1TUtmTriggerMenuRcd,,,9999-12-31 23:59:59.000' \
### --nThread 8 -n -1 \
### '''
### 
### command_reNano = '''cmsDriver.py reNanoFromReHLT \
### --conditions 142X_mcRun3_2025_realistic_v7 \
### --step RAW2DIGI,L1Reco,RECO,RECOSIM,PAT,NANO \
### --datatier NANOAODSIM \
### --eventcontent NANOAODSIM \
### --hltProcess HLTX \
### --mc --era Run3_2025 \
### --customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run3 \
### --nThread 8 -n -1 \
### '''
### 
### # only used to customize filterbits
### command_reNano_only = '''cmsDriver.py reNano \
### --conditions 150X_mcRun3_2024_realistic_v2 \
### --step NANO \
### --datatier NANOAODSIM \
### --eventcontent NANOAODSIM \
### --mc --era Run3_2024 \
### --customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run3 \
### --nThreads 8 -n -1 \
### '''

# FOR DATA
# conditions for DataTRKchanges related to MkFit
# conditions found here: https://cms-talk.web.cern.ch/t/gem-request-for-including-gts-gemmaskedstrips-gemdeadstrips/55154/7
#--conditions 141X_dataRun3_HLT_v2 \
# conditions for IBV given here in comment from Marino (copying over comments from AlCa in a separate ticket)
# https://its.cern.ch/jira/browse/CMSHLT-3589?focusedId=7026717&page=com.atlassian.jira.plugin.system.issuetabpanels%3Acomment-tabpanel#comment-7026717
# sometimes you need additional L1 customizations in the HLT command, here's an example of that
#--custom_conditions 'L1Menu_Collisions2024_v1_3_0_xml,L1TUtmTriggerMenuRcd,,,9999-12-31 23:59:59.000' \
# it's possible you need to repack L1
# --step L1REPACK:Full,HLT:2025CIBCOff \

# use if you have RAW inputs only (called up from Tape with rucio, or possibly available right after it's collected)
#command_reHLT = '''cmsDriver.py reHLT \
#--conditions 150X_dataRun3_HLT_Candidate_2025_07_07_13_28_32 \
#--step HLT:2025CIBCOff \
#--eventcontent RAW \
#--processName HLTX \
#--data --era Run3_2025 \
#--nThread 8 -n -1 \
#'''

#command_reNano = '''cmsDriver.py reNanoFromReHLT \
#--conditions 150X_dataRun3_Prompt_Candidate_2025_07_07_13_31_03 \
#--step RAW2DIGI,L1Reco,RECO,PAT,NANO \
#--datatier NANOAOD \
#--eventcontent NANOAOD \
#--hltProcess HLTX \
#--data --era Run3_2025 \
#--customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run3 \
#--nThread 8 -n -1 \
#'''

# use if you have RAW-RECO inputs (more common now after July 12th, 2025, usually saves you from rucio-ing more files)
# should be faster because RAW2DIGI and L1Reco steps do not need to be performed again
command_reHLT = '''cmsDriver.py reHLT \
--conditions 150X_dataRun3_HLT_Candidate_2025_07_07_13_28_32 \
--step HLT:2025CIBCOff \
--eventcontent RECO \
--processName HLTX \
--data --era Run3_2025 \
--nThread 8 -n -1 \
'''

command_reNano = '''cmsDriver.py reNanoFromReHLT \
--conditions 150X_dataRun3_Prompt_Candidate_2025_07_07_13_31_03 \
--step PAT,NANO \
--datatier NANOAOD \
--eventcontent NANOAOD \
--hltProcess HLTX \
--data --era Run3_2025 \
--customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run3 \
--nThread 8 -n -1 \
'''

# only used to customize filterbits
command_reNano_only = '''cmsDriver.py reNano \
--conditions 150X_dataRun3_Prompt_v1 \
--step NANO \
--datatier NANOAOD \
--eventcontent NANOAOD \
--data --era Run3_2025 \
--customise Configuration/DataProcessing/RecoTLR.customisePostEra_Run3 \
--nThread 8 -n -1 \
'''

# WARNING
# this line uses the most recent command_reNano_only, which might be data OR MC
# depending on what you have commented out above
# quick way to do that in vim is :,+18s/^/#/
command_reNano = command_reNano_only if OnlyReNano else command_reNano

# basic automatic handling to check common reHLT submission errors
# if any of this impedes you and you know what you're doing, comment out and proceed
# otherwise, this block will prevent the script from making files until it completes without errors
error = False
check_filelist_name = input_filelist.split("/")[-1].upper()
dataset_names = ["Muon0", "Muon1", "EGamma0", "EGamma1", "Tau"] # updated Feb 2025, note these can change over time
check_names   = any([(dataset.upper() in check_filelist_name) for dataset in dataset_names])
if not ( (("--mc" in command_reHLT) and ("--mc" in command_reHLT)) or 
         (("--data" in command_reHLT) and ("--data" in command_reNano)) ):
  print('\033[31m\033[5m',end="") # set terminal blinking red
  print("Mismatching --mc and --data tags detected in your reHLT and reNano commands!")
  print('\033[0m',end="") # reset
  error = True
    
isMC, isData = False, False
if (("--mc" in command_reHLT) and ("--mc" in command_reNano)):
  isMC = True
  if ((check_names) and ("ERA" in check_filelist_name.upper())):
    print("Your input filelist appears to be for Data.")
    print("Are you sure you're submitting the right thing?")
    error = True
  if (("SIM" not in command_reHLT) or ("SIM" not in command_reNano)):
    print("Check your --eventcontent arguments")
    print("MC should be RAWSIM for reHLT")
    print("MC should be NANOAODSIM for reNano (and so should --datatier)")
    error = True
  if ("FullMC" not in command_reHLT):
    print("Check your --step for reHLT")
    print("MC should be L1REPACK:FullMC,HLT:USER") # USER cff is configuarable
    error = True
  if ("auto" in command_reHLT):
    print("Check your --conditions")
    print("MC should be configured with the same GT as it was produced with. This can be found on CMS DAS (click dbs show).")
    error = True

if (("--data" in command_reHLT) and ("--data" in command_reNano)):
  isData = True
  if not ((check_names) and ("ERA" in check_filelist_name.upper())):
    print("Your input filelist doesn't appear to be for Data.")
    print("If it is, please rename it to a format like 'Muon0_2024EraI.root'")
    error = True
  if (("SIM" in command_reHLT) or ("SIM" in command_reNano)):
    print("Check your --eventcontent arguments")
    print("Data should be RAW for reHLT")
    print("Data should be NANOAOD for reNano (and so should --datatier")
    error = True
  if ("L1" not in command_reHLT):
    print('\033[31m\033[5m',end="") # set terminal blinking red
    print("L1 NOT BEING REDONE! ARE YOU SURE THAT'S WHAT YOU WANT?")
    print('\033[0m',end="") # reset
    error = False # just a warning...
  #if ("Full" not in command_reHLT):
  #  print("Check your --step for reHLT")
  #  print("Data should be L1REPACK:Full,HLT:USER") # USER cff is configuarable
  #  error = True
  if ("auto" in command_reHLT):
    print("Check your --conditions")
    print("Data should usually match the GT on the relevant section of the hltGetConfig twiki")
    print("If running a testjob with that GT fails, ask for help in the HLTUserSupport channel on mattermost")
    error = True

if error: 
  if   (isMC and (not isData)): print("Errors messages are assuming you're submitting an MC sample")
  elif (isData and (not isMC)): print("Errors messages are assuming you're submitting a Data sample")
  else: print("Error messages above don't know if you're submitting Data or MC. Fix that first, and try again.")
  print("Please fix! Exiting...")
  sys.exit() # calling an unimported library to crash the script instead of importing a library to end it "correctly"

RAW_files = []
with open(input_filelist) as f:
  RAW_files = f.read().splitlines()
max_files_RAW = len(RAW_files)

MiniAOD_files = []
with open(input_filelist) as f:
  MiniAOD_files = f.read().splitlines()
max_files_MINI = len(MiniAOD_files)

use_files = MiniAOD_files if OnlyReNano else RAW_files
max_files = max_files_MINI if OnlyReNano else max_files_RAW

# check if any jobs already finished
output_dir_files = os.listdir(output_dir)
finished_job_idxs = [file.replace("reNano_out_","").replace(".root","") for file in output_dir_files]
remaining_jobs = max_files - len(finished_job_idxs)
print(f"making files to resubmit {remaining_jobs} jobs")

job_file_name = "condor_jobs.sh"
SCRAM_ARCH = "el9_amd64_gcc12"
with open(job_file_name, "w") as job_file:
  print("#!/bin/sh", file=job_file)
  print(f"cd {CMSSW_dir}", file=job_file)
#  print("export X509_USER_PROXY=/afs/cern.ch/user/b/ballmond/.x509up_u134427", file=job_file)
  print("export X509_USER_PROXY=/afs/cern.ch/user/l/lportale/x509up_u102305", file=job_file)
  print("source /cvmfs/cms.cern.ch/cmsset_default.sh", file=job_file)
  print(f"export SCRAM_ARCH={SCRAM_ARCH}", file=job_file)
  print("eval `scramv1 runtime -sh`", file=job_file)
  print(f"cd {work_dir}", file=job_file)
  print("echo -n 'extra log cwd: '; pwd", file=job_file)
  print("echo 'extra log CONDOR_SCRATCH_DIR: ' ${_CONDOR_SCRATCH_DIR}", file=job_file)
  print("", file=job_file)
  for i, infile in enumerate(use_files):
    splitFile = infile.split("/")
    if (splitFile[-1] in finished_job_idxs): continue
    filehash = splitFile[-4] + splitFile[-3] + "_" + splitFile[-1] if (isData and not OnlyReNano) else splitFile[-1]
    #if (i in finished_job_idxs): continue
    # $1 is the first input parameter to condor_jobs.sh (i.e. source condor_jobs.sh argument)
    # it is the queue value generated by condor when submitting sub_condor.sub
    print(f"if [ $1 -eq {i} ]; then", file=job_file)
    print("  TEMP_DIR=${_CONDOR_SCRATCH_DIR}", file=job_file)
    # do reHLT, then use output as input to reNano, then delete reHLT (too large to store on EOS)
    intermediate_file = "${TEMP_DIR}/"+f"reHLT_out_{i}_{filehash}"
    final_file        = "${TEMP_DIR}/"+f"reNano_out_{i}_{filehash}"
    python_file_HLT   = f"reHLT_{filehash.split('.root')[0]}.py"
    python_file_Nano  = f"reNano_{filehash.split('.root')[0]}.py"
    if (OnlyReNano):
      print(f"  {command_reNano} --filein {infile} --fileout {final_file} --python_filename {python_file_Nano};", file=job_file)
    else: 
      print(f"  {command_reHLT} --filein {infile} --fileout {intermediate_file} --python_filename {python_file_HLT};", file=job_file)
      print(f"  {command_reNano} --filein file:{intermediate_file} --fileout {final_file} --python_filename {python_file_Nano};", file=job_file)
      print(f"  rm {intermediate_file};", file=job_file)
    # best practice with condor jobs is to manually move output instead of writing output files directly to EOS
    print(f"  mv {final_file} {output_dir}", file=job_file)
    print("  echo -n 'extra log ls condor scratch'; ls ${TEMP_DIR};", file=job_file)
    print("fi", file=job_file)

print(f"commands printed to {job_file_name}")

# some very lazy handling so you don't overwrite dirs :)
new_job_dir = work_dir + "/" + job_info_dir
ls_cwd = os.listdir()
nAgains = len([exist_dir for exist_dir in ls_cwd if job_info_dir in exist_dir])
if os.path.exists(new_job_dir):
  new_job_dir += "_" + str(nAgains)
  batch_name += "_" + str(nAgains)

os.mkdir(new_job_dir)
sub_file_name = "sub_condor.sub"
with open(sub_file_name, "w") as sub_file:
  print(f"batch_name = {batch_name}", file=sub_file)
  print(f"executable = {work_dir}/{job_file_name}", file=sub_file)
  print("arguments  = $(ProcId)", file=sub_file)
  print(f"output     = {new_job_dir}/job.$(ClusterId).$(ProcId).out", file=sub_file)
  print(f"error      = {new_job_dir}/job.$(ClusterId).$(ProcId).err", file=sub_file)
  print(f"log        = {new_job_dir}/job.$(ClusterId).log", file=sub_file)
  print("request_cpus = 2", file=sub_file)
  print("request_memory = 8000", file=sub_file)
  print("request_disk = 8000000", file=sub_file)
  print("+JobFlavour = \"workday\"", file=sub_file)
  print("", file=sub_file)
  print("# Send the job to Held state on failure.", file=sub_file)
  print("on_exit_hold = (ExitBySignal == True) || (ExitCode != 0) || (!(ExitSignal =?= UNDEFINED))", file=sub_file)
  print("# Periodically retry the jobs every 10 minutes, up to a maximum of 5 retries.", file=sub_file)
  print("periodic_release =  (NumJobStarts < 5) && ((CurrentTime - EnteredCurrentStatus) > 600)", file=sub_file)
  print("", file=sub_file)
  print(f"queue {remaining_jobs}", file=sub_file)

print("submit via")
print(f"condor_submit {sub_file_name}")
print()
