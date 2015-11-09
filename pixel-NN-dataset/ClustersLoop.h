#ifndef pixel_NN_dataset_ClustersLoop_H
#define pixel_NN_dataset_ClustersLoop_H

#include <string>
#include <vector>
#include <TTree.h>
#include <EventLoop/Algorithm.h>

#define NUMBER  0
#define POS1    1
#define POS2    2
#define POS3    3
#define ERRORX1 4
#define ERRORY1 5
#define ERRORX2 6
#define ERRORY2 7
#define ERRORX3 8
#define ERRORY3 9

class ClustersLoop : public EL::Algorithm
{
public:
	// set in driver script
	std::string outputName;
	int NNtype;

	TTree *outtree;  //!

	// output variables
	int out_RunNumber; //!
	int out_EventNumber; //!
	int out_ClusterNumber; //!
	int out_sizeX; //!
	int out_sizeY; //!
	float out_localEtaPixelIndexWeightedPosition; //!
	float out_localPhiPixelIndexWeightedPosition; //!
	int out_layer; //!
	int out_barrelEC; //!
	int out_etaModule; //!
	float out_phi; //!
	float out_theta; //!
	std::vector<float> out_matrix; //!
	std::vector<float> out_pitches; //!

	float out_nparticles1; //!
	float out_nparticles2; //!
	float out_nparticles3; //!
	float out_position_id_X_0; //!
	float out_position_id_Y_0; //!
	float out_position_id_X_1; //!
	float out_position_id_Y_1; //!
	float out_position_id_X_2; //!
	float out_position_id_Y_2; //!

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

	size_t getMatrixSize();

	ClassDef(ClustersLoop, 1);
};

#endif
