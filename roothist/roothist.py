import argparse
import sys
import uproot
import numpy
import awkward as ak
import matplotlib.pyplot as plt
import ROOT


def replace_spaces(text):
    return text.replace("[space]", " ")


# Colors
colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kBlack]
linestyles = [ 1, 9, 7, 1 ]
#linestyles = [ 1, 1, 1, 1 ]

ROOT.gROOT.SetBatch()

# Define plot style
ROOT.gStyle.SetOptStat(0000)
ROOT.gStyle.SetOptFit(0000)

ROOT.gStyle.SetCanvasBorderMode(0)
ROOT.gStyle.SetCanvasColor(ROOT.kWhite)
ROOT.gStyle.SetCanvasDefH(600)
ROOT.gStyle.SetCanvasDefW(700)
ROOT.gStyle.SetCanvasDefX(0)
ROOT.gStyle.SetCanvasDefY(0)

ROOT.gStyle.SetPadTopMargin(0.08)
ROOT.gStyle.SetPadBottomMargin(0.15)
ROOT.gStyle.SetPadLeftMargin(0.13)
ROOT.gStyle.SetPadRightMargin(0.02)

ROOT.gStyle.SetHistLineColor(1)
ROOT.gStyle.SetHistLineStyle(0)
ROOT.gStyle.SetHistLineWidth(1)
ROOT.gStyle.SetEndErrorSize(2)
ROOT.gStyle.SetMarkerStyle(20)
ROOT.gStyle.SetMarkerSize(0.9)

ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetTitleFont(42)
ROOT.gStyle.SetTitleColor(1)
ROOT.gStyle.SetTitleTextColor(1)
ROOT.gStyle.SetTitleFillColor(10)
ROOT.gStyle.SetTitleFontSize(0.05)

ROOT.gStyle.SetTitleColor(1, "XYZ")
ROOT.gStyle.SetTitleFont(42, "XYZ")
ROOT.gStyle.SetTitleSize(0.05, "XYZ")
ROOT.gStyle.SetTitleXOffset(1.00)
ROOT.gStyle.SetTitleYOffset(0.90)

ROOT.gStyle.SetLabelColor(1, "XYZ")
ROOT.gStyle.SetLabelFont(42, "XYZ")
ROOT.gStyle.SetLabelOffset(0.007, "XYZ")
ROOT.gStyle.SetLabelSize(0.04, "XYZ")

ROOT.gStyle.SetAxisColor(1, "XYZ")
ROOT.gStyle.SetStripDecimals(True)
ROOT.gStyle.SetTickLength(0.03, "XYZ")
ROOT.gStyle.SetNdivisions(510, "XYZ")
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)

ROOT.gStyle.SetPaperSize(20., 20.)
ROOT.gStyle.SetHatchesLineWidth(5)
ROOT.gStyle.SetHatchesSpacing(0.05)

ROOT.TGaxis.SetExponentOffset(-0.08, 0.01, "Y")


def make_slice(sliceText):
    """
    Return the slice object corresponding to the equivalent slice expression as a string.
    Examples:
    > L = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    > L(make_slice("3"))
    [4]
    > L(make_slice(":3"))
    [1, 2, 3]
    > L(make_slice("1:3"))
    [2, 3]
    > L(make_slice("::2"))
    [1, 3, 5, 7, 9]
    """

    split = sliceText.split(":")
    if len(split) == 1:
        return int(sliceText)
    else:
        return slice(*map(lambda x: int(x.strip()) if x.strip() else None, sliceText.split(':')))


if (__name__ == "__main__"):
    """
    """

    ## Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--output",
        default="tmp.pdf",
        help="Output file name (default=tmp.pdf)",
        )
    parser.add_argument(
        "-f", "--file",
        help="File for which to make histogram (for multiple histograms from different files, separate files by a comma ',')",
        required=True,
        )
    parser.add_argument(
        "-b", "--branch",
        help="Branch to histogram (for multiple histograms from different branches, separate branches by a comma ',')",
        required=True,
        )
    parser.add_argument(
        "-i", "--index",
        help="axis-0 index of the array to histogram (can use slicing)",
        )
    parser.add_argument(
        "-j", "--jindex",
        help="axis-1 index of the array to histogram",
        type=int
        )
    parser.add_argument(
        "-filter", "--filter",
        help="Filter the array using the specified array. Example synthax: data.[\"branch_name\"]==1. No space allowed!",
        )
    parser.add_argument(
        "-n", "--nbins",
        help="Number of bins",
        )
    parser.add_argument(
        "-min", "--min",
        help="Minimum",
        )
    parser.add_argument(
        "-max", "--max",
        help="Maximum",
        )
    parser.add_argument(
        "-l", "--legend",
        help="Legend (comma separated legend for several histograms, (space=[space])",
        )
    parser.add_argument(
        "-ls", "--logscale",
        help="Log scale for y-axis",
        action="store_true",
        )
    parser.add_argument(
        "-lx", "--labelx",
        help="x-axis label (space=[space])",
        default="",
        )
    parser.add_argument(
        "-ly", "--labely",
        help="y-axis label (space=[space])",
        default="",
        )


    ## Parse arguments
    args = parser.parse_args()

    file_names = args.file.split(",")
    branch_names = args.branch.split(",")
    if args.legend is not None:
        legends = replace_spaces(args.legend).split(",")
    else:
        legends = None

    if len(file_names) != len(branch_names):
        print("ERROR: The number of branches and files must be equal!")
        sys.exit()

    if args.filter:
        filters = args.filter.split(",")

    number_of_histograms = len(file_names)
    histogram = [ None for x in range(number_of_histograms) ]

    if legends is not None and len(legends) != number_of_histograms:
        print("WARNING: Number of legend (%d) different from number of histograms (%d)." %(len(legend), number_of_histograms))
        print("         Will not draw legends")
        legends = []

    if number_of_histograms == 1:
        ROOT.gStyle.SetOptStat(111111)


    ## Make plot
    canvas = ROOT.TCanvas("", "", 700, 600)
    legend = ROOT.TLegend(0.65, 0.8-(number_of_histograms-2)*0.1, 0.95, 0.9)

    for ihist in range(number_of_histograms):

        file_name = file_names[ihist]
        branch_name = branch_names[ihist]

        ## Open ROOT file
        data = uproot.open(file_name)

        ## Read the branch data
        # Get branch data as an ak array
        branch = data[branch_name].array()

        if args.filter:
            filter_expr = filters[ihist]
            if filter_expr:
                filter_ = eval(filter_expr)
                branch = branch[filter_]

        # Get only selected leaves/events
        if args.index:
            branch = branch[make_slice(args.index)]

        if args.jindex:
            branch = branch[ak.num(branch, axis=1)>args.jindex]
            branch = branch[:, args.jindex]

        branch = ak.flatten(branch, axis=None)


        # Binning
        if ihist == 0:
            if args.nbins:
                nbins = int(args.nbins)
            else:
                nbins = 50

            if args.min:
                min_ = float(args.min)
            else:
                min_ = 0.9*min(branch)

            if args.max:
                max_ = float(args.max)
            else:
                max_ = 1.1*max(branch)


        # Draw histogram
        histogram[ihist] = ROOT.TH1D("", "", nbins, min_, max_)
        for x in branch: histogram[ihist].Fill(x)

        histogram[ihist].SetLineColor(colors[ihist])
        histogram[ihist].SetLineStyle(linestyles[ihist])
        histogram[ihist].SetLineWidth(2)
        histogram[ihist].Draw("SAME")
        #histogram[ihist].Draw("E1P SAME")
        if legends is not None and len(legends)>ihist and legends[ihist] != "None":
            legend.AddEntry(histogram[ihist], legends[ihist], "l")

        # Axes title
        if ihist == 0:
            histogram[ihist].GetXaxis().SetTitle(replace_spaces(args.labelx))
            histogram[ihist].GetYaxis().SetTitle(replace_spaces(args.labely))

    if args.logscale:
        canvas.SetLogy()

    legend.Draw("SAME")
    canvas.SaveAs(args.output)
