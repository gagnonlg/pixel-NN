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
COLORS = [ROOT.kRed, ROOT.kBlack, ROOT.kBlue]
MARKERS = [21, 8, 23]
DIRECTIONS = ['X', 'Y']
VARIABLES = ['pull', 'corr_pull', 'residuals']
CONDITIONALS = [
    'eta',
    'phi',
    'cluster_size',
    'cluster_size_X',
    'cluster_size_Y'
]


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
        hdict[name] = hist
    return hdict


def _init_root():
    ROOT.gROOT.SetBatch()
    ROOT.gROOT.LoadMacro("atlasstyle/AtlasStyle.C")
    ROOT.gROOT.LoadMacro("atlasstyle/AtlasUtils.C")
    ROOT.SetAtlasStyle()


def _fit(thist):
    sig = thist.GetStdDev()
    thist.Fit('gaus', 'Q0', '', -3 * sig, 3 * sig)
    fit = thist.GetFunction('gaus')
    return fit.GetParameter('Mean'), fit.GetParameter('Sigma')


def _fwhm(thist):
    bin1 = thist.FindFirstBinAbove(thist.GetMaximum() * 0.5)
    bin2 = thist.FindLastBinAbove(thist.GetMaximum() * 0.5)
    return thist.GetBinCenter(bin2) - thist.GetBinCenter(bin1)


def _draw_atlas_label(preliminary):
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


def _layer_name(layer):
    return layer.upper() if layer == 'ibl' else layer[0].upper() + layer[1:]


def _plot_1d(hsdict, variable, nparticle, direction, preliminary):
    # pylint: disable=too-many-locals

    name = '_'.join([variable, str(nparticle), direction])

    canvas = ROOT.TCanvas('canvas_' + name, '', 0, 0, 800, 600)
    legend = ROOT.TLegend(0.6, 0.6, 0.9, 0.85)
    legend.SetBorderSize(0)
    stack = ROOT.THStack('stk_' + name, '')

    for layer, color, marker in zip(LAYERS, COLORS, MARKERS):
        LOG.debug((name, layer))
        hist = hsdict[name + '_' + layer]
        hist.Scale(1.0 / hist.Integral())
        hist.SetLineColor(color)
        hist.SetMarkerColor(color)
        hist.SetMarkerStyle(marker)

        hist.Rebin(2)
        width = hist.GetBinWidth(1)
        stack.Add(hist)

        if 'pull' in variable:
            mean, sigma = _fit(hist)
        else:
            mean = hist.GetMean()
            sigma = _fwhm(hist)

        legend.AddEntry(
            hist,
            '#splitline{%s clusters}'
            '{#mu = %.3f %s, %s = %.3f %s}' % (
                _layer_name(layer),
                mean,
                'mm' if 'residuals' in variable else '',
                "fwhm" if 'residuals' in variable else "#sigma",
                sigma,
                'mm' if 'residuals' in variable else '',
            ),
            'LP'
        )

    stack.SetTitle(
        ';Truth hit {v} {bu};Particle density / {w} {u}'.format(
            v=variable.replace('corr_', ''),
            bu='[mm]' if 'residuals' in variable else '',
            w=width,
            u='mm' if 'residuals' in variable else '',
        )
    )

    stack.Draw('hist nostack')
    stack.Draw('p same nostack')

    scaley = 1.3
    if nparticle > 1:
        scaley = 1.7

    if 'pull' in variable:
        rangex = 5.0
    else:
        if direction == 'X':
            if nparticle == 1:
                rangex = 0.04
            else:
                rangex = 0.05
        else:
            rangex = 0.4

    stack.SetMaximum(stack.GetMaximum('nostack') * scaley)
    stack.GetXaxis().SetRangeUser(- rangex, rangex)

    _draw_atlas_label(preliminary)
    legend.Draw()

    txt = ROOT.TLatex()
    txt.SetNDC()
    txt.SetTextSize(txt.GetTextSize() * 0.65)
    txt.DrawLatex(0.2, 0.78, 'PYTHIA8 dijet, 1.8 < p_{T}^{jet} < 2.5 TeV')
    txt.DrawText(
        0.2,
        0.73,
        '{}-particle clusters'.format(nparticle)
    )
    txt.DrawText(0.2, 0.68, 'local {} direction'.format(direction))

    canvas.SaveAs(name + '.pdf')


def _plot_1d_hists(hsdict, preliminary=False):

    prod = itertools.product(VARIABLES, NPARTICLES, DIRECTIONS)
    for var, npart, direc in prod:
        _plot_1d(
            hsdict=hsdict,
            variable=var,
            nparticle=npart,
            direction=direc,
            preliminary=preliminary
        )


def _plot_2d(hsdict, variable, nparticle, layer, preliminary):

    name = '_'.join([variable, str(nparticle), '2D', layer])
    th2 = hsdict[name]

    ROOT.gStyle.SetPalette(ROOT.kInvertedDarkBodyRadiator)
    ROOT.gStyle.SetNumberContours(255)
    ROOT.gStyle.SetPadRightMargin(0.15)

    canvas = ROOT.TCanvas('canvas_' + name, '', 0, 0, 800, 600)

    th2.Rebin2D(2, 2)

    th2.GetZaxis().SetTitle(
        "Particles / {x} x {y} {u}".format(
            x=th2.GetXaxis().GetBinWidth(1),
            y=th2.GetYaxis().GetBinWidth(1),
            u='mm^{2}' if 'residual' in variable else ''
        )
    )
    th2.GetZaxis().SetLabelSize(0.04)

    if 'residual' in variable:
        th2.GetXaxis().SetRangeUser(-0.05, 0.05)
        th2.GetYaxis().SetRangeUser(-0.5, 0.5)
    else:
        th2.GetXaxis().SetRangeUser(-5, 5)
        th2.GetYaxis().SetRangeUser(-5, 5)

    th2.SetTitle(
        ';Truth hit X {v} {u};Truth hit Y {v} {u}'.format(
            v=variable.replace('corr_', ''),
            u='[mm]' if 'residual' in variable else ''
        )
    )

    th2.Draw('COLZ')

    _draw_atlas_label(preliminary)

    txt = ROOT.TLatex()
    txt.SetNDC()
    txt.SetTextSize(txt.GetTextSize() * 0.65)
    txt.DrawLatex(0.2, 0.82, 'PYTHIA8 dijet, 1.8 < p_{T}^{jet} < 2.5 TeV')
    txt.DrawText(
        0.2,
        0.77,
        '{}-particle clusters'.format(nparticle)
    )

    txt.DrawText(
        0.2,
        0.72,
        layer.upper() if layer == 'ibl' else layer[0].upper() + layer[1:]
    )

    canvas.SaveAs(name + '.pdf')


def _plot_2d_hists(hsdict, preliminary):

    prod = itertools.product(VARIABLES, NPARTICLES, LAYERS)
    for var, npart, lyr in prod:
        _plot_2d(
            hsdict=hsdict,
            variable=var,
            nparticle=npart,
            layer=lyr,
            preliminary=preliminary
        )


def _varlabel(var):
    if var == 'eta':
        return '#eta', ''
    if var == 'phi':
        return '#phi', ''
    if var == 'cluster_size':
        return 'Cluster size', ''
    if var == 'cluster_size_X':
        return 'Cluster size in X direction', ''
    if var == 'cluster_size_Y':
        return 'Cluster size in Y direction', ''


def _plot_2d_cond(hsdict, variable, cond, nparticle, direction, layer, prelim):
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    name = '_'.join([variable, str(nparticle), direction, '2D', cond, layer])
    LOG.debug(name)
    hist = hsdict[name].ProfileX(name + "_pfx", 1, -1, "s")

    canvas = ROOT.TCanvas("canvas_" + name, '', 0, 0, 800, 600)
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.85)
    legend.SetBorderSize(0)

    if 'cluster_size' not in cond:
        hist.Rebin(4)
    hist.SetFillColor(ROOT.kYellow)
    hist.SetMarkerSize(0)
    hist.Draw("E4")
    hist.Draw("hist same")

    if 'pull' in variable:
        rangey = 5.0
    elif direction == 'X':
        rangey = 0.05
    else:
        rangey = 0.5

    if cond == 'cluster_size':
        rangex = (0, 50)
    elif cond.startswith('cluster_size_'):
        rangex = (0, 10)
    else:
        rangex = (-3, 3)

    hist.SetMaximum(rangey)
    hist.SetMinimum(-rangey)
    hist.GetXaxis().SetRangeUser(*rangex)

    lbl, unit = _varlabel(cond)
    hist.SetTitle(
        ';{c} {bcu};{v} / {w} {cu}'.format(
            c=lbl,
            bcu=('[{}]'.format(unit) if unit != '' else ''),
            v='Truth hit {} {}'.format(
                variable.replace('corr_', ''),
                '[mm]' if 'residuals' in variable else ''
            ),
            cu=unit,
            w=hist.GetBinWidth(1)
        )
    )

    legend.AddEntry(hist, '#mu #pm 1 #sigma', 'LF')
    legend.Draw()

    _draw_atlas_label(prelim)

    txt = ROOT.TLatex()
    txt.SetNDC()
    txt.SetTextSize(txt.GetTextSize() * 0.65)
    txt.DrawLatex(0.2, 0.82, 'PYTHIA8 dijet, 1.8 < p_{T}^{jet} < 2.5 TeV')
    txt.DrawText(
        0.2,
        0.77,
        '{}-particle clusters'.format(nparticle)
    )

    txt.DrawText(0.2, 0.72, 'Local {} direction'.format(direction))

    txt.DrawText(
        0.2,
        0.67,
        layer.upper() if layer == 'ibl' else layer[0].upper() + layer[1:]
    )

    canvas.SaveAs(name + '.pdf')


def _plot_2d_cond_hists(hsdict, preliminary):

    prod = itertools.product(
        VARIABLES,
        CONDITIONALS,
        NPARTICLES,
        DIRECTIONS,
        LAYERS
    )

    for var, cond, npart, direc, lyr in prod:
        _plot_2d_cond(
            hsdict=hsdict,
            variable=var,
            cond=cond,
            nparticle=npart,
            direction=direc,
            layer=lyr,
            prelim=preliminary
        )


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
    # _plot_1d_hists(hists, preliminary=args.preliminary)
    # _plot_2d_hists(hists, preliminary=args.preliminary)
    _plot_2d_cond_hists(hists, preliminary=args.preliminary)
    return 0


if __name__ == '__main__':
    sys.exit(_main())