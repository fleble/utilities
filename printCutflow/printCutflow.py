import uproot
import argparse


def calculate_cut_efficiencies(cutflow):
    """Print cut efficiencies for cuts needed for defining some of the variables.

    For instance, to compute deltaR between leading 2 jets, events needs
    to have at least 2 jets.

    Args:
        cutflow (dict[str, float]):
            Keys are cut names
            Values are numbers of processed events (sum of gen weights)
 
    Returns:
        dict[key, list]
            Keys are "Names", "SumGenWeights", "Absolute", "Relative"
            Values are list of cuts names, sum of gen weights, absolute and
            relative efficiencies for those cuts
    """

    cut_names = []
    sum_gen_weights = []
    absolute_efficiencies = []
    relative_efficiencies = []

    sum_gen_weight_no_cut = cutflow["Initial"]
    for cut_name, sum_gen_weight in cutflow.items():
        cut_names.append(cut_name)
        sum_gen_weights.append(sum_gen_weight)
        if cut_name == "Initial":
            absolute_efficiency = 1.
            relative_efficiency = 1.
        else:
            absolute_efficiency = sum_gen_weight/sum_gen_weight_no_cut
            previous_cut_absolute_efficiency = absolute_efficiencies[-1]
            if previous_cut_absolute_efficiency > 0:
                relative_efficiency = absolute_efficiency / previous_cut_absolute_efficiency
            else:
                relative_efficiency = 0

        absolute_efficiencies.append(absolute_efficiency)
        relative_efficiencies.append(relative_efficiency)


    efficiencies = {
        "Names": cut_names,
        "SumGenWeights": sum_gen_weights,
        "Absolute": absolute_efficiencies,
        "Relative": relative_efficiencies,
    }

    return efficiencies


def print_cutflow(cut_names, absolute_efficiencies, relative_efficiencies):
    """Print cutflow table.

    Args:
        cut_names (list[str])
        absolute_efficiencies (list[float])
        relative_efficiencies (list[float])
 
    Returns:
        None
    """

    len_column1 = max([ len(k) for k in cut_names])

    print("\nCutflow:")
    print("\tCut" + (len_column1-3)*" " + "  Abs. eff. [%]   Rel. eff. [%]")
    for cut_name, absolute_efficiency, relative_efficiency in zip(cut_names, absolute_efficiencies, relative_efficiencies):
        absolute_efficiency = 100*absolute_efficiency
        relative_efficiency = 100*relative_efficiency
        spaces = (len_column1 - len(cut_name) + (absolute_efficiency<10))*" "
        spaces2 = (11 - (absolute_efficiency==100))*" "
        print("\t%s%s  %.2f%s%.2f" %(cut_name, spaces, absolute_efficiency, spaces2, relative_efficiency))
    print("")
 
    return


def main(file_name, tree_name):
    """Drives cutflow printing.

    Args:
        file_name (str)
        tree_name (str)

    Returns:
        None
    """ 

    with uproot.open(args.file + ":" + args.tree) as tree:
         cutflow = { branch_name: tree[branch_name].array()[0] for branch_name in tree.keys() }
         efficiency_dict = calculate_cut_efficiencies(cutflow)
         print_cutflow(efficiency_dict["Names"], efficiency_dict["Absolute"], efficiency_dict["Relative"])
         
    return


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
        default="CutFlow",
        help="Cut flow tree name",
        )

    args = parser.parse_args()
    main(args.file, args.tree)
