import itertools
import ROOT

ROOT.gROOT.SetBatch(True)

templates = [
   ('residuals_{n}_{d}', '(Output_positions_{d} - Output_true_{d})'),
   ('pull_{n}_{d}', '(Output_positions_{d} - Output_true_{d})/Output_uncert_{d}'),
   ('corr_pull_{n}_{d}', '(Output_corr_positions_{d} - Output_corr_true_{d})/Output_corr_uncert_{d}'),
   ('residuals_{n}_2D', '(Output_positions_Y - Output_true_Y):(Output_positions_X - Output_true_X)'),
   ('pull_{n}_2D', '((Output_positions_Y - Output_true_Y)/Output_uncert_Y):((Output_positions_X - Output_true_X)/Output_uncert_X)'),
   ('corr_pull_{n}_2D', '(Output_corr_positions_Y - Output_corr_true_Y)/Output_corr_uncert_Y:(Output_corr_positions_X - Output_corr_true_X)/Output_corr_uncert_X'),
   ('residuals_{n}_{d}_2D_eta', '(Output_positions_{d} - Output_true_{d}):globalEta'),
   ('residuals_{n}_{d}_2D_phi', '(Output_positions_{d} - Output_true_{d}):globalPhi'),
   ('residuals_{n}_{d}_2D_cluster_size', '(Output_positions_{d} - Output_true_{d}):cluster_size'),
   ('residuals_{n}_{d}_2D_cluster_size_X', '(Output_positions_{d} - Output_true_{d}):cluster_size_X'),
   ('residuals_{n}_{d}_2D_cluster_size_Y', '(Output_positions_{d} - Output_true_{d}):cluster_size_Y'),
   ('pull_{n}_{d}_2D_eta', '(Output_positions_{d} - Output_true_{d})/Output_uncert_{d}:globalEta'),
   ('pull_{n}_{d}_2D_phi', '(Output_positions_{d} - Output_true_{d})/Output_uncert_{d}:globalPhi'),
   ('pull_{n}_{d}_2D_cluster_size', '(Output_positions_{d} - Output_true_{d})/Output_uncert_{d}:cluster_size'),
   ('pull_{n}_{d}_2D_cluster_size_X', '(Output_positions_{d} - Output_true_{d})/Output_uncert_{d}:cluster_size_X'),
   ('pull_{n}_{d}_2D_cluster_size_Y', '(Output_positions_{d} - Output_true_{d})/Output_uncert_{d}:cluster_size_Y'),
   ('corr_pull_{n}_{d}_2D_eta', '(Output_corr_positions_{d} - Output_true_{d})/Output_corr_uncert_{d}:globalEta'),
   ('corr_pull_{n}_{d}_2D_phi', '(Output_corr_positions_{d} - Output_true_{d})/Output_corr_uncert_{d}:globalPhi'),
   ('corr_pull_{n}_{d}_2D_cluster_size', '(Output_corr_positions_{d} - Output_true_{d})/Output_corr_uncert_{d}:cluster_size'),
   ('corr_pull_{n}_{d}_2D_cluster_size_X', '(Output_corr_positions_{d} - Output_true_{d})/Output_corr_uncert_{d}:cluster_size_X'),
   ('corr_pull_{n}_{d}_2D_cluster_size_Y', '(Output_corr_positions_{d} - Output_true_{d})/Output_corr_uncert_{d}:cluster_size_Y'),
]

numbers = [1, 2, 3]
directions = ['X', 'Y']
layers = [
    ('ibl', '((NN_layer==0)&&(NN_barrelEC==0))'),
    ('barrel', '((NN_layer>0)&&(NN_barrelEC==0))'),
    ('endcap', '(NN_barrelEC!=0)'),
]

done = set()

def gen_variables():
    global done
    it = itertools.product(templates, numbers, directions, layers)
    for (h,v), n, d, (ln,lc) in it:
        name = h.format(n=n,d=d) + '_' + ln
        if name in done:
            continue
        else:
            done.add(name)
        var = v.format(i=(n-1), d=d)
        cond = '(Output_number_true=={})'.format(n)
        if lc is not None:
            cond += ('&&' + lc)
        yield name, var, cond

def get_range(var):

    def _range(var):
        if '_uncert_' in var:
            return 100, -5, 5
        if 'positions_X' in var:
            return 100, -0.05, 0.05
        if 'positions_Y' in var:
            return 100, -0.5, 0.5
        if var == 'globalEta':
            return 100, -5, 5
        if var == 'globalPhi':
            return 100, -4, 4
        if var == 'cluster_size':
            return 50, 0, 50
        if var in ['cluster_size_X', 'cluster_size_Y']:
            return 8, 0, 8

    fields = var.split(':')
    if len(fields) == 1:
        r = _range(fields[0])
        return '({},{},{})'.format(*r)
    else:
        r = _range(fields[1]) + _range(fields[0])
        return '({},{},{},{},{},{})'.format(*r)

def make_hist(tree, name, var, cond):
    print name

    if '_2D' in name:
        varg = '{}>>{}{}'.format(var,name,get_range(var))
    else:
        varg = '{}>>{}{}'.format(var,name,get_range(var))
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
