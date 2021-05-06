import argparse
import sys
import uproot
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
        "-l", "--list",
        help="Cast ak array into a list to display the whole array",
        action="store_true",
        )
    parser.add_argument(
        "-n", "--number",
        help="Print as table: entry number | value",
        action="store_true",
        )
    parser.add_argument(
        "-a", "--apply",
        help="Apply a function on the array (e.g. sum)",
        )


    ## Parse arguments
    args = parser.parse_args()

    ## Open ROOT file
    data = uproot.open(args.file)

    ## Read the branch data
    # Get branch data as an ak array
    branch = data[args.branch].arrays()

    # Check if there is only 1 branch
    fields = branch.fields
    if len(fields) > 1:
        print("ERROR: Path does not point to a branch. Exit.")
        sys.exit(1)
    elif len(fields) == 0:
        print("ERROR: ak array has no fields! Exit.")
        sys.exit(1)

    # Get the branch leaves (as an ak array)
    branchName = fields[0]
    branch = branch[branchName]

    # Cast into a list (useful for printing out the all leaves/events)
    if args.list:
        branch = ak.to_list(branch)

    # Get only selected leaves/events
    if args.index:
        branch = branch[make_slice(args.index)]

    # Apply a function over the array
    if args.apply:
        branch = eval(args.apply+"(branch)")

    if not args.apply:
        print("Content of branch %s:" %(args.branch))
    else:
        print(args.apply+"(" + args.branch + "):")

    if not args.number:
        print(branch)
    else:
        print("Entry\tValue")
        for idx, x in enumerate(branch):
            print("%d\t%s" %(idx, x))

