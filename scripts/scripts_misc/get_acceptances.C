void get_acceptances(){

  //TFile *f = new TFile("VBShadronic_quickEff_ZZnunujj.newBckp.root","read");
  //TFile *f = new TFile("VBShadronic_quickEff_ZZjjjj.newBckp.root","read");
  TFile *f = new TFile("VBShadronic_quickEff_WWjjjj.newBckp.root","read");
  TDirectory *d = (TDirectory*)f->Get("BTagNanoAOD");
  //d->ls();
  
  TH1F* h_their_METboosted    = (TH1F*)d->Get("h_their_METboosted");
  TH1F* h_their_METresolved   = (TH1F*)d->Get("h_their_METresolved");
  TH1F* h_their_withBboosted  = (TH1F*)d->Get("h_their_withBboosted");
  TH1F* h_their_noBboosted    = (TH1F*)d->Get("h_their_noBboosted");
  TH1F* h_their_withBresolved = (TH1F*)d->Get("h_their_withBresolved");
  TH1F* h_their_tot           = (TH1F*)d->Get("h_their_tot");
  TH1F* h_our_METboosted      = (TH1F*)d->Get("h_our_METboosted");
  TH1F* h_our_METresolved     = (TH1F*)d->Get("h_our_METresolved");
  TH1F* h_our_withBboosted    = (TH1F*)d->Get("h_our_withBboosted");
  TH1F* h_our_noBboosted      = (TH1F*)d->Get("h_our_noBboosted");
  TH1F* h_our_withBresolved   = (TH1F*)d->Get("h_our_withBresolved");
  TH1F* h_our_tot             = (TH1F*)d->Get("h_our_tot");
  TH1F* h_add_METboosted      = (TH1F*)d->Get("h_add_METboosted");
  TH1F* h_add_METresolved     = (TH1F*)d->Get("h_add_METresolved");
  TH1F* h_add_withBboosted    = (TH1F*)d->Get("h_add_withBboosted");
  TH1F* h_add_noBboosted      = (TH1F*)d->Get("h_add_noBboosted");
  TH1F* h_add_withBresolved   = (TH1F*)d->Get("h_add_withBresolved");
  TH1F* h_tot                 = (TH1F*)d->Get("h_tot");
  TH1F* h_pass                = (TH1F*)d->Get("h_pass");

  Float_t yield_their_METboosted    = h_their_METboosted    ->Integral();
  Float_t yield_their_METresolved   = h_their_METresolved   ->Integral();
  Float_t yield_their_withBboosted  = h_their_withBboosted  ->Integral();
  Float_t yield_their_noBboosted    = h_their_noBboosted    ->Integral();
  Float_t yield_their_withBresolved = h_their_withBresolved ->Integral();
  Float_t yield_their_tot           = h_their_tot           ->Integral();

  Float_t yield_our_METboosted      = h_our_METboosted      ->Integral();
  Float_t yield_our_METresolved     = h_our_METresolved     ->Integral();
  Float_t yield_our_withBboosted    = h_our_withBboosted    ->Integral();
  Float_t yield_our_noBboosted      = h_our_noBboosted      ->Integral();
  Float_t yield_our_withBresolved   = h_our_withBresolved   ->Integral();
  Float_t yield_our_tot             = h_our_tot             ->Integral();

  Float_t yield_add_METboosted      = h_add_METboosted      ->Integral();
  Float_t yield_add_METresolved     = h_add_METresolved     ->Integral();
  Float_t yield_add_withBboosted    = h_add_withBboosted    ->Integral();
  Float_t yield_add_noBboosted      = h_add_noBboosted      ->Integral();
  Float_t yield_add_withBresolved   = h_add_withBresolved   ->Integral();
  Float_t yield_tot                 = h_tot                 ->Integral();
  Float_t yield_pass                = h_pass                ->Integral();

  Float_t gain_METboosted      = 100. * (yield_add_METboosted - yield_their_METboosted) / yield_their_METboosted;
  Float_t gain_METresolved     = 100. * (yield_add_METresolved - yield_their_METresolved) / yield_their_METresolved;
  Float_t gain_withBboosted    = 100. * (yield_add_withBboosted - yield_their_withBboosted) / yield_their_withBboosted;
  Float_t gain_noBboosted      = 100. * (yield_add_noBboosted - yield_their_noBboosted) / yield_their_noBboosted;
  Float_t gain_withBresolved   = 100. * (yield_add_withBresolved - yield_their_withBresolved) / yield_their_withBresolved;
  Float_t gain_tot             = 100. * (yield_pass - yield_their_tot) / yield_their_tot;

  std::cout 
    << "Total yield    (gain, tot, our, their): " 
    << gain_tot <<"%, " 
    << yield_pass << ", " << yield_our_tot << ", " << yield_their_tot << std::endl

    << "METboosted     (gain, tot, our, their): "
    << gain_METboosted <<"%,   " 
    << yield_add_METboosted << ", " << yield_our_METboosted << ", " << yield_their_METboosted << std::endl

    << "METresolved    (gain, tot, our, their): "
    << gain_METresolved <<"%,   " 
    << yield_add_METresolved << ", " << yield_our_METresolved << ", " << yield_their_METresolved << std::endl

    << "withBboosted   (gain, tot, our, their): "
    << gain_withBboosted <<"%,   " 
    << yield_add_withBboosted << ", " << yield_our_withBboosted << ", " << yield_their_withBboosted << std::endl

    << "noBboosted     (gain, tot, our, their): "
    << gain_noBboosted <<"%,   " 
    << yield_add_noBboosted << ", " << yield_our_noBboosted << ", " << yield_their_noBboosted << std::endl

    << "withBresolved  (gain, tot, our, their): "
    << gain_withBresolved << "%,   " 
    << yield_add_withBresolved << ", " << yield_our_withBresolved << ", " << yield_their_withBresolved << std::endl;



                
}
