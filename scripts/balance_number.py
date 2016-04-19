import argparse
import os
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--skip', type=int, default=0)
p.add_argument('--nclusters', type=int, default=12000000)
p.add_argument('--fractions', nargs='*', default=[22,26,52], type=int)
p.add_argument('--input', required=True)
p.add_argument('--output', required=True)
args = p.parse_args()

assert(len(args.fractions) == 3)

rootcorebin = os.environ['ROOTCOREBIN']
path = '{}/bin/x86_64-slc6-gcc49-opt/balanceNumber'.format(rootcorebin)

subprocess.call([
    path,
    str(args.skip),
    str(args.nclusters),
    str(args.fractions[0]),
    str(args.fractions[1]),
    str(args.fractions[2]),
    args.input,
    args.output
])

exit(0)
