import argparse
import shutil
import ROOT
import logging

version_major = 0 # incremented when dataset composition changes
version_minor = 0 # incremented when bugs are fixed

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
args = argp.parse_args()

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

clustersLoop = ROOT.ClustersLoop()
# set options
job.algsAdd(clustersLoop)

if args.driver == "direct":
    logging.info("Using the direct driver")
    driver = ROOT.EL.DirectDriver()
elif args.driver == "grid":
    logging.info("Using the grid driver")
    driver = ROOT.EL.PrunDriver()

name =  "user.%nickname%.%in:name[2]%."
name += args.process if args.process is not None else "%in:name[3]"
name += ".%in:name[5]%.%in:name[6]%."
name += "NNInput_%d_%d" % (version_major, version_minor)

driver.options().setString("nc_outputSampleName", name)

logging.info("submitting job")
if args.overwrite:
    shutil.rmtree(args.submit_dir, ignore_errors=True)
driver.submitOnly(job, args.submit_dir)
