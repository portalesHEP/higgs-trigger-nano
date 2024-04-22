void EffFromNtuples(){

  TFile *f_in = new TFile("Run23C_VBFincl_newVarL1_withCHFcut.root","READ");
  TDirectoryFile *d_in = (TDirectoryFile*)f_in->Get("VBFNanoAOD");

  TTree *t_in = (TTree*)d_in->Get("VBFtree");

  t_in->Show(0);

  TH1F *h_mjj_pass = new TH1F("h_mjj_pass","",30,200,2000);
  TH1F *h_mjj_tot  = new TH1F("h_mjj_tot","",30,200,2000);

  t_in->Draw("mjj>>h_mjj_pass","passVBFincl && detajj>3.5 && pt2 > 70 && (pt1>130 || (pt1 > 70 && j1_pt> 130))");

  t_in->Draw("mjj>>h_mjj_tot","detajj>3.5 && pt2 > 70 && (pt1>130 || (pt1 > 70 && j1_pt> 130))");


  h_mjj_pass->Divide(h_mjj_tot);
  h_mjj_pass->Draw("hist");
  


}
