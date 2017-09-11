""" Program to produce the pixel clustering NN performance plots """
import argparse
import array
import collections
import importlib
import itertools
import logging
import os
import shutil
import sys

import ROOT

figures = importlib.import_module('.figures', 'pixel-NN')



LOG = logging.getLogger(os.path.basename(__file__))
NPARTICLES = [1, 2, 3]
LAYERS = ['ibl', 'barrel', 'endcap']
COLORS = [ROOT.kRed, ROOT.kBlack, ROOT.kBlue]
MARKERS = [21, 8, 23]
DIRECTIONS = ['X', 'Y']
#VARIABLES = ['pull', 'corr_pull', 'residuals', 'corr_residuals']
VARIABLES = ['corr_pull', 'corr_residuals']
CONDITIONALS = [
    'eta',
    'phi',
    'cluster_size',
    'cluster_size_X',
    'cluster_size_Y'
]

PALETTE_SET = False


def _set_palette():
    """ Set the custom color palette

    It is the default InvertedDarkBodyRadiator palette with white as
    the first color.
    See https://root.cern.ch/doc/master/TColor_8cxx_source.html#l02473
    """
    global PALETTE_SET  # pylint: disable=global-statement
    if not PALETTE_SET:
        stops = array.array('d', [
            0.0000, 0.1250, 0.2500,
            0.3750, 0.5000, 0.6250,
            0.7500, 0.8750, 1.0000
        ])
        red = array.array('d', [
            1.0, 234./255., 237./255.,
            230./255., 212./255., 156./255.,
            99./255., 45./255., 0./255.
        ])
        green = array.array('d', [
            1.0, 238./255.,
            238./255., 168./255.,
            101./255., 45./255.,
            0./255., 0./255., 0./255.
        ])
        blue = array.array('d', [
            1.0, 95./255., 11./255.,
            8./255., 9./255., 3./255.,
            1./255., 1./255., 0./255.
        ])
        ROOT.TColor.CreateGradientColorTable(
            9,
            stops,
            red,
            green,
            blue,
            255,
            1.0
        )
        PALETTE_SET = True


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


def _fit(thist):
    mu = thist.GetMean();
    sig = thist.GetStdDev()
    thist.Fit('gaus', 'Q0', '', mu - 3 * sig, mu + 3 * sig)
    fit = thist.GetFunction('gaus')
    return fit.GetParameter('Mean'), fit.GetParameter('Sigma')


def _fwhm(thist):
    bin1 = thist.FindFirstBinAbove(thist.GetMaximum() * 0.5)
    bin2 = thist.FindLastBinAbove(thist.GetMaximum() * 0.5)
    return thist.GetBinCenter(bin2) - thist.GetBinCenter(bin1)


def _layer_name(layer):
    return layer.upper() if layer == 'ibl' else layer[0].upper() + layer[1:]


def _plot_1d(hsdict, variable, nparticle, direction, preliminary):
    # pylint: disable=too-many-locals

    name = '_'.join([variable, str(nparticle), direction])

    canvas = ROOT.TCanvas('canvas_' + name, '', 0, 0, 800, 600)
    legend = ROOT.TLegend(0.61, 0.6, 0.91, 0.85)
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
            '{#mu = %.2f %s, %s = %.2f %s}' % (
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
            v=variable.replace('corr_', '').rstrip('s'),
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

    print 'SETTING RANGE AT ' + str(rangex)
    stack.GetXaxis().SetRangeUser(-rangex, rangex)
    stack.SetMaximum(stack.GetMaximum('nostack') * scaley)

    figures.draw_atlas_label(preliminary)
    legend.Draw()

    txt = ROOT.TLatex()
    txt.SetNDC()
    txt.SetTextSize(txt.GetTextSize() * 0.75)
    txt.DrawLatex(0.2, 0.79, 'PYTHIA8 dijet, 1.8 < p_{T}^{jet} < 2.5 TeV')
    txt.DrawText(
        0.2,
        0.74,
        '{}-particle{} clusters'.format(nparticle, '' if nparticle==1 else 's')
    )
    txt.DrawText(0.2, 0.69, 'local {} direction'.format(direction.lower()))

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

    _set_palette()
    ROOT.gStyle.SetNumberContours(255)

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
    ROOT.TGaxis.SetMaxDigits(4)

    if 'residual' in variable:
        th2.GetXaxis().SetRangeUser(-0.05, 0.05)
        th2.GetYaxis().SetRangeUser(-0.5, 0.5)
    else:
        th2.GetXaxis().SetRangeUser(-5, 5)
        th2.GetYaxis().SetRangeUser(-5, 5)

    th2.GetXaxis().SetLabelSize(0.04)
    th2.GetYaxis().SetLabelSize(0.04)

    th2.SetTitle(
        ';Truth hit local x {v} {u};Truth hit local y {v} {u}'.format(
            v=variable.replace('corr_', '').rstrip('s'),
            u='[mm]' if 'residual' in variable else ''
        )
    )

    th2.Draw('COLZ')

    figures.draw_atlas_label(preliminary)

    txt = ROOT.TLatex()
    txt.SetNDC()
    txt.SetTextSize(txt.GetTextSize() * 0.75)
    txt.DrawLatex(0.2, 0.82, 'PYTHIA8 dijet, 1.8 < p_{T}^{jet} < 2.5 TeV')
    txt.DrawText(
        0.2,
        0.77,
        '{}-particle{} clusters'.format(nparticle, '' if nparticle==1 else 's')
    )

    txt.DrawText(
        0.2,
        0.72,
        layer.upper() if layer == 'ibl' else layer[0].upper() + layer[1:]
    )

    canvas.SaveAs(name + '.pdf')


def _plot_2d_hists(hsdict, preliminary):
    oldmargin = ROOT.gStyle.GetPadRightMargin()
    ROOT.gStyle.SetPadRightMargin(0.15)

    prod = itertools.product(VARIABLES, NPARTICLES, LAYERS)
    for var, npart, lyr in prod:
        _plot_2d(
            hsdict=hsdict,
            variable=var,
            nparticle=npart,
            layer=lyr,
            preliminary=preliminary
        )

    ROOT.gStyle.SetPadRightMargin(oldmargin)


def _varlabel(var):
    if var == 'eta':
        return 'Cluster global #eta', ''
    if var == 'phi':
        return 'Cluster global #phi', ''
    if var == 'cluster_size':
        return 'Cluster size', ''
    if var == 'cluster_size_X':
        return 'Cluster size in local X direction', ''
    if var == 'cluster_size_Y':
        return 'Cluster size in local Y direction', ''


def _plot_2d_cond(hsdict, variable, cond, nparticle, direction, prelim):
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements

    hist_incl = None
    for lyr in LAYERS:
        name = '_'.join([variable, str(nparticle), direction, '2D', cond, lyr])
        LOG.debug(name)
        if hist_incl is None:
            hist_incl = hsdict[name]
        else:
            hist_incl.Add(hsdict[name])

    name = '_'.join([variable, str(nparticle), direction, '2D', cond])

    hist = hist_incl.ProfileX(
        name + "_pfx",
        1,
        -1,
        "s"
    )

    canvas = ROOT.TCanvas("canvas_" + name, '', 0, 0, 800, 600)
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.85)
    legend.SetBorderSize(0)

    if 'cluster_size' not in cond:
        hist.Rebin(4)
    elif 'cluster_size_X' not in cond and 'cluster_size_Y' not in cond:
        hist.Rebin(5)

    hist_err = hist.Clone(hist.GetName() + "_err")
    hist_err.SetFillColor(ROOT.kYellow)
    hist_err.SetMarkerSize(0)

    if 'pull' in variable:
        rangey = 6.5
    elif direction == 'X':
        rangey = 0.066
    else:
        rangey = 0.66

    if 'cluster_size' in cond:
        if 'size_X' in cond or 'size_Y' in cond:
            rangex = (1, 8)
        else:
            rangex = (1, 25)
    elif 'eta' in cond:
        rangex = (-2.5, 2.5)
    else:
        rangex = (-3, 3)

    if 'cluster_size' == cond:
        bins = [1, 5, 10, 15, 25]
        hist_err.SetBins(len(bins)-1, array.array('d', bins))
        hist.SetBins(len(bins)-1, array.array('d', bins))

    hist_err.SetMaximum(rangey)
    hist_err.SetMinimum(-rangey)
    hist_err.GetXaxis().SetRangeUser(rangex[0], rangex[1])
    hist.SetMaximum(rangey)
    hist.SetMinimum(-rangey)
    hist.GetXaxis().SetRangeUser(rangex[0], rangex[1])


    for i in range(1, hist.GetNbinsX() + 2):
        if hist.GetBinError(i) == 0:
            hist.GetXaxis().SetRange(0, i-1)
            break

    hist_err.Draw("E2")
    hist.Draw("hist same")

    lbl, unit = _varlabel(cond)
    hist_err.SetTitle(
        ';{c} {bcu};{v} {l} {w} {cu}'.format(
            c=lbl,
            bcu=('[{}]'.format(unit) if unit != '' else ''),
            v='Truth hit {} {}'.format(
                variable.replace('corr_', '').rstrip('s'),
                '[mm]' if 'residuals' in variable else ''
            ),
            l='/',
            cu=unit,
            w=hist.GetBinWidth(1)
        )
    )

    legend.Draw()

    figures.draw_atlas_label(prelim)

    txt = ROOT.TLatex()
    txt.SetNDC()
    txt.SetTextSize(txt.GetTextSize() * 0.75)
    txt.DrawLatex(0.2, 0.82, 'PYTHIA8 dijet, 1.8 < p_{T}^{jet} < 2.5 TeV')
    txt.DrawText(
        0.2,
        0.77,
        '{}-particle{} clusters'.format(nparticle, '' if nparticle==1 else 's')
    )

    txt.DrawText(0.2, 0.72, 'Local {} direction'.format(direction.lower()))

    canvas.SaveAs(name + '.pdf')


def _plot_2d_cond_hists(hsdict, preliminary):

    ROOT.gStyle.SetErrorX(0.5)

    prod = itertools.product(
        VARIABLES,
        CONDITIONALS,
        NPARTICLES,
        DIRECTIONS,
    )

    for var, cond, npart, direc in prod:
        _plot_2d_cond(
            hsdict=hsdict,
            variable=var,
            cond=cond,
            nparticle=npart,
            direction=direc,
            prelim=preliminary
        )


########################################################################
# Main


def _main():
    args = _get_args()
    logging.basicConfig(level=args.loglevel)
    LOG.info('input: %s', args.input)
    LOG.info('output: %s', args.output)
    hists = _get_histograms(args.input)
    try:
        os.makedirs(args.output)
    except os.error:
        pass
    os.chdir(args.output)
    for histname, thist in hists.iteritems():
        LOG.debug('%s: %s', histname, str(thist))
    _plot_1d_hists(hists, preliminary=args.preliminary)
    _plot_2d_hists(hists, preliminary=args.preliminary)
    _plot_2d_cond_hists(hists, preliminary=args.preliminary)
    return 0


if __name__ == '__main__':
    sys.exit(_main())
