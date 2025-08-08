#!/usr/bin/env python
import os, sys, glob
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
import argparse
from itertools import combinations
import numpy as np
from array import array
#importing tools from nanoAOD processing set up to store the ratio histograms in a root file
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import deltaR

from selections import *

def get_path_dict(year):
    if '23' in year:
        triggers = { # need to have three for convenience
            'VBFincl' : [
                'VBF_DiPFJet105_40_Mjj1000_Detajj3p5',
                'VBF_DiPFJet105_40_Mjj1000_Detajj3p5_TriplePFJet',
                'VBF_DiPFJet105_40_Mjj1000_Detajj3p5_TriplePFJet',
            ],
            'VBFjets' : [
                'VBF_DiPFJet70_40_Mjj600_Detajj2p5_DiPFJet60_JetMatchingQuadJet',
                'VBF_DiPFJet70_40_Mjj600_Detajj2p5_DiPFJet60_JetMatchingFiveJet',
                'VBF_DiPFJet70_40_Mjj600_Detajj2p5_DiPFJet60_JetMatchingSixJet',
            ],
            'VBFmet'  : [
                'VBF_DiPFJet75_40_Mjj500_Detajj2p5_PFMET85',
                'VBF_DiPFJet75_40_Mjj500_Detajj2p5_PFMET85_TriplePFJet',
                'VBF_DiPFJet75_40_Mjj500_Detajj2p5_PFMET85_TriplePFJet',

            ],
            'VBFphot' : [
                'VBF_DiPFJet45_Mjj500_Detajj2p5_Photon12',
                'VBF_DiPFJet45_Mjj500_Detajj2p5_Photon12',
                'VBF_DiPFJet45_Mjj500_Detajj2p5_Photon12',
            ],
            'VBFele'  : [
                'VBF_DiPFJet45_Mjj500_Detajj2p5_Ele12_eta2p1_WPTight_Gsf',
                'VBF_DiPFJet45_Mjj500_Detajj2p5_Ele12_eta2p1_WPTight_Gsf',
                'VBF_DiPFJet45_Mjj500_Detajj2p5_Ele12_eta2p1_WPTight_Gsf',
            ],
            'VBFmu'   : [
                'VBF_DiPFJet90_40_Mjj600_Detajj2p5_Mu3_TrkIsoVVL',
                'VBF_DiPFJet90_40_Mjj600_Detajj2p5_Mu3_TrkIsoVVL_TriplePFJet',
                'VBF_DiPFJet90_40_Mjj600_Detajj2p5_Mu3_TrkIsoVVL_TriplePFJet',
            ],
            'VBFtau'  : [
                'VBF_DiPFJet45_Mjj500_Detajj2p5_MediumDeepTauPFTauHPS45_L2NN_eta2p1',
                'VBF_DiPFJet45_Mjj500_Detajj2p5_MediumDeepTauPFTauHPS45_L2NN_eta2p1',
                'VBF_DiPFJet45_Mjj500_Detajj2p5_MediumDeepTauPFTauHPS45_L2NN_eta2p1',
            ],
        }
        return triggers
    elif '24' in year:
        triggers = { # need to have three for convenience
            'VBFincl' : [
                'VBF_DiPFJet125_45_Mjj1050',
                'VBF_DiPFJet125_45_Mjj1200',
                'VBF_DiPFJet125_45_Mjj1200',
            ],
            'VBFjets' : [
                'VBF_DiPFJet75_45_Mjj800_DiPFJet60',
                'VBF_DiPFJet75_45_Mjj850_DiPFJet60',
                'VBF_DiPFJet75_45_Mjj850_DiPFJet60',
            ],
            'VBFmet'  : [
                'VBF_DiPFJet80_45_Mjj650_PFMETNoMu85',
                'VBF_DiPFJet80_45_Mjj750_PFMETNoMu85',
                'VBF_DiPFJet80_45_Mjj750_PFMETNoMu85',
            ],
            'VBFphot' : [
                'VBF_DiPFJet50_Mjj650_Photon22',
                'VBF_DiPFJet50_Mjj750_Photon22',
                'VBF_DiPFJet50_Mjj750_Photon22',
            ],
            'VBFele'  : [
                'VBF_DiPFJet50_Mjj600_Ele22_eta2p1_WPTight_Gsf',
                'VBF_DiPFJet50_Mjj650_Ele22_eta2p1_WPTight_Gsf',
                'VBF_DiPFJet50_Mjj650_Ele22_eta2p1_WPTight_Gsf',
            ],
            'VBFmu'   : [
                'VBF_DiPFJet95_45_Mjj750_Mu3_TrkIsoVVL',
                'VBF_DiPFJet95_45_Mjj850_Mu3_TrkIsoVVL',
                'VBF_DiPFJet95_45_Mjj850_Mu3_TrkIsoVVL',
            ],
            'VBFtau'  : [
                'VBF_DiPFJet45_Mjj650_MediumDeepTauPFTauHPS45_L2NN_eta2p1',
                'VBF_DiPFJet45_Mjj750_MediumDeepTauPFTauHPS45_L2NN_eta2p1',
                'VBF_DiPFJet45_Mjj750_MediumDeepTauPFTauHPS45_L2NN_eta2p1',
            ],
            'VBFtauPNet' : [
                'VBF_DiPFJet45_Mjj650_PNetTauhPFJet45_L2NN_eta2p3',
                'VBF_DiPFJet45_Mjj750_PNetTauhPFJet45_L2NN_eta2p3',
                'VBF_DiPFJet45_Mjj750_PNetTauhPFJet45_L2NN_eta2p3',
            ],
            'VBFditau' : [
                'VBF_DoubleMediumDeepTauPFTauHPS20_eta2p1',
                'VBF_DoubleMediumDeepTauPFTauHPS20_eta2p1',
                'VBF_DoubleMediumDeepTauPFTauHPS20_eta2p1',
            ],
            'VBFditauPNet' : [
                'VBF_DoublePNetTauhPFJet20_eta2p2',
                'VBF_DoublePNetTauhPFJet20_eta2p2',
                'VBF_DoublePNetTauhPFJet20_eta2p2',
            ],
        }
        return triggers
        
    elif '25' in year:
        triggers = { # need to have three for convenience
            'VBFincl' : [
                'VBF_DiPFJet125_45_Mjj1050',
                'VBF_DiPFJet125_45_Mjj1150',
                'VBF_DiPFJet125_45_Mjj1250',
            ],
            'VBFjets' : [
                'VBF_DiPFJet75_45_Mjj800_DiPFJet60',
                'VBF_DiPFJet75_45_Mjj900_DiPFJet60',
                'VBF_DiPFJet75_45_Mjj1000_DiPFJet60',
            ],
            'VBFmet'  : [
                'VBF_DiPFJet80_45_Mjj650_PFMETNoMu85',
                'VBF_DiPFJet80_45_Mjj750_PFMETNoMu85',
                'VBF_DiPFJet80_45_Mjj850_PFMETNoMu85',
            ],
            'VBFphot' : [
                'VBF_DiPFJet50_Mjj650_Photon22',
                'VBF_DiPFJet50_Mjj750_Photon22',
                'VBF_DiPFJet50_Mjj850_Photon22',
            ],
            'VBFele'  : [
                'VBF_DiPFJet50_Mjj600_Ele22_eta2p1_WPTight_Gsf',
                'VBF_DiPFJet50_Mjj700_Ele22_eta2p1_WPTight_Gsf',
                'VBF_DiPFJet50_Mjj800_Ele22_eta2p1_WPTight_Gsf',
            ],
            'VBFmu'   : [
                'VBF_DiPFJet95_45_Mjj750_Mu3_TrkIsoVVL',
                'VBF_DiPFJet95_45_Mjj850_Mu3_TrkIsoVVL',
                'VBF_DiPFJet95_45_Mjj950_Mu3_TrkIsoVVL',
            ],
            'VBFtauPNet' : [
                'VBF_DiPFJet45_Mjj650_PNetTauhPFJet45_L2NN_eta2p3',
                'VBF_DiPFJet45_Mjj750_PNetTauhPFJet45_L2NN_eta2p3',
                'VBF_DiPFJet45_Mjj850_PNetTauhPFJet45_L2NN_eta2p3',
            ],
            'VBFditauPNet' : [
                'VBF_DiPFJet115_40_Mjj850_DoublePNetTauhPFJet20_eta2p3',
                'VBF_DiPFJet115_40_Mjj1000_DoublePNetTauhPFJet20_eta2p3',
                'VBF_DiPFJet115_40_Mjj1100_DoublePNetTauhPFJet20_eta2p3',
            ],
        }
        return triggers
    else:
        print("VBF paths only available for 2023, 2024 & 2025!")
        return {}










def get_L1_dict(year):
    if '23' in year:
        triggers = { # need to have three for convenience
            'VBFincl' : [
                'DoubleJet_110_35_DoubleJet35_Mass_Min620',
                'DoubleJet_110_35_DoubleJet35_Mass_Min620',
                'DoubleJet_110_35_DoubleJet35_Mass_Min620',
            ],
            'VBFjets' : [
                'DoubleJet_60_30_DoubleJet30_Mass_Min500_DoubleJetCentral50',
                'DoubleJet_60_30_DoubleJet30_Mass_Min500_DoubleJetCentral50',
                'DoubleJet_60_30_DoubleJet30_Mass_Min500_DoubleJetCentral50',
            ],
            'VBFmet'  : [
                'DoubleJet_65_30_DoubleJet30_Mass_Min400_ETMHF65',
                'DoubleJet_65_30_DoubleJet30_Mass_Min400_ETMHF65',
                'DoubleJet_65_30_DoubleJet30_Mass_Min400_ETMHF65',

            ],
            'VBFphot' : [
                'DoubleJet40_Mass_Min450_IsoEG10er2p1_RmOvlp_dR0p2',
                'DoubleJet40_Mass_Min450_IsoEG10er2p1_RmOvlp_dR0p2',
                'DoubleJet40_Mass_Min450_IsoEG10er2p1_RmOvlp_dR0p2',
            ],
            'VBFele'  : [
                'DoubleJet40_Mass_Min450_IsoEG10er2p1_RmOvlp_dR0p2',
                'DoubleJet40_Mass_Min450_IsoEG10er2p1_RmOvlp_dR0p2',
                'DoubleJet40_Mass_Min450_IsoEG10er2p1_RmOvlp_dR0p2',
            ],
            'VBFmu'   : [
                'DoubleJet_80_30_DoubleJet30_Mass_Min500_Mu3OQ',
                'DoubleJet_80_30_DoubleJet30_Mass_Min500_Mu3OQ',
                'DoubleJet_80_30_DoubleJet30_Mass_Min500_Mu3OQ',
            ],
            'VBFtau'  : [
                'DoubleJet35_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5',
                'DoubleJet35_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5',
                'DoubleJet35_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5',
            ],
        }
        return triggers
    elif '24' in year:
        triggers = { # need to have three for convenience
            'VBFincl' : [
                'DoubleJet_110_35_DoubleJet35_Mass_Min800',
                'DoubleJet_110_35_DoubleJet35_Mass_Min850',
                'DoubleJet_110_35_DoubleJet35_Mass_Min850',
            ],
            'VBFjets' : [
                'DoubleJet_65_35_DoubleJet35_Mass_Min600_DoubleJetCentral50',
                'DoubleJet_65_35_DoubleJet35_Mass_Min650_DoubleJetCentral50',
                'DoubleJet_65_35_DoubleJet35_Mass_Min650_DoubleJetCentral50',
            ],
            'VBFmet'  : [
                'DoubleJet_70_35_DoubleJet35_Mass_Min500_ETMHF65',
                'DoubleJet_70_35_DoubleJet35_Mass_Min550_ETMHF65',
                'DoubleJet_70_35_DoubleJet35_Mass_Min550_ETMHF65',

            ],
            'VBFphot' : [
                'DoubleJet45_Mass_Min550_LooseIsoEG20er2p1_RmOvlp_dR0p2',
                'DoubleJet45_Mass_Min600_LooseIsoEG20er2p1_RmOvlp_dR0p2',
                'DoubleJet45_Mass_Min600_LooseIsoEG20er2p1_RmOvlp_dR0p2',
            ],
            'VBFele'  : [
                'DoubleJet45_Mass_Min550_LooseIsoEG20er2p1_RmOvlp_dR0p2',
                'DoubleJet45_Mass_Min600_LooseIsoEG20er2p1_RmOvlp_dR0p2',
                'DoubleJet45_Mass_Min600_LooseIsoEG20er2p1_RmOvlp_dR0p2',
            ],
            'VBFmu'   : [
                'DoubleJet_85_35_DoubleJet35_Mass_Min600_Mu3OQ',
                'DoubleJet_85_35_DoubleJet35_Mass_Min650_Mu3OQ',
                'DoubleJet_85_35_DoubleJet35_Mass_Min650_Mu3OQ',
            ],
            'VBFtau'  : [
                'DoubleJet45_Mass_Min550_IsoTau45er2p1_RmOvlp_dR0p5',
                'DoubleJet45_Mass_Min600_IsoTau45er2p1_RmOvlp_dR0p5',
                'DoubleJet45_Mass_Min600_IsoTau45er2p1_RmOvlp_dR0p5',
            ],
        }
        return triggers
        
    elif '25' in year:
        triggers = { # need to have three for convenience
            'VBFincl' : [
                'DoubleJet_110_35_DoubleJet35_Mass_Min1000',
                'DoubleJet_110_35_DoubleJet35_Mass_Min1100',
                'DoubleJet_110_35_DoubleJet35_Mass_Min1200',
            ],
            'VBFjets' : [
                'DoubleJet_65_35_DoubleJet35_Mass_Min750_DoubleJetCentral50',
                'DoubleJet_65_35_DoubleJet35_Mass_Min850_DoubleJetCentral50',
                'DoubleJet_65_35_DoubleJet35_Mass_Min950_DoubleJetCentral50',
            ],
            'VBFmet'  : [
                'DoubleJet_70_35_DoubleJet35_Mass_Min600_ETMHF65',
                'DoubleJet_70_35_DoubleJet35_Mass_Min700_ETMHF65',
                'DoubleJet_70_35_DoubleJet35_Mass_Min800_ETMHF65',

            ],
            'VBFphot' : [
                'DoubleJet45_Mass_Min550_LooseIsoEG20er2p1_RmOvlp_dR0p2',
                'DoubleJet45_Mass_Min600_LooseIsoEG20er2p1_RmOvlp_dR0p2',
                'DoubleJet45_Mass_Min700_LooseIsoEG20er2p1_RmOvlp_dR0p2',
            ],
            'VBFele'  : [
                'DoubleJet45_Mass_Min550_LooseIsoEG20er2p1_RmOvlp_dR0p2',
                'DoubleJet45_Mass_Min600_LooseIsoEG20er2p1_RmOvlp_dR0p2',
                'DoubleJet45_Mass_Min700_LooseIsoEG20er2p1_RmOvlp_dR0p2',
            ],
            'VBFmu'   : [
                'DoubleJet_85_35_DoubleJet35_Mass_Min700_Mu3OQ',
                'DoubleJet_85_35_DoubleJet35_Mass_Min800_Mu3OQ',
                'DoubleJet_85_35_DoubleJet35_Mass_Min900_Mu3OQ',
            ],
            'VBFtau'  : [
                'DoubleJet45_Mass_Min600_IsoTau45er2p1_RmOvlp_dR0p5',
                'DoubleJet45_Mass_Min700_IsoTau45er2p1_RmOvlp_dR0p5',
                'DoubleJet45_Mass_Min800_IsoTau45er2p1_RmOvlp_dR0p5',
            ],
        }
        return triggers
    else:
        print("VBF paths only available for 2023, 2024 & 2025!")
        return {}












    

class TrigBtagAnalysis(Module):
    def __init__(self):
        self.writeHistFile=True

    def beginJob(self,histFile=None,histDirName=None):

        Module.beginJob(self,histFile,histDirName)
        triggerVersion =  str(histFile.GetName()).replace('histos_VBFTrigNanoAOD_RunD_','')\
                                                 .replace('.root','')
        print('version: {}'.format(triggerVersion))
        self.triggerVersion = triggerVersion.split('_')[2]
        self.period = triggerVersion.split('_')[1]
        print("VERSION: {}".format(self.triggerVersion), " PERIOD: {}".format(self.period))

        ### Histograms
        self.h_cutflow = ROOT.TH1F("h_cutflow","; steps",10,-0.5,9.5)
        self.addObject(self.h_cutflow)
        
        ### TTree
        self.out = ROOT.TTree("VBFtree","VBFtree")

        # Run info
        self.run                 = np.empty((1), dtype="float32")
        self.luminosityBlock     = np.empty((1), dtype="float32")
        self.event               = np.empty((1), dtype="float32")
        self.bunchCrossing       = np.empty((1), dtype="float32")
        self.npv                 = np.empty((1), dtype="float32")
        self.npu                 = np.empty((1), dtype="float32")
        self.out.Branch( "run",   self.run             ,"run/F"   )   
        self.out.Branch( "LB",    self.luminosityBlock ,"LB/F"    )
        self.out.Branch( "event", self.event           ,"event/F" )
        self.out.Branch( "BX",    self.bunchCrossing   ,"BX/F"    )
        self.out.Branch( "npv",    self.npv   ,"npv/F"    )
        self.out.Branch( "npu",    self.npu   ,"npu/F"    )
        # -- 

        # offline objects
        self.njets    = array('i',   [0])
        self.jets_pt  = array('f',99*[0])
        self.jets_eta = array('f',99*[0])
        self.jets_phi = array('f',99*[0])
        self.jets_id  = array('f',99*[0])
        self.jets_CHF = array('f',99*[0])
        self.jets_rawfactor = array('f',99*[0])
        self.jets_btagPNetB = array('f',99*[0])
        self.jets_btagPNetCvB = array('f',99*[0])
        self.jets_btagPNetCvL = array('f',99*[0])
        self.jets_btagPNetQvG = array('f',99*[0])
        self.jets_btagPNetTauVJet = array('f',99*[0])


        self.nele     = array('i',   [0])
        self.ele_pt   = array('f',99*[0])
        self.ele_eta  = array('f',99*[0])
        self.ele_phi  = array('f',99*[0])
        self.ele_id   = array('f',99*[0])
        self.nmu      = array('i',   [0])
        self.mu_pt    = array('f',99*[0])
        self.mu_eta   = array('f',99*[0])
        self.mu_phi   = array('f',99*[0])
        self.mu_id    = array('f',99*[0])
        self.mu_charge    = array('f',99*[0])
        self.ntau     = array('i',   [0])
        self.tau_pt   = array('f',99*[0])
        self.tau_eta  = array('f',99*[0])
        self.tau_phi  = array('f',99*[0])
        self.tau_charge  = array('f',99*[0])
        self.tau_idJet   = array('f',99*[0])
        self.tau_idEle   = array('f',99*[0])
        self.tau_idMuon  = array('f',99*[0])
        self.tau_PNETidJet   = array('f',99*[0])
        self.tau_PNETidEle   = array('f',99*[0])
        self.tau_PNETidMuon  = array('f',99*[0])
        self.nphot    = array('i',   [0])
        self.phot_pt  = array('f',99*[0])
        self.phot_eta = array('f',99*[0])
        self.phot_phi = array('f',99*[0])
        self.phot_id  = array('f',99*[0])
        self.phot_mvaid  = array('f',99*[0])
        self.phot_eleveto  = array('f',99*[0])
        self.MET_et   = array('f',99*[0])
        self.MET_phi  = array('f',99*[0])
        self.PUPPIMET_et  = array('f',99*[0])
        self.PUPPIMET_phi = array('f',99*[0])
        self.out.Branch( "njets",    self.njets    , "njets/I" )  
        self.out.Branch( "jets_pt",  self.jets_pt  , "jets_pt[njets]/F" )   
        self.out.Branch( "jets_eta", self.jets_eta , "jets_eta[njets]/F")
        self.out.Branch( "jets_phi", self.jets_phi , "jets_phi[njets]/F")
        self.out.Branch( "jets_id",  self.jets_id  , "jets_id[njets]/F" )
        self.out.Branch( "jets_CHF",  self.jets_CHF  , "jets_CHF[njets]/F" )
        self.out.Branch( "jets_rawfactor",  self.jets_rawfactor  , "jets_rawfactor[njets]/F" )
        self.out.Branch( "jets_btagPNetB",  self.jets_btagPNetB  , "jets_btagPNetB[njets]/F" )
        self.out.Branch( "jets_btagPNetCvB",  self.jets_btagPNetCvB  , "jets_btagPNetCvB[njets]/F" )
        self.out.Branch( "jets_btagPNetCvL",  self.jets_btagPNetCvL  , "jets_btagPNetCvL[njets]/F" )
        self.out.Branch( "jets_btagPNetQvG",  self.jets_btagPNetQvG  , "jets_btagPNetQvG[njets]/F" )
        self.out.Branch( "jets_btagPNetTauVJet",  self.jets_btagPNetTauVJet  , "jets_btagPNetTauVJet[njets]/F" )

        self.out.Branch( "nele",    self.nele    , "nele/I" )  
        self.out.Branch( "ele_pt",   self.ele_pt   , "ele_pt[nele]/F"  )   
        self.out.Branch( "ele_eta",  self.ele_eta  , "ele_eta[nele]/F" )
        self.out.Branch( "ele_phi",  self.ele_phi  , "ele_phi[nele]/F" )
        self.out.Branch( "ele_id",   self.ele_id   , "ele_id[nele]/F"  )
        self.out.Branch( "nmu",    self.nmu    , "nmu/I" )  
        self.out.Branch( "mu_pt",    self.mu_pt    , "mu_pt[nmu]/F"   )   
        self.out.Branch( "mu_eta",   self.mu_eta   , "mu_eta[nmu]/F"  )
        self.out.Branch( "mu_phi",   self.mu_phi   , "mu_phi[nmu]/F"  )
        self.out.Branch( "mu_id",    self.mu_id    , "mu_id[nmu]/F"   )
        self.out.Branch( "mu_charge",   self.mu_charge   , "mu_charge[nmu]/F"  )
        self.out.Branch( "ntau",    self.ntau    , "ntau/I" )  
        self.out.Branch( "tau_pt",   self.tau_pt   , "tau_pt[ntau]/F"  )   
        self.out.Branch( "tau_eta",  self.tau_eta  , "tau_eta[ntau]/F" )
        self.out.Branch( "tau_phi",  self.tau_phi  , "tau_phi[ntau]/F" )
        self.out.Branch( "tau_charge",  self.tau_charge  , "tau_charge[ntau]/F" )
        self.out.Branch( "tau_idJet",   self.tau_idJet   , "tau_idJet[ntau]/F"  )
        self.out.Branch( "tau_idEle",   self.tau_idEle   , "tau_idEle[ntau]/F"  )
        self.out.Branch( "tau_idMuon",   self.tau_idMuon   , "tau_idMuon[ntau]/F"  )
        self.out.Branch( "tau_PNETidJet",   self.tau_PNETidJet   , "tau_PNETidJet[ntau]/F"  )
        self.out.Branch( "tau_PNETidEle",   self.tau_PNETidEle   , "tau_PNETidEle[ntau]/F"  )
        self.out.Branch( "tau_PNETidMuon",  self.tau_PNETidMuon  , "tau_PNETidMuon[ntau]/F"  )
        self.out.Branch( "nphot",    self.nphot    , "nphot/I" )  
        self.out.Branch( "phot_pt",  self.phot_pt  , "phot_pt[nphot]/F" )   
        self.out.Branch( "phot_eta", self.phot_eta , "phot_eta[nphot]/F")
        self.out.Branch( "phot_phi", self.phot_phi , "phot_phi[nphot]/F")
        self.out.Branch( "phot_id",  self.phot_id  , "phot_id[nphot]/F" )
        self.out.Branch( "phot_mvaid",  self.phot_mvaid  , "phot_mvaid[nphot]/F" )
        self.out.Branch( "phot_eleveto",  self.phot_eleveto  , "phot_eleveto[nphot]/F" )
        self.out.Branch( "MET_et",   self.MET_et   , "MET_et/F"  )   
        self.out.Branch( "MET_phi",  self.MET_phi  , "MET_phi/F" )
        self.out.Branch( "PUPPIMET_et",  self.PUPPIMET_et   , "PUPPIMET_et/F"  )   
        self.out.Branch( "PUPPIMET_phi", self.PUPPIMET_phi  , "PUPPIMET_phi/F"  )   
        # --

        # L1 jets
        self.L1_njets    = array('i',   [0])
        self.L1_jets_pt  = array('f',99*[0])
        self.L1_jets_eta = array('f',99*[0])
        self.L1_jets_phi = array('f',99*[0])


        
        # HLT objects
        self.HLT_njets    = array('i',   [0])
        self.HLT_jets_pt  = array('f',99*[0])
        self.HLT_jets_eta = array('f',99*[0])
        self.HLT_jets_phi = array('f',99*[0])
        self.HLT_jets_id  = array('f',99*[0])
        self.HLT_jets_l1pt= array('f',99*[0])

        self.HLT_nele     = array('i',   [0])
        self.HLT_ele_pt   = array('f',99*[0])
        self.HLT_ele_eta  = array('f',99*[0])
        self.HLT_ele_phi  = array('f',99*[0])
        self.HLT_ele_id   = array('f',99*[0])
        self.HLT_ele_l1pt = array('f',99*[0])

        self.HLT_nmu      = array('i',   [0])
        self.HLT_mu_pt    = array('f',99*[0])
        self.HLT_mu_eta   = array('f',99*[0])
        self.HLT_mu_phi   = array('f',99*[0])
        self.HLT_mu_id    = array('f',99*[0])
        self.HLT_mu_l1pt  = array('f',99*[0])

        self.HLT_ntau     = array('i',   [0])
        self.HLT_tau_pt   = array('f',99*[0])
        self.HLT_tau_eta  = array('f',99*[0])
        self.HLT_tau_phi  = array('f',99*[0])
        self.HLT_tau_id   = array('f',99*[0])
        self.HLT_tau_l1pt = array('f',99*[0])

        self.HLT_nphot    = array('i',   [0])
        self.HLT_phot_pt  = array('f',99*[0])
        self.HLT_phot_eta = array('f',99*[0])
        self.HLT_phot_phi = array('f',99*[0])
        self.HLT_phot_id  = array('f',99*[0])
        self.HLT_phot_l1pt= array('f',99*[0])

        self.out.Branch( "L1_njets",    self.L1_njets    , "L1_njets/I" )  
        self.out.Branch( "L1_jets_pt",  self.L1_jets_pt  , "L1_jets_pt[njets]/F" )   
        self.out.Branch( "L1_jets_eta", self.L1_jets_eta , "L1_jets_eta[njets]/F")
        self.out.Branch( "L1_jets_phi", self.L1_jets_phi , "L1_jets_phi[njets]/F")

        self.out.Branch( "HLT_njets",    self.HLT_njets    , "HLT_njets/I" )  
        self.out.Branch( "HLT_jets_pt",  self.HLT_jets_pt  , "HLT_jets_pt[njets]/F" )   
        self.out.Branch( "HLT_jets_eta", self.HLT_jets_eta , "HLT_jets_eta[njets]/F")
        self.out.Branch( "HLT_jets_phi", self.HLT_jets_phi , "HLT_jets_phi[njets]/F")
        self.out.Branch( "HLT_jets_id",  self.HLT_jets_id  , "HLT_jets_id[njets]/F" )
        self.out.Branch( "HLT_jets_l1pt",self.HLT_jets_l1pt, "HLT_jets_l1pt[njets]/F" )

        self.out.Branch( "HLT_nele",     self.HLT_nele     , "HLT_nele/I" )  
        self.out.Branch( "HLT_ele_pt",   self.HLT_ele_pt   , "HLT_ele_pt[nele]/F"  )   
        self.out.Branch( "HLT_ele_eta",  self.HLT_ele_eta  , "HLT_ele_eta[nele]/F" )
        self.out.Branch( "HLT_ele_phi",  self.HLT_ele_phi  , "HLT_ele_phi[nele]/F" )
        self.out.Branch( "HLT_ele_id",   self.HLT_ele_id   , "HLT_ele_id[nele]/F"  )
        self.out.Branch( "HLT_ele_l1pt", self.HLT_ele_l1pt , "HLT_ele_l1pt[njets]/F" )

        self.out.Branch( "HLT_nmu",      self.HLT_nmu      , "HLT_nmu/I" )  
        self.out.Branch( "HLT_mu_pt",    self.HLT_mu_pt    , "HLT_mu_pt[nmu]/F"   )   
        self.out.Branch( "HLT_mu_eta",   self.HLT_mu_eta   , "HLT_mu_eta[nmu]/F"  )
        self.out.Branch( "HLT_mu_phi",   self.HLT_mu_phi   , "HLT_mu_phi[nmu]/F"  )
        self.out.Branch( "HLT_mu_id",    self.HLT_mu_id    , "HLT_mu_id[nmu]/F"   )
        self.out.Branch( "HLT_mu_l1pt",  self.HLT_mu_l1pt  , "HLT_mu_l1pt[nmu]/F" )

        self.out.Branch( "HLT_ntau",     self.HLT_ntau     , "HLT_ntau/I" )  
        self.out.Branch( "HLT_tau_pt",   self.HLT_tau_pt   , "HLT_tau_pt[ntau]/F"  )   
        self.out.Branch( "HLT_tau_eta",  self.HLT_tau_eta  , "HLT_tau_eta[ntau]/F" )
        self.out.Branch( "HLT_tau_phi",  self.HLT_tau_phi  , "HLT_tau_phi[ntau]/F" )
        self.out.Branch( "HLT_tau_id",   self.HLT_tau_id   , "HLT_tau_id[ntau]/F"  )
        self.out.Branch( "HLT_tau_l1pt", self.HLT_tau_l1pt , "HLT_tau_l1pt[njets]/F" )

        self.out.Branch( "HLT_nphot",    self.HLT_nphot    , "HLT_nphot/I" )  
        self.out.Branch( "HLT_phot_pt",  self.HLT_phot_pt  , "HLT_phot_pt[nphot]/F" )   
        self.out.Branch( "HLT_phot_eta", self.HLT_phot_eta , "HLT_phot_eta[nphot]/F")
        self.out.Branch( "HLT_phot_phi", self.HLT_phot_phi , "HLT_phot_phi[nphot]/F")
        self.out.Branch( "HLT_phot_id",  self.HLT_phot_id  , "HLT_phot_id[nphot]/F" )
        self.out.Branch( "HLT_phot_l1pt",self.HLT_phot_l1pt, "HLT_phot_l1pt[njets]/F" )

        # --                         

        # HLT paths flags
        # --

        self.passVBFincl_2j = np.empty((1), dtype="float32")
        self.passVBFincl_3j = np.empty((1), dtype="float32")
        self.passVBFjets_4j = np.empty((1), dtype="float32")
        self.passVBFjets_5j = np.empty((1), dtype="float32")
        self.passVBFjets_6j = np.empty((1), dtype="float32")
        self.passVBFmet_2j  = np.empty((1), dtype="float32")
        self.passVBFmet_3j  = np.empty((1), dtype="float32")
        self.passVBFmu_2j   = np.empty((1), dtype="float32")
        self.passVBFmu_3j   = np.empty((1), dtype="float32")
        self.passVBFele     = np.empty((1), dtype="float32")
        self.passVBFphot    = np.empty((1), dtype="float32")
        self.passVBFtau     = np.empty((1), dtype="float32")
        self.passVBFtauPNet = np.empty((1), dtype="float32")
        self.passVBFditau   = np.empty((1), dtype="float32")
        self.passVBFditauPNet   = np.empty((1), dtype="float32")
        self.out.Branch("passVBFincl_2j", self.passVBFincl_2j , "passVBFincl_2j/F" )
        self.out.Branch("passVBFincl_3j", self.passVBFincl_3j , "passVBFincl_3j/F" )
        self.out.Branch("passVBFjets_4j", self.passVBFjets_4j , "passVBFjets_4j/F" )
        self.out.Branch("passVBFjets_5j", self.passVBFjets_5j , "passVBFjets_5j/F" )
        self.out.Branch("passVBFjets_6j", self.passVBFjets_6j , "passVBFjets_6j/F" )
        self.out.Branch("passVBFmet_2j" , self.passVBFmet_2j  , "passVBFmet_2j/F"  )
        self.out.Branch("passVBFmet_3j" , self.passVBFmet_3j  , "passVBFmet_3j/F"  )
        self.out.Branch("passVBFmu_2j"  , self.passVBFmu_2j   , "passVBFmu_2j/F"   )
        self.out.Branch("passVBFmu_3j"  , self.passVBFmu_3j   , "passVBFmu_3j/F"   )
        self.out.Branch("passVBFele"    , self.passVBFele     , "passVBFele/F"     )
        self.out.Branch("passVBFphot"   , self.passVBFphot    , "passVBFphot/F"    )
        self.out.Branch("passVBFtau"    , self.passVBFtau     , "passVBFtau/F"     )
        self.out.Branch("passVBFtauPNet", self.passVBFtauPNet , "passVBFtauPNet/F"     )
        self.out.Branch("passVBFditau"    , self.passVBFditau     , "passVBFditau/F"     )
        self.out.Branch("passVBFditauPNet", self.passVBFditauPNet , "passVBFditauPNet/F"     )


        self.passHHparking = np.empty((1), dtype="float32")
        self.out.Branch("passHHparking", self.passHHparking, "passHHparking/F" )
        self.passHHparking_ref = np.empty((1), dtype="float32")
        self.out.Branch("passHHparking_ref", self.passHHparking_ref, "passHHparking_ref/F" )

        self.passHHparking_tau = np.empty((1), dtype="float32")
        self.out.Branch("passHHparking_tau", self.passHHparking_tau, "passHHparking_tau/F" )
        self.passHHparking_tauref1 = np.empty((1), dtype="float32")
        self.out.Branch("passHHparking_tauref1", self.passHHparking_tauref1, "passHHparking_tauref1/F" )
        self.passHHparking_tauref2 = np.empty((1), dtype="float32")
        self.out.Branch("passHHparking_tauref2", self.passHHparking_tauref2, "passHHparking_tauref2/F" )

        self.passHHparking_tau25 = np.empty((1), dtype="float32")
        self.out.Branch("passHHparking_tau25", self.passHHparking_tau25, "passHHparking_tau25/F" )
        self.passHHparking_tau25ref1 = np.empty((1), dtype="float32")
        self.out.Branch("passHHparking_tau25ref1", self.passHHparking_tau25ref1, "passHHparking_tau25ref1/F" )
        self.passHHparking_tau25ref2 = np.empty((1), dtype="float32")
        self.out.Branch("passHHparking_tau25ref2", self.passHHparking_tau25ref2, "passHHparking_tau25ref2/F" )



        self.passDiphotonMVA = np.empty((1), dtype="float32")
        self.out.Branch("passDiphotonMVA", self.passDiphotonMVA, "passDiphotonMVA/F" )
        
        self.passVBFmet_old_2j  = np.empty((1), dtype="float32")
        self.passVBFmet_old_3j  = np.empty((1), dtype="float32")
        self.out.Branch("passVBFmet_old_2j" , self.passVBFmet_old_2j  , "passVBFmet_old_2j/F"  )
        self.out.Branch("passVBFmet_old_3j" , self.passVBFmet_old_3j  , "passVBFmet_old_3j/F"  )


        # L1 seeds flags
        self.passL1VBFincl = np.empty((1), dtype="float32")
        self.passL1VBFjets = np.empty((1), dtype="float32")
        self.passL1VBFmet  = np.empty((1), dtype="float32")
        self.passL1VBFmu   = np.empty((1), dtype="float32")
        self.passL1VBFele  = np.empty((1), dtype="float32")
        self.passL1VBFphot = np.empty((1), dtype="float32")
        self.passL1VBFtau  = np.empty((1), dtype="float32")
        
        self.passL1VBFincl_bkp = np.empty((1), dtype="float32")
        self.passL1VBFjets_bkp = np.empty((1), dtype="float32")
        self.passL1VBFmet_bkp  = np.empty((1), dtype="float32")
        self.passL1VBFmu_bkp   = np.empty((1), dtype="float32")
        self.passL1VBFele_bkp  = np.empty((1), dtype="float32")
        self.passL1VBFphot_bkp = np.empty((1), dtype="float32")
        self.passL1VBFtau_bkp  = np.empty((1), dtype="float32")

        self.out.Branch("passL1VBFincl", self.passL1VBFincl , "passL1VBFincl/F" )
        self.out.Branch("passL1VBFjets", self.passL1VBFjets , "passL1VBFjets/F" )
        self.out.Branch("passL1VBFmet" , self.passL1VBFmet  , "passL1VBFmet/F"  )
        self.out.Branch("passL1VBFmu"  , self.passL1VBFmu   , "passL1VBFmu/F"   )
        self.out.Branch("passL1VBFele" , self.passL1VBFele  , "passL1VBFele/F"  )
        self.out.Branch("passL1VBFphot", self.passL1VBFphot , "passL1VBFphot/F" )
        self.out.Branch("passL1VBFtau" , self.passL1VBFtau  , "passL1VBFtau/F" )
        
        self.out.Branch("passL1VBFincl_bkp", self.passL1VBFincl_bkp , "passL1VBFincl_bkp/F" )
        self.out.Branch("passL1VBFjets_bkp", self.passL1VBFjets_bkp , "passL1VBFjets_bkp/F" )
        self.out.Branch("passL1VBFmet_bkp" , self.passL1VBFmet_bkp  , "passL1VBFmet_bkp/F"  )
        self.out.Branch("passL1VBFmu_bkp"  , self.passL1VBFmu_bkp   , "passL1VBFmu_bkp/F"   )
        self.out.Branch("passL1VBFele_bkp" , self.passL1VBFele_bkp  , "passL1VBFele_bkp/F"  )
        self.out.Branch("passL1VBFphot_bkp", self.passL1VBFphot_bkp , "passL1VBFphot_bkp/F" )
        self.out.Branch("passL1VBFtau_bkp" , self.passL1VBFtau_bkp  , "passL1VBFtau_bkp/F" )
        # --

        self.passL1HT280 = np.empty((1), dtype="float32")
        self.out.Branch("passL1HT280", self.passL1HT280, "passL1HT280/F" )

        self.passL1DiTau = np.empty((1), dtype="float32")
        self.out.Branch("passL1DiTau", self.passL1DiTau, "passL1DiTau/F" )

        self.passL1DiTauJet = np.empty((1), dtype="float32")
        self.out.Branch("passL1DiTauJet", self.passL1DiTauJet, "passL1DiTauJet/F" )





        # --

        self.addObject(self.out)


    def analyze(self, event):
        met       = Object(event, "MET") if 'Winter' in self.period else Object(event, "PFMET")
        PUPPImet  = Object(event, "PuppiMET")
        hlt       = Object(event, "HLT")
        PV        = Object(event, "PV" )
        PU        = Object(event, "PV")
        L1        = Object(event, "L1")
        jets      = Collection(event, "Jet")
        muons     = Collection(event,"Muon")
        photons   = Collection(event,"Photon")
        electrons = Collection(event,'Electron')
        taus      = Collection(event,'Tau')
        trigobj   = Collection(event,"TrigObj")
        #L1Jet     = Collection(event,"L1Jet")
        triggerVersion = self.triggerVersion
        
        #if event.run<367661: # First run including VBF paths for parking
        #    return False

        #custom check for hlt, returning 0 if path not defined in NanoAOD
        def hlt_accept(path):
            if hasattr(hlt,path):
                return eval('hlt.{}'.format(path))
            else:
                return 0

        def L1_accept(seed):
            if hasattr(L1,seed):
                return eval('L1.{}'.format(seed))
            else:
                return 0



        self.h_cutflow.Fill(0)

        goodmuons = [m for m in muons if m.pt>26. and m.tightId and abs(m.eta)<2.4]
        refAccept = hlt_accept('IsoMu24') and len(goodmuons)>=1
       
        # comment out for MC
        if not refAccept:
            return False
        self.h_cutflow.Fill(1)

        def jetID(jet): # 2024 jet ID requirements
            if abs(jet.eta) <= 2.6:
                return jet.chEmEF < 0.8 and \
                    jet.chMultiplicity > 0 and \
                    jet.chHEF > 0.01 and \
                    jet.nConstituents > 1 and \
                    jet.neEmEF < 0.9 and \
                    jet.muEF < 0.8 and \
                    jet.neHEF < 0.99
            if abs(jet.eta) > 2.6 and abs(jet.eta) <= 2.7:
                return jet.chEmEF < 0.8 and \
                    jet.neEmEF < 0.9 and \
                    jet.muEF < 0.8 and \
                    jet.neHEF < 0.99
            if abs(jet.eta) > 2.7 and abs(jet.eta) <= 3.0:
                return jet.neHEF < 0.99
            if abs(jet.eta) > 3.0:
                return jet.neEmEF < 0.40 and jet.neMultiplicity>=2
                
        
        
        ak4jets = [j for j in jets \
                   if  j.pt > 20 \
                   and abs(j.eta) < 4.7# \
                   #and jetID(j)
                   #and (j.jetId==6)
        #           and (j.chHEF>0.2)
        ]

        if len(ak4jets)<2:
            return False
        self.h_cutflow.Fill(2)

        self.njets[0]= len(ak4jets)
        for idx,j in enumerate(ak4jets):
            self.jets_pt[idx]  = ak4jets[idx].pt    
            self.jets_eta[idx] = ak4jets[idx].eta   
            self.jets_phi[idx] = ak4jets[idx].phi
            self.jets_id[idx]  = float(jetID(ak4jets[idx])) if '25' in self.period else ak4jets[idx].jetId
            self.jets_CHF[idx]  = ak4jets[idx].chHEF
            self.jets_rawfactor[idx]  = ak4jets[idx].rawFactor
            self.jets_btagPNetB[idx]       = ak4jets[idx].btagPNetB
            self.jets_btagPNetCvB[idx]     = ak4jets[idx].btagPNetCvB
            self.jets_btagPNetCvL[idx]     = ak4jets[idx].btagPNetCvL
            self.jets_btagPNetQvG[idx]     = ak4jets[idx].btagPNetQvG
            self.jets_btagPNetTauVJet[idx] = ak4jets[idx].btagPNetTauVJet

                
        self.nmu[0] = len(goodmuons)
        for idx, m in enumerate(goodmuons):
            self.mu_pt[idx]  = goodmuons[idx].pt      
            self.mu_eta[idx] = goodmuons[idx].eta     
            self.mu_phi[idx] = goodmuons[idx].phi     
            self.mu_id[idx]  = goodmuons[idx].tightId 
            self.mu_charge[idx]  = goodmuons[idx].charge

        phots = [p for p in photons if (p.pt > 10 and 
                                        abs(p.eta) < 1.4442 and 
                                        p.cutBased>2)]
        self.nphot[0] = len(phots)
        for idx, m in enumerate(phots):
            self.phot_pt[idx]  = phots[idx].pt      
            self.phot_eta[idx] = phots[idx].eta     
            self.phot_phi[idx] = phots[idx].phi     
            self.phot_id[idx]  = phots[idx].cutBased
            self.phot_mvaid[idx]  = phots[idx].mvaID_WP80
            self.phot_eleveto[idx] = phots[idx].electronVeto
              
        self.MET_et[0]  = met.pt
        self.MET_phi[0] = met.phi
        self.PUPPIMET_et[0]  = PUPPImet.pt
        self.PUPPIMET_phi[0] = PUPPImet.phi

        goodelectrons = [t for t in electrons if t.pt>20. and abs(t.eta)<2.4 ]
        self.nele[0] = len(goodelectrons)
        for idx, m in enumerate(goodelectrons):
            self.ele_pt[idx]  = goodelectrons[idx].pt      
            self.ele_eta[idx] = goodelectrons[idx].eta     
            self.ele_phi[idx] = goodelectrons[idx].phi     
            #self.ele_id[idx]  = goodelectrons[idx].mvaIso_Fall17V2_WP80
            self.ele_id[idx]  = goodelectrons[idx].mvaIso

        # no ID requirements, to do PNet/DeepTau comparisons
        goodtaus = [t for t in taus if t.pt>20. and abs(t.eta)<2.4]
        # loosest ID requirements
        #goodtaus = [t for t in taus if t.pt>20. and abs(t.eta)<2.4 and t.idDeepTau2018v2p5VSe>=1 and t.idDeepTau2018v2p5VSmu>=1 and t.idDeepTau2018v2p5VSjet>=1 ]
        # Tau POG recommendations for MuTau (i.e. this is what Tau CQM uses)
        #goodtaus = [t for t in taus if t.pt>20. and abs(t.eta)<2.4 and t.idDeepTau2018v2p5VSe>=2 and t.idDeepTau2018v2p5VSmu>=4 and t.idDeepTau2018v2p5VSjet>=5 ]
        self.ntau[0] = len(goodtaus)
        for idx, m in enumerate(goodtaus):
            self.tau_pt[idx]  = goodtaus[idx].pt      
            self.tau_eta[idx] = goodtaus[idx].eta     
            self.tau_phi[idx] = goodtaus[idx].phi
            self.tau_charge[idx] = goodtaus[idx].charge
            self.tau_idJet[idx]  = goodtaus[idx].idDeepTau2018v2p5VSjet
            self.tau_idEle[idx]  = goodtaus[idx].idDeepTau2018v2p5VSe
            self.tau_idMuon[idx] = goodtaus[idx].idDeepTau2018v2p5VSmu
            self.tau_PNETidJet[idx]  = goodtaus[idx].rawPNetVSjet
            self.tau_PNETidEle[idx]  = goodtaus[idx].rawPNetVSe
            self.tau_PNETidMuon[idx] = goodtaus[idx].rawPNetVSmu

        #print('getting triggers for {}'.format(self.period))
        if '23' in self.period:
            triggers = get_path_dict('23')
        elif '24' in self.period:
            triggers = get_path_dict('24')
        elif '25' in self.period:
            triggers = get_path_dict('25')

        if '23' in self.period:
            seeds = get_L1_dict('23')
        elif '24' in self.period:
            seeds = get_L1_dict('24')
        elif '25' in self.period:
            seeds = get_L1_dict('25')
            
            
        #hltAccept = hlt_accept(triggers["VBFincl"][0])

        self.passVBFincl_2j[0] = hlt_accept(triggers["VBFincl"][0])
        self.passVBFincl_3j[0] = hlt_accept(triggers["VBFincl"][1])

        self.passVBFjets_4j[0] = hlt_accept(triggers["VBFjets"][0])
        self.passVBFjets_5j[0] = hlt_accept(triggers["VBFjets"][1])
        self.passVBFjets_6j[0] = hlt_accept(triggers["VBFjets"][2])

        self.passVBFmet_2j[0]  = hlt_accept(triggers["VBFmet"][0])
        self.passVBFmet_3j[0]  = hlt_accept(triggers["VBFmet"][1])

        self.passVBFmu_2j[0]   = hlt_accept(triggers["VBFmu"][0])
        self.passVBFmu_3j[0]   = hlt_accept(triggers["VBFmu"][1])

        self.passVBFele[0]     = hlt_accept(triggers["VBFele"][0])
        self.passVBFphot[0]    = hlt_accept(triggers["VBFphot"][0])
        self.passVBFtau[0]     = 0 if "25" in self.period else hlt_accept(triggers["VBFtau"][0])
        self.passVBFtauPNet[0] = hlt_accept(triggers["VBFtauPNet"][0])
        self.passVBFditau[0]     = 0 if "25" in self.period else hlt_accept(triggers["VBFditau"][0])
        self.passVBFditauPNet[0] = hlt_accept(triggers["VBFditauPNet"][0])

        self.passVBFmet_old_2j[0]  = 0#hlt_accept("DiJet110_35_Mjj650_PFMET110")
        self.passVBFmet_old_3j[0]  = 0#hlt_accept("TripleJet110_35_35_Mjj650_PFMET110")
  
        self.passHHparking[0]     = hlt_accept("PFHT250_QuadPFJet25_PNet2BTagMean0p55")
        self.passHHparking_ref[0] = hlt_accept("PFHT250_QuadPFJet25")
        self.passHHparking_tau[0] = hlt_accept("PFHT250_QuadPFJet25_PNet1BTag0p20_PNet1Tauh0p50")
        self.passHHparking_tauref1[0] = hlt_accept("IsoMu24_eta2p1_PFHT250_QuadPFJet25_PNet1Tauh0p50")
        self.passHHparking_tauref2[0] = hlt_accept("IsoMu24_eta2p1_PFHT250_QuadPFJet25")
        
        self.passHHparking_tau25[0] = hlt_accept("L1HT200_QuadPFJet20_PNet1BTag0p50_PNet1Tauh0p50")
        self.passHHparking_tau25ref1[0] = hlt_accept("IsoMu24_eta2p1_L1HT200_QuadPFJet25_PNet1Tauh0p50")
        self.passHHparking_tau25ref2[0] = hlt_accept("IsoMu24_eta2p1_L1HT200_QuadPFJet25")

        
        self.passDiphotonMVA[0] = 0 #0 if event.run < 380963 else hlt_accept("DiphotonMVA14p25_Mass90") ### FIXME: different paths for 24 & 25

        
        self.passL1VBFincl[0] = L1_accept(seeds["VBFincl"][0])
        self.passL1VBFjets[0] = L1_accept(seeds["VBFjets"][0])
        self.passL1VBFmet[0]  = L1_accept(seeds["VBFmet"][0])
        self.passL1VBFmu[0]   = L1_accept(seeds["VBFmu"][0])
        self.passL1VBFele[0]  = L1_accept(seeds["VBFele"][0])
        self.passL1VBFphot[0] = L1_accept(seeds["VBFphot"][0])
        self.passL1VBFtau[0]  = L1_accept(seeds["VBFtau"][0])
        
        self.passL1VBFincl_bkp[0] = L1_accept(seeds["VBFincl"][2])
        self.passL1VBFjets_bkp[0] = L1_accept(seeds["VBFjets"][2])
        self.passL1VBFmet_bkp[0]  = L1_accept(seeds["VBFmet"][2])
        self.passL1VBFmu_bkp[0]   = L1_accept(seeds["VBFmu"][2])
        self.passL1VBFele_bkp[0]  = L1_accept(seeds["VBFele"][2])
        self.passL1VBFphot_bkp[0] = L1_accept(seeds["VBFphot"][2])
        self.passL1VBFtau_bkp[0]  = L1_accept(seeds["VBFtau"][2])
            


        self.passL1HT280[0] = L1.HTT280er
        self.passL1DiTau[0] = L1.DoubleIsoTau34er2p1
        self.passL1DiTauJet[0] = L1.DoubleTau_Iso34_Iso23_er2p1_Jet55_RmOvlp_dR0p5







        # save trigger objects
        #ID of the object: 11 = Electron (PixelMatched e/gamma), 22 = Photon (PixelMatch-vetoed e/gamma), 13 = Muon, 15 = Tau, 1 = Jet, 6 = FatJet, 2 = MET, 3 = HT, 4 = MHT
        triggerJets = [obj for obj in trigobj if obj.id==1]
        triggerEle  = [obj for obj in trigobj if obj.id==11]
        triggerMu   = [obj for obj in trigobj if obj.id==13]
        triggerPhot = [obj for obj in trigobj if obj.id==22]
        triggerTau  = [obj for obj in trigobj if obj.id==15]
        triggerMET  = [obj for obj in trigobj if obj.id==2]


#        self.L1_njets[0] = len(L1Jet)
#        if len(L1Jet)>0:
#            for idx, m in enumerate(L1Jet):
#        
#                self.L1_jets_pt[idx]  = L1Jet[idx].pt      
#                self.L1_jets_eta[idx] = L1Jet[idx].eta     
#                self.L1_jets_phi[idx] = L1Jet[idx].phi     



        
        self.HLT_njets[0] = len(triggerJets)
        if len(triggerJets)>0:
            for idx, m in enumerate(triggerJets):
                self.HLT_jets_pt[idx]  = triggerJets[idx].pt      
                self.HLT_jets_eta[idx] = triggerJets[idx].eta     
                self.HLT_jets_phi[idx] = triggerJets[idx].phi     
                self.HLT_jets_id[idx]  = triggerJets[idx].filterBits
                self.HLT_jets_l1pt[idx] = triggerJets[idx].l1pt

        self.HLT_nele[0] = len(triggerEle)
        if len(triggerEle)>0:
            for idx, m in enumerate(triggerEle):
                self.HLT_ele_pt[idx]  = triggerEle[idx].pt      
                self.HLT_ele_eta[idx] = triggerEle[idx].eta     
                self.HLT_ele_phi[idx] = triggerEle[idx].phi     
                self.HLT_ele_id[idx]  = triggerEle[idx].filterBits
                self.HLT_ele_l1pt[idx] = triggerEle[idx].l1pt

        self.HLT_nmu[0] = len(triggerMu)
        if len(triggerMu)>0:
            for idx, m in enumerate(triggerMu):
                self.HLT_mu_pt[idx]  = triggerMu[idx].pt      
                self.HLT_mu_eta[idx] = triggerMu[idx].eta     
                self.HLT_mu_phi[idx] = triggerMu[idx].phi     
                self.HLT_mu_id[idx]  = triggerMu[idx].filterBits
                self.HLT_mu_l1pt[idx] = triggerMu[idx].l1pt

        self.HLT_nphot[0] = len(triggerPhot)
        if len(triggerPhot)>0:
            for idx, m in enumerate(triggerPhot):
                self.HLT_phot_pt[idx]  = triggerPhot[idx].pt      
                self.HLT_phot_eta[idx] = triggerPhot[idx].eta     
                self.HLT_phot_phi[idx] = triggerPhot[idx].phi     
                self.HLT_phot_id[idx]  = triggerPhot[idx].filterBits
                self.HLT_phot_l1pt[idx] = triggerPhot[idx].l1pt

        self.HLT_ntau[0] = len(triggerTau)
        if len(triggerTau)>0:
            for idx, m in enumerate(triggerTau):
                self.HLT_tau_pt[idx]  = triggerTau[idx].pt      
                self.HLT_tau_eta[idx] = triggerTau[idx].eta     
                self.HLT_tau_phi[idx] = triggerTau[idx].phi     
                self.HLT_tau_id[idx]  = triggerTau[idx].filterBits
                self.HLT_tau_l1pt[idx] = triggerTau[idx].l1pt

        self.run[0] = event.run
        self.luminosityBlock[0] = event.luminosityBlock
        self.event[0] = event.event
        self.bunchCrossing[0] = event.bunchCrossing
        self.npv[0] = PV.npvs
        #self.npu[0] = PU.nPU
        self.npu[0] = PU.npvs


        self.out.Fill()

        return True


TrigBtagAnalysisConstr = lambda: TrigBtagAnalysis()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Args')
    
    parser.add_argument('--version', default='VBFparking')
    parser.add_argument('--era', default = '24B',
                        choices = ['23C','23D',
                                   '24B','24C','24D','24E','24F','24G','24H','24I','24ABC',
                                   '25B','25C','25BC',
                                   'Winter23', 'Winter24']) # more to be added
    parser.add_argument('--input', default = '/store/data/Run2023C/Muon0/NANOAOD/PromptNanoAODv12_v2-v2/2820000/c4f41a7d-89c6-46dc-bad4-e83ab5ea39ed.root') # ~50k evts
    parser.add_argument('--outdir', default = './')
    parser.add_argument('--id', default = '')
    args = parser.parse_args()

    preselection="1"

    #files = ['root://cms-xrd-global.cern.ch/' + args.input if '/store/' in args.input else args.input]
    files = []
    with open('Zmu_nano_grouped.tmp.txt', 'r') as f:
        files = [line.strip() for line in f if line.strip()]

    print(files)

    histFile = f"{args.outdir}/histos_{args.era}_{args.version}_{args.id}.root"
#python3 vbf_ntuples.py --era 25BC --version 250625_ZmuSkims_noL1Jet --outdir /eos/user/l/lportale/VBFparkingNtuples --input /eos/home-l/lportale/STEAM/RAWtoNANO/nanoaod_0.root --id 0

    golden_json={
        "23C": './data/golden_json/Cert_Collisions2023_eraC_367095_368224_Golden.json',
        "24B": './data/golden_json/Cert_Collisions2024_eraB_Golden.json',
        "24C": './data/golden_json/Cert_Collisions2024_eraC_Golden.json',
        "24D": './data/golden_json/Cert_Collisions2024_eraD_Golden.json',
        "24E": './data/golden_json/Cert_Collisions2024_eraE_Golden.json',
        "24F": './data/golden_json/Cert_Collisions2024_eraF_Golden.json',
        #"24Ev2": './data/golden_json/Cert_Collisions2024_381477_381594_Golden.json',
    }
    if args.era in golden_json:
        p=PostProcessor(
            ".",
            files,
            cut=preselection,
            branchsel=None,
            modules=[TrigBtagAnalysisConstr()],
            noOut=True,
            histFileName=histFile,
            histDirName="VBFNanoAOD",
            jsonInput=golden_json[args.era]
        )
    else: # no golden json (yet) for 24
        p=PostProcessor(
            ".",
            files,
            cut=preselection,
            branchsel=None,
            modules=[TrigBtagAnalysisConstr()],
            noOut=True,
            histFileName=histFile,
            histDirName="VBFNanoAOD",
        )
        
    p.run()
