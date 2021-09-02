import uproot3
import argparse


def list2str(L, strForConcatenation=""):
    """
    Takes a list of elements convertible to str and optionally a string.
    Returns the concatenation of elements in the list separated by the optional string.

    """

    if len(L)==0:
        return("")
    else:
        s = L[0]
        for el in L[1:]: s = s + strForConcatenation + str(el)
        return(s)


def getType(fullType):
    return(str(fullType).split("'")[1].split(".")[-1])



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
        "-nb", "--nobold",
        help="Do not use bold",
        action="store_true"
        )
    parser.add_argument(
        "-nel", "--noemptyline",
        help="No empty lines",
        action="store_true"
        )


    args = parser.parse_args()

    filename = args.file
    depth = int(args.depth)

    file_ = uproot3.open(filename)

    if args.noemptyline: newline = ""
    else: newline = "\n"

    if depth>0 and hasattr(file_, "keys"):
        for in1 in file_.keys():
            in1 = in1.decode("utf-8")
            f1 = file_[in1]
            type_ = getType(type(f1))
            element = list2str(in1.split(";")[:-1])
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
            if args.nobold:
                print(newline + type_ + "\t" + element + nevtsStr )
            else:
                print("\033[1m" + newline + type_ + "\t" + element + nevtsStr + "\033[0m")
            if depth>1:
                if hasattr(f1, "keys"):
                    for in2 in f1.keys():
                        in2 = in2.decode("utf-8")
                        type_ = getType(type(f1[in2]))
                        print(4*" " + type_ + "\t" + in2)
                        if depth>2:
                            f2 = f1[in2]
                            if hasattr(f2, "keys"):
                                for in3 in f2.keys():
                                    in3 = in3.decode("utf-8")
                                    print(8*" " + in3)



