#ifndef pixel_NN_dataset_ClustersLoop_H
#define pixel_NN_dataset_ClustersLoop_H

#include <string>
#include <TTree.h>
#include <EventLoop/Algorithm.h>

class ClustersLoop : public EL::Algorithm
{
public:
	std::string outputName;
	TTree *outtree;  //!

	// output variables
	int out_EventNumber; //!

	// have to explicitely ask for default constructor
	// if we don't, job submission from driver script fails
	ClustersLoop () = default;
	virtual EL::StatusCode setupJob (EL::Job& job);
	virtual EL::StatusCode fileExecute ();
	virtual EL::StatusCode histInitialize ();
	virtual EL::StatusCode changeInput (bool firstFile);
	virtual EL::StatusCode initialize ();
	virtual EL::StatusCode execute ();
	virtual EL::StatusCode postExecute ();
	virtual EL::StatusCode finalize ();
	virtual EL::StatusCode histFinalize ();

	ClassDef(ClustersLoop, 1);
};

#endif
