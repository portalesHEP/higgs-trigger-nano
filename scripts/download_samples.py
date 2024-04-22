import os

filename = 'textfiles/Run2022F.txt'

with open(filename,'r') as f:
    lines = f.read().splitlines()

print(lines)

prefix = 'root://cmsxrootd.fnal.gov/'

output = 'samples/Run2022F/'


for line in lines:
    cmd = 'xrdcp %s/%s %s/.'%(prefix,line,output)
    os.system(cmd)
