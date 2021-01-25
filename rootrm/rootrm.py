import ROOT
import argparse


if (__name__ == "__main__"):

    ## Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--files",
        help="File to in which to remove a histogram"
        )
    parser.add_argument(
        "-hist", "--histogramName",
        help="Name of the histogram to remove"
        )


    args = parser.parse_args()

    # Get name of the ROOT files
    if not args.files.endswith(".root"):
        with open (args.files, "r") as txtfile:
            rootFiles = txtfile.readlines()
        filenames = [ x.replace("\n", "") for x in rootFiles ]
    else:
        filenames = args.files.split(",")

    # Get histograms names
    histnames = args.histogramName.split(",")

    for filename in filenames:
        tfile = ROOT.TFile.Open(filename, "UPDATE")
        print("In %s:" %filename)
        for histname0 in histnames:
            if not histname0.endswith(";1"):
                histname = histname0 + ";1"
            tfile.Delete(histname)
            print("Histogram %s has been deleted from ROOT file" %histname0)
        tfile.Close()
