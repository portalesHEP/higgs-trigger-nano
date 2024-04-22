float mjj(float pt1,float pt2,
	  float eta1,float eta2,
	  float phi1,float phi2){
  return TMath::Sqrt(
    2*pt1*pt2*(
      TMath::CosH(eta1-eta2)-TMath::Cos(phi1-phi2)
      )
    );
}

void check_L1(){

  TFile *f = new TFile("./Data_Muon_test.root","read");
  //TFile *f = new TFile("./MC_VBFHinv_nano_test.root","read");
  
  TTree *t = (TTree*)f->Get("Events");

  //TString display_var = "L1Jet_pt[0]:Jet_pt[0]:L1Jet_pt[1]:Jet_pt[1]:mjj(Jet_pt[0],Jet_pt[1],Jet_eta[0],Jet_eta[1],Jet_phi[0],Jet_phi[1])";
  //TString display_var = "L1Jet_pt[0]:Jet_pt[0]:L1Jet_pt[1]:Jet_pt[1]:mjj(L1Jet_pt[0],L1Jet_pt[1],L1Jet_eta[0],L1Jet_eta[1],L1Jet_phi[0],L1Jet_phi[1])";
  TString display_var = "run:L1Jet_bx[0]:L1Jet_bx[1]:L1Jet_pt[0]:L1Jet_pt[1]:L1Jet_eta[0]:L1Jet_eta[1]:L1Jet_phi[0]:L1Jet_phi[1]:mjj(L1Jet_pt[0],L1Jet_pt[1],L1Jet_eta[0],L1Jet_eta[1],L1Jet_phi[0],L1Jet_phi[1])";

  TString cutstr = "run>367660 && nJet==2 && nL1Jet==2 &&!L1_DoubleJet_110_35_DoubleJet35_Mass_Min620 && L1Jet_pt[0]>110 && L1Jet_pt[1]>35 && 620<mjj(L1Jet_pt[0],L1Jet_pt[1],L1Jet_eta[0],L1Jet_eta[1],L1Jet_phi[0],L1Jet_phi[1])";
  //TString cutstr = "run>367660 && nJet==2 && nL1Jet==2 && L1_DoubleJet_110_35_DoubleJet35_Mass_Min620 && L1Jet_pt[0]>110 && L1Jet_pt[1]>35 && 620>mjj(L1Jet_pt[0],L1Jet_pt[1],L1Jet_eta[0],L1Jet_eta[1],L1Jet_phi[0],L1Jet_phi[1])";



  //TString cutstr = "run>367660 && nJet==2 && nL1Jet==2 &&L1_DoubleJet_90_30_DoubleJet30_Mass_Min620 && L1Jet_pt[0]>90 && L1Jet_pt[1]>30 && 620>mjj(L1Jet_pt[0],L1Jet_pt[1],L1Jet_eta[0],L1Jet_eta[1],L1Jet_phi[0],L1Jet_phi[1])";
  //TString cutstr = "run>367660 && nJet==2 && nL1Jet==2 && L1_DoubleJet_90_30_DoubleJet30_Mass_Min620 && L1Jet_pt[0]>90 && L1Jet_pt[1]>30 && 620<mjj(L1Jet_pt[0],L1Jet_pt[1],L1Jet_eta[0],L1Jet_eta[1],L1Jet_phi[0],L1Jet_phi[1]) && (fabs(L1Jet_eta[0])>3 || fabs(L1Jet_eta[1])>3)";

  t->Scan(display_var,cutstr);
  


}
/*

<algorithm>
    <name>L1_DoubleJet_110_35_DoubleJet35_Mass_Min620</name>
    <expression>comb{JET110,JET35} AND mass_inv{JET35,JET35}[MASS_MIN_620]</expression>
    <index>356</index>
    <module_id>0</module_id>
    <module_index>356</module_index>
    <comment>https://its.cern.ch/jira/browse/CMSLITDPG-102</comment>
    <cut>
      <name>MASS_MIN_620</name>
      <object/>
      <type>MASS</type>
      <minimum>+6.2000000000000000E+02</minimum>
      <maximum>+1.5198200000000000E+05</maximum>
      <data/>
    </cut>
    <object_requirement>
      <name>JET35</name>
      <type>JET</type>
      <comparison_operator>.ge.</comparison_operator>
      <threshold>+3.5000000000000000E+01</threshold>
      <bx_offset>0</bx_offset>
    </object_requirement>
    <object_requirement>
      <name>JET110</name>
      <type>JET</type>
      <comparison_operator>.ge.</comparison_operator>
      <threshold>+1.1000000000000000E+02</threshold>
      <bx_offset>0</bx_offset>
    </object_requirement>
  </algorithm>
*/
