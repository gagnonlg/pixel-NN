""" Program to produce the pixel clustering NN performance plots """
import argparse
import collections
import logging
import os
import sys

import ROOT


LOG = logging.getLogger(os.path.basename(__file__))
NPARTICLES = [1, 2, 3]
LAYERS = ['ibl', 'barrel', 'endcap']
DIRECTIONS = ['X', 'Y']


def _get_args():
    args = argparse.ArgumentParser()
    args.add_argument('input')
    args.add_argument('output')
    args.add_argument('--force', action='store_true')
    args.add_argument('--loglevel', choices=['DEBUG', 'INFO'], default='INFO')
    args.add_argument('--preliminary', action='store_true')
    return args.parse_args()


def _get_histograms(path):
    tfile = ROOT.TFile(path, 'READ')
    ROOT.SetOwnership(tfile, False)
    hdict = collections.OrderedDict()
    for name in [br.GetName() for br in tfile.GetListOfKeys()]:
        hist = tfile.Get(name)
        hist.Scale(1.0 / hist.Integral())
        hdict[name] = hist
    return hdict


def _init_root():
    ROOT.gROOT.SetBatch()
    ROOT.gROOT.LoadMacro("atlasstyle/AtlasStyle.C")
    ROOT.gROOT.LoadMacro("atlasstyle/AtlasUtils.C")
    ROOT.SetAtlasStyle()


def _plot_1d_residuals(hsdict, preliminary=False):

    npart = 1
    direc = 'X'
    name = 'residuals_{}_{}'.format(npart, direc)

    cnv = ROOT.TCanvas('canvas_' + name, '', 0, 0, 800, 600)
    stk = ROOT.THStack()
    leg = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    leg.SetBorderSize(0)
    width = 0
    for lyr in LAYERS:
        h_name = '{}_{}'.format(name, lyr)
        hist = hsdict[h_name]
        if lyr == 'ibl':
            hist.SetLineColor(ROOT.kRed)
            hist.SetMarkerColor(ROOT.kRed)
            hist.SetMarkerStyle(21)  # square
            leg.AddEntry(hist, 'IBL clusters', 'LP')
        elif lyr == 'barrel':
            hist.SetLineColor(ROOT.kBlack)
            hist.SetMarkerColor(ROOT.kBlack)
            hist.SetMarkerStyle(8)  # circle
            leg.AddEntry(hist, 'Barrel clusters', 'LP')
        else:  # endcap
            hist.SetLineColor(ROOT.kBlue)
            hist.SetMarkerColor(ROOT.kBlue)
            hist.SetMarkerStyle(23)  # inverted triangle
            leg.AddEntry(hist, 'Endcap clusters', 'LP')
        hist.Rebin(2)
        width = hist.GetBinWidth(1)
        stk.Add(hist)
    stk.SetTitle(
        ';Truth hit residual [mm];Cluster density / {} mm'.format(width)
    )
    stk.Draw('hist nostack')
    stk.Draw('p same nostack')
    leg.Draw()
    stk.SetMaximum(stk.GetMaximum('nostack') * 1.3)
    stk.GetXaxis().SetRangeUser(-0.04, 0.04)
    ROOT.ATLAS_LABEL(0.2, 0.88)
    txt = ROOT.TLatex()
    txt.SetNDC()
    txt.DrawText(
        0.33,
        0.88,
        'Simulation {}'.format('Preliminary' if preliminary else 'Internal')
    )
    txt.SetTextSize(txt.GetTextSize() * 0.65)
    txt.DrawLatex(0.2, 0.78, 'PYTHIA8 dijet, 1.8 < p_{T}^{jet} < 2.5 TeV')
    txt.DrawText(
        0.2,
        0.73,
        '{} particle{} clusters'.format(npart, 's' if npart > 1 else '')
    )
    txt.DrawText(0.2, 0.68, 'local {} direction'.format(direc))
    cnv.SaveAs(name + '.pdf')


########################################################################
# Main


def _main():
    args = _get_args()
    logging.basicConfig(level=args.loglevel)
    _init_root()
    LOG.info('input: %s', args.input)
    LOG.info('output: %s', args.output)
    hists = _get_histograms(args.input)
    for histname, thist in hists.iteritems():
        LOG.debug('%s: %s', histname, str(thist))
    _plot_1d_residuals(hists, preliminary=args.preliminary)

    return 0


if __name__ == '__main__':
    sys.exit(_main())
