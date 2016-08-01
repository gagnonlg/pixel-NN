#include <pixel-NN/ClustersLoop.h>
#include <pixel-NN/ValidationHistograms.h>

void ValidationHistograms::add_histograms_to_worker(EL::Worker *wk)
{
	wk->addOutput(&h_total_charge);
}

void ValidationHistograms::fill_histograms(ClustersLoop *data)
{
	double total_charge = 0;
	for (auto c: data->out_matrix)
		total_charge += c;
	h_total_charge.Fill(total_charge);
}
