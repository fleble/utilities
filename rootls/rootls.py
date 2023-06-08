import uproot3
import argparse

from helpers.generalUtilities import list_to_str


def get_type(full_type):
    return(str(full_type).split("'")[1].split(".")[-1])



if (__name__ == "__main__"):

    ## Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--file",
        help="File to ls",
        required=True,
        )
    parser.add_argument(
        "-d", "--depth",
        help="Depth to ls",
        default=2,
        )
    parser.add_argument(
        "-nb", "--no_bold",
        help="Do not use bold",
        action="store_true"
        )
    parser.add_argument(
        "-nel", "--no_empty_line",
        help="No empty lines",
        action="store_true"
        )


    args = parser.parse_args()

    filename = args.file
    depth = int(args.depth)

    file_ = uproot3.open(filename)

    if args.no_empty_line: newline = ""
    else: newline = "\n"

    if depth>0 and hasattr(file_, "keys"):
        for in1 in file_.keys():
            in1 = in1.decode("utf-8")
            f1 = file_[in1]
            type_ = get_type(type(f1))
            element = list_to_str(in1.split(";")[:-1])
            if type_ == "TTree":
                k0 = list(f1.keys())[0]
                nevts = len(f1[k0])
                if element == "Events":
                    name = "events" if nevts > 1 else "event"
                else:
                    name = "entries" if nevts > 1 else "entry"
                nevtsStr = " (%d %s)" %(nevts, name)
            else:
                nevtsStr = ""
            if args.no_bold:
                print(newline + type_ + "\t" + element + nevtsStr )
            else:
                print("\033[1m" + newline + type_ + "\t" + element + nevtsStr + "\033[0m")
            if depth>1:
                if hasattr(f1, "keys"):
                    for in2 in f1.keys():
                        in2 = in2.decode("utf-8")
                        type_ = get_type(type(f1[in2]))
                        print(4*" " + type_ + "\t" + in2)
                        if depth>2:
                            f2 = f1[in2]
                            if hasattr(f2, "keys"):
                                for in3 in f2.keys():
                                    in3 = in3.decode("utf-8")
                                    print(8*" " + in3)

