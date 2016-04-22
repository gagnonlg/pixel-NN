import argparse
import os
import subprocess
import random
from datetime import datetime

random.seed(datetime.now())
seed = random.randint(1,2**30)

p = argparse.ArgumentParser()
p.add_argument('--input', required=True)
p.add_argument('--output', required=True)
p.add_argument('--seed', default=seed, type=int)
args = p.parse_args()

rootcorebin = os.environ['ROOTCOREBIN']
path = '{}/bin/x86_64-slc6-gcc49-opt/shuffle_tree'.format(rootcorebin)

subprocess.call([
    path,
    str(args.seed),
    args.input,
    args.output
])

exit(0)
