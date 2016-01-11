import argparse
from rootpy.io import root_open

p = argparse.ArgumentParser()
p.add_argument('--input', required=True)
p.add_argument('--output')
p.add_argument('--nmax', type=int)
p.add_argument('--tree', default='NNinput')
args = p.parse_args()

output = open(args.output, 'w') if args.output else None
root_open(args.input).get(args.tree).csv(limit=args.nmax, stream=output)
