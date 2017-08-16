""" Create the number NN performance graphs """
# pylint: disable=no-member
import argparse
import collections
import importlib
import time

import numpy as np
import ROOT
import root_numpy
import sklearn.metrics

figures = importlib.import_module('.figures', 'pixel-NN')  # pylint: disable=invalid-name


TEST_PATH = "/lcg/storage15/atlas/gagnon/work/2017-06-12_NN-note/AnalysisBase/source/38707.atlas11.lps.umontreal.ca_user.lgagnon.361027.Pythia8EvtGen_A14NNPDF23LO_jetjet_JZ7W.NNinput.e3668_s3126.abee11334d.1_EXT0/submitDir/data-NNinput/user.lgagnon.361027.Pythia8EvtGen_A14NNPDF23LO_jetjet_JZ7W.NNinput.e3668_s3126.abee11334d.1_EXT0.root"  # noqa pylint: disable=line-too-long

LCONDS = [
    ('IBL', '((NN_barrelEC == 0) && (NN_layer == 0))'),
    ('Barrel', '((NN_barrelEC == 0) && (NN_layer > 0))'),
    ('Endcap', '(NN_barrelEC != 0)')
]


def _get_args():
    args = argparse.ArgumentParser()
    args.add_argument('--input', default=TEST_PATH)
    return args.parse_args()


def _load_data(path):
    data = collections.OrderedDict()
    for name, cond in LCONDS:
        data[name] = root_numpy.root2array(
            path,
            treename='NNinput',
            branches=[
                ("Output_number", -1, 3),
                "Output_number_true",
                "Output_number_estimated"
            ],
            selection=cond,
            stop=10000000
        )
        data[name]['Output_number_true'][
            np.where(data[name]['Output_number_true'] > 3)
        ] = 3
    return data


def _roc_graph(data, classes, prelim=False):
    # pylint: disable=too-many-locals
    pos, neg = classes

    canvas = ROOT.TCanvas('c_{}vs{}.format(pos, neg)', '', 0, 0, 800, 600)
    canvas.SetLogx()

    graphs = ROOT.TMultiGraph()
    leg = ROOT.TLegend(0.63, 0.7, 0.9, 0.9)

    for layer in data:
        if pos == 3:
            pos_sel = data[layer]['Output_number_true'] >= pos
        else:
            pos_sel = data[layer]['Output_number_true'] == pos

        if neg == 3:
            neg_sel = data[layer]['Output_number_true'] >= neg
        else:
            neg_sel = data[layer]['Output_number_true'] == neg

        isel = np.where(
            np.logical_or(
                pos_sel,
                neg_sel,
            )
        )[0]

        fpr, tpr, _ = sklearn.metrics.roc_curve(
            data[layer]['Output_number_true'][isel],
            data[layer]['Output_number'][isel][:, pos - 1],
            pos_label=pos
        )
        auc = sklearn.metrics.auc(fpr, tpr)

        graph = ROOT.TGraph(fpr.size)

        if layer == 'IBL':
            graph.SetLineStyle(1)
            graph.SetLineColor(ROOT.kRed)
        elif layer == 'Barrel':
            graph.SetLineStyle(2)
            graph.SetLineColor(ROOT.kBlack)
        else:
            graph.SetLineStyle(9)
            graph.SetLineColor(ROOT.kBlue)

        root_numpy.fill_graph(graph, np.column_stack((fpr, tpr)))
        graph.SetLineWidth(2)
        graphs.Add(graph)
        leg.AddEntry(graph, '{}, AUC: {:.2f}'.format(layer, auc), 'L')

    graphs.SetTitle(
        ';Pr({pos} particle | {neg} particle);Pr({pos} particle | {pos} particle)'.format(  # noqa
            pos=pos,
            neg=neg
        )
    )
    graphs.SetMaximum(1.5)
    graphs.Draw('AL')

    line = ROOT.TF1("line", "x", 0, 1)
    line.SetLineStyle(3)
    line.SetLineColor(ROOT.kGray + 2)
    line.Draw("same")
    leg.AddEntry(line, 'Random, AUC: 0.50', 'L')

    leg.SetTextSize(leg.GetTextSize() * 0.65)
    leg.SetBorderSize(0)
    leg.Draw()

    figures.draw_atlas_label(prelim)
    txt = ROOT.TLatex()
    txt.SetNDC()
    txt.SetTextSize(txt.GetTextSize() * 0.65)
    txt.DrawLatex(0.2, 0.82, 'PYTHIA8 dijet, 1.8 < p_{T}^{jet} < 2.5 TeV')

    canvas.SaveAs('ROC_{}vs{}.pdf'.format(pos, neg))


def _main():

    t_0 = time.time()
    args = _get_args()
    print '==> Loading data from ' + args.input
    out = _load_data(args.input)
    print '==> Drawing the ROC curves'
    _roc_graph(out, (3, 2))
    _roc_graph(out, (3, 1))
    _roc_graph(out, (2, 3))
    _roc_graph(out, (2, 1))
    _roc_graph(out, (1, 2))
    _roc_graph(out, (1, 3))
    print '==> Completed in {:.2f}s'.format(time.time() - t_0)

if __name__ == '__main__':
    _main()
