#ifndef __VALIDATION_HISTOGRAMS_H__
#define __VALIDATION_HISTOGRAMS_H__

#include <string>

#include <EventLoop/Worker.h>
#include <TH1D.h>

// forward decl
class ClustersLoop;


static const char* hist_name(std::string prefix, std::string name)
{
	std::string hname = "h_" + prefix + "_" + name;
	return hname.c_str();
}

#define HIST1(name, prefix, nbins, xlow, xup)	\
	h_##name(hist_name(prefix, #name), "", nbins, xlow, xup)

struct ValidationHistograms {
       ValidationHistograms(std::string name="")
	:
        HIST1(total_charge, name, 1000, 0, 5e6)
	{};

	TH1D h_total_charge;

	void add_histograms_to_worker(EL::Worker *wk);
	void fill_histograms(ClustersLoop *data);

	ClassDef(ValidationHistograms, 1);
};



#undef HIST1

#endif
