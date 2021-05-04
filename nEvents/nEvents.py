import uproot
import argparse


if (__name__ == "__main__"):
    """
    Return the number of events in a list of ROOT files.
    Examples:
    $ python nEvents file1.root,file2.root
    $ python nEvents list.txt
    where
    $ cat list.txt
    file1.root
    file2.root

    Depends on uproot.

    """


    ## Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--files",
        help="ROOT files separated by a comma \
              or txt file with list of ROOT files"
        )
    parser.add_argument(
        "-hr", "--humanReadable",
        action="store_true",
        help="Number of events in a human readable format"
        )

    args = parser.parse_args()

    # If list of ROOT files in txt file
    if not args.files.endswith(".root"):
        with open (args.files, "r") as txtfile:
            rootFiles = txtfile.readlines()
        rootFiles = [ x.replace("\n", "") for x in rootFiles ]
    # Else we assume coma separated list of ROOT files
    else:
        rootFiles = args.files.split(",")

    # Counting number of events
    nEvts = 0
    for fileName in rootFiles:
        file_ = uproot.open(fileName)
        nEvts += len(file_["Events"].arrays())

    if args.humanReadable:
        if nEvts < 1e3:
            nEvtsStr = str(nEvts)
        elif nEvts>= 1e3 and nEvts<1e6:
            nEvtsStr = str(int(nEvts//1e3)) + "k"
        elif nEvts>= 1e6 and nEvts<1e9:
            nEvtsStr = str(int(nEvts//1e6)) + "M"
        elif nEvts>= 1e9 and nEvts<1e12:
            nEvtsStr = str(int(nEvts//1e9)) + "G"
        else:
            nEvtsStr = str(int(nEvts//1e12)) + "T"
    else:
        nEvtsStr = str(nEvts)

    print(nEvtsStr)

