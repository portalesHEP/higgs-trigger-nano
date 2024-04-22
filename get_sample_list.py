import os

das_cmd = 'dasgoclient -query=\"file dataset={}\" 2>&1 | tee data/dataset_lists/{}.txt'

datasets = {
    #'Run22C_Muon' : '/Muon/Run2022C-PromptNanoAODv10-v1/NANOAOD',
    #'Run22D_Muon' : '/Muon/Run2022D-PromptNanoAODv10_v2-v1/NANOAOD',
    #'Run22E_Muon' : '/Muon/Run2022E-PromptNanoAODv10_v1-v3/NANOAOD',
    #'Run22F_Muon' : '/Muon/Run2022F-PromptNanoAODv10_v1-v2/NANOAOD',
    #'Run22G_Muon' : '/Muon/Run2022G-PromptNanoAODv10_v1-v1/NANOAOD',

    #'Run22C_JetMET' : '/JetMET/Run2022C-PromptNanoAODv10-v1/NANOAOD',
    #'Run22D_JetMET' : '/JetMET/Run2022D-PromptNanoAODv10_v2-v1/NANOAOD',
    #'Run22E_JetMET' : '/JetMET/Run2022E-PromptNanoAODv10_v1-v3/NANOAOD',
    #'Run22F_JetMET' : '/JetMET/Run2022F-PromptNanoAODv10_v1-v2/NANOAOD',
    #'Run22G_JetMET' : '/JetMET/Run2022G-PromptNanoAODv10_v1-v1/NANOAOD',

    #'Run18D_SingleMuon' : '/SingleMuon/Run2018D-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD  run=325022',
    #'Run18D_JetHT' : '/JetHT/Run2018D-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD run=325022',
                       
#   'Run23C_Muon0-1': '/Muon0/Run2023C-PromptMiniAOD_v1_NanoAODv12-v1/NANOAOD',
#   'Run23C_Muon0-2': '/Muon0/Run2023C-PromptMiniAOD_v2_NanoAODv12-v1/NANOAOD',
#   'Run23C_Muon0-3': '/Muon0/Run2023C-PromptMiniAOD_v3_NanoAODv12-v1/NANOAOD',
#   'Run23C_Muon0-4': '/Muon0/Run2023C-PromptMiniAOD_v4_NanoAODv12-v1/NANOAOD',
#   'Run23C_Muon1-1': '/Muon1/Run2023C-PromptMiniAOD_v1_NanoAODv12-v1/NANOAOD',
#   'Run23C_Muon1-2': '/Muon1/Run2023C-PromptMiniAOD_v2_NanoAODv12-v1/NANOAOD',
#   'Run23C_Muon1-3': '/Muon1/Run2023C-PromptMiniAOD_v3_NanoAODv12-v1/NANOAOD',
#   'Run23C_Muon1-4': '/Muon1/Run2023C-PromptMiniAOD_v4_NanoAODv12-v1/NANOAOD',

#    'Run23D_Muon0-1':'/Muon0/Run2023D-PromptReco-v1/NANOAOD', 
#    'Run23D_Muon0-2':'/Muon0/Run2023D-PromptReco-v2/NANOAOD',
#    'Run23D_Muon1-1':'/Muon1/Run2023D-PromptReco-v1/NANOAOD',
#    'Run23D_Muon1-2':'/Muon1/Run2023D-PromptReco-v2/NANOAOD',

    'Run24A_Muon0':'/Muon0/Run2024A-PromptReco-v1/NANOAOD', 
    'Run24A_Muon1':'/Muon1/Run2024A-PromptReco-v1/NANOAOD',
    'Run24B_Muon0':'/Muon0/Run2024B-PromptReco-v1/NANOAOD',
    'Run24B_Muon1':'/Muon1/Run2024B-PromptReco-v1/NANOAOD',
    'Run24C_Muon0':'/Muon0/Run2024C-PromptReco-v1/NANOAOD',
    'Run24C_Muon1':'/Muon1/Run2024C-PromptReco-v1/NANOAOD',
#
#    'Run23C_JetMET0-1': '/JetMET0/Run2023C-PromptMiniAOD_v1_NanoAODv12-v1/NANOAOD',
#    'Run23C_JetMET0-2': '/JetMET0/Run2023C-PromptMiniAOD_v2_NanoAODv12-v1/NANOAOD',
#    'Run23C_JetMET0-3': '/JetMET0/Run2023C-PromptMiniAOD_v3_NanoAODv12-v1/NANOAOD',
#    'Run23C_JetMET0-4': '/JetMET0/Run2023C-PromptMiniAOD_v4_NanoAODv12-v1/NANOAOD',
#    'Run23C_JetMET1-1': '/JetMET1/Run2023C-PromptMiniAOD_v1_NanoAODv12-v1/NANOAOD',
#    'Run23C_JetMET1-2': '/JetMET1/Run2023C-PromptMiniAOD_v2_NanoAODv12-v1/NANOAOD',
#    'Run23C_JetMET1-3': '/JetMET1/Run2023C-PromptMiniAOD_v3_NanoAODv12-v1/NANOAOD',
#    'Run23C_JetMET1-4': '/JetMET1/Run2023C-PromptMiniAOD_v4_NanoAODv12-v1/NANOAOD',

#    'Run3Winter23_VBFHinv' :  '/VBFHToInvisible_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Winter23NanoAOD-126X_mcRun3_2023_forPU65_v1-v2/NANOAODSIM',
#
#    'Run23D_JetMET0-1': '/JetMET0/Run2023D-PromptReco-v1/NANOAOD',
#    'Run23D_JetMET0-2': '/JetMET0/Run2023D-PromptReco-v2/NANOAOD',
#    'Run23D_JetMET1-1': '/JetMET1/Run2023D-PromptReco-v1/NANOAOD',
#    'Run23D_JetMET1-2': '/JetMET1/Run2023D-PromptReco-v2/NANOAOD',

    #'Nano18_VBFHcc': '/VBFHToCC_M-125_dipoleRecoilOn_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v2/NANOAODSIM',
    #'Nano18_VBFHtautau': '/VBFHToTauTau_M125_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM',
    #'Nano18_VBFHinv': '/VBF_HToInvisible_M125_TuneCP5_withDipoleRecoil_13TeV_powheg_pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM',
    #'Nano18_VBFHrhogamma': '/VBF_HToRhoGamma_M125_TuneCP5_PSWeights_13TeV_powheg_pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM',
    #'Nano23_VBFHinv' : '/VBFHToInvisible_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v2/NANOAODSIM',
    #'Nano23_VBFHbb' : '/VBFHto2B_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-KeepRAW_130X_mcRun3_2023_realistic_postBPix_v2-v2/NANOAODSIM'
    #'Nano23_VBFHinv' : '/VBFHToInvisible_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v5-v2/NANOAODSIM',
}                               

for key in datasets:
    os.system(das_cmd.format(datasets[key],key))
