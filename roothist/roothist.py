import argparse
import sys
import uproot
import numpy
import awkward as ak
import matplotlib.pyplot as plt
import ROOT

from helpers.generalUtilities import make_slice

ROOT.gROOT.SetBatch()

colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kBlack, ROOT.kGray+1]
line_styles = [1, 9, 7, 2, 3]


def __get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--output",
        default="tmp.pdf",
        help="Output file name (default=tmp.pdf)",
        )
    parser.add_argument(
        "-from_thist", "--from_thist",
        action="store_true",
        help="The branch name points to already existing THist histograms",
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
        "-norm1", "--normalize_to_1",
        help="Normalize to unit area",
        required=False,
        action="store_true",
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
    parser.add_argument(
        "-ymin", "--ymin",
        help="y min value",
        type=float,
        )
    parser.add_argument(
        "-ymax", "--ymax",
        help="y max value",
        type=float,
        )
    parser.add_argument(
        "-nsb", "--no_stat_box",
        help="Do not show stat box",
        required=False,
        action="store_true",
        )

    return parser.parse_args()


def __setup_style():
    ROOT.gStyle.SetOptStat(000000)
    ROOT.gStyle.SetOptFit(0000000)

    ROOT.gStyle.SetCanvasBorderMode(0)
    ROOT.gStyle.SetCanvasColor(ROOT.kWhite)
    ROOT.gStyle.SetCanvasDefH(600)
    ROOT.gStyle.SetCanvasDefW(700)
    ROOT.gStyle.SetCanvasDefX(0)
    ROOT.gStyle.SetCanvasDefY(0)

    ROOT.gStyle.SetPadTopMargin(0.08)
    ROOT.gStyle.SetPadBottomMargin(0.15)
    ROOT.gStyle.SetPadLeftMargin(0.13)
    ROOT.gStyle.SetPadRightMargin(0.06)

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


def __get_binning(args, branch):
    if args.nbins:
        n_bins = int(args.nbins)
    else:
        n_bins = 50

    if args.min:
        min_ = float(args.min)
    else:
        min_ = 0.9*min(branch)

    if args.max:
        max_ = float(args.max)
    else:
        max_ = 1.1*max(branch)

    return n_bins, min_, max_


def __get_histogram_from_array(args, file_name, branch_name, filter_expression, binning=None):

    ## Open ROOT file
    data = uproot.open(file_name)

    ## Read the branch data
    # Get branch data as an ak array
    branch = data[branch_name].array()

    if args.filter:
        if filter_expression is not None:
            filter_ = eval(filter_expression)
            branch = branch[filter_]

    # Get only selected leaves/events
    if args.index:
        branch = branch[make_slice(args.index)]

    if args.jindex:
        branch = branch[ak.num(branch, axis=1)>args.jindex]
        branch = branch[:, args.jindex]

    branch = ak.flatten(branch, axis=None)

    # Binning
    if binning is None:
        n_bins, min_, max_ = __get_binning(args, branch)
    else:
        n_bins, min_, max_ = binning

    # Draw histogram
    histogram = ROOT.TH1D("", "", n_bins, min_, max_)
    for x in branch: histogram.Fill(x)

    if args.normalize_to_1:
        histogram.Scale(1 / histogram.Integral())

    return histogram


def main():

    args = __get_arguments()
    __setup_style()

    file_names = args.file.split(",")
    branch_names = args.branch.split(",")
    if args.legend is not None:
        legends = args.legend.split(",")
    else:
        legends = None

    if len(file_names) != len(branch_names):
        print("ERROR: The number of branches and files must be equal!")
        sys.exit()

    if args.filter:
        filters = args.filter.split(",")
    else:
        filters = None

    number_of_histograms = len(file_names)
    histograms = [ None for x in range(number_of_histograms) ]

    if legends is not None and len(legends) != number_of_histograms:
        print("WARNING: Number of legend (%d) different from number of histograms (%d)." %(len(legend), number_of_histograms))
        print("         Will not draw legends")
        legends = []

    if number_of_histograms == 1 and not args.no_stat_box:
        ROOT.gStyle.SetOptStat(111111)


    ## Make plot
    canvas = ROOT.TCanvas("", "", 700, 600)
    legend = ROOT.TLegend(0.65, 0.8-(number_of_histograms-2)*0.08, 0.92, 0.9)
    draw_legend = False

    for ihist in range(number_of_histograms):
        if args.from_thist:
            pass

        else:
            file_name = file_names[ihist]
            branch_name = branch_names[ihist]
            filter_expression = filters[ihist] if filters is not None else None
            if filter_expression == "None": filter_expression = None
            color = colors[ihist]
            line_style = line_styles[ihist]
            legend_label = legends[ihist] if legends is not None else None

            histogram = __get_histogram_from_array(args, file_name, branch_name, filter_expression, binning=None)
            histograms.append(histogram)
            #histogram[ihist].Draw("E1P SAME")
            if legend_label not in (None, "None"):
            #if legends is not None and len(legends)>ihist and legends[ihist] != "None":
                draw_legend = True
                legend.AddEntry(histogram, legend_label, "l")

        histogram.SetLineColor(color)
        histogram.SetLineStyle(line_style)
        histogram.SetLineWidth(2)
        histogram.Draw("HIST SAME")

        # Axes title
        histogram.GetXaxis().SetTitle(args.labelx)
        histogram.GetYaxis().SetTitle(args.labely)


        if args.ymax is not None and args.ymin is not None:
            histogram.GetYaxis().SetRangeUser(args.ymin, args.ymax)

    if args.logscale:
        canvas.SetLogy()

    if draw_legend:
        legend.Draw("SAME")
    canvas.SaveAs(args.output)


if __name__ == "__main__":
    main()

