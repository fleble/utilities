import argparse
import sys
import re
from collections import Counter

import pandas as pd
import uproot
import numpy as np
import awkward as ak


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
    Example:
    $ rdump -f QCD_Pt_3200toInf_TuneCP5_13TeV_pythia8.root -b Events/FatJet_tau1 -l -i :10
    will print the FatJet _au1 variable for the first 10 events of file QCD_Pt_3200toInf_TuneCP5_13TeV_pythia8.root
    """

    ## Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--file",
        help="File to ls",
        required=True,
        )
    parser.add_argument(
        "-b", "--branch",
        help="Branch to print out",
        required=True,
        )
    parser.add_argument(
        "-i", "--index",
        help="Index of the array to print out (can use slicing)",
        )
    parser.add_argument(
        "-flat", "--flatten",
        help="Flatten arrays (over the different events)",
        action="store_true",
        )
    parser.add_argument(
        "-filter", "--filter",
        help="Filter the array using the specified array. Example synthax: data.[\"branch_name\"]==1. No space allowed!",
        )
    parser.add_argument(
        "-pd", "--pandas",
        help="Cast into pandas dataframe",
        action="store_true",
        )
    parser.add_argument(
        "-l", "--list",
        help="Cast ak array into a list to display the whole array",
        action="store_true",
        )
    parser.add_argument(
        "-lf", "--list_format",
        help="Format of each element. e.g. .2f",
        )
    parser.add_argument(
        "-c", "--count",
        help="Count unique values in the array",
        action="store_true",
        )
    parser.add_argument(
        "-cf", "--countFormat",
        choices=["fraction", "number"],
        default="fraction",
        help="Format in which to express output from unique values counting. Choices=%(choices)s. Default=%(default)s",
        )
    parser.add_argument(
        "-n", "--number",
        help="Print as table: entry number | value",
        action="store_true",
        )
    parser.add_argument(
        "-a", "--apply",
        help="Apply a function on the array. Example synthax: ak.sum(ARRAY,axis=1). No space allowed!",
        )
    parser.add_argument(
        "-sv", "--sort_values",
        help="If --pandas, name of the column to sort values by",
        )


    ## Parse arguments
    args = parser.parse_args()

    ## Open ROOT file
    data = uproot.open(args.file)

    ## Read the branch data
    # Get branch data as an ak array
    branche_names = args.branch.split(",")
    branches = ak.Array({branch_name: data[branch_name].array() for branch_name in branche_names})

#    # Check if there is only 1 branch
#    fields = branch_names
#    if len(fields) > 1:
#        if args.pandas:
#            data_frame = ak.to_pandas(branches)
#            if args.sort_values:
#                data_frame.sort_values(by=args.sort_values, inplace=True)
#            with pd.option_context(
#                "display.max_rows", None,
#                "display.max_columns", None,
#                "display.precision", 5,
#                "display.expand_frame_repr", False
#                #"max_colwidth", 20
#                ):
#                print(data_frame)
#            exit(0)
#
#        else:
#            print("ERROR: Several branches is only compatible with --pandas")
#            sys.exit(1)
#    elif len(fields) == 0:
#        print("ERROR: ak array has no fields! Exit.")
#        sys.exit(1)
#    else:
#        # Get the branch leaves (as an ak array)
#        branch_name = fields[0]
#        branch = branches[branch_name]

    # Filter the array
    if args.filter:
        filter_text_for_printout = args.filter\
            .replace("data[\"", "")\
            .replace("[\"", "")\
            .replace("\"]", "")\
            .replace(".array()", "")
        filter_text_for_printout = args.filter
        filter_ = eval(args.filter)
        filter_count = ak.count(filter_, axis=-1)
        for branch_name in branches.fields:
            count = ak.count(branches[branch_name], axis=-1)
            if ak.all(count == filter_count):
                branches[branch_name] = branches[branch_name][filter_]

    # Cast to pandas dataframe
    if args.pandas:
        data_frame = ak.to_pandas(branches)
        if args.sort_values:
            data_frame.sort_values(by=args.sort_values, inplace=True)
        with pd.option_context(
            "display.max_rows", None,
            "display.max_columns", None,
            "display.precision", 5,
            "display.expand_frame_repr", False
            #"max_colwidth", 20
            ):
            print(data_frame)
        exit(0)


    branch_name = branch_names[0]
    branch = branches[branch_name]

    # Cast into a list (useful for printing out the all leaves/events)
    if args.list:
        branch = ak.to_list(branch)

    # Get only selected leaves/events
    if args.index:
        branch = branch[make_slice(args.index)]

    if args.flatten:
        branch = ak.flatten(branch, axis=None)

    # Count unique values
    if args.count:
        counter = Counter(branch)

    # Apply a function over the array
    if args.apply:
        variable_name = args.apply.replace("ARRAY", args.branch)
        branch = eval(args.apply.replace("ARRAY", "branch"))

    # Header line
    if not args.apply:
        print("Content of branch %s:" %(args.branch))
    elif args.count:
        print("Unique values and counts in branch %s:" %(args.branch))
    else:
        print(variable_name)

    if args.filter:
        print("with selection: %s" %filter_text_for_printout)

    # Print asked information
    if args.count:
        total_count = 0
        if args.countFormat == "fraction":
            unit = "%"
            unit_factor = 100/sum(counter.values())
        elif args.countFormat == "number":
            unit = ""
            unit_factor = 1
        for value in sorted(counter.keys()):
            count = counter[value]
            count = count*unit_factor
            print("%s: %d %s" %(value, count, unit))
            total_count += count
        print("%s: %d %s" %("Total", total_count, unit))
    
    else:
        if not args.number:
            print(branch)
        else:
            print("Entry\tValue")
            for idx, x in enumerate(branch):
                if args.list_format:
                    if len(x) == 0:
                        x_str = "[]"
                    else:
                        x_str = "["
                        for y in x:
                            s = "%" + args.list_format
                            x_str += s %(y) + ", "
                        x_str = x_str[:-2] + "]"
                else:
                   x_str = x
                print("%d\t%s" %(idx, x_str))

