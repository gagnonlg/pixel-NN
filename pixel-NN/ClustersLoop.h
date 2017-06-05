#ifndef pixel_NN_dataset_ClustersLoop_H
#define pixel_NN_dataset_ClustersLoop_H

#include <map>
#include <string>
#include <vector>
#include <TTree.h>
#include <TVector3.h>
#include <AthContainers/DataVector.h>
#include <EventLoop/Algorithm.h>
#include <xAODTracking/TrackMeasurementValidation.h>
#include <pixel-NN/ValidationHistograms.h>

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
	bool dilute;
	double scaleIBL;
	bool doValidation;
	bool inclusive;

	int fraction1; //!
	int fraction2; //!

	TTree *outtree;  //!

	// output variables
	double out_RunNumber; //!
	double out_EventNumber; //!
	double out_ClusterNumber; //!
	double out_sizeX; //!
	double out_sizeY; //!
	double out_localEtaPixelIndexWeightedPosition; //!
	double out_localPhiPixelIndexWeightedPosition; //!
	double out_layer; //!
	double out_barrelEC; //!
	double out_etaModule; //!
	double out_phi; //!
	double out_theta; //!
	double out_globalX; //!
	double out_globalY; //!
	double out_globalZ; //!
	double out_globalEta; //!
	std::vector<double> out_matrix; //!
	std::vector<double> out_pitches; //!

	double out_nparticles1; //!
	double out_nparticles2; //!
	double out_nparticles3; //!
	double out_nparticles_excess; //!
	double out_position_id_X_0; //!
	double out_position_id_Y_0; //!
	double out_position_id_X_1; //!
	double out_position_id_Y_1; //!
	double out_position_id_X_2; //!
	double out_position_id_Y_2; //!

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

	void clustersLoop(const DataVector<xAOD::TrackMeasurementValidation>*);
	void init_validation_histograms();
	void fill_validation_histograms();

	// validation histograms map
	std::map<std::string, ValidationHistograms> validation_hists;

	ClassDef(ClustersLoop, 1);
};

#endif
