#include <EventLoop/Job.h>
#include <EventLoop/StatusCode.h>
#include <EventLoop/Worker.h>
#include <xAODRootAccess/Init.h>
#include <xAODRootAccess/TEvent.h>
#include <pixel-NN-dataset/ClustersLoop.h>

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
	return EL::StatusCode::SUCCESS;
}

EL::StatusCode ClustersLoop :: execute ()
{
	return EL::StatusCode::SUCCESS;
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

EL::StatusCode ClustersLoop :: initialize ()
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
