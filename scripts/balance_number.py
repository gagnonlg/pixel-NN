import argparse
import os
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--ntrain', type=int, default=12000000)
p.add_argument('--ntest', type=int, default=5000000)
p.add_argument('--fractions', nargs='*', default=[0.22,0.26,0.52], type=float)
p.add_argument('--input', required=True)
p.add_argument('--output', required=True)
args = p.parse_args()

assert(len(args.fractions) == 3)

rootcorebin = os.environ['ROOTCOREBIN']
path = '{}/bin/x86_64-slc6-gcc49-opt/balanceNumber'.format(rootcorebin)

output = args.output.replace('.root', '')

subprocess.call([
    path,
    str(args.ntrain),
    str(args.ntest),
    str(args.fractions[0]),
    str(args.fractions[1]),
    str(args.fractions[2]),
    args.input,
    output + '.training.root',
    output + '.test.root'
])

exit(0)
