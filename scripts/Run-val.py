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
argp.add_argument('--ignore-errors', action='store_true')
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

try:
    driver.submit(job, "submitDir")
except SystemError:
    if args.ignore_errors:
        print "*** caught SystemError, ignoring it"
    else:
        raise

#########################################

import glob

input_paths = glob.glob("submitDir/data-NNinput/*.root")
output_path = "test.root"

import importlib
validation = importlib.import_module('.validation', 'pixel-NN')
validation.make_histograms(input_paths, output_path)
