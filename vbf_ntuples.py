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
        
    else:
        print("VBF paths only available for 2023 & 2024!")
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
        self.ntau     = array('i',   [0])
        self.tau_pt   = array('f',99*[0])
        self.tau_eta  = array('f',99*[0])
        self.tau_phi  = array('f',99*[0])
        self.tau_idJet   = array('f',99*[0])
        self.tau_idEle   = array('f',99*[0])
        self.tau_idMuon  = array('f',99*[0])
        self.nphot    = array('i',   [0])
        self.phot_pt  = array('f',99*[0])
        self.phot_eta = array('f',99*[0])
        self.phot_phi = array('f',99*[0])
        self.phot_id  = array('f',99*[0])
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
        self.out.Branch( "ntau",    self.ntau    , "ntau/I" )  
        self.out.Branch( "tau_pt",   self.tau_pt   , "tau_pt[ntau]/F"  )   
        self.out.Branch( "tau_eta",  self.tau_eta  , "tau_eta[ntau]/F" )
        self.out.Branch( "tau_phi",  self.tau_phi  , "tau_phi[ntau]/F" )
        self.out.Branch( "tau_idJet",   self.tau_idJet   , "tau_idJet[ntau]/F"  )
        self.out.Branch( "tau_idEle",   self.tau_idEle   , "tau_idEle[ntau]/F"  )
        self.out.Branch( "tau_idMuon",   self.tau_idMuon   , "tau_idMuon[ntau]/F"  )
        self.out.Branch( "nphot",    self.nphot    , "nphot/I" )  
        self.out.Branch( "phot_pt",  self.phot_pt  , "phot_pt[nphot]/F" )   
        self.out.Branch( "phot_eta", self.phot_eta , "phot_eta[nphot]/F")
        self.out.Branch( "phot_phi", self.phot_phi , "phot_phi[nphot]/F")
        self.out.Branch( "phot_id",  self.phot_id  , "phot_id[nphot]/F" )
        self.out.Branch( "MET_et",   self.MET_et   , "MET_et/F"  )   
        self.out.Branch( "MET_phi",  self.MET_phi  , "MET_phi/F" )
        self.out.Branch( "PUPPIMET_et",  self.PUPPIMET_et   , "PUPPIMET_et/F"  )   
        self.out.Branch( "PUPPIMET_phi", self.PUPPIMET_phi  , "PUPPIMET_phi/F"  )   
        # --

        # HLT objects
        self.HLT_njets    = array('i',   [0])
        self.HLT_jets_pt  = array('f',99*[0])
        self.HLT_jets_eta = array('f',99*[0])
        self.HLT_jets_phi = array('f',99*[0])
        self.HLT_jets_id  = array('f',99*[0])
        self.HLT_nele     = array('i',   [0])
        self.HLT_ele_pt   = array('f',99*[0])
        self.HLT_ele_eta  = array('f',99*[0])
        self.HLT_ele_phi  = array('f',99*[0])
        self.HLT_ele_id   = array('f',99*[0])
        self.HLT_nmu      = array('i',   [0])
        self.HLT_mu_pt    = array('f',99*[0])
        self.HLT_mu_eta   = array('f',99*[0])
        self.HLT_mu_phi   = array('f',99*[0])
        self.HLT_mu_id    = array('f',99*[0])
        self.HLT_ntau     = array('i',   [0])
        self.HLT_tau_pt   = array('f',99*[0])
        self.HLT_tau_eta  = array('f',99*[0])
        self.HLT_tau_phi  = array('f',99*[0])
        self.HLT_tau_id   = array('f',99*[0])
        self.HLT_nphot    = array('i',   [0])
        self.HLT_phot_pt  = array('f',99*[0])
        self.HLT_phot_eta = array('f',99*[0])
        self.HLT_phot_phi = array('f',99*[0])
        self.HLT_phot_id  = array('f',99*[0])
        self.out.Branch( "HLT_njets",    self.HLT_njets    , "HLT_njets/I" )  
        self.out.Branch( "HLT_jets_pt",  self.HLT_jets_pt  , "HLT_jets_pt[njets]/F" )   
        self.out.Branch( "HLT_jets_eta", self.HLT_jets_eta , "HLT_jets_eta[njets]/F")
        self.out.Branch( "HLT_jets_phi", self.HLT_jets_phi , "HLT_jets_phi[njets]/F")
        self.out.Branch( "HLT_jets_id",  self.HLT_jets_id  , "HLT_jets_id[njets]/F" )
        self.out.Branch( "HLT_nele",     self.HLT_nele     , "HLT_nele/I" )  
        self.out.Branch( "HLT_ele_pt",   self.HLT_ele_pt   , "HLT_ele_pt[nele]/F"  )   
        self.out.Branch( "HLT_ele_eta",  self.HLT_ele_eta  , "HLT_ele_eta[nele]/F" )
        self.out.Branch( "HLT_ele_phi",  self.HLT_ele_phi  , "HLT_ele_phi[nele]/F" )
        self.out.Branch( "HLT_ele_id",   self.HLT_ele_id   , "HLT_ele_id[nele]/F"  )
        self.out.Branch( "HLT_nmu",      self.HLT_nmu      , "HLT_nmu/I" )  
        self.out.Branch( "HLT_mu_pt",    self.HLT_mu_pt    , "HLT_mu_pt[nmu]/F"   )   
        self.out.Branch( "HLT_mu_eta",   self.HLT_mu_eta   , "HLT_mu_eta[nmu]/F"  )
        self.out.Branch( "HLT_mu_phi",   self.HLT_mu_phi   , "HLT_mu_phi[nmu]/F"  )
        self.out.Branch( "HLT_mu_id",    self.HLT_mu_id    , "HLT_mu_id[nmu]/F"   )
        self.out.Branch( "HLT_ntau",     self.HLT_ntau     , "HLT_ntau/I" )  
        self.out.Branch( "HLT_tau_pt",   self.HLT_tau_pt   , "HLT_tau_pt[ntau]/F"  )   
        self.out.Branch( "HLT_tau_eta",  self.HLT_tau_eta  , "HLT_tau_eta[ntau]/F" )
        self.out.Branch( "HLT_tau_phi",  self.HLT_tau_phi  , "HLT_tau_phi[ntau]/F" )
        self.out.Branch( "HLT_tau_id",   self.HLT_tau_id   , "HLT_tau_id[ntau]/F"  )
        self.out.Branch( "HLT_nphot",    self.HLT_nphot    , "HLT_nphot/I" )  
        self.out.Branch( "HLT_phot_pt",  self.HLT_phot_pt  , "HLT_phot_pt[nphot]/F" )   
        self.out.Branch( "HLT_phot_eta", self.HLT_phot_eta , "HLT_phot_eta[nphot]/F")
        self.out.Branch( "HLT_phot_phi", self.HLT_phot_phi , "HLT_phot_phi[nphot]/F")
        self.out.Branch( "HLT_phot_id",  self.HLT_phot_id  , "HLT_phot_id[nphot]/F" )
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
        self.out.Branch("passL1VBFincl", self.passL1VBFincl , "passL1VBFincl/F" )
        self.out.Branch("passL1VBFjets", self.passL1VBFjets , "passL1VBFjets/F" )
        self.out.Branch("passL1VBFmet" , self.passL1VBFmet  , "passL1VBFmet/F"  )
        self.out.Branch("passL1VBFmu"  , self.passL1VBFmu   , "passL1VBFmu/F"   )
        self.out.Branch("passL1VBFele" , self.passL1VBFele  , "passL1VBFele/F"  )
        self.out.Branch("passL1VBFphot", self.passL1VBFphot , "passL1VBFphot/F" )
        self.out.Branch("passL1VBFtau" , self.passL1VBFtau  , "passL1VBFtau/F" )
        # --

        # --

        self.addObject(self.out)


    def analyze(self, event):
        met = Object(event, "PFMET")
        PUPPImet = Object(event, "PuppiMET")
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
        triggerVersion = self.triggerVersion
        
        #if event.run<367661: # First run including VBF paths for parking
        #    return False

        #custom check for hlt, returning 0 if path not defined in NanoAOD
        def hlt_accept(path):
            if hasattr(hlt,path):
                return eval('hlt.{}'.format(path))
            else:
                return 0

        self.h_cutflow.Fill(0)

        goodmuons = [m for m in muons if m.pt>26. and m.tightId and abs(m.eta)<2.4]
        refAccept = hlt_accept('IsoMu24') and len(goodmuons)>=1
       
        # comment out for MC
        if not refAccept:
            return False
        self.h_cutflow.Fill(1)

        ak4jets = [j for j in jets \
                   if  j.pt > 20 \
                   and abs(j.eta) < 4.7 \
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
            self.jets_id[idx]  = ak4jets[idx].jetId
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


        phots = [p for p in photons if (p.pt > 20 and 
                                        abs(p.eta) < 1.4442 and 
                                        p.cutBased>2)]
        self.nphot[0] = len(phots)
        for idx, m in enumerate(phots):
            self.phot_pt[idx]  = phots[idx].pt      
            self.phot_eta[idx] = phots[idx].eta     
            self.phot_phi[idx] = phots[idx].phi     
            self.phot_id[idx]  = phots[idx].cutBased
              
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

        # Tau reccomendation for MuTau FS is VVLoose vs Electron, Tight vs Muon, Medium vs Jet
        goodtaus = [t for t in taus if t.pt>20. and abs(t.eta)<2.4 and t.idDeepTau2018v2p5VSe>=1 and t.idDeepTau2018v2p5VSmu>=1 and t.idDeepTau2018v2p5VSjet>=1 ]
        self.ntau[0] = len(goodtaus)
        for idx, m in enumerate(goodtaus):
            self.tau_pt[idx]  = goodtaus[idx].pt      
            self.tau_eta[idx] = goodtaus[idx].eta     
            self.tau_phi[idx] = goodtaus[idx].phi     
            self.tau_idJet[idx]  = goodtaus[idx].idDeepTau2018v2p5VSjet
            self.tau_idEle[idx]  = goodtaus[idx].idDeepTau2018v2p5VSe
            self.tau_idMuon[idx] = goodtaus[idx].idDeepTau2018v2p5VSmu

        #print('getting triggers for {}'.format(self.period))
        if '23' in self.period:
            triggers = get_path_dict('23')
        elif '24' in self.period:
            triggers = get_path_dict('24')
            
        hltAccept = hlt_accept(triggers["VBFincl"][0])

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
        self.passVBFtau[0]     = hlt_accept(triggers["VBFtau"][0])
        self.passVBFtauPNet[0] = hlt_accept(triggers["VBFtauPNet"][0])
        self.passVBFditau[0]     = hlt_accept(triggers["VBFditau"][0])
        self.passVBFditauPNet[0] = hlt_accept(triggers["VBFditauPNet"][0])

        self.passVBFmet_old_2j[0]  = 0#hlt_accept("DiJet110_35_Mjj650_PFMET110")
        self.passVBFmet_old_3j[0]  = 0#hlt_accept("TripleJet110_35_35_Mjj650_PFMET110")
  
        self.passHHparking[0]     = 0#hlt_accept("PFHT280_QuadPFJet30_PNet2BTagMean0p55")
        self.passHHparking_ref[0] = 0#hlt_accept("PFHT280_QuadPFJet30")


        if '23' in self.period:
            self.passL1VBFincl[0] = L1.DoubleJet_90_30_DoubleJet30_Mass_Min620
            if '23D' in self.period: 
                self.passL1VBFincl[0] = L1.DoubleJet_90_30_DoubleJet30_Mass_Min620 or \
                                        L1.DoubleJet_90_30_DoubleJet30_Mass_Min800
                
                self.passL1VBFjets[0] = L1.DoubleJet_60_30_DoubleJet30_Mass_Min500_DoubleJetCentral50
                self.passL1VBFmet[0]  = L1.DoubleJet_65_30_DoubleJet30_Mass_Min400_ETMHF65
                self.passL1VBFmu[0]   = L1.DoubleJet_80_30_DoubleJet30_Mass_Min500_Mu3OQ
                self.passL1VBFele[0]  = L1.DoubleJet40_Mass_Min450_IsoEG10er2p1_RmOvlp_dR0p2
                self.passL1VBFphot[0] = L1.DoubleJet40_Mass_Min450_IsoEG10er2p1_RmOvlp_dR0p2
                self.passL1VBFtau[0]  = L1.DoubleJet45_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5 or \
                                        L1.DoubleJet35_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5 
        elif '24' in self.period:
            self.passL1VBFincl[0] = L1.DoubleJet_110_35_DoubleJet35_Mass_Min800
                
            self.passL1VBFjets[0] = L1.DoubleJet_65_35_DoubleJet35_Mass_Min600_DoubleJetCentral50
            self.passL1VBFmet[0]  = L1.DoubleJet_70_35_DoubleJet35_Mass_Min500_ETMHF65
            self.passL1VBFmu[0]   = L1.DoubleJet_85_35_DoubleJet35_Mass_Min600_Mu3OQ
            self.passL1VBFele[0]  = L1.DoubleJet45_Mass_Min550_LooseIsoEG20er2p1_RmOvlp_dR0p2
            self.passL1VBFphot[0] = L1.DoubleJet45_Mass_Min550_LooseIsoEG20er2p1_RmOvlp_dR0p2
            self.passL1VBFtau[0]  = L1.DoubleJet45_Mass_Min550_IsoTau45er2p1_RmOvlp_dR0p5
 

        # save trigger objects
        #ID of the object: 11 = Electron (PixelMatched e/gamma), 22 = Photon (PixelMatch-vetoed e/gamma), 13 = Muon, 15 = Tau, 1 = Jet, 6 = FatJet, 2 = MET, 3 = HT, 4 = MHT
        triggerJets = [obj for obj in trigobj if obj.id==1]
        triggerEle  = [obj for obj in trigobj if obj.id==11]
        triggerMu   = [obj for obj in trigobj if obj.id==13]
        triggerPhot = [obj for obj in trigobj if obj.id==22]
        triggerTau  = [obj for obj in trigobj if obj.id==15]
        triggerMET  = [obj for obj in trigobj if obj.id==2]


        self.HLT_njets[0] = len(triggerJets)
        if len(triggerJets)>0:
            for idx, m in enumerate(triggerJets):
                self.HLT_jets_pt[idx]  = triggerJets[idx].pt      
                self.HLT_jets_eta[idx] = triggerJets[idx].eta     
                self.HLT_jets_phi[idx] = triggerJets[idx].phi     
                self.HLT_jets_id[idx]  = triggerJets[idx].filterBits

        self.HLT_nele[0] = len(triggerEle)
        if len(triggerEle)>0:
            for idx, m in enumerate(triggerEle):
                self.HLT_ele_pt[idx]  = triggerEle[idx].pt      
                self.HLT_ele_eta[idx] = triggerEle[idx].eta     
                self.HLT_ele_phi[idx] = triggerEle[idx].phi     
                self.HLT_ele_id[idx]  = triggerEle[idx].filterBits

        self.HLT_nmu[0] = len(triggerMu)
        if len(triggerMu)>0:
            for idx, m in enumerate(triggerMu):
                self.HLT_mu_pt[idx]  = triggerMu[idx].pt      
                self.HLT_mu_eta[idx] = triggerMu[idx].eta     
                self.HLT_mu_phi[idx] = triggerMu[idx].phi     
                self.HLT_mu_id[idx]  = triggerMu[idx].filterBits

        self.HLT_nphot[0] = len(triggerPhot)
        if len(triggerPhot)>0:
            for idx, m in enumerate(triggerPhot):
                self.HLT_phot_pt[idx]  = triggerPhot[idx].pt      
                self.HLT_phot_eta[idx] = triggerPhot[idx].eta     
                self.HLT_phot_phi[idx] = triggerPhot[idx].phi     
                self.HLT_phot_id[idx]  = triggerPhot[idx].filterBits

        self.HLT_ntau[0] = len(triggerTau)
        if len(triggerTau)>0:
            for idx, m in enumerate(triggerTau):
                self.HLT_tau_pt[idx]  = triggerTau[idx].pt      
                self.HLT_tau_eta[idx] = triggerTau[idx].eta     
                self.HLT_tau_phi[idx] = triggerTau[idx].phi     
                self.HLT_tau_id[idx]  = triggerTau[idx].filterBits
                

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
    
    parser.add_argument('--version', default='VBFincl',
                        choices = ['VBFincl',
                                   'VBFjets',
                                   'VBFmet',
                                   'VBFmu',
                                   'VBFele',
                                   'VBFphot',
                                   'VBFtau'])
    parser.add_argument('--era', default = '24B',
                        choices = ['23C','23D','24B','24C','24D','24E','24ABC','Winter23']) # more to be added
    parser.add_argument('--input', default = '/store/data/Run2023C/Muon0/NANOAOD/PromptNanoAODv12_v2-v2/2820000/c4f41a7d-89c6-46dc-bad4-e83ab5ea39ed.root') # ~50k evts
    parser.add_argument('--outdir', default = './')
    parser.add_argument('--id', default = '')
    args = parser.parse_args()

    preselection="1"

    files = ['root://cms-xrd-global.cern.ch/' + args.input if '/store/' in args.input else args.input]
    print(files)

    histFile = f"{args.outdir}/histos_{args.era}_{args.version}_{args.id}.root"

    golden_json={
        "23C": './data/golden_json/Cert_Collisions2023_eraC_367095_368224_Golden.json',
        "24B": './data/golden_json/Cert_Collisions2024_eraB_Golden.json',
        "24C": './data/golden_json/Cert_Collisions2024_eraC_Golden.json',
        # D and E use a big JSON which contains C, D, Ev1, and Ev2
        "24D": './data/golden_json/Cert_Collisions2024_378981_381594_Golden.json',
        "24E": './data/golden_json/Cert_Collisions2024_378981_381594_Golden.json',
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
