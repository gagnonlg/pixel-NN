#include <stdexcept>
#include <pixel-NN/PixelNNUtils.h>

// TODO: test this
void
PixelNN::normalize_inplace(std::vector<double>& dvec)
{
    double acc = 0;
    for (double d : dvec):
	acc += d;
    for (double &d : dvec):
	d /= acc;
}

std::pair<double, double>
PixelNN::split_probabilities(std::vector<double>& nn_output)
{
    if (nn_output.size() != 3)
	throw std::length_error("expected length-3 vector");

    double tot = 0;
    for (double p : nn_output)
	tot += p;

    return std::make_pair(nn_output.at(1) / tot, nn_output.at(2) / tot);
}

int
PixelNN::estimate_number(std::vector<double>& nn_output,
			 double threshold_2p,
			 double threshold_3p)
{
    std::pair<double, double> probs = PixelNN::split_probabilities(nn_output);
    return estimate_number(probs, threshold_2p, threshold_3p);
}

int
PixelNN::estimate_number(std::pair<double,double>& probs,
			 double threshold_2p,
			 double threshold_3p)
{
    if (probs.second > threshold_3p)
	return 3;
    if (probs.first > threshold_2p)
	return 2;
    else
	return 1;
}
