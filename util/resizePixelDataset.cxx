#include <cstdlib>
#include <TChain.h>
#include <TFile.h>
#include <TTree.h>

int main(int argc, char *argv[])
{
	int i;
	size_t n1,c1;
	size_t n2,c2;
	size_t n3,c3;

	n1 = c1 = n2 = c2 = n3 = c3 = 0;

	for (i = 1; i < argc && argv[i][0] == '-'; i += 2) {
		if (!argv[i+1]) {
			std::fprintf(stderr, "too few arguments\n");
			return 1;
		}
		switch (argv[i][1]) {
		case '1':
			n1 = std::atoll(argv[i+1]);
			break;
		case '2':
			n2 = std::atoll(argv[i+1]);
			break;
		case '3':
			n3 = std::atoll(argv[i+1]);
			break;
		default:
			std::fprintf(stderr, "unrecognized argument\n");
			return 1;
		}
	}

	if (argc - i < 2) {
		std::fprintf(stderr, "usage: %s [-{1,2,3} N] out.root in.root in2.root ...\n", argv[0]);
		return 1;
	}

	char *outname = argv[i++];

	TChain chain("NNinput");
	for (; i < argc; i++)
		chain.Add(argv[i]);

	chain.GetEntry(0);
	TFile outfile(outname, "CREATE");
	if (outfile.IsZombie()) {
		std::fprintf(stderr, "error creating outfile\n");
		return 1;
	}

	TTree *tree = (TTree*)chain.GetTree()->CloneTree(0);

	int particles1;
	if (chain.FindBranch("NN_nparticles1"))
		chain.SetBranchAddress("NN_nparticles1", &particles1);
	else
		particles1 = 1;

	int particles2;
	if (chain.FindBranch("NN_nparticles2"))
		chain.SetBranchAddress("NN_nparticles2", &particles2);
	else if (chain.FindBranch("NN_position_id_X_1")) {
		particles1 = 0;
		particles2 = 1;
	} else {
		particles2 = 0;
	}

	int particles3;
	if (chain.FindBranch("NN_nparticles3"))
		chain.SetBranchAddress("NN_nparticles3", &particles3);
	else if (chain.FindBranch("NN_position_id_X_2")) {
		particles1 = 0;
		particles2 = 0;
		particles3 = 1;
	} else {
		particles3 = 0;
	}

	for (Long64_t j = 0; j < chain.GetEntries() && (c1 < n1 || c2 < n2 || c3 < n3); ++j) {
		chain.GetEntry(j);
		if ((c1 < n1) && particles1) {
			c1++;
			tree->Fill();
		} else if ((c2 < n2) && particles2) {
			c2++;
			tree->Fill();
		} else if ((c3 < n3) && particles3) {
			c3++;
			tree->Fill();
		}
	}

	if (c1 < n1)
		std::fprintf(stderr, "WARNING: missing 1 particles clusters\n");
	if (c2 < n2)
		std::fprintf(stderr, "WARNING: missing 2 particles clusters\n");
	if (c3 < n3)
		std::fprintf(stderr, "WARNING: missing 3 particles clusters\n");

	outfile.Write(0,TObject::kWriteDelete);


	return 0;
}
