import argparse
import sys
import re
from collections import Counter

import pandas as pd
import uproot
import numpy as np
import awkward as ak

from helpers.generalUtilities import make_slice


if __name__ == "__main__":
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
        required=False,
    )
    parser.add_argument(
        "-cb", "--create_branches",
        help="Create a branch on the fly. "
             "Syntax: column1_name:expression1;column2_name:expression2 "
             "Use data[\"branch_name\"].array()==1 to build the expressions.",
    )
    parser.add_argument(
        "-i", "--index",
        help="Index of the array to print out (can use slicing)",
    )
    parser.add_argument(
        "-j", "--jindex",
        help="axis-1 index of the array to print out (can use slicing)",
    )
    parser.add_argument(
        "-flat", "--flatten",
        help="Flatten arrays (over the different events)",
        action="store_true",
    )
    parser.add_argument(
        "-filter", "--filter",
        help="Filter the array using the specified array. Example synthax: data[\"branch_name\"].array()==1",
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
        help="If --pandas, comma-separated names of the columns to sort values by",
    )
    parser.add_argument(
        "-descending", "--descending",
        help="If --pandas and --sort_values, descending order",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-no_index", "--no_index",
        help="If --pandas, do not print indices",
        default=False,
        action="store_true",
    )


    ## Parse arguments
    args = parser.parse_args()

    ## Open ROOT file
    data = uproot.open(args.file)

    ## Read the branch data
    # Get branch names
    branch_names_to_dump = []
    additional_branch_name = []

    if args.branch:
        branch_names_to_dump += args.branch.split(",")

    if args.create_branches:
        pattern = "data\[[\"\']([0-9a-zA-Z_]+)[\"\']\]\.array\(\)"
        additional_branch_name += re.findall(pattern, args.create_branches)
        
    branch_names_to_read = branch_names_to_dump + additional_branch_name

    # Get branch data as an ak array
    branches = {}
    for branch_name in branch_names_to_read:
        if branch_name.endswith(".ref"):
            branch = data[branch_name.replace(".ref", "")].array().ref
        else:
            branch = data[branch_name].array()
        branches[branch_name] = branch

    if args.create_branches:
       for branch_name_expression in args.create_branches.split(";"):
           branch_name, expression = branch_name_expression.split(":")
           branches[branch_name] = eval(expression)
           branch_names_to_dump.append(branch_name)

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
        for branch_name in branches.keys():
            count = ak.count(branches[branch_name], axis=-1)
            branches[branch_name] = branches[branch_name][filter_]

    if args.index:
        event_indices = make_slice(args.index)
    if args.jindex:
        axis1_indices = make_slice(args.jindex)

    # Cast to pandas dataframe
    if args.pandas:
        data_frame = ak.to_pandas(ak.Array(branches), how="outer")
        if args.index:
            data_frame = data_frame.loc(axis=0)[event_indices]

        if args.sort_values:
            data_frame.sort_values(
                by=args.sort_values.split(","),
                inplace=True,
                ascending=not args.descending,
            )

        with pd.option_context(
            "display.max_rows", None,
            "display.max_columns", None,
            "display.precision", 5,
            "display.expand_frame_repr", False,
            ):
            cols = {x: x.split("/")[-1] for x in data_frame.columns}
            data_frame.rename(columns=cols, inplace=True)
            print(data_frame.to_string(index=not args.no_index))

        exit(0)


    branch_name = branch_names_to_dump[0]
    branch = branches[branch_name]

    # Get only selected leaves/events
    if args.index:
        branch = branch[event_indices]

    if args.jindex:
        if isinstance(axis1_indices, int):
            branch = branch[ak.num(branch, axis=1) > axis1_indices]
        branch = branch[:, axis1_indices]

    if args.flatten:
        branch = ak.flatten(branch, axis=None)

    # Apply a function over the array
    if args.apply:
        variable_name = args.apply.replace("ARRAY", args.branch)
        branch = eval(args.apply.replace("ARRAY", "branch"))

    # Cast into a list (useful for printing out the all leaves/events)
    if args.list:
        branch = ak.to_list(branch)

    # Count unique values
    if args.count:
        counter = Counter(branch)

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
            txt = "%s: %" + args.list_format + " %s"
            print(txt % (value, count, unit))
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

