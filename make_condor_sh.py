# Braden Allmond Jun 26, 2024
# usage #
# python3 make_condor_sh.py
# python3 make_condor_sh.py --era 24D --version VBFtau
# open {job_file_name}.sh, copy one command from any IF-FI block, and test (takes < 3 minutes)
# if successful, submit
# condor_submit condor_sub.sub
# # # # #
# This script makes two other files.
# {job_file_name}.sh   - a chain of IF-FI statements to take advantage of condor's queue-ing submission style
# {sub_file_name}.sub  - configures the condor environment
# This script also automatically makes a jobs directory to contain logs/errors/outputs from condor jobs
# By default, files are stored on /eos space

import os
import argparse
parser = argparse.ArgumentParser(description='Make condor files.')
parser.add_argument('--era',     dest='era',     default="24B",     action='store')
parser.add_argument('--version', dest='version', default="VBFincl", action='store')
args = parser.parse_args()

def trim_dir(indir, searchword, splitter="/"):
  temp = indir.split(splitter)
  end  = temp.index(searchword)
  temp = splitter.join(temp[:end+1])
  return temp


cwd = os.getcwd() #current working directory (place script is executed from)
work_dir   = cwd
CMSSW_dir  = trim_dir(cwd, "src")
output_dir = "/eos/user/b/ballmond/VBFparkingLouis"

era = args.era
version = args.version
input_filelist = work_dir + "/data/dataset_lists/Run" + era + "_MUON.txt"

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
print(f"input filelist: {input_filelist}")
print()

command = f"python3 vbf_ntuples.py --era {era} --version {version} --outdir {output_dir}"

NanoAOD_files = []
with open(input_filelist) as f:
  NanoAOD_files = f.read().splitlines()

job_file_name = "condor_jobs.sh"
SCRAM_ARCH = "el9_amd64_gcc12"
with open(job_file_name, "w") as job_file:
  print("#!/bin/sh", file=job_file)
  print(f"cd {CMSSW_dir}", file=job_file)
  print("export X509_USER_PROXY=/afs/cern.ch/user/b/ballmond/.x509up_u134427", file=job_file)
  print("source /cvmfs/cms.cern.ch/cmsset_default.sh", file=job_file)
  print(f"export SCRAM_ARCH={SCRAM_ARCH}", file=job_file)
  print("eval `scramv1 runtime -sh`", file=job_file)
  print(f"cd {work_dir}", file=job_file)
  print("", file=job_file)
  for i, infile in enumerate(NanoAOD_files):
    print(f"if [ $1 -eq {i} ]; then", file=job_file)
    print(f"{command} --input {infile} --id {i}", file=job_file)
    print("fi", file=job_file)

print(f"commands printed to {job_file_name}")

sub_file_name = "sub_condor.sub"
job_info_dir  = "_".join([version,era,"Jobs"])
with open(sub_file_name, "w") as sub_file:
  print(f"executable = {work_dir}/{job_file_name}", file=sub_file)
  print("arguments  = $(ProcId)", file=sub_file)
  print(f"output     = {work_dir}/{job_info_dir}/job.$(ClusterId).$(ProcId).out", file=sub_file)
  print(f"error      = {work_dir}/{job_info_dir}/job.$(ClusterId).$(ProcId).err", file=sub_file)
  print(f"log        = {work_dir}/{job_info_dir}/job.$(ClusterId).log", file=sub_file)
  print("+JobFlavour = \"espresso\"", file=sub_file)
  print("", file=sub_file)
  print("# Send the job to Held state on failure.", file=sub_file)
  print("on_exit_hold = (ExitBySignal == True) || (ExitCode != 0) || (!(ExitSignal =?= UNDEFINED))", file=sub_file)
  print("# Periodically retry the jobs every 10 minutes, up to a maximum of 5 retries.", file=sub_file)
  print("periodic_release =  (NumJobStarts < 5) && ((CurrentTime - EnteredCurrentStatus) > 600)", file=sub_file)
  print("", file=sub_file)
  print(f"queue {i}", file=sub_file) # leaked variable from loop above, example of 'memory unsafe python'

# some very lazy handling so you don't overwrite dirs :)
new_job_dir = work_dir + "/" + job_info_dir
if os.path.exists(new_job_dir):
  new_job_dir += "_again"
os.mkdir(new_job_dir)

print("submit via")
print(f"condor_submit {sub_file_name}")
print()
