#include <cstdlib>
#include <TChain.h>
#include <TFile.h>
#include <TTree.h>

int main(int argc, char *argv[])
{
	int i;
	size_t n,c;
	size_t skip = 0;
	char *treename = "NNinput";

	n = c = 0;

	for (i = 1; i < argc && argv[i][0] == '-'; i += 2) {
		if (!argv[i+1]) {
			std::fprintf(stderr, "too few arguments\n");
			return 1;
		}
		switch (argv[i][1]) {
		case 'n':
			n = std::atoll(argv[i+1]);
			break;
		case 's':
			skip = std::atoll(argv[i+1]);
			break;
		case 't':
			treename = argv[i+1];
			break;
		default:
			std::fprintf(stderr, "unrecognized argument: %s\n", argv[i]);
			return 1;
		}
	}

	if (argc - i < 2) {
		std::fprintf(stderr, "usage: %s [-n N] out.root in.root in2.root ...\n", argv[0]);
		return 1;
	}

	char *outname = argv[i++];

	TChain chain(treename);
	for (; i < argc; i++)
		chain.Add(argv[i]);

	chain.GetEntry(0);
	TFile outfile(outname, "CREATE");
	if (outfile.IsZombie()) {
		std::fprintf(stderr, "error creating outfile\n");
		return 1;
	}

	TTree *tree = (TTree*)chain.GetTree()->CloneTree(0);

	for (Long64_t j = skip; j < chain.GetEntries() && c < n; ++j) {
		chain.GetEntry(j);
		if (n > 0) {
			c++;
			tree->Fill();
		}
	}

	outfile.Write(0,TObject::kWriteDelete);

	return 0;
}
