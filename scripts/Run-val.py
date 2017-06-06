import argparse
import os
import shutil
import subprocess
import ROOT
import logging

logging.basicConfig(level=logging.INFO)

logging.info('Initialization')
ROOT.xAOD.Init().ignore()

logging.info('Parsing arguments')
argp = argparse.ArgumentParser()
argp.add_argument('--input', required=True)
argp.add_argument('--nevents', type=int)
args = argp.parse_args()

logging.info("Searching for datasets")
sampleHandler = ROOT.SH.SampleHandler()
ROOT.SH.ScanDir().scan(sampleHandler, args.input)
logging.info("found %d datasets" % len(sampleHandler))

logging.info('Setting up the NNinput creation job')
job = ROOT.EL.Job()
job.sampleHandler(sampleHandler)

if args.nevents is not None:
    logging.info("processing a maximum of %d events", args.nevents)
    job.options().setDouble(ROOT.EL.Job.optMaxEvents, args.nevents)

clustersLoop = ROOT.ClustersLoop()
clustersLoop.scaleIBL = 1 # scale set to 1
clustersLoop.doValidation = False
clustersLoop.inclusive = True;
job.algsAdd(clustersLoop)

output = ROOT.EL.OutputStream("NNinput")
job.outputAdd(output)
ntuple = ROOT.EL.NTupleSvc("NNinput")
job.algsAdd(ntuple)
clustersLoop.outputName = "NNinput"

logging.info("submitting NNinput creation job")
shutil.rmtree("submitDir", ignore_errors=True)
driver = ROOT.EL.DirectDriver()
driver.submitOnly(job, "submitDir")


#########################################

import glob

input_path = glob.glob("submitDir/data-NNinput/*.root")[0]
print input_path
NN_path = "/afs/cern.ch/user/l/lgagnon/private/NN_note/run/PixelNN_TTrainedNetworks.root"
output_path = "test.root"

vloop = ROOT.ValidationLoop(input_path, NN_path, output_path);
vloop.Loop()

import importlib
validation = importlib.import_module('.validation', 'pixel-NN')
validation.make_histograms(output_path, 'hists_test.root')