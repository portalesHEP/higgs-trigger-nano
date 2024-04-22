float mjj(float pt1,float pt2,
	  float eta1,float eta2,
	  float phi1,float phi2){
  return TMath::Sqrt(
    2*pt1*pt2*(
      TMath::CosH(eta1-eta2)-TMath::Cos(phi1-phi2)
      )
    );
}

void check_VBFHbb(){

  TFile *f = new TFile("./VBFHbb_nano_all/nano_20.root","read");
  //TFile *f = new TFile("./MC_VBFHinv_nano_test.root","read");
  
  TTree *t = (TTree*)f->Get("Events");


  TString passVBFJets = "(HLT_VBF_DiPFJet75_45_Mjj600_Detajj2p5_DiPFJet60_JetMatchingQuadJet||HLT_VBF_DiPFJet75_45_Mjj600_Detajj2p5_DiPFJet60_JetMatchingFiveJet||HLT_VBF_DiPFJet75_45_Mjj600_Detajj2p5_DiPFJet60_JetMatchingSixJet)";
  TString passVBFincl = "(HLT_VBF_DiPFJet125_45_Mjj1000_Detajj3p5||HLT_VBF_DiPFJet125_45_Mjj1000_Detajj3p5_TriplePFJet)";
  TString passHH = "(HLT_PFHT280_QuadPFJet30_PNet2BTagMean0p55)";
  TString passVBFHbb = "(HLT_QuadPFJet103_88_75_15_DoublePFBTagDeepJet_1p3_7p7_VBF1||HLT_QuadPFJet103_88_75_15_PFBTagDeepJet_1p3_VBF2)";

  TString plotvar = "(" + passVBFJets + " || " + passVBFincl + " || " + passHH + ") : " + passVBFHbb;


  TString passParking = passVBFJets + " || " + passVBFincl + " || " + passHH;
  TString passHbbNotParking = "!(" + passParking +  ") && "+passVBFHbb;

    t->Draw(plotvar,"","colz text");
    
    Float_t N_tot = t->Draw("HLTriggerFinalPath","","goff");
    Float_t N_passParking = t->Draw("HLTriggerFinalPath",passParking,"goff");
    Float_t N_passHbb_notParking = t->Draw("HLTriggerFinalPath",passHbbNotParking,"goff");


    std::cout << "Eff parking = " << N_passParking/N_tot << endl
	      << "Eff tot     = " << (N_passParking+N_passHbb_notParking)/N_tot << endl;



}
