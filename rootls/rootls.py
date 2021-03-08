import uproot
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
        help="File to ls"
        )
    parser.add_argument(
        "-d", "--depth",
        default=2,
        help="Depth to ls"
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

    file_ = uproot.open(filename)

    if args.noemptyline: newline = ""
    else: newline = "\n"

    if depth>0 and hasattr(file_, "keys"):
        for in1 in file_.keys():
            type_ = getType(type(file_[in1]))
            element = list2str(in1.decode("utf-8").split(";")[:-1])
            if args.nobold:
                print(newline + type_ + "\t" + element )
            else:
                print("\033[1m" + newline + type_ + "\t" + element + "\033[0m")
            if depth>1:
                f1 = file_[in1]
                if hasattr(f1, "keys"):
                    for in2 in f1.keys():
                        type_ = getType(type(f1[in2]))
                        #type_ = getType(type(file_[in1][in2]))
                        print(4*" " + type_ + "\t" + in2.decode("utf-8"))
                        if depth>2:
                            f2 = f1[in2]
                            if hasattr(f2, "keys"):
                                for in3 in f2.keys():
                                    print(8*" " + in3.decode("utf-8"))



