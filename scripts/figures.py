""" Program to produce the pixel clustering NN performance plots """
import argparse
import collections
import itertools
import logging
import os
import sys

import ROOT


LOG = logging.getLogger(os.path.basename(__file__))
NPARTICLES = [1, 2, 3]
LAYERS = ['ibl', 'barrel', 'endcap']
DIRECTIONS = ['X', 'Y']
VARIABLES = ['pull', 'corr_pull', 'residuals']


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


def _fit(thist):
    sig = thist.GetStdDev()
    thist.Fit('gaus', '0', '', -3 * sig, 3 * sig)
    fit = thist.GetFunction('gaus')
    return fit.GetParameter('Mean'), fit.GetParameter('Sigma')


def _fwhm(thist):
    bin1 = thist.FindFirstBinAbove(thist.GetMaximum() * 0.5)
    bin2 = thist.FindLastBinAbove(thist.GetMaximum() * 0.5)
    return thist.GetBinCenter(bin2) - thist.GetBinCenter(bin1)


class Plot(object):
    """ Encapsulate plotting code """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, var, name, nparticle, direction):
        self.var = var.replace('corr_', '')
        self.nparticle = nparticle
        self.direction = direction
        self.canvas = ROOT.TCanvas('canvas_' + name, '', 0, 0, 800, 600)
        self.stack = ROOT.THStack()
        self.legend = ROOT.TLegend(0.6, 0.6, 0.9, 0.9)
        self.legend.SetBorderSize(0)
        self.hists = []
        self.width = None
        self.unit = None
        self.name = name

        self.scaley = 1.3
        if nparticle > 1:
            self.scaley = 1.7

        if var == 'pull':
            self.rangex = 5.0
        else:
            if direction == 'X':
                if nparticle == 1:
                    self.rangex = 0.04
                else:
                    self.rangex = 0.05
            else:
                self.rangex = 0.4

    def add(self, hist, layer, color, marker):
        """ Add hist to plot """
        self.hists.append(hist)
        hist.SetLineColor(color)
        hist.SetMarkerColor(color)
        hist.SetMarkerStyle(marker)

        if self.var == 'pull':
            mean, sigma = _fit(hist)
        else:
            mean = hist.GetMean()
            sigma = _fwhm(hist)

        self.unit = '' if self.var == 'pull' else 'mm'
        self.legend.AddEntry(
            hist,
            '#splitline{%s clusters}'
            '{#mu = %.3f %s, %s = %.3f %s}' % (
                layer,
                mean,
                self.unit,
                "fwhm" if self.var == 'residuals' else "#sigma",
                sigma,
                self.unit
            ),
            'LP'
        )

        hist.Rebin(2)
        self.width = hist.GetBinWidth(1)
        self.stack.Add(hist)

    def draw(self, preliminary=False):
        """ Draw the plot """
        bunit = '[{}]'.format(self.unit) if self.var != 'pull' else ''
        self.stack.SetTitle(
            ';Truth hit {} {};Cluster density / {} {}'.format(
                self.var,
                bunit,
                self.width,
                self.unit
            )
        )
        self.stack.Draw('hist nostack')
        self.stack.Draw('p same nostack')
        self.stack.SetMaximum(self.stack.GetMaximum('nostack') * self.scaley)
        self.stack.GetXaxis().SetRangeUser(-self.rangex, self.rangex)

        self.legend.Draw()

        ROOT.ATLAS_LABEL(0.2, 0.88)
        txt = ROOT.TLatex()
        txt.SetNDC()
        txt.DrawText(
            0.33,
            0.88,
            'Simulation {}'.format(
                'Preliminary' if preliminary else 'Internal'
            )
        )
        txt.SetTextSize(txt.GetTextSize() * 0.65)
        txt.DrawLatex(0.2, 0.78, 'PYTHIA8 dijet, 1.8 < p_{T}^{jet} < 2.5 TeV')
        txt.DrawText(
            0.2,
            0.73,
            '{}-particle clusters'.format(self.nparticle)
        )
        txt.DrawText(0.2, 0.68, 'local {} direction'.format(self.direction))
        self.canvas.SaveAs(self.name + '.pdf')


def _plot_1d_hists(hsdict, preliminary=False):

    prod = itertools.product(VARIABLES, NPARTICLES, DIRECTIONS)
    for var, npart, direc in prod:

        name = '_'.join([var, str(npart), direc])
        LOG.info(name)

        plot = Plot(var, name, npart, direc)

        for lyr in LAYERS:
            h_name = '{}_{}'.format(name, lyr)
            hist = hsdict[h_name]
            if lyr == 'ibl':
                plot.add(
                    hist=hist,
                    layer='IBL',
                    color=ROOT.kRed,
                    marker=21  # square
                )
            elif lyr == 'barrel':
                plot.add(
                    hist=hist,
                    layer='Barrel',
                    color=ROOT.kBlack,
                    marker=8  # circle
                )
            else:  # endcap
                plot.add(
                    hist=hist,
                    layer='Endcap',
                    color=ROOT.kBlue,
                    marker=23  # inverted triangle
                )

        plot.draw(preliminary)

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
    _plot_1d_hists(hists, preliminary=args.preliminary)

    return 0


if __name__ == '__main__':
    sys.exit(_main())
