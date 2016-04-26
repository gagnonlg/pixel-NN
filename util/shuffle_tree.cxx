#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <vector>

#include <TFile.h>
#include <TTree.h>


std::vector<Long64_t> gen_range(Long64_t start, Long64_t stop)
{
	std::vector<Long64_t> r;
	for (Long64_t i = start; i < stop; i++)
		r.push_back(i);
	return r;
}

// usage: <seed> <input> <output>
int main(int argc, char *argv[])
{
	if (argc != 4) {
		std::fprintf(stderr, "usage: %s <seed> <input> <output>\n", argv[0]);
		return 1;
	}

	unsigned seed = atoi(argv[1]);

	TFile tfile(argv[2]);
	if (tfile.IsZombie()) {
		std::fprintf(stderr, "unable to open ROOT file\n");
		return 1;
	}

	TTree *tree = (TTree*)tfile.Get("NNinput");
	if (!tree) {
		std::fprintf(stderr, "unable to get TTree\n");
		return 1;
	}

	TFile outfile(argv[3], "CREATE");
	TTree *newtree = tree->CloneTree(0);

	std::vector<Long64_t> indices = gen_range(0, tree->GetEntries());
	shuffle(indices.begin(), indices.end(), std::default_random_engine(seed));

	Int_t nread = tree->LoadBaskets(2328673567232LL);

	for (Long64_t& i : indices) {
		tree->GetEntry(i);
		newtree->Fill();
	}

	outfile.Write(0, TObject::kWriteDelete);
}
