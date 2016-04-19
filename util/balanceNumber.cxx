#include <algorithm>
#include <cstdlib>
#include <cstdio>

#include <TFile.h>
#include <TTree.h>

// usage: balanceNumber <skip> <nclusters> <fraction1> <fraction2> <fraction3> <in> <out>
// argv indices:        1      2           3           4           5           6    7
int main(int argc, char *argv[])
{
	if (argc != 8) {
		std::fprintf(stderr, "usage: balanceNumber <skip> <nclusters> <fraction1> <fraction2> <fraction3> <in> <out>\n");
		return 3;
	}

	Long64_t skip = std::strtoll(argv[1], NULL, 0);
	Long64_t nclusters = std::strtoll(argv[2], NULL, 0);
	double fraction1 = std::atof(argv[3]);
	double fraction2 = std::atof(argv[4]);
	double fraction3 = std::atof(argv[5]);

	TFile tfile(argv[6]);
	if (tfile.IsZombie()) {
		std::fprintf(stderr, "unable to open ROOT file\n");
		return 1;
	}

	TTree *tree = (TTree*)tfile.Get("NNinput");
	if (!tree) {
		std::fprintf(stderr, "unable to get TTree\n");
		return 2;
	}

	tree->SetBranchStatus("*", 0);

	double nparticles1;
	tree->SetBranchStatus("NN_nparticles1", 1);
	tree->SetBranchAddress("NN_nparticles1", &nparticles1);
	tree->GetBranch("NN_nparticles1")->LoadBaskets();
	double nparticles2;
	tree->SetBranchStatus("NN_nparticles2", 1);
	tree->SetBranchAddress("NN_nparticles2", &nparticles2);
	tree->GetBranch("NN_nparticles2")->LoadBaskets();
	double nparticles3;
	tree->SetBranchStatus("NN_nparticles3", 1);
	tree->SetBranchAddress("NN_nparticles3", &nparticles3);
	tree->GetBranch("NN_nparticles3")->LoadBaskets();

	TFile outfile(argv[7], "CREATE");
	TTree *newtree = tree->CloneTree(0);

	Long64_t n1 = 0;
	Long64_t total1 = fraction1 * nclusters;
	Long64_t n2 = 0;
	Long64_t total2 = fraction2 * nclusters;
	Long64_t n3 = 0;
	Long64_t total3 = fraction3 * nclusters;

	Long64_t total = std::min(total1 + total2 + total3, tree->GetEntries());

	for (Long64_t i = skip; i < total; i++) {
		tree->GetEntry(i);
		if ((nparticles1 == 1 && n1++ < total1) ||
		    (nparticles2 == 1 && n2++ < total2) ||
		    (nparticles3 == 1 && n3++ < total3))
			newtree->Fill();
	}

	outfile.Write(0, TObject::kWriteDelete);

	return 0;
}
