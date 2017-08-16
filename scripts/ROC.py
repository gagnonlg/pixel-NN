import root_numpy
import time
import numpy as np
import sklearn.metrics
import ROOT

ROOT.gROOT.SetBatch()
ROOT.gROOT.LoadMacro("atlasstyle/AtlasStyle.C")
ROOT.gROOT.LoadMacro("atlasstyle/AtlasUtils.C")
ROOT.SetAtlasStyle()


path = "/lcg/storage15/atlas/gagnon/work/2017-06-12_NN-note/AnalysisBase/source/38707.atlas11.lps.umontreal.ca_user.lgagnon.361027.Pythia8EvtGen_A14NNPDF23LO_jetjet_JZ7W.NNinput.e3668_s3126.abee11334d.1_EXT0/submitDir/data-NNinput/user.lgagnon.361027.Pythia8EvtGen_A14NNPDF23LO_jetjet_JZ7W.NNinput.e3668_s3126.abee11334d.1_EXT0.root"

t0 = time.time()
out = root_numpy.root2array(
    path,
    treename='NNinput',
    branches=[("Output_number", -1, 3), "Output_number_true"],
    #selection="NN_nparticles1 == 1",
    stop=1000000
)

def roc_graph(data, classes):
    pos, neg = classes
    isel = np.where(
        np.logical_or(
            data['Output_number_true'] == pos,
            data['Output_number_true'] == neg
        )
    )[0]
    fpr, tpr, thr = sklearn.metrics.roc_curve(
        out['Output_number_true'][isel],
        out['Output_number'][isel][:, pos - 1],
        pos_label=pos
    )

    canvas = ROOT.TCanvas('c_{}vs{}.format(pos, neg)', '' , 0, 0, 800, 600)
    canvas.SetLogx()
    graph = ROOT.TGraph(fpr.size)
    root_numpy.fill_graph(graph, np.column_stack((fpr, tpr)))
    graph.SetTitle(';Pr({pos} particle | {neg} particle);Pr({pos} particle | {pos} particle)'.format(
        pos=pos,
        neg=neg
    ))
    graph.SetLineWidth(2)
    graph.Draw('AL')

    line = ROOT.TF1("line", "x", 0, 1)
    line.SetLineStyle(2)
    line.Draw("same")

    canvas.SaveAs('ROC_{}vs{}.pdf'.format(pos, neg))

roc_graph(out, (3, 2))
roc_graph(out, (3, 1))
roc_graph(out, (2, 3))
roc_graph(out, (2, 1))

print time.time() - t0

