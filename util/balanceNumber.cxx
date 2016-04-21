#include <algorithm>
#include <cstdlib>
#include <cstdio>

#include <TFile.h>
#include <TTree.h>

Long64_t balance(char *outpath,
		 TTree *tree,
		 double fraction1,
		 double fraction2,
		 double fraction3,
		 Long64_t nclusters,
		 Long64_t istart);

// usage: balanceNumber <ntrain> <ntest> <fraction1> <fraction2> <fraction3> <in> <out-train> <out-test>
// argv indices:        1        2       3           4           5           6    7           8
int main(int argc, char *argv[])
{
	if (argc != 9) {
		std::fprintf(stderr, "usage: balanceNumber <ntrain> <ntest> <fraction1> <fraction2> <fraction3> <in> <outtrain> <outtest>\n");
		return 3;
	}

	Long64_t ntrain = std::strtoll(argv[1], NULL, 0);
	Long64_t ntest = std::strtoll(argv[2], NULL, 0);
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

	Long64_t test_start = balance(argv[7], tree, fraction1, fraction2, fraction3, ntrain, 0);
	balance(argv[8], tree, fraction1, fraction2, fraction3, ntest, test_start);

	return 0;
}

Long64_t balance(char *outpath,
		 TTree *tree,
		 double fraction1,
		 double fraction2,
		 double fraction3,
		 Long64_t nclusters,
		 Long64_t istart)
{
	double nparticles1;
	tree->SetBranchAddress("NN_nparticles1", &nparticles1);
	double nparticles2;
	tree->SetBranchAddress("NN_nparticles2", &nparticles2);
	double nparticles3;
	tree->SetBranchAddress("NN_nparticles3", &nparticles3);

	TFile outfile(outpath, "CREATE");
	TTree *newtree = tree->CloneTree(0);

	Long64_t n1 = 0;
	Long64_t total1 = fraction1 * nclusters;
	Long64_t n2 = 0;
	Long64_t total2 = fraction2 * nclusters;
	Long64_t n3 = 0;
	Long64_t total3 = fraction3 * nclusters;

	Long64_t total = total1 + total2 + total3;
	Long64_t maxevt = tree->GetEntries();

	Long64_t i = istart;
	for (; i < maxevt && (n1+n2+n3) < total; i++) {
		tree->GetEntry(i);
		if (nparticles1 == 1) {
			if (n1 < total1) {
				n1++;
				newtree->Fill();
			}
		} else if (nparticles2 == 1) {
			if (n2 < total2) {
				n2++;
				newtree->Fill();
			}
		} else if (nparticles3 == 1) {
			if (n3 < total3) {
				n3++;
				newtree->Fill();
			}
		} else {
			std::fprintf(stderr, "nparticles1/2/3 == 0!\n");
		}

	}

	outfile.Write(0, TObject::kWriteDelete);

	return i;
}
