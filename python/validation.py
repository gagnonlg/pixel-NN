import itertools
import re
import ROOT

ROOT.gROOT.SetBatch(True)

def make_histograms(input_path, output_path):

    tfile = ROOT.TFile.Open(input_path, "READ")
    ttree = tfile.Get("NNValidation")

    ofile = ROOT.TFile.Open(output_path, "RECREATE")

    for name, var, cond in gen_hists_triplets():
        # print '==> ' + name
        # print '  -> ' + var
        # print '  -> ' + cond
        hist(
            ttree,
            name,
            var,
            cond
        )
    ofile.Write("", ROOT.TObject.kWriteDelete)


def hist(ttree, name, var, cond):
    ttree.Draw("{}>>{}(1000)".format(var, name), cond)
    return ROOT.gROOT.Get(name)

def gen_hists_triplets():
    for name, var, cond in gen_res_triplets():
        yield name, var , cond
    for name, var, cond in gen_res_triplets():
        name = name.replace('residuals', 'pull')
        var = '(' + var + ')' + '/' + get_uncert_var(name)
        yield name, var, cond

def get_uncert_var(name):
    var = 'Output_uncertainty_'
    m = re.match('h_.*_(.*)_(.*)_.*', name)
    var += m.group(1)
    var += '[{}]'.format(int(m.group(2)) - 1)
    return var

def gen_res_triplets():
    name = 'h_residuals'
    dirs = ['X', 'Y']
    layers = [
        ('all', ''),
        ('ibl', 'NN_layer==0 && NN_barrelEC==0'),
        ('barrel', 'NN_layer>0 && NN_barrelEC==0'),
        ('endcaps', 'NN_barrelEC!=0')
    ]

    mult = [
        (1, 'NN_nparticles1==1'),
        (2, 'NN_nparticles2==1'),
        (3, '(NN_nparticles3==1) && (NN_nparticles_excess==0)')
    ]

    iter = itertools.product(dirs, layers, mult)

    for d, (lname, lcond), (npart, ncond) in iter:

        idx = 2 * (npart - 1) + int(d == 'Y')

        name = 'h_residuals_{}_{}_{}'.format(d, npart, lname)

        var = 'Output_estimated_positions[%d] - Output_true_positions[%d]' % \
              (idx, idx)

        if lcond == '':
            cond = ncond
        else:
            cond = '({})&&({})'.format(lcond, ncond)

        yield name, var, cond
