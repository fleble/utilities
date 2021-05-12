import argparse
import sys
import uproot
import numpy
import awkward as ak
import matplotlib.pyplot as plt


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
        "-f", "--file",
        help="File for which to make histogram",
        required=True,
        )
    parser.add_argument(
        "-b", "--branch",
        help="Branch to histogram",
        required=True,
        )
    parser.add_argument(
        "-i", "--index",
        help="Index of the array to print out (can use slicing)",
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


    ## Parse arguments
    args = parser.parse_args()

    ## Open ROOT file
    data = uproot.open(args.file)

    ## Read the branch data
    # Get branch data as an ak array
    branch = data[args.branch].arrays()

    # Check if there is only 1 branch
    fields = branch.fields
    if len(fields) > 1:
        print("ERROR: Path does not point to a branch. Exit.")
        sys.exit(1)
    elif len(fields) == 0:
        print("ERROR: ak array has no fields! Exit.")
        sys.exit(1)

    # Get the branch leaves (as an ak array)
    branchName = fields[0]
    branch = branch[branchName]

    # Get only selected leaves/events
    if args.index:
        branch = branch[make_slice(args.index)]

    branch = ak.flatten(branch, axis=None)


    ## Make plot
    import ROOT
    
    # Define plot style
    ROOT.gStyle.SetOptStat(0)

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
    ROOT.gStyle.SetTitleSize(0.07, "XYZ")
    ROOT.gStyle.SetTitleXOffset(1.00)
    ROOT.gStyle.SetTitleYOffset(0.90)

    ROOT.gStyle.SetLabelColor(1, "XYZ")
    ROOT.gStyle.SetLabelFont(42, "XYZ")
    ROOT.gStyle.SetLabelOffset(0.007, "XYZ")
    ROOT.gStyle.SetLabelSize(0.06, "XYZ")

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


    # Binning
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
    ROOT.gStyle.SetOptStat(111111)
    canvas = ROOT.TCanvas("", "", 700, 600)
    histogram = ROOT.TH1D("", "", nbins, min_, max_)
    for x in branch: histogram.Fill(x)

    histogram.SetLineColor(ROOT.kRed)
    histogram.Draw()

    canvas.SaveAs("./tmp.pdf")

