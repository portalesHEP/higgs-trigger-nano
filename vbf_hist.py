#!/usr/bin/env python
import ROOT
import math 
import time
import os
import numpy as np
from array import array
import uproot
import pandas as pd
import argparse

# highest mjj among all jet pairs (with pT>60 GeV, id tight) + additional variables for VBF jets
ROOT.gInterpreter.Declare('''
float get_VBF_var(TString var,
                  ROOT::VecOps::RVec<Float_t> pt,
                  ROOT::VecOps::RVec<Float_t> eta,
                  ROOT::VecOps::RVec<Float_t> phi,
                  ROOT::VecOps::RVec<Float_t> id,
                  ROOT::VecOps::RVec<Float_t> chf,
                  ROOT::VecOps::RVec<Float_t> rawfactor,
                  Float_t pt1cut,
                  Float_t pt2cut,
                  Float_t idcut,
                  Bool_t applyRawFactor) {
    
    Double_t mjj      = -1;
    Double_t detajj   = -1;
    Double_t etabest  = -999;
    Double_t etabest2 = -999;
    Double_t ptbest  = -999;
    Double_t ptbest2 = -999;
    Double_t chfbest  = -1;
    Double_t chfbest2 = -1;
    Int_t idx_vbf1 = -1;
    Int_t idx_vbf2 = -1;

    const auto size = pt.size();
    for (size_t idx1=0; idx1<size; ++idx1){
        for (size_t idx2=0; idx2<idx1; ++idx2){
        
            // VBF jets have to pass the ptcut2
            if (pt[idx1]<pt2cut || pt[idx2]<pt2cut)
                continue;
                           
            // in any case, we want tightly ID'd jets (just a safety, the condition should never be true)
            if (id[idx1]<idcut || id[idx2]<idcut)
                continue;
            
            // if minimal selection applies, get thtPt
            ROOT::Math::PtEtaPhiMVector p1,p2;
            if(!applyRawFactor){
                p1.SetPt(pt[idx1]).SetEta(eta[idx1]).SetPhi(phi[idx1]).SetM(0.);
                p2.SetPt(pt[idx2]).SetEta(eta[idx2]).SetPhi(phi[idx2]).SetM(0.);
            } else {
                p1.SetPt(pt[idx1]*(1.-rawfactor[idx1])).SetEta(eta[idx1]).SetPhi(phi[idx1]).SetM(0.);
                p2.SetPt(pt[idx2]*(1.-rawfactor[idx2])).SetEta(eta[idx2]).SetPhi(phi[idx2]).SetM(0.);
            }
            // check if the pair has best mjj, if so store VBF jets quantities
            if ((p1+p2).mass() > mjj) {
                mjj      = (p1+p2).mass();
                detajj   = abs(eta[idx1]-eta[idx2]);
                etabest  = (p1.pt()>p2.pt()) ? p1.eta():p2.eta();
                etabest2 = (p1.pt()>p2.pt()) ? p2.eta():p1.eta();
                ptbest   = (p1.pt()>p2.pt()) ? p1.pt():p2.pt();
                ptbest2  = (p1.pt()>p2.pt()) ? p2.pt():p1.pt();
                chfbest  = (p1.pt()>p2.pt()) ? chf[idx1]:chf[idx2];
                chfbest2 = (p1.pt()>p2.pt()) ? chf[idx2]:chf[idx1];
                idx_vbf1 = idx1;
                idx_vbf2 = idx2;
            }
        }
    }
    if (var=="mjj") 
        return mjj;
    if (var=="detajj")
        return detajj;
    if (var=="eta")
        return etabest;
    if (var=="eta2")
        return etabest2;
    if (var=="pt")
        return ptbest;
    if (var=="pt2")
        return ptbest2;
    if (var=="chf")
        return chfbest;
    if (var=="chf2")
        return chfbest2;
    if (var=="idx1")
        return idx_vbf1;
    if (var=="idx2")
        return idx_vbf2;

    return -999.;
}
'''
)

ROOT.gInterpreter.Declare('''
float get_metnomu(Float_t met_pt,
                  Float_t met_phi,
                  ROOT::VecOps::RVec<Float_t> mu_pt,
                  ROOT::VecOps::RVec<Float_t> mu_eta,
                  ROOT::VecOps::RVec<Float_t> mu_phi
                  ) {
    
            ROOT::Math::PtEtaPhiMVector pp1(met_pt, 0, met_phi, 0.);
            ROOT::Math::PtEtaPhiMVector pp2(mu_pt[0], mu_eta[0], mu_phi[0], 0.);
            return (pp1+pp2).pt();
}
'''
)

ROOT.gInterpreter.Declare('''
float good_tau_idx(ROOT::VecOps::RVec<Float_t> tau_pt,
                   ROOT::VecOps::RVec<Float_t> tau_eta,
                   ROOT::VecOps::RVec<Float_t> tau_idJet,
                   ROOT::VecOps::RVec<Float_t> tau_idMu,
                   ROOT::VecOps::RVec<Float_t> tau_idEle,
                   int secondTau
                  ) {
            float bestidx = -1;
            float secondidx = -1;
            const auto size = tau_pt.size();

            if(secondTau==1 && size<2) return bestidx;

            float bestpt=-1;
            float secondpt=-1;

            for (size_t idx1=0; idx1<size; ++idx1){
              if( !(fabs(tau_eta[idx1])<2.4 && tau_idJet[idx1]>=5 && tau_idMu[idx1]>=4 && tau_idEle[idx1] >=2) ) continue;

              if (tau_pt[idx1] > bestpt){
                bestpt = tau_pt[idx1];
                bestidx = idx1;
              } else if (tau_pt[idx1] > secondpt) {
                secondpt = tau_pt[idx1];
                secondidx = idx1;
              }
            }

            if(secondTau==1) return secondidx;
            return bestidx;

}
'''
)


ROOT.gInterpreter.Declare('''
int good_jet_idx(int idx, ROOT::VecOps::RVec<Float_t> jet_pt){
    int best_idx1=-1;
    int best_idx2=-1;
    float best_pt1 = -1;
    float best_pt2 = -1;

    if (jet_pt.size()<2)
        return -1;

    for (size_t idx1=0; idx1<jet_pt.size(); ++idx1){
        if (jet_pt[idx1]>best_pt1) {
            best_pt1 = jet_pt[idx1];
            best_idx1 = idx1;
        }
        else if (jet_pt[idx1]>best_pt2) {
            best_pt2 = jet_pt[idx1];
            best_idx2 = idx1;
        }
    }
    if (idx==1)
        return best_idx1;
    else if (idx==2)
        return best_idx2;
    else
        return -1;

}

''')
ROOT.gInterpreter.Declare('''
float get_dr(Float_t eta1,
             Float_t phi1,
             Float_t eta2,
             Float_t phi2) {
    
            Float_t deta2 = (eta1 - eta2) * (eta1 - eta2);
            Float_t dphi2 = (phi1 - phi2) * (phi1 - phi2);
            Float_t dr = sqrt(deta2 + dphi2);
            return dr;
}
'''
)

def generate_histos(infile, outfile):
    fout = ROOT.TFile.Open(outfile,"RECREATE")

    df = ROOT.RDataFrame('VBFNanoAOD/VBFtree',infile)

    veto_runs = [378994,378997,379000,379001,379002,379004,379006,379008,379009,379010,379315,379316,379317,379318,379337]
    for run in veto_runs:
        df = df.Filter('run!={}'.format(run))
    
    #################
    # VBF inclusive #
    #################
    
    #pt1cut = 155.
    #pt2cut = 60.
    #mjjcut = 1500.
    #idcut = 6
    pt1cut = 125.
    pt2cut = 50.
    mjjcut = 1500.
    idcut = 6
    
    df_base = df.Define('mjj2',    'get_VBF_var( "mjj", jets_pt,jets_eta,jets_phi,jets_id,jets_CHF,jets_rawfactor,{},{},{},0)'.format(pt1cut,pt2cut,idcut))\
                .Define('mjjl1',    'get_VBF_var( "mjj", L1_jets_pt,L1_jets_eta,L1_jets_phi,jets_id,jets_CHF,jets_rawfactor,{},{},{},0)'.format(110,35,0))\
                .Define('mjjl1_115_35',    'get_VBF_var( "mjj", L1_jets_pt,L1_jets_eta,L1_jets_phi,jets_id,jets_CHF,jets_rawfactor,{},{},{},0)'.format(115,35,0))\
                .Define('mjjl1_110_40',    'get_VBF_var( "mjj", L1_jets_pt,L1_jets_eta,L1_jets_phi,jets_id,jets_CHF,jets_rawfactor,{},{},{},0)'.format(110,40,0))\
                .Define('mjjl1_115_40',    'get_VBF_var( "mjj", L1_jets_pt,L1_jets_eta,L1_jets_phi,jets_id,jets_CHF,jets_rawfactor,{},{},{},0)'.format(115,40,0))\
                .Define('ptj1',  'jets_pt[0]')\
                .Define('ptj2', 'jets_pt[1]')\
                .Define('l1idx1', 'good_jet_idx(1,L1_jets_pt)')\
                .Define('l1idx2', 'good_jet_idx(2,L1_jets_pt)')\
                .Define('l1ptj1', 'L1_jets_pt[l1idx1]')\
                .Define('l1ptj2', 'L1_jets_pt[l1idx2]')

    df_den = {}
    df_den['mjj']    = df_base.Filter('jets_pt[0]>{} && jets_pt[1]>{}'.format(pt1cut,pt2cut))
    df_den['pt1']    = df_base.Filter('mjj2>{} && jets_pt[1]>{}'.format(mjjcut,pt2cut))
    df_den['pt2']    = df_base.Filter('mjj2>{} && jets_pt[0]>{}'.format(mjjcut,pt1cut))

    df_num = { 'mjj' : {}, 'pt1' : {}, 'pt2' : {}}
    df_num['mjj']['HLT'] = df_den['mjj'].Filter('passVBFincl_2j || passVBFincl_3j')
    df_num['mjj']['L1']  = df_den['mjj'].Filter('passL1VBFincl')
    df_num['pt1']['HLT'] = df_den['pt2'].Filter('passVBFincl_2j || passVBFincl_3j')
    df_num['pt1']['L1']  = df_den['pt2'].Filter('passL1VBFincl')
    df_num['pt2']['HLT'] = df_den['pt2'].Filter('passVBFincl_2j || passVBFincl_3j')
    df_num['pt2']['L1']  = df_den['pt2'].Filter('passL1VBFincl')
    
    df_num['mjj']['HLT_L1MOD1'] = df_den['mjj'].Filter('(passVBFincl_2j || passVBFincl_3j) && mjjl1>900.')
    df_num['mjj']['L1_L1MOD1']  = df_den['mjj'].Filter('passL1VBFincl && mjjl1>900.')
    df_num['mjj']['HLT_L1MOD2'] = df_den['mjj'].Filter('(passVBFincl_2j || passVBFincl_3j) && mjjl1>1000.')
    df_num['mjj']['L1_L1MOD2']  = df_den['mjj'].Filter('passL1VBFincl && mjjl1>1000.')
    df_num['mjj']['HLT_L1MOD3_115_40'] = df_den['mjj'].Filter('(passVBFincl_2j || passVBFincl_3j) && l1ptj1>115 && l1ptj2>40')
    df_num['mjj']['L1_L1MOD3_115_40']  = df_den['mjj'].Filter('passL1VBFincl && l1ptj1>115 && l1ptj2>40')
    df_num['mjj']['HLT_L1MOD3_115_35'] = df_den['mjj'].Filter('(passVBFincl_2j || passVBFincl_3j) && l1ptj1>115 && l1ptj2>35')
    df_num['mjj']['L1_L1MOD3_115_35']  = df_den['mjj'].Filter('passL1VBFincl && l1ptj1>115 && l1ptj2>35')
    df_num['mjj']['HLT_L1MOD3_110_40'] = df_den['mjj'].Filter('(passVBFincl_2j || passVBFincl_3j) && l1ptj1>110 && l1ptj2>40')
    df_num['mjj']['L1_L1MOD3_110_40']  = df_den['mjj'].Filter('passL1VBFincl && l1ptj1>110 && l1ptj2>40')

    df_num['pt1']['HLT_L1MOD1'] = df_den['pt1'].Filter('(passVBFincl_2j || passVBFincl_3j) && mjjl1>900.')
    df_num['pt1']['L1_L1MOD1']  = df_den['pt1'].Filter('passL1VBFincl && mjjl1>900.')
    df_num['pt1']['HLT_L1MOD2'] = df_den['pt1'].Filter('(passVBFincl_2j || passVBFincl_3j) && mjjl1>1000.')
    df_num['pt1']['L1_L1MOD2']  = df_den['pt1'].Filter('passL1VBFincl && mjjl1>1000.')
    df_num['pt1']['HLT_L1MOD3_115_40'] = df_den['pt1'].Filter('(passVBFincl_2j || passVBFincl_3j) && l1ptj1>115 && l1ptj2>40')
    df_num['pt1']['L1_L1MOD3_115_40']  = df_den['pt1'].Filter('passL1VBFincl && l1ptj1>115 && l1ptj2>40')
    df_num['pt1']['HLT_L1MOD3_115_35'] = df_den['pt1'].Filter('(passVBFincl_2j || passVBFincl_3j) && l1ptj1>115 && l1ptj2>35')
    df_num['pt1']['L1_L1MOD3_115_35']  = df_den['pt1'].Filter('passL1VBFincl && l1ptj1>115 && l1ptj2>35')
    df_num['pt1']['HLT_L1MOD3_110_40'] = df_den['pt1'].Filter('(passVBFincl_2j || passVBFincl_3j) && l1ptj1>110 && l1ptj2>40')
    df_num['pt1']['L1_L1MOD3_110_40']  = df_den['pt1'].Filter('passL1VBFincl && l1ptj1>110 && l1ptj2>40')
    
    df_num['pt2']['HLT_L1MOD1'] = df_den['pt2'].Filter('(passVBFincl_2j || passVBFincl_3j) && mjjl1>900.')
    df_num['pt2']['L1_L1MOD1']  = df_den['pt2'].Filter('passL1VBFincl && mjjl1>900.')
    df_num['pt2']['HLT_L1MOD2'] = df_den['pt2'].Filter('(passVBFincl_2j || passVBFincl_3j) && mjjl1>1000.')
    df_num['pt2']['L1_L1MOD2']  = df_den['pt2'].Filter('passL1VBFincl && mjjl1>1000.')
    df_num['pt2']['HLT_L1MOD3_115_40'] = df_den['pt2'].Filter('(passVBFincl_2j || passVBFincl_3j) && l1ptj1>115 && l1ptj2>40')
    df_num['pt2']['L1_L1MOD3_115_40']  = df_den['pt2'].Filter('passL1VBFincl && l1ptj1>115 && l1ptj2>40')
    df_num['pt2']['HLT_L1MOD3_115_35'] = df_den['pt2'].Filter('(passVBFincl_2j || passVBFincl_3j) && l1ptj1>115 && l1ptj2>35')
    df_num['pt2']['L1_L1MOD3_115_35']  = df_den['pt2'].Filter('passL1VBFincl && l1ptj1>115 && l1ptj2>35')
    df_num['pt2']['HLT_L1MOD3_110_40'] = df_den['pt2'].Filter('(passVBFincl_2j || passVBFincl_3j) && l1ptj1>110 && l1ptj2>40')
    df_num['pt2']['L1_L1MOD3_110_40']  = df_den['pt2'].Filter('passL1VBFincl && l1ptj1>110 && l1ptj2>40')
    
    hnum = {'mjj' : {}, 'pt1' : {}, 'pt2' : {}}
    hden = {}

    nbin = 25
    hden['mjj'] = df_den['mjj'].Histo1D(('hden','',   nbin,0,2500),'mjj2')
    hnum['mjj'] = { 'HLT': df_num['mjj']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,2500),'mjj2'),
                    'L1':  df_num['mjj']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,2500),'mjj2'),
                    'HLT_L1MOD1': df_num['mjj']['HLT_L1MOD1'].Histo1D( ('hnum_HLT_l1mod1','',    nbin,0,2500),'mjj2'),
                    'L1_L1MOD1':  df_num['mjj']['L1_L1MOD1'].Histo1D(  ('hnum_l1_l1mod1','',    nbin,0,2500),'mjj2'),
                    'HLT_L1MOD2': df_num['mjj']['HLT_L1MOD2'].Histo1D( ('hnum_HLT_l1mod2','',    nbin,0,2500),'mjj2'),
                    'L1_L1MOD2':  df_num['mjj']['L1_L1MOD2'].Histo1D(  ('hnum_l1_l1mod2','',    nbin,0,2500),'mjj2'),
                    'HLT_L1MOD3_115_40': df_num['mjj']['HLT_L1MOD3_115_40'].Histo1D( ('hnum_HLT_l1mod3_115_40','',   nbin,0,2500),'mjj2'),
                    'L1_L1MOD3_115_40':  df_num['mjj']['L1_L1MOD3_115_40'].Histo1D(  ('hnum_l1_l1mod3_115_40','',    nbin,0,2500),'mjj2'),
                    'HLT_L1MOD3_115_35': df_num['mjj']['HLT_L1MOD3_115_35'].Histo1D( ('hnum_HLT_l1mod3_115_35','',   nbin,0,2500),'mjj2'),
                    'L1_L1MOD3_115_35':  df_num['mjj']['L1_L1MOD3_115_35'].Histo1D(  ('hnum_l1_l1mod3_115_35','',    nbin,0,2500),'mjj2'),
                    'HLT_L1MOD3_110_40': df_num['mjj']['HLT_L1MOD3_110_40'].Histo1D( ('hnum_HLT_l1mod3_110_40','',   nbin,0,2500),'mjj2'),
                    'L1_L1MOD3_110_40':  df_num['mjj']['L1_L1MOD3_110_40'].Histo1D(  ('hnum_l1_l1mod3_110_40','',    nbin,0,2500),'mjj2'),
                   }
    
    hden['pt1'] = df_den['pt1'].Histo1D(('hden','',   nbin,0,300),'ptj1')
    hnum['pt1'] = { 'HLT': df_num['pt1']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,300),'ptj1'),
                    'L1':  df_num['pt1']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,300),'ptj1'),
                    'HLT_L1MOD1': df_num['pt1']['HLT_L1MOD1'].Histo1D( ('hnum_HLT_l1mod1','',    nbin,0,2500),'ptj1'),
                    'L1_L1MOD1':  df_num['pt1']['L1_L1MOD1'].Histo1D(  ('hnum_l1_l1mod1','',    nbin,0,2500),'ptj1'),
                    'HLT_L1MOD2': df_num['pt1']['HLT_L1MOD2'].Histo1D( ('hnum_HLT_l1mod2','',    nbin,0,2500),'ptj1'),
                    'L1_L1MOD2':  df_num['pt1']['L1_L1MOD2'].Histo1D(  ('hnum_l1_l1mod2','',    nbin,0,2500),'ptj1'),
                    'HLT_L1MOD3_115_40': df_num['pt1']['HLT_L1MOD3_115_40'].Histo1D( ('hnum_HLT_l1mod3_115_40','',   nbin,0,2500),'ptj1'),
                    'L1_L1MOD3_115_40':  df_num['pt1']['L1_L1MOD3_115_40'].Histo1D(  ('hnum_l1_l1mod3_115_40','',    nbin,0,2500),'ptj1'),
                    'HLT_L1MOD3_115_35': df_num['pt1']['HLT_L1MOD3_115_35'].Histo1D( ('hnum_HLT_l1mod3_115_35','',   nbin,0,2500),'ptj1'),
                    'L1_L1MOD3_115_35':  df_num['pt1']['L1_L1MOD3_115_35'].Histo1D(  ('hnum_l1_l1mod3_115_35','',    nbin,0,2500),'ptj1'),
                    'HLT_L1MOD3_110_40': df_num['pt1']['HLT_L1MOD3_110_40'].Histo1D( ('hnum_HLT_l1mod3_110_40','',   nbin,0,2500),'ptj1'),
                    'L1_L1MOD3_110_40':  df_num['pt1']['L1_L1MOD3_110_40'].Histo1D(  ('hnum_l1_l1mod3_110_40','',    nbin,0,2500),'ptj1')}

    hden['pt2'] = df_den['pt2'].Histo1D(('hden','',   nbin,0,200),'ptj2')
    hnum['pt2'] = { 'HLT': df_num['pt2']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,200),'ptj2'),
                    'L1':  df_num['pt2']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,200),'ptj2'),
                    'HLT_L1MOD1': df_num['pt2']['HLT_L1MOD1'].Histo1D( ('hnum_HLT_l1mod1','',    nbin,0,2500),'ptj2'),
                    'L1_L1MOD1':  df_num['pt2']['L1_L1MOD1'].Histo1D(  ('hnum_l1_l1mod1','',    nbin,0,2500),'ptj2'),
                    'HLT_L1MOD2': df_num['pt2']['HLT_L1MOD2'].Histo1D( ('hnum_HLT_l1mod2','',    nbin,0,2500),'ptj2'),
                    'L1_L1MOD2':  df_num['pt2']['L1_L1MOD2'].Histo1D(  ('hnum_l1_l1mod2','',    nbin,0,2500),'ptj2'),
                    'HLT_L1MOD3_115_40': df_num['pt2']['HLT_L1MOD3_115_40'].Histo1D( ('hnum_HLT_l1mod3_115_40','',   nbin,0,2500),'ptj2'),
                    'L1_L1MOD3_115_40':  df_num['pt2']['L1_L1MOD3_115_40'].Histo1D(  ('hnum_l1_l1mod3_115_40','',    nbin,0,2500),'ptj2'),
                    'HLT_L1MOD3_115_35': df_num['pt2']['HLT_L1MOD3_115_35'].Histo1D( ('hnum_HLT_l1mod3_115_35','',   nbin,0,2500),'ptj2'),
                    'L1_L1MOD3_115_35':  df_num['pt2']['L1_L1MOD3_115_35'].Histo1D(  ('hnum_l1_l1mod3_115_35','',    nbin,0,2500),'ptj2'),
                    'HLT_L1MOD3_110_40': df_num['pt2']['HLT_L1MOD3_110_40'].Histo1D( ('hnum_HLT_l1mod3_110_40','',   nbin,0,2500),'ptj2'),
                    'L1_L1MOD3_110_40':  df_num['pt2']['L1_L1MOD3_110_40'].Histo1D(  ('hnum_l1_l1mod3_110_40','',    nbin,0,2500),'ptj2')}
    
    fout.cd()
    
    hden['mjj'].Write('hden_incl_mjj')
    hden['pt1'].Write('hden_incl_pt1')
    hden['pt2'].Write('hden_incl_pt2')
    
    hnum['mjj']['HLT'].Write('hnum_incl_HLT_mjj')
    hnum['pt1']['HLT'].Write('hnum_incl_HLT_pt1')
    hnum['pt2']['HLT'].Write('hnum_incl_HLT_pt2')
    
    hnum['mjj']['L1'].Write('hnum_incl_L1_mjj')
    hnum['pt1']['L1'].Write('hnum_incl_L1_pt1')
    hnum['pt2']['L1'].Write('hnum_incl_L1_pt2')

    
    hnum['mjj']['HLT_L1MOD1'].Write('hnum_incl_HLT_L1MOD1_mjj')
    hnum['mjj']['L1_L1MOD1'].Write('hnum_incl_L1_L1MOD1_mjj')
    hnum['mjj']['HLT_L1MOD2'].Write('hnum_incl_HLT_L1MOD2_mjj')
    hnum['mjj']['L1_L1MOD2'].Write('hnum_incl_L1_L1MOD2_mjj')
    hnum['mjj']['HLT_L1MOD3_115_40'].Write('hnum_incl_HLT_L1MOD3_115_40_mjj')
    hnum['mjj']['L1_L1MOD3_115_40'].Write('hnum_incl_L1_L1MOD3_115_40_mjj')
    hnum['mjj']['HLT_L1MOD3_115_35'].Write('hnum_incl_HLT_L1MOD3_115_35_mjj')
    hnum['mjj']['L1_L1MOD3_115_35'].Write('hnum_incl_L1_L1MOD3_115_35_mjj')
    hnum['mjj']['HLT_L1MOD3_110_40'].Write('hnum_incl_HLT_L1MOD3_110_40_mjj')
    hnum['mjj']['L1_L1MOD3_110_40'].Write('hnum_incl_L1_L1MOD3_110_40_mjj')

    ###########
    # VBF+MET #
    ###########
    
    pt1cut = 100.
    pt2cut = 60.
    mjjcut = 1000.
    idcut = 6

    df_base = df.Define('mjj2',    'get_VBF_var( "mjj", jets_pt,jets_eta,jets_phi,jets_id,jets_CHF,jets_rawfactor,{},{},{},0)'.format(pt1cut,pt2cut,idcut))\
                .Define('ptj1',  'jets_pt[0]')\
                .Define('ptj2', 'jets_pt[1]')\
                .Define('metnomu', 'get_metnomu(MET_et,MET_phi,mu_pt,mu_eta,mu_phi)')

    df_den = {}
    df_den['mjj']    = df_base.Filter('metnomu > 200 && jets_pt[0]>{} && jets_pt[1]>{}'.format(pt1cut,pt2cut))
    df_den['met']    = df_base.Filter('mjj2>{} &&  jets_pt[0]>{} && jets_pt[1]>{}'.format(mjjcut,pt1cut,pt2cut))
    df_den['pt1']    = df_base.Filter('metnomu > 200 && mjj2>{} && jets_pt[1]*(1.-jets_rawfactor[1])>{}'.format(mjjcut,pt2cut))
    df_den['pt2']    = df_base.Filter('metnomu > 200 && mjj2>{} && jets_pt[0]*(1.-jets_rawfactor[0])>{}'.format(mjjcut,pt1cut))

    df_num = { 'mjj' : {}, 'pt1' : {}, 'pt2' : {}, 'met' : {}}
    df_num['mjj']['HLT'] = df_den['mjj'].Filter('passVBFmet_2j || passVBFmet_3j')
    df_num['mjj']['L1']  = df_den['mjj'].Filter('passL1VBFmet')
    df_num['pt1']['HLT'] = df_den['pt2'].Filter('passVBFmet_2j || passVBFmet_3j')
    df_num['pt1']['L1']  = df_den['pt2'].Filter('passL1VBFmet')
    df_num['pt2']['HLT'] = df_den['pt2'].Filter('passVBFmet_2j || passVBFmet_3j')
    df_num['pt2']['L1']  = df_den['pt2'].Filter('passL1VBFmet')
    df_num['met']['HLT'] = df_den['met'].Filter('passVBFmet_2j || passVBFmet_3j')
    df_num['met']['L1']  = df_den['met'].Filter('passL1VBFmet')

    hnum = {'mjj' : {}, 'pt1' : {}, 'pt2' : {}}
    hden = {}

    nbin = 25
    hden['mjj'] = df_den['mjj'].Histo1D(('hden','',   nbin,0,2500),'mjj2')
    hnum['mjj'] = { 'HLT': df_num['mjj']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,2500),'mjj2'),
                    'L1':  df_num['mjj']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,2500),'mjj2')}
    hden['pt1'] = df_den['pt1'].Histo1D(('hden','',   nbin,0,300),'ptj1')
    hnum['pt1'] = { 'HLT': df_num['pt1']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,300),'ptj1'),
                    'L1':  df_num['pt1']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,300),'ptj1')}

    hden['pt2'] = df_den['pt2'].Histo1D(('hden','',   nbin,0,200),'ptj2')
    hnum['pt2'] = { 'HLT': df_num['pt2']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,200),'ptj2'),
                    'L1':  df_num['pt2']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,200),'ptj2')}
    
    hden['met'] = df_den['met'].Histo1D(('hden','',   nbin,0,400),'metnomu')
    hnum['met'] = { 'HLT': df_num['met']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,400),'metnomu'),
                    'L1':  df_num['met']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,400),'metnomu')}
   
    fout.cd()
    
    hden['mjj'].Write('hden_met_mjj')
    hden['pt1'].Write('hden_met_pt1')
    hden['pt2'].Write('hden_met_pt2')
    hden['met'].Write('hden_met_met')
    
    hnum['mjj']['HLT'].Write('hnum_met_HLT_mjj')
    hnum['pt1']['HLT'].Write('hnum_met_HLT_pt1')
    hnum['pt2']['HLT'].Write('hnum_met_HLT_pt2')
    hnum['met']['HLT'].Write('hnum_met_HLT_met')
    
    hnum['mjj']['L1'].Write('hnum_met_L1_mjj')
    hnum['pt1']['L1'].Write('hnum_met_L1_pt1')
    hnum['pt2']['L1'].Write('hnum_met_L1_pt2')
    hnum['met']['L1'].Write('hnum_met_L1_met')


    ###########
    # VBF+tau #
    ###########
    
    pt1cut = 60.
    pt2cut = 60.
    mjjcut = 1000.
    idcut = 6

    df_base = df.Filter('ntau>=1')\
                .Define('mjj2',    'get_VBF_var( "mjj", jets_pt,jets_eta,jets_phi,jets_id,jets_CHF,jets_rawfactor,{},{},{},0)'.format(pt1cut,pt2cut,idcut))\
                .Define('ptj1',  'jets_pt[0]')\
                .Define('ptj2', 'jets_pt[1]')\
                .Define('tauidx','good_tau_idx(tau_pt,tau_eta,tau_idJet,tau_idMuon,tau_idEle,0)')\
                .Filter('tauidx>=0')\
                .Define('pttau1','tau_pt[tauidx]')\
                .Define('DR1','get_dr(tau_eta[tauidx],tau_phi[tauidx],jets_eta[0],jets_phi[0])')\
                .Define('DR2','get_dr(tau_eta[tauidx],tau_phi[tauidx],jets_eta[1],jets_phi[1])')

    df_den = {}
    df_den['mjj']    = df_base.Filter('DR1>0.5 && DR2>0.5 && pttau1 > 50 && jets_pt[0]>{} && jets_pt[1]>{}'.format(pt1cut,pt2cut))
    df_den['pttau']  = df_base.Filter('DR1>0.5 && DR2>0.5 && mjj2>{} &&  jets_pt[0]>{} && jets_pt[1]>{}'.format(mjjcut,pt1cut,pt2cut))
    df_den['pt1']    = df_base.Filter('DR1>0.5 && DR2>0.5 && pttau1 > 50 && mjj2>{} && jets_pt[1]*(1.-jets_rawfactor[1])>{}'.format(mjjcut,pt2cut))
    df_den['pt2']    = df_base.Filter('DR1>0.5 && DR2>0.5 && pttau1 > 50 && mjj2>{} && jets_pt[0]*(1.-jets_rawfactor[0])>{}'.format(mjjcut,pt1cut))

    df_num = { 'mjj' : {}, 'pt1' : {}, 'pt2' : {}, 'pttau' : {}}
    df_num['mjj']['HLT'] = df_den['mjj'].Filter('passVBFtau')
    df_num['mjj']['L1']  = df_den['mjj'].Filter('passL1VBFtau')
    df_num['pt1']['HLT'] = df_den['pt1'].Filter('passVBFtau')
    df_num['pt1']['L1']  = df_den['pt1'].Filter('passL1VBFtau')
    df_num['pt2']['HLT'] = df_den['pt2'].Filter('passVBFtau')
    df_num['pt2']['L1']  = df_den['pt2'].Filter('passL1VBFtau')
    df_num['pttau']['HLT'] = df_den['pttau'].Filter('passVBFtau')
    df_num['pttau']['L1']  = df_den['pttau'].Filter('passL1VBFtau')

    hnum = {'mjj' : {}, 'pt1' : {}, 'pt2' : {}, 'pttau' : {}}
    hden = {}

    nbin = 25
    hden['mjj'] = df_den['mjj'].Histo1D(('hden','',   nbin,0,2500),'mjj2')
    hnum['mjj'] = { 'HLT': df_num['mjj']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,2500),'mjj2'),
                    'L1':  df_num['mjj']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,2500),'mjj2')}
    hden['pt1'] = df_den['pt1'].Histo1D(('hden','',   nbin,0,300),'ptj1')
    hnum['pt1'] = { 'HLT': df_num['pt1']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,300),'ptj1'),
                    'L1':  df_num['pt1']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,300),'ptj1')}

    hden['pt2'] = df_den['pt2'].Histo1D(('hden','',   nbin,0,200),'ptj2')
    hnum['pt2'] = { 'HLT': df_num['pt2']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,200),'ptj2'),
                    'L1':  df_num['pt2']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,200),'ptj2')}
    
    hden['pttau'] = df_den['pttau'].Histo1D(('hden','',   nbin,0,400),'pttau1')
    hnum['pttau'] = { 'HLT': df_num['pttau']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,400),'pttau1'),
                    'L1':  df_num['pttau']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,400),'pttau1')}
   
    fout.cd()
    
    hden['mjj'].Write('hden_tau_mjj')
    hden['pt1'].Write('hden_tau_pt1')
    hden['pt2'].Write('hden_tau_pt2')
    hden['pttau'].Write('hden_tau_pttau')
    
    hnum['mjj']['HLT'].Write('hnum_tau_HLT_mjj')
    hnum['pt1']['HLT'].Write('hnum_tau_HLT_pt1')
    hnum['pt2']['HLT'].Write('hnum_tau_HLT_pt2')
    hnum['pttau']['HLT'].Write('hnum_tau_HLT_pttau')
    
    hnum['mjj']['L1'].Write('hnum_tau_L1_mjj')
    hnum['pt1']['L1'].Write('hnum_tau_L1_pt1')
    hnum['pt2']['L1'].Write('hnum_tau_L1_pt2')
    hnum['pttau']['L1'].Write('hnum_tau_L1_pttau')

    #############
    # VBF+ditau #
    #############
    
    pt1cut = 100.
    pt2cut = 60.
    mjjcut = 1000.
    idcut = 6

    pt1cut = 60.
    pt2cut = 60.
    mjjcut = 1000.
    idcut = 6

    df_base = df.Filter('ntau>=2')\
                .Define('mjj2',    'get_VBF_var( "mjj", jets_pt,jets_eta,jets_phi,jets_id,jets_CHF,jets_rawfactor,{},{},{},0)'.format(pt1cut,pt2cut,idcut))\
                .Define('ptj1',  'jets_pt[0]')\
                .Define('ptj2', 'jets_pt[1]')\
                .Define('tauidx','good_tau_idx(tau_pt,tau_eta,tau_idJet,tau_idMuon,tau_idEle,1)')\
                .Filter('tauidx>=0')\
                .Define('pttau2','tau_pt[tauidx]')

    df_den = {}
    df_den['mjj']    = df_base.Filter('pttau2 > 50 && jets_pt[0]>{} && jets_pt[1]>{}'.format(pt1cut,pt2cut))
    df_den['pttau']  = df_base.Filter('mjj2>{} &&  jets_pt[0]>{} && jets_pt[1]>{}'.format(mjjcut,pt1cut,pt2cut))
    df_den['pt1']    = df_base.Filter('pttau2 > 50 && mjj2>{} && jets_pt[1]*(1.-jets_rawfactor[1])>{}'.format(mjjcut,pt2cut))
    df_den['pt2']    = df_base.Filter('pttau2 > 50 && mjj2>{} && jets_pt[0]*(1.-jets_rawfactor[0])>{}'.format(mjjcut,pt1cut))

    df_num = { 'mjj' : {}, 'pt1' : {}, 'pt2' : {}, 'pttau' : {}}
    df_num['mjj']['HLT'] = df_den['mjj'].Filter('passVBFtau')
    df_num['mjj']['L1']  = df_den['mjj'].Filter('passL1VBFtau')
    df_num['pt1']['HLT'] = df_den['pt2'].Filter('passVBFtau')
    df_num['pt1']['L1']  = df_den['pt2'].Filter('passL1VBFtau')
    df_num['pt2']['HLT'] = df_den['pt2'].Filter('passVBFtau')
    df_num['pt2']['L1']  = df_den['pt2'].Filter('passL1VBFtau')
    df_num['pttau']['HLT'] = df_den['pttau'].Filter('passVBFtau')
    df_num['pttau']['L1']  = df_den['pttau'].Filter('passL1VBFtau')

    hnum = {'mjj' : {}, 'pt1' : {}, 'pt2' : {}, 'pttau' : {}}
    hden = {}

    nbin = 25
    hden['mjj'] = df_den['mjj'].Histo1D(('hden','',   nbin,0,2500),'mjj2')
    hnum['mjj'] = { 'HLT': df_num['mjj']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,2500),'mjj2'),
                    'L1':  df_num['mjj']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,2500),'mjj2')}
    hden['pt1'] = df_den['pt1'].Histo1D(('hden','',   nbin,0,300),'ptj1')
    hnum['pt1'] = { 'HLT': df_num['pt1']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,300),'ptj1'),
                    'L1':  df_num['pt1']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,300),'ptj1')}

    hden['pt2'] = df_den['pt2'].Histo1D(('hden','',   nbin,0,200),'ptj2')
    hnum['pt2'] = { 'HLT': df_num['pt2']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,200),'ptj2'),
                    'L1':  df_num['pt2']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,200),'ptj2')}
    
    hden['pttau'] = df_den['pttau'].Histo1D(('hden','',   nbin,0,400),'pttau2')
    hnum['pttau'] = { 'HLT': df_num['pttau']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,400),'pttau2'),
                    'L1':  df_num['pttau']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,400),'pttau2')}
   
    fout.cd()
    
    hden['mjj'].Write('hden_ditau_mjj')
    hden['pt1'].Write('hden_ditau_pt1')
    hden['pt2'].Write('hden_ditau_pt2')
    hden['pttau'].Write('hden_ditau_pttau')
    
    hnum['mjj']['HLT'].Write('hnum_ditau_HLT_mjj')
    hnum['pt1']['HLT'].Write('hnum_ditau_HLT_pt1')
    hnum['pt2']['HLT'].Write('hnum_ditau_HLT_pt2')
    hnum['pttau']['HLT'].Write('hnum_ditau_HLT_pttau')
    
    hnum['mjj']['L1'].Write('hnum_ditau_L1_mjj')
    hnum['pt1']['L1'].Write('hnum_ditau_L1_pt1')
    hnum['pt2']['L1'].Write('hnum_ditau_L1_pt2')
    hnum['pttau']['L1'].Write('hnum_ditau_L1_pttau')

    ###########
    # VBF+muo #
    ###########
    
    pt1cut = 115.
    pt2cut = 60.
    mjjcut = 1100.
    idcut = 6

    df_base = df.Define('mjj2',    'get_VBF_var( "mjj", jets_pt,jets_eta,jets_phi,jets_id,jets_CHF,jets_rawfactor,{},{},{},0)'.format(pt1cut,pt2cut,idcut))\
                .Define('ptj1',  'jets_pt[0]')\
                .Define('ptj2', 'jets_pt[1]')

    df_den = {}
    df_den['mjj']    = df_base.Filter('jets_pt[0]>{} && jets_pt[1]>{}'.format(pt1cut,pt2cut))
    df_den['pt1']    = df_base.Filter('mjj2>{} && jets_pt[1]*(1.-jets_rawfactor[1])>{}'.format(mjjcut,pt2cut))
    df_den['pt2']    = df_base.Filter('mjj2>{} && jets_pt[0]*(1.-jets_rawfactor[0])>{}'.format(mjjcut,pt1cut))

    df_num = { 'mjj' : {}, 'pt1' : {}, 'pt2' : {}}
    df_num['mjj']['HLT'] = df_den['mjj'].Filter('passVBFmu_2j || passVBFmu_3j')
    df_num['mjj']['L1']  = df_den['mjj'].Filter('passL1VBFmu')
    df_num['pt1']['HLT'] = df_den['pt2'].Filter('passVBFmu_2j || passVBFmu_3j')
    df_num['pt1']['L1']  = df_den['pt2'].Filter('passL1VBFmu')
    df_num['pt2']['HLT'] = df_den['pt2'].Filter('passVBFmu_2j || passVBFmu_3j')
    df_num['pt2']['L1']  = df_den['pt2'].Filter('passL1VBFmu')

    hnum = {'mjj' : {}, 'pt1' : {}, 'pt2' : {}}
    hden = {}

    nbin = 25
    hden['mjj'] = df_den['mjj'].Histo1D(('hden','',   nbin,0,2500),'mjj2')
    hnum['mjj'] = { 'HLT': df_num['mjj']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,2500),'mjj2'),
                    'L1':  df_num['mjj']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,2500),'mjj2')}
    hden['pt1'] = df_den['pt1'].Histo1D(('hden','',   nbin,0,300),'ptj1')
    hnum['pt1'] = { 'HLT': df_num['pt1']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,300),'ptj1'),
                    'L1':  df_num['pt1']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,300),'ptj1')}

    hden['pt2'] = df_den['pt2'].Histo1D(('hden','',   nbin,0,200),'ptj2')
    hnum['pt2'] = { 'HLT': df_num['pt2']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,200),'ptj2'),
                    'L1':  df_num['pt2']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,200),'ptj2')}
    
    fout.cd()
    
    hden['mjj'].Write('hden_mu_mjj')
    hden['pt1'].Write('hden_mu_pt1')
    hden['pt2'].Write('hden_mu_pt2')
    
    hnum['mjj']['HLT'].Write('hnum_mu_HLT_mjj')
    hnum['pt1']['HLT'].Write('hnum_mu_HLT_pt1')
    hnum['pt2']['HLT'].Write('hnum_mu_HLT_pt2')
    
    hnum['mjj']['L1'].Write('hnum_mu_L1_mjj')
    hnum['pt1']['L1'].Write('hnum_mu_L1_pt1')
    hnum['pt2']['L1'].Write('hnum_mu_L1_pt2')

    
    ###########
    # VBF+pho #
    ###########
    
    pt1cut = 65.
    pt2cut = 65.
    mjjcut = 1000.
    idcut = 6

    df_base = df.Filter('nphot>=1')\
                .Define('mjj2',    'get_VBF_var( "mjj", jets_pt,jets_eta,jets_phi,jets_id,jets_CHF,jets_rawfactor,{},{},{},0)'.format(pt1cut,pt2cut,idcut))\
                .Define('ptj1',  'jets_pt[0]')\
                .Define('ptj2', 'jets_pt[1]')\
                .Define('ptphot','phot_pt[0]')

    df_den = {}
    df_den['mjj']    = df_base.Filter('ptphot > 30 && jets_pt[0]>{} && jets_pt[1]>{}'.format(pt1cut,pt2cut))
    df_den['ptphot']  = df_base.Filter('mjj2>{} &&  jets_pt[0]>{} && jets_pt[1]>{}'.format(mjjcut,pt1cut,pt2cut))
    df_den['pt1']    = df_base.Filter('ptphot > 30 && mjj2>{} && jets_pt[1]*(1.-jets_rawfactor[1])>{}'.format(mjjcut,pt2cut))
    df_den['pt2']    = df_base.Filter('ptphot > 30 && mjj2>{} && jets_pt[0]*(1.-jets_rawfactor[0])>{}'.format(mjjcut,pt1cut))

    df_num = { 'mjj' : {}, 'pt1' : {}, 'pt2' : {}, 'ptphot' : {}}
    df_num['mjj']['HLT'] = df_den['mjj'].Filter('passVBFphot')
    df_num['mjj']['L1']  = df_den['mjj'].Filter('passL1VBFphot')
    df_num['pt1']['HLT'] = df_den['pt2'].Filter('passVBFphot')
    df_num['pt1']['L1']  = df_den['pt2'].Filter('passL1VBFphot')
    df_num['pt2']['HLT'] = df_den['pt2'].Filter('passVBFphot')
    df_num['pt2']['L1']  = df_den['pt2'].Filter('passL1VBFphot')
    df_num['ptphot']['HLT'] = df_den['ptphot'].Filter('passVBFphot')
    df_num['ptphot']['L1']  = df_den['ptphot'].Filter('passL1VBFphot')

    hnum = {'mjj' : {}, 'pt1' : {}, 'pt2' : {}, 'ptphot' : {}}
    hden = {}

    nbin = 25
    hden['mjj'] = df_den['mjj'].Histo1D(('hden','',   nbin,0,2500),'mjj2')
    hnum['mjj'] = { 'HLT': df_num['mjj']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,2500),'mjj2'),
                    'L1':  df_num['mjj']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,2500),'mjj2')}
    hden['pt1'] = df_den['pt1'].Histo1D(('hden','',   nbin,0,300),'ptj1')
    hnum['pt1'] = { 'HLT': df_num['pt1']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,300),'ptj1'),
                    'L1':  df_num['pt1']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,300),'ptj1')}

    hden['pt2'] = df_den['pt2'].Histo1D(('hden','',   nbin,0,200),'ptj2')
    hnum['pt2'] = { 'HLT': df_num['pt2']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,200),'ptj2'),
                    'L1':  df_num['pt2']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,200),'ptj2')}
    
    hden['ptphot'] = df_den['ptphot'].Histo1D(('hden','',   nbin,0,400),'ptphot')
    hnum['ptphot'] = { 'HLT': df_num['ptphot']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,400),'ptphot'),
                    'L1':  df_num['ptphot']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,400),'ptphot')}
   
    fout.cd()
    
    hden['mjj'].Write('hden_phot_mjj')
    hden['pt1'].Write('hden_phot_pt1')
    hden['pt2'].Write('hden_phot_pt2')
    hden['ptphot'].Write('hden_phot_ptphot')
    
    hnum['mjj']['HLT'].Write('hnum_phot_HLT_mjj')
    hnum['pt1']['HLT'].Write('hnum_phot_HLT_pt1')
    hnum['pt2']['HLT'].Write('hnum_phot_HLT_pt2')
    hnum['ptphot']['HLT'].Write('hnum_phot_HLT_ptphot')
    
    hnum['mjj']['L1'].Write('hnum_phot_L1_mjj')
    hnum['pt1']['L1'].Write('hnum_phot_L1_pt1')
    hnum['pt2']['L1'].Write('hnum_phot_L1_pt2')
    hnum['ptphot']['L1'].Write('hnum_phot_L1_ptphot')

    
    ###########
    # VBF+jet #
    ###########
    
    pt1cut = 100.
    pt2cut = 60.
    mjjcut = 1000.
    idcut = 6

    df_base = df.Filter('njets>=4')\
                .Define('mjj2',    'get_VBF_var( "mjj", jets_pt,jets_eta,jets_phi,jets_id,jets_CHF,jets_rawfactor,{},{},{},0)'.format(pt1cut,pt2cut,idcut))\
                .Define('ptj1',  'jets_pt[0]')\
                .Define('ptj2', 'jets_pt[1]')\
                .Define('ptj3', 'jets_pt[2]')\
                .Define('ptj4', 'jets_pt[3]')\

    df_den = {}
    df_den['mjj']    = df_base.Filter('jets_pt[0]>{} && jets_pt[1]>{} && jets_pt[2]>{} && jets_pt[3]>{}'.format(pt1cut,75,75,pt2cut))
    df_den['pt1']    = df_base.Filter('mjj2>{} && jets_pt[1]*(1.-jets_rawfactor[1])>{}'.format(mjjcut,pt2cut))
    df_den['pt2']    = df_base.Filter('mjj2>{} && jets_pt[0]*(1.-jets_rawfactor[0])>{}'.format(mjjcut,pt1cut))

    df_num = { 'mjj' : {}, 'pt1' : {}, 'pt2' : {}}
    df_num['mjj']['HLT'] = df_den['mjj'].Filter('passVBFjets_4j || passVBFjets_5j')
    df_num['mjj']['L1']  = df_den['mjj'].Filter('passL1VBFjets')
    df_num['pt1']['HLT'] = df_den['pt2'].Filter('passVBFjets_4j || passVBFjets_5j')
    df_num['pt1']['L1']  = df_den['pt2'].Filter('passL1VBFjets')
    df_num['pt2']['HLT'] = df_den['pt2'].Filter('passVBFjets_4j || passVBFjets_5j')
    df_num['pt2']['L1']  = df_den['pt2'].Filter('passL1VBFjets')

    hnum = {'mjj' : {}, 'pt1' : {}, 'pt2' : {}}
    hden = {}

    nbin = 25
    hden['mjj'] = df_den['mjj'].Histo1D(('hden','',   nbin,0,2500),'mjj2')
    hnum['mjj'] = { 'HLT': df_num['mjj']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,2500),'mjj2'),
                    'L1':  df_num['mjj']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,2500),'mjj2')}
    hden['pt1'] = df_den['pt1'].Histo1D(('hden','',   nbin,0,300),'ptj1')
    hnum['pt1'] = { 'HLT': df_num['pt1']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,300),'ptj1'),
                    'L1':  df_num['pt1']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,300),'ptj1')}

    hden['pt2'] = df_den['pt2'].Histo1D(('hden','',   nbin,0,200),'ptj2')
    hnum['pt2'] = { 'HLT': df_num['pt2']['HLT'].Histo1D( ('hnum_HLT','',   nbin,0,200),'ptj2'),
                    'L1':  df_num['pt2']['L1'].Histo1D(  ('hnum_l1','',    nbin,0,200),'ptj2')}
    
    fout.cd()
    
    hden['mjj'].Write('hden_mu_mjj')
    hden['pt1'].Write('hden_mu_pt1')
    hden['pt2'].Write('hden_mu_pt2')
    
    hnum['mjj']['HLT'].Write('hnum_mu_HLT_mjj')
    hnum['pt1']['HLT'].Write('hnum_mu_HLT_pt1')
    hnum['pt2']['HLT'].Write('hnum_mu_HLT_pt2')
    
    hnum['mjj']['L1'].Write('hnum_mu_L1_mjj')
    hnum['pt1']['L1'].Write('hnum_mu_L1_pt1')
    hnum['pt2']['L1'].Write('hnum_mu_L1_pt2')





    
    fout.Close()
    
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Args')
    
    parser.add_argument('--version', default='VBFparking')
    parser.add_argument('--era', default = '24B',
                        choices = ['23C','23D','24B','24C','24D','24E','24F','24G','24H','24I','24ABC','Winter23', 'Winter24']) # more to be added
    parser.add_argument('--input', default = '/eos/home-l/lportale/VBFparkingNtuples/histos_24G_STEAM_241010_999.root')
    parser.add_argument('--outdir', default = './')
    #parser.add_argument('--input', default = '')
    args = parser.parse_args()

    preselection="1"

    infile = args.input#f"/eos/home-l/lportale/VBFparkingNtuples/histos_{args.era}_{args.version}_{args.id}.root" #args.input
    print(infile)

    outfile = f"{args.outdir}/eff"+ infile.split('/')[8]
    
    #outfile = f"{args.outdir}/effhistos_{args.era}_{args.version}_{args.id}.root"

    generate_histos(infile, outfile)
