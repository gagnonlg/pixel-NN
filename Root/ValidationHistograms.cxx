#include <algorithm>
#include <pixel-NN/ClustersLoop.h>
#include <pixel-NN/ValidationHistograms.h>

void ValidationHistograms::add_histograms_to_worker(EL::Worker *wk)
{
	wk->addOutput(&h_total_charge);
	wk->addOutput(&h_multiplicity);
	wk->addOutput(&h_max_charge);
	wk->addOutput(&h_matrix0_charge);
	wk->addOutput(&h_matrix18_charge);
	wk->addOutput(&h_matrix24_charge);
}

void ValidationHistograms::fill_histograms(ClustersLoop *data)
{
	/* total charge */
	double total_charge = 0;
	for (auto c: data->out_matrix)
		total_charge += c;
	h_total_charge.Fill(total_charge);

	/* multiplicity */
	int mult = 0;
	for (auto c: data->out_matrix)
		mult += (c > 0);
	h_multiplicity.Fill(mult);

	/* max charge */
	h_max_charge.Fill(*std::max_element(data->out_matrix.begin(), data->out_matrix.end()));

	/* individual pixels charge distribution */
	h_matrix0_charge.Fill(data->out_matrix.at(0));
	h_matrix18_charge.Fill(data->out_matrix.at(18));
	h_matrix24_charge.Fill(data->out_matrix.at(24));
}
