import argparse
import os
import shutil
import subprocess
import ROOT
import logging

dirp = os.path.dirname(os.path.realpath(__file__))
try:
    version  = subprocess.check_output("cd %s && git describe --long" % dirp, shell=True).replace('.','-').strip()
except OSError:
    version = ""

logging.basicConfig(level=logging.INFO)

argp = argparse.ArgumentParser()
argp.add_argument("--grid-input", default="",
                  help="input dataset on the grid")
argp.add_argument("--process", default="unknown",
                  help="process identifier for output dataset name")
argp.add_argument("--scandirs", default=[], nargs="*",
                  help="searched directories when running locally")
argp.add_argument("--submit-dir", default="submitDir",
                  help="output directory")
argp.add_argument("--driver", choices=["direct", "grid"], default="direct",
                  help="job type")
argp.add_argument("--overwrite", action='store_const', const=True, default=False)
argp.add_argument("--nevents", type=int, default=None)
argp.add_argument("--type",
                  choices=['number','pos1','pos2','pos3'],
                  default='number')
argp.add_argument("--version", default=None, help="version id used when cannot use git")
args = argp.parse_args()

if version == "":
    version = "0-1_%s" % ('?' if args.version is None else args.version)

if args.overwrite:
    logging.warning("overwriting %s directory (if present)" % args.submit_dir)

ROOT.gROOT.Macro("$ROOTCOREDIR/scripts/load_packages.C")
ROOT.xAOD.Init().ignore()

logging.info("searching for datasets")
sampleHandler = ROOT.SH.SampleHandler()
if args.driver == "direct":
    for d in args.scandirs:
        ROOT.SH.scanDir(sampleHandler,d)
else:
    ROOT.SH.scanDQ2(sampleHandler, args.grid_input)
sampleHandler.setMetaString('nc_tree', 'CollectionTree')
logging.info("found %d datasets" % len(sampleHandler))

job = ROOT.EL.Job()
job.sampleHandler(sampleHandler)

if args.nevents is not None:
    logging.info("processing a maximum of %d events", args.nevents)
    job.options().setDouble(ROOT.EL.Job.optMaxEvents, args.nevents)

clustersLoop = ROOT.ClustersLoop()
# set options
clustersLoop.NNtype = {
    'number' : 0,
    'pos1'   : 1,
    'pos2'   : 2,
    'pos3'   : 3
}[args.type]
logging.info("creating input for %s neural network", args.type)
job.algsAdd(clustersLoop)

output = ROOT.EL.OutputStream("NNinput")
job.outputAdd(output)
ntuple = ROOT.EL.NTupleSvc("NNinput")
job.algsAdd(ntuple)

clustersLoop.outputName = "NNinput"

if args.driver == "direct":
    logging.info("Using the direct driver")
    driver = ROOT.EL.DirectDriver()
elif args.driver == "grid":
    logging.info("Using the grid driver")
    driver = ROOT.EL.PrunDriver()

# 1 : group
# 2 : perf-idtracking:group
# 3 : perf-idtracking
# 4 : <DSID>
# 5 : <PROCESS>
# 6 : <DATATYPE>
# 7 : <TAGS>
name =  "user.%nickname%.%in:name[4]%."
name += args.process if args.process is not None else "%in:name[5]"
name += ".%in:name[6]%.%in:name[7]%."
name += "$s-%s" % (args.type , version)

logging.info("Will tag with version %s" % version)


driver.options().setString("nc_outputSampleName", name)

logging.info("submitting job")
if args.overwrite:
    shutil.rmtree(args.submit_dir, ignore_errors=True)
driver.submitOnly(job, args.submit_dir)
