import itertools
import ROOT

ROOT.gROOT.SetBatch(True)

templates = [
    ('residuals_{n}_{d}', '(Output_positions_{d}[{i}] - Output_true_{d}[{i}])'),
    ('pull_{n}_{d}', '(Output_positions_{d}[{i}] - Output_true_{d}[{i}])/Output_uncert_{d}[{i}]'),
    ('corr_residuals_{n}_{d}', '(Output_corr_positions_{d}[{i}] - Output_corr_true_{d}[{i}])'),
    ('corr_pull_{n}_{d}', '(Output_corr_positions_{d}[{i}] - Output_corr_true_{d}[{i}])/Output_corr_uncert_{d}[{i}]')
]

numbers = [1, 2, 3]
directions = ['X', 'Y']
layers = [
    ('all', None),
    ('ibl', '((NN_layer==0)&&(NN_barrelEC==0))'),
    ('barrel', '((NN_layer>0)&&(NN_barrelEC==0))'),
    ('endcap', '(NN_barrelEC!=0)'),
]

def gen_variables():
    it = itertools.product(templates, numbers, directions, layers)
    for (h,v), n, d, (ln,lc) in it:
        name = h.format(n=n,d=d) + '_' + ln
        var = v.format(i=(n-1), d=d)
        cond = '(Output_number_true=={})'.format(n)
        if lc is not None:
            cond += ('&&' + lc)
        yield name, var, cond

def get_range(name):
    if 'residuals' in name:
        if 'X' in name:
            return -0.05, 0.05
        else:
            return -0.5, 0.5
    else:
        return -5, 5

def make_hist(tree, name, var, cond):
    print name, var, cond
    binmin, binmax = get_range(name)
    varg = '{}>>{}(1000,{},{})'.format(var,name,binmin,binmax)
    tree.Draw(varg, cond)
    hist = ROOT.gROOT.Get(name)
    return hist


def make_all_hists(tree):
    for vars in gen_variables:
        make_hist(tree, *vars)

def make_histograms(input_path, output_path):
    infile = ROOT.TFile(input_path)
    tree = infile.Get('NNinput')
    outfile = ROOT.TFile(output_path, 'RECREATE')
    for vars in gen_variables():
        make_hist(tree, *vars)
    outfile.Write()
