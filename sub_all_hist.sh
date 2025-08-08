VERSION="STEAM_241113_L1jet"

#python3 make_histo_condor_sh.py --era 24B --version ${VERSION}
#python3 make_histo_condor_sh.py --era 24C --version ${VERSION}
#python3 make_histo_condor_sh.py --era 24D --version ${VERSION}
#python3 make_histo_condor_sh.py --era 24E --version ${VERSION}
#python3 make_histo_condor_sh.py --era 24F --version ${VERSION}
#python3 make_histo_condor_sh.py --era 24G --version ${VERSION}
python3 make_histo_condor_sh.py --era 24H --version ${VERSION}
#python3 make_histo_condor_sh.py --era 24I --version ${VERSION}


#condor_submit sub_histo_condor_24B_${VERSION}.sub
#condor_submit sub_histo_condor_24C_${VERSION}.sub
#condor_submit sub_histo_condor_24D_${VERSION}.sub
#condor_submit sub_histo_condor_24E_${VERSION}.sub
#condor_submit sub_histo_condor_24F_${VERSION}.sub
#condor_submit sub_histo_condor_24G_${VERSION}.sub
condor_submit sub_histo_condor_24H_${VERSION}.sub
#condor_submit sub_histo_condor_24I_${VERSION}.sub


#python3 make_condor_sh.py --era Winter24 --version ${VERSION}
#condor_submit sub_condor_Winter24_${VERSION}.sub
