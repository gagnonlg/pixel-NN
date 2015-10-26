#ifndef pixel_NN_dataset_ClustersLoop_H
#define pixel_NN_dataset_ClustersLoop_H

#include <EventLoop/Algorithm.h>

class ClustersLoop : public EL::Algorithm
{
public:

	ClustersLoop ();
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
