import ROOT

ROOT.gROOT.SetBatch()
ROOT.gROOT.LoadMacro("atlasstyle/AtlasStyle.C")
ROOT.gROOT.LoadMacro("atlasstyle/AtlasUtils.C")
ROOT.SetAtlasStyle()

def draw_atlas_label(preliminary):
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
