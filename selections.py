from itertools import combinations
import ROOT

# VBF jets selection
def has_vbf_jets(jets,pt1,pt2,mjjcut):
    DoubleJet = jets[0].pt>pt1 and jets[1].pt>pt2
    if not DoubleJet:
        return False
    
    has_vbf = False
    for jet_pair in combinations(jets,2):
        p1 = jet_pair[0]
        p2 = jet_pair[1]
        if p1.pt>pt2 and p2.pt>pt2:
            tlv1 = ROOT.TLorentzVector()
            tlv2 = ROOT.TLorentzVector()
            tlv1.SetPtEtaPhiM(p1.pt,p1.eta,p1.phi,0)
            tlv2.SetPtEtaPhiM(p2.pt,p2.eta,p2.phi,0)
            tlv12 = tlv1+tlv2
            mjj = tlv12.M()
            if mjj > mjjcut:
                has_vbf = True

    return has_vbf

### VBF + 2 jets:
def pass_VBFdijet(jets, vbf1cut, vbf2cut, centcut, mjjcut, ctagged=False):

    ak4jets = [j for j in jets if j.pt > 20 and abs(j.eta) < 4.7] # PFHT
    
    if len(ak4jets)<4:
        return False
    
    if not has_vbf_jets(ak4jets,vbf1cut,vbf2cut,mjjcut):
        return False

    centralJets = [j for j in jets if j.pt > vbf2cut and abs(j.eta) < 2.52]
    forwardJets = [j for j in jets if j.pt > vbf2cut and abs(j.eta) >= 2.52]

    event_pass = False
    # 4 central jets
    if len(centralJets)>3:
        if centralJets[0].pt>vbf1cut and centralJets[2].pt>centcut and centralJets[3].pt>vbf2cut:
            event_pass = True
    # 3 central jets + 1 forward
    if len(centralJets)>2 and len(forwardJets)>0:
        if centralJets[0].pt>vbf1cut and centralJets[1].pt>centcut and centralJets[2].pt>vbf2cut and forwardJets[0].pt>centcut:
            event_pass = True
        if centralJets[1].pt>centcut and centralJets[2].pt>vbf2cut and forwardJets[0].pt>vbf1cut:
            event_pass = True
        if centralJets[0].pt>vbf1cut and centralJets[2].pt>centcut and forwardJets[0].pt>vbf2cut:
            event_pass = True
    
    # 2 central jets + 2 forwards
    if len(centralJets)>1 and len(forwardJets)>1:
        if centralJets[0].pt>vbf1cut and centralJets[1].pt>centcut:
            if forwardJets[0].pt>centcut and forwardJets[1].pt>vbf2cut:
                event_pass = True
        if centralJets[1].pt>centcut:
            if forwardJets[0].pt>vbf1cut and forwardJets[1].pt>vbf2cut:
                event_pass = True


    if not event_pass:
        return False

    # if c-tagging requested, identify the two VBF jets and find two additional c-tagged jets with pT > centcut
    if ctagged:
        idx_vbf1 = -1
        idx_vbf2 = -1
        for idx1, jet1 in enumerate(ak4jets):
            for idx2, jet2 in enumerate(ak4jets):
                if idx2<=idx1:
                    continue
                if jet1.pt>vbf2cut and jet2.pt>vbf2cut:
                    tlv1 = ROOT.TLorentzVector()
                    tlv2 = ROOT.TLorentzVector()
                    tlv1.SetPtEtaPhiM(jet1.pt,jet1.eta,jet1.phi,0)
                    tlv2.SetPtEtaPhiM(jet2.pt,jet2.eta,jet2.phi,0)
                    tlv12 = tlv1+tlv2
                    mjj = tlv12.M()
                    if mjj > mjjcut:
                        idx_vbf1 = idx1
                        idx_vbf2 = idx2
        
        idx_cjet1=-1
        idx_cjet2=-1
        for idx, jet in enumerate(ak4jets):
            if idx==idx_vbf1 or idx==idx_vbf2:
                continue
            if jet.pt<centcut:
                continue

            #if idx_cjet1>-1 and jet.btagDeepB>0.2783: 
	    if idx_cjet1>-1 and jet.btagDeepCvB>0.4:
                idx_cjet2=idx
            #if idx_cjet1==-1 and jet.btagDeepB>0.71:
            if idx_cjet1==-1 and jet.btagDeepCvL>0.225:
                idx_cjet1=idx

        if idx_cjet1==-1 or idx_cjet2==-1:
            event_pass = False
            
    return event_pass



### VBF + 2 jets:
def pass_VBFgamma(jets, photons, vbf1cut, vbf2cut, gammacut, mjjcut):

    ak4jets = [j for j in jets if j.pt > 20 and abs(j.eta) < 4.7] # PFHT
    
    if len(ak4jets)<2:
        return False
        
    # medium ID photons in barrel
    phots = [p for p in photons if (p.pt > 10 and abs(p.eta) < 1.4442 and p.cutBased>2)]
    phots.sort(key = lambda x: x.pt, reverse = True)

    if len(phots)<1:
        return False

    if not has_vbf_jets(ak4jets,vbf1cut,vbf2cut,mjjcut):
        return False


    if phots[0].pt < gammacut:
        return False

    return True

    
