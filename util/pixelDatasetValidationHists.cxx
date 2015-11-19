#include <cstdio>
#include <map>
#include <string>
#include <TH1D.h>
#include <TChain.h>
#include <TFile.h>

#define NUMBER1 1
#define NUMBER2 2
#define NUMBER3 3
#define POS1 4
#define POS2 5
#define POS3 6

int main(int argc, char *argv[])
{
	if (argc < 4) {
		std::fprintf(stderr, "usage: %s <number1/number2/number3/pos1/pos2/pos3> outfile.root data.root ...\n", argv[0]);
		return 1;
	}

	TChain chain("NNinput");
	for (int i = 3; i < argc; i++)
		chain.Add(argv[i]);

	TFile outfile(argv[2], "CREATE");

	std::map<std::string, TH1D*> hists;
	hists["layer"] =    new TH1D("h_layer", "", 4, 0, 4);
	hists["barrelEC"] = new TH1D("h_barrelEC", "", 11, -5, 5);
	hists["phi"] =      new TH1D("h_phi", "", 100, -5, 5);
	hists["theta"] =    new TH1D("h_theta", "", 100, -5, 5);

	int type;

	if (std::string(argv[1]).compare("number1") == 0) {
		type = NUMBER1;
	} else if (std::string(argv[1]).compare("number2") == 0) {
		type = NUMBER2;
	} else if (std::string(argv[1]).compare("number3") == 0) {
		type = NUMBER3;
	} else if (std::string(argv[1]).compare("pos1") == 0) {
		type = POS1;
	} else if (std::string(argv[1]).compare("pos2") == 0) {
		type = POS2;
	} else if (std::string(argv[1]).compare("pos3") == 0) {
		type = POS3;
	} else {
		std::fprintf(stderr, "unknown type\n");
		return 1;
	}

	int NN_layer;
	int NN_barrelEC;
	float NN_phi;
	float NN_theta;
	int NN_nparticles1;
	int NN_nparticles2;
	int NN_nparticles3;
	float NN_position_id_X_0;
	float NN_position_id_Y_0;
	float NN_position_id_X_1;
	float NN_position_id_Y_1;
	float NN_position_id_X_2;
	float NN_position_id_Y_2;


#define CONNECT(b) chain.SetBranchAddress(#b, &b)

	CONNECT(NN_layer);
	CONNECT(NN_barrelEC);
	CONNECT(NN_phi);
	CONNECT(NN_theta);


	if (type == NUMBER1 || type == NUMBER2 || type == NUMBER3) {
		CONNECT(NN_nparticles1);
		CONNECT(NN_nparticles2);
		CONNECT(NN_nparticles3);
	}

	if (type >= POS1) {
		hists["position_X_0"] = new TH1D("h_position_X_0", "", 200, -10, 10);
		CONNECT(NN_position_id_X_0);
		hists["position_Y_0"] = new TH1D("h_position_Y_0", "", 200, -10, 10);
		CONNECT(NN_position_id_Y_0);
	}
	if (type >= POS2) {
		hists["position_X_1"] = new TH1D("h_position_X_1", "", 200, -10, 10);
		CONNECT(NN_position_id_X_1);
		hists["position_Y_1"] = new TH1D("h_position_Y_1", "", 200, -10, 10);
		CONNECT(NN_position_id_Y_1);
	}
	if (type >= POS3) {
		hists["position_X_2"] = new TH1D("h_position_X_2", "", 200, -10, 10);
		CONNECT(NN_position_id_X_2);
		hists["position_Y_2"] = new TH1D("h_position_Y_2", "", 200, -10, 10);
		CONNECT(NN_position_id_Y_2);
	}

#undef CONNECT

	for (Long64_t i = 0; i < chain.GetEntries(); ++i) {
		chain.GetEntry(i);
		if ((type == NUMBER1 && !NN_nparticles1) ||
		    (type == NUMBER2 && !NN_nparticles2) ||
		    (type == NUMBER3 && !NN_nparticles3))
		    continue;

		hists["layer"]->Fill(NN_layer);
		hists["barrelEC"]->Fill(NN_barrelEC);
		hists["phi"]->Fill(NN_phi);
		hists["theta"]->Fill(NN_theta);

		if (type >= POS1) {
			hists["position_X_0"]->Fill(NN_position_id_X_0);
			hists["position_Y_0"]->Fill(NN_position_id_Y_0);
		}
		if (type >= POS2) {
			hists["position_X_1"]->Fill(NN_position_id_X_1);
			hists["position_Y_1"]->Fill(NN_position_id_Y_1);
		}
		if (type >= POS3) {
			hists["position_X_2"]->Fill(NN_position_id_X_2);
			hists["position_Y_2"]->Fill(NN_position_id_Y_2);
		}
	}

	outfile.Write();

	return 0;
}

