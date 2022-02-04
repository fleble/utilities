import uproot
import argparse


if (__name__ == "__main__"):

    ## Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--file",
        help="File to ls",
        required=True,
    )
    parser.add_argument(
        "-t", "--tree",
        help="Tree to show",
        required=True,
    )

    args = parser.parse_args()
    
    file = uproot.open(args.file + ":" + args.tree)
    file.show(name_width=45)
