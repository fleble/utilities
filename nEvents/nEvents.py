import uproot
import argparse

from helpers import generalUtilities as gUtl


def __get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--files",
        help="ROOT files separated by a comma \
              or filename expansion, \
              or txt file with list of ROOT files.",
    )
    parser.add_argument(
        "-hr", "--human_readable",
        action="store_true",
        help="Number of events in a human readable format.",
    )
    parser.add_argument(
        "-t", "--ttree",
        help="Name of the events TTree (or the TTree for which to get size). Default=Events.",
        default="Events",
    )
    parser.add_argument(
        "-filter", "--filter",
        help="Filter the array using the specified array. Example synthax: data.[\"branch_name\"]==1. No space allowed!",
    )

    return parser.parse_args()


def main():
    """Return the number of events in a list of ROOT files.

    Examples:
    $ python nEvents -f file1.root,file2.root
    $ python nEvents -f file{1..2}.root
    $ python nEvents -f list.txt
    $ cat list.txt
    file1.root
    file2.root
    $ # the + can combine several syntaxes:
    $ python nEvents -f list.txt+file{5..10}.root 
    """

    args = __get_arguments()

    root_files = gUtl.make_file_list(args.files)

    # Counting number of events
    n_events = 0
    for file_name in root_files:
        file_ = uproot.open(file_name)
        events = file_[args.ttree]
        f0 = events.keys()[0]
        n_events += events[f0].num_entries

    # Human readable output
    if args.human_readable:
        if n_events < 1e3:
            n_events_str = str(n_events)
        elif n_events>= 1e3 and n_events<1e6:
            n_events_str = str(int(n_events//1e3)) + "k"
        elif n_events>= 1e6 and n_events<1e9:
            n_events_str = str(int(n_events//1e6)) + "M"
        elif n_events>= 1e9 and n_events<1e12:
            n_events_str = str(int(n_events//1e9)) + "G"
        else:
            n_events_str = str(int(n_events//1e12)) + "T"
    else:
        n_events_str = str(n_events)

    print(n_events_str)


if __name__ == "__main__":
    main()

