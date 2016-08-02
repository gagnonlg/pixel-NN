import argparse
import itertools as it
import os.path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import ROOT
import root_numpy

args = argparse.ArgumentParser()
args.add_argument('path_16')
args.add_argument('path_15')
args = args.parse_args()

tfile_16 = ROOT.TFile(args.path_16)
tfile_15 = ROOT.TFile(args.path_15)

tree_16 = tfile_16.Get("NNinput")
tree_15 = tfile_15.Get("NNinput")

conditions = [
    (None, 'all'),
    ('NN_barrelEC==0&&NN_layer==0', 'ibl'),
    ('NN_barrelEC==0&&NN_layer==1', 'blayer')
]

stats = [
    (np.mean, 'mean'),
    (np.std, 'std'),
    (np.median, 'median'),
    (np.amin, 'min'),
    (np.amax, 'max')
]

def calc_matrix(tree, condition=None, stat_op=np.mean):

    stat = np.zeros(7*7)

    for i, branch in enumerate(["NN_matrix{}".format(i) for i in range(7*7)]):
        print "  -> {}".format(branch)
        array = root_numpy.tree2array(tree, branches=branch, selection=condition)
        stat[i] = stat_op(array)
    matrix = stat.reshape((7,7))

    return matrix

def get_matrices(condition, name, stat_op, stat_name):

    def calc(tree, num):
        fname = 'matrix_{}_{}_{}.gz'.format(num, name, stat_name)

        if os.path.exists(fname):
            matrix = np.loadtxt(fname)
        else:
            matrix = calc_matrix(tree, condition, stat_op)
            np.savetxt(fname, matrix)
        return matrix

    m16 = calc(tree_16, 16)
    m15 = calc(tree_15, 15)

    return m16, m15

def graphs(matrix_16, matrix_15, name, stat_name):

    name = '{}_{}'.format(name, stat_name)

    plt.imshow(matrix_16, interpolation='none', cmap='Reds')
    plt.colorbar()
    plt.savefig('matrix_16_{}.png'.format(name))
    plt.close()

    plt.imshow(matrix_15, interpolation='none', cmap='Reds')
    plt.colorbar()
    plt.savefig('matrix_15_{}.png'.format(name))
    plt.close()

    diff = matrix_16 - matrix_15
    vmax = np.max(diff)
    vmin = -vmax
    plt.imshow(diff, interpolation='none', cmap='bwr', vmin=vmin, vmax=vmax)
    plt.colorbar()
    plt.savefig('matrix_16-15_{}.png'.format(name))
    plt.close()

    rel_diff = diff / matrix_15
    vmax = np.max(rel_diff)
    vmin = -vmax
    plt.imshow(rel_diff, interpolation='none', cmap='bwr', vmin=vmin, vmax=vmax)
    plt.colorbar()
    plt.savefig('matrix_16-15_rel_{}.png'.format(name))
    plt.close()

for (stat_op, stat_name),(cond,name) in it.product(stats,conditions):
    print "==> {} {}".format(stat_name, name)
    m16, m15 = get_matrices(cond, name, stat_op, stat_name)
    graphs(m16, m15, name, stat_name)


