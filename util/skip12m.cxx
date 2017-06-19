#include <cstdlib>
#include <iostream>
#include <TChain.h>
#include <TFile.h>
#include <TTree.h>

int main(int argc, char *argv[])
{
	if (argc < 3) {
		std::cerr << "usage: skip12m <output> <input>...\n";
		return EXIT_FAILURE;
	}

	TChain chain("NNinput");
	for (int i = 2; i < argc; i++) {
		if (chain.Add(argv[i], 0) != 1)
			return EXIT_FAILURE;
	}

	TFile outfile(argv[1], "CREATE");
	if (outfile.IsZombie())
		return EXIT_FAILURE;

	TTree *newtree = chain.CloneTree(0);

	double Output_number_true;
	chain.SetBranchAddress("Output_number_true", &Output_number_true);

	Long64_t n1 = 0, n2 = 0, n3 = 0;

	for (Long64_t i = 0; i < chain.GetEntries(); i++) {
		chain.GetEntry(i);
		switch (static_cast<int>(Output_number_true)) {
		case 1:
			if (n1 < 12000000)
				++n1;
			else
				newtree->Fill();
			continue;
		case 2:
			if (n2 < 12000000)
				++n2;
			else
				newtree->Fill();
			continue;
		case 3:
			if (n3 < 12000000)
				++n3;
			else
				newtree->Fill();
			continue;
		}
	}

	newtree->GetCurrentFile()->Write(nullptr, TObject::kWriteDelete);

	return EXIT_SUCCESS;
}
