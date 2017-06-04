// -*- mode: c++ -*-

#include <utility>
#include <vector>

namespace PixelNN {

    enum Direction { X, Y };

    void
    normalize_inplace(std::vector<double>& dvec);

    std::pair<double, double>
    split_probabilities(std::vector<double>& nn_output);

    int
    estimate_number(std::vector<double>& nn_output,
    		    double threshold_2p = 0.6,
    		    double threshold_3p = 0.2);


    int
    estimate_number(std::pair<double, double>& probs,
		    double threshold_2p = 0.6,
		    double threshold_3p = 0.2);

    std::vector<double>
    hit_positions(std::vector<double>& nn_output); // TODO: other parameters

    double
    hit_position_uncertainty(std::vector<double>& nn_output, Direction d);
}

