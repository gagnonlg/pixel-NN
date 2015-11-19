import argparse
import sys
import AtlasStyle
import AtlasUtils
import ROOT

def parseArgs(argList):
    p = argparse.ArgumentParser()
    p.add_argument('new')
    p.add_argument('old')
    return p.parse_args(argList)

def ratio(key, newFile, oldFile,
          xlabel="",xmin=0,xmax=1000, maxf=1.5):
    histNew = newFile.Get(key)
    histOld = oldFile.Get(key)

    canvas = ROOT.TCanvas("c_%s" % key, "", 0, 0, 600, 600)
    padUp = ROOT.TPad("pu_%s" % key, "", 0, 0.3, 1, 1)
    padUp.SetBottomMargin(0)
    padUp.Draw()
    padUp.cd()

    histNew.SetTitle(";%s;Fraction of clusters" % xlabel)
    histNew.GetXaxis().SetRangeUser(xmin,xmax)
    histNew.SetMaximum(histNew.GetMaximum() * maxf)
    histNew.SetStats(0)
    histNew.SetLineColor(ROOT.kRed)
    histNew.DrawNormalized()
    histOld.DrawNormalized("same")

    leg = ROOT.TLegend(0.7,0.7,0.9,0.9)
    leg.SetBorderSize(0)
    leg.AddEntry(histNew, 'New format', 'L')
    leg.AddEntry(histOld, 'Old format', 'L')
    leg.Draw()


    canvas.cd()
    padDown = ROOT.TPad("pd_%s" % key, "", 0, 0.05, 1, 0.3)
    padDown.SetTopMargin(0)
    padDown.SetBottomMargin(0.25)
    padDown.SetGridy()
    padDown.Draw()
    padDown.cd()

    histRatio = histNew.Clone("histRatio_%s" % key)
    histRatio.SetTitle('')
    histRatio.GetYaxis().SetTitle('New format / Old format')
    histRatio.GetYaxis().SetTitleSize(0.09)
    histRatio.GetYaxis().SetTitleOffset(0.7);
    histRatio.GetXaxis().SetTitle(xlabel)
    histRatio.GetXaxis().SetTitleSize(0.14)
    histRatio.GetXaxis().SetTitleOffset(0.7)

    histRatio.SetLineColor(ROOT.kBlack)
    histRatio.SetMinimum(0.0)
    histRatio.SetMaximum(5.0)
    histRatio.Sumw2()
    histRatio.SetStats(0)
    histRatio.Divide(histOld)
    histRatio.SetMarkerStyle(20)
    histRatio.Draw("ep")


    canvas.SaveAs("hist_%s.pdf" % key)

def main(argList):
    args = parseArgs(argList)
    ROOT.SetAtlasStyle()
    newFile = ROOT.TFile(args.new)
    oldFile = ROOT.TFile(args.old)

    ratio("h_layer", newFile, oldFile,
          xlabel='Layer',
          xmin=0, xmax=4)

    ratio("h_barrelEC", newFile, oldFile,
          xlabel='Barrel (0)  or Endcap (+/-2)',
          xmin=-2, xmax=2)

    ratio("h_phi", newFile, oldFile,
          xlabel='Phi [rad]',
          xmin=-2, xmax=2,
          maxf=2)

    ratio("h_theta", newFile, oldFile,
          xlabel='Theta [rad]',
          xmin=-5, xmax=5)


    if newFile.Get('h_position_X_0'):

        ratio("h_position_X_0", newFile, oldFile,
              xlabel='X position 1 [index]',
              xmin=-2, xmax=2)

        ratio("h_position_Y_0", newFile, oldFile,
              xlabel='Y position 1 [index]',
              xmin=-2, xmax=2)

    if newFile.Get('h_position_X_1'):

        ratio("h_position_X_1", newFile, oldFile,
              xlabel='X position 2 [index]',
              xmin=-2, xmax=2)

        ratio("h_position_Y_1", newFile, oldFile,
              xlabel='Y position 2 [index]',
              xmin=-2, xmax=2)

    if newFile.Get('h_position_X_2'):

        ratio("h_position_X_2", newFile, oldFile,
              xlabel='X position 3 [index]',
              xmin=-2, xmax=2)

        ratio("h_position_Y_2", newFile, oldFile,
              xlabel='Y position 3 [index]',
              xmin=-2, xmax=2)



if __name__ == '__main__':
    main(sys.argv[1:])

