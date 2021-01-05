import uproot
import argparse


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


    args = parser.parse_args()

    filename = args.file
    depth = int(args.depth)

    file_ = uproot.open(filename)

    if depth>0 and hasattr(file_, "keys"):
        for in1 in file_.keys():
            type_ = getType(type(file_[in1]))
            print( "\033[1m\n" + type_ + "\t" + in1.decode("utf-8") + ":\033[0m")
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



