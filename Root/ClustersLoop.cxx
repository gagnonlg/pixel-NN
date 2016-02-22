#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <utility>
#include <vector>
#include <TFile.h>
#include <AthContainers/AuxElement.h>
#include <EventLoop/Job.h>
#include <EventLoop/StatusCode.h>
#include <EventLoop/Worker.h>
#include <xAODEventInfo/EventInfo.h>
#include <xAODRootAccess/Init.h>
#include <xAODRootAccess/TEvent.h>
#include <xAODTracking/TrackMeasurementValidation.h>
#include <pixel-NN/ClustersLoop.h>

ClassImp(ClustersLoop)

EL::StatusCode ClustersLoop :: setupJob (EL::Job& job)
{
	job.useXAOD();
	xAOD::TReturnCode rc = xAOD::Init();
	if (! rc.isSuccess()) {
		Error("setupJob()", "Failed to execute xAOD::Init()");
		return EL::StatusCode::FAILURE;
	}
	return EL::StatusCode::SUCCESS;
}

EL::StatusCode ClustersLoop :: histInitialize ()
{
	outtree = new TTree("NNinput", "NNinput");
	outtree->SetDirectory(wk()->getOutputFile(outputName));

	outtree->Branch("RunNumber", &out_RunNumber);
	outtree->Branch("EventNumber", &out_EventNumber);
	outtree->Branch("ClusterNumber", &out_ClusterNumber);
	outtree->Branch("NN_sizeX", &out_sizeX);
	outtree->Branch("NN_sizeY", &out_sizeY);
	outtree->Branch("NN_localEtaPixelIndexWeightedPosition",
			&out_localEtaPixelIndexWeightedPosition);
	outtree->Branch("NN_localPhiPixelIndexWeightedPosition",
			&out_localPhiPixelIndexWeightedPosition);
	outtree->Branch("NN_layer", &out_layer);
	outtree->Branch("NN_barrelEC", &out_barrelEC);
	outtree->Branch("NN_etaModule", &out_etaModule);
	outtree->Branch("NN_phi", &out_phi);
	outtree->Branch("NN_theta", &out_theta);

	return EL::StatusCode::SUCCESS;
}

EL::StatusCode ClustersLoop :: initialize ()
{
	xAOD::TEvent* event = wk()->xaodEvent();

	const DataVector<xAOD::TrackMeasurementValidation> *clusters;
	xAOD::TReturnCode rc = event->retrieve(clusters, "PixelClusters");
	if (! rc.isSuccess()) {
		Error("Initialize()", "Failed to retrieve PixelClusters");
		return EL::StatusCode::FAILURE;
	}

	const xAOD::TrackMeasurementValidation *cl = clusters->at(0);
	out_sizeX = cl->auxdata<int>("NN_sizeX");
	out_sizeY = cl->auxdata<int>("NN_sizeY");
	out_matrix.resize(out_sizeX * out_sizeY);

	float *matrixPtr = out_matrix.data();
	char matrixbranch[strlen("NN_matrix???") + 1];
	for (int i = 0; i < out_sizeX*out_sizeY; i++) {
		std::sprintf(matrixbranch, "NN_matrix%d", i);
		outtree->Branch(matrixbranch, matrixPtr + i);
	}

	out_pitches.resize(out_sizeY);
	float *pitchesPtr = out_pitches.data();
	char pitchesbranch[strlen("NN_pitches???") + 1];
	for (int i = 0; i < out_sizeY; i++) {
		std::sprintf(pitchesbranch, "NN_pitches%d", i);
		outtree->Branch(pitchesbranch, pitchesPtr + i);
	}

	if (NNtype == NUMBER) {
		outtree->Branch("NN_nparticles1", &out_nparticles1);
		outtree->Branch("NN_nparticles2", &out_nparticles2);
		outtree->Branch("NN_nparticles3", &out_nparticles3);
	} else if (NNtype < ERRORX1) {
		if (NNtype >= POS1) {
			outtree->Branch("NN_position_id_X_0",
					&out_position_id_X_0);
			outtree->Branch("NN_position_id_Y_0",
					&out_position_id_Y_0);
		}
		if (NNtype >= POS2) {
			outtree->Branch("NN_position_id_X_1",
					&out_position_id_X_1);
			outtree->Branch("NN_position_id_Y_1",
					&out_position_id_Y_1);
		}
		if (NNtype >= POS3) {
			outtree->Branch("NN_position_id_X_2",
					&out_position_id_X_2);
			outtree->Branch("NN_position_id_Y_2",
					&out_position_id_Y_2);
		}
	}

	return EL::StatusCode::SUCCESS;
}

EL::StatusCode ClustersLoop :: execute ()
{
	xAOD::TEvent* event = wk()->xaodEvent();

	const xAOD::EventInfo *eventInfo = 0;
	xAOD::TReturnCode rc = event->retrieve(eventInfo, "EventInfo");
	if (! rc.isSuccess()) {
		Error("execute()", "Failed to retrieve EventInfo");
		return EL::StatusCode::FAILURE;
	}

	out_RunNumber = eventInfo->runNumber();
	out_EventNumber = eventInfo->eventNumber();

	const DataVector<xAOD::TrackMeasurementValidation> *clusters;
	rc = event->retrieve(clusters, "PixelClusters");
	if (! rc.isSuccess()) {
		Error("Initialize()", "Failed to retrieve PixelClusters");
		return EL::StatusCode::FAILURE;
	}

	clustersLoop(clusters);

	return EL::StatusCode::SUCCESS;
}

#define accessor(n,t,v) SG::AuxElement::ConstAccessor< t > n (v)

accessor(a_sizeX, int, "NN_sizeX");
accessor(a_sizeY, int, "NN_sizeY");
accessor(a_posX, std::vector<float>, "NN_positions_indexX");
accessor(a_posY, std::vector<float>, "NN_positions_indexY");
accessor(a_localEtaPixelIndexWeightedPosition, float,
	 "NN_localEtaPixelIndexWeightedPosition");
accessor(a_localPhiPixelIndexWeightedPosition, float,
	 "NN_localPhiPixelIndexWeightedPosition");
accessor(a_layer, int, "layer");
accessor(a_bec, int, "bec");
accessor(a_etaModule, int, "eta_module");
accessor(a_matrix, std::vector<float>, "NN_matrixOfCharge");
accessor(a_pitches, std::vector<float>, "NN_vectorOfPitchesY");
accessor(a_theta, std::vector<float>,  "NN_theta");
accessor(a_phi, std::vector<float>,  "NN_phi");

#undef accessor

typedef std::vector<std::pair<float,float> > Positions;

bool pairComp(std::pair<float,float> a, std::pair<float,float> b)
{
	if (a.first == b.first)
		return a.second < b.second;
	else
		return a.first < b.first;
}

Positions sortedPositions(std::vector<float>& xs, std::vector<float>& ys)
{
	Positions ps;
	for (size_t i = 0; i < xs.size(); i++)
		ps.push_back(std::make_pair(xs.at(i), ys.at(i)));
	std::sort(ps.begin(), ps.end(), pairComp);
	return ps;
}

void ClustersLoop::clustersLoop(const DataVector<xAOD::TrackMeasurementValidation>* clusters)
{
	out_ClusterNumber = 0;
	for (auto c : *clusters) {
		out_ClusterNumber += 1;

		/* fetch cluster observables */
		const std::vector<float> matrix = a_matrix(*c);
		std::vector<float> posX = a_posX(*c);
		std::vector<float> posY = a_posY(*c);
		const std::vector<float> pitches = a_pitches(*c);
		out_localEtaPixelIndexWeightedPosition =
			a_localEtaPixelIndexWeightedPosition(*c);
		out_localPhiPixelIndexWeightedPosition =
			a_localPhiPixelIndexWeightedPosition(*c);
		out_layer = a_layer(*c);
		out_barrelEC = a_bec(*c);
		out_etaModule = a_etaModule(*c);
		std::vector<float> theta = a_theta(*c);
		std::vector<float> phi = a_phi(*c);
		int sizeX = a_sizeX(*c);
		int sizeY = a_sizeY(*c);

		/* check if good cluster */
		// matrix size
		if (matrix.size() == 0)
			continue;
		if ((int)matrix.size() != sizeX * sizeY)
			continue;
		if (matrix.size() != out_matrix.size())
			continue;
		// NN_sizeX value
		if (sizeX == -100)
			continue;
		// nparticles
		if (posX.size() == 0)
			continue;
		if ((NNtype == POS1 && posX.size() != 1) ||
		    (NNtype == POS2 && posX.size() != 2) ||
		    (NNtype == POS3 && posX.size() != 3))
			continue;
		// BEC
		if (abs(out_barrelEC > 2))
			continue;

		/* Fill charge matrix */
		for (size_t i = 0; i < matrix.size(); i++)
			out_matrix.at(i) = matrix.at(i);

		/* Fill vector of pitches */
		for (size_t i = 0; i < pitches.size(); i++)
			out_pitches.at(i) = pitches.at(i);

		/* Determine number of particles */
		out_nparticles1 = posX.size() == 1;
		out_nparticles2 = posX.size() == 2;
		out_nparticles3 = posX.size() == 3;

		/* Sort and store the positions */
		out_position_id_X_0 = 0;
		out_position_id_Y_0 = 0;
		out_position_id_X_1 = 0;
		out_position_id_Y_1 = 0;
		out_position_id_X_2 = 0;
		out_position_id_Y_2 = 0;
		Positions ps = sortedPositions(posX, posY);
		if (NNtype >= POS1) {
			out_position_id_X_0 = ps.at(0).first;
			out_position_id_Y_0 = ps.at(0).second;
		}
		if (NNtype >= POS2) {
			out_position_id_X_1 = ps.at(1).first;
			out_position_id_Y_1 = ps.at(1).second;
		}
		if (NNtype >= POS3) {
			out_position_id_X_2 = ps.at(2).first;
			out_position_id_Y_2 = ps.at(2).first;
		}
		if (std::isinf(out_position_id_X_0) ||
		    std::isinf(out_position_id_Y_0) ||
		    std::isinf(out_position_id_X_1) ||
		    std::isinf(out_position_id_Y_1) ||
		    std::isinf(out_position_id_X_2) ||
		    std::isinf(out_position_id_Y_2))
			continue;

		/* Loop over angles */
		for (size_t i = 0; i < theta.size(); i++) {
			out_theta = theta.at(i);
			if (out_theta == 0 || std::isnan(out_theta))
				continue;
			out_phi   = phi.at(i);
			if (out_barrelEC == 2) {
				out_theta *= -1;
				out_phi   *= -1;
			}
			outtree->Fill();
		}
	}
}

/*-------------------- unneeded stuff -----------------------------------------*/

EL::StatusCode ClustersLoop :: fileExecute ()
{
	return EL::StatusCode::SUCCESS;
}

EL::StatusCode ClustersLoop :: changeInput (bool /*firstFile*/)
{
	return EL::StatusCode::SUCCESS;
}



EL::StatusCode ClustersLoop :: postExecute ()
{
	return EL::StatusCode::SUCCESS;
}

EL::StatusCode ClustersLoop :: finalize ()
{
	return EL::StatusCode::SUCCESS;
}

EL::StatusCode ClustersLoop :: histFinalize ()
{
	return EL::StatusCode::SUCCESS;
}
