import argparse
import math
import sys
import os

utils_directory = os.path.dirname(__file__)
sys.path.append(utils_directory + "/../utils/")
import utils


if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--file",
        help="File to cat",
        required=True,
        )
    parser.add_argument(
        "-p", "--percentage",
        help="Fraction of the file to cat, e.g. 5 means 5 percents",
        required=True,
        type=int
        )

    args = parser.parse_args()


    # Number of line in the file to cat
    n_lines_in_file = int(utils.run_bash_command("cat %s | wc -l" %(args.file)))

    # Number of lines to print
    n_lines_to_print = int(round(n_lines_in_file * args.percentage/100))

    # Print first lines
    print(utils.run_bash_command("cat %s | head -n %d" %(args.file, n_lines_to_print)))
