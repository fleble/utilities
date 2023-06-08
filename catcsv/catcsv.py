import argparse

try:
    import pandas as pd
    pandas_imported = True
except:
    pandas_imported = False


def print_row(row, max_len, n_cols):

    line = ""
    for ic in range(n_cols-1):
        N = max_len[ic] - len(row[ic])
        line = line + row[ic] + N*" " + " | "
    N = max_len[n_cols-1] - len(row[n_cols-1])
    line = line + row[n_cols-1]

    print(line)

    return


if __name__ == "__main__":
    """
    Print csv file content with alignement of the beginning of each column
    to make it easily legible in terminal.
    """

    ## Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--file",
        help="csv file to cat"
    )
    parser.add_argument(
        "-d", "--delimiter",
        help="csv file delimiter",
        default=","
    )
    parser.add_argument(
        "-n", "--nrows",
        help="Number of rows to display"
    )
    parser.add_argument(
        "-nc", "--no_columns",
        help="csv file does not have column names in 1st row",
        action="store_true"
    )
    parser.add_argument(
        "-sc", "--show_columns",
        help="Comma-separated list of columns to show",
    )
    parser.add_argument(
        "-dc", "--drop_columns",
        help="Comma-separated list of columns to drop",
    )
    parser.add_argument(
        "-cc", "--create_columns",
        help="Create columns on the fly. "
             "Syntax: column1_name:expression1,column2_name:expression2 "
             "Use df.column_name to build the expressions.",
    )
    parser.add_argument(
        "-s", "--sort",
        help="Comma separated list of column names to use for sorting the csv\n \
              e.g. --sort=col1,col3"
    )
    parser.add_argument(
        "-o", "--order",
        help="with --sort: + for ascending order, - for descending order",
        choices=["+", "-"],
        default="+"
    )
    parser.add_argument(
        "-i", "--print_index",
        help="print index column",
        action="store_true"
    )

    args = parser.parse_args()


    if pandas_imported:
        ## Read csv file
        df = pd.read_csv(args.file, delimiter=args.delimiter)

        if args.drop_columns:
            df.drop(args.drop_columns.split(","), axis=1, inplace=True)

        if args.show_columns:
            columns_to_drop = [x for x in df.columns if x not in args.show_columns.split(",")]
            df.drop(columns_to_drop, axis=1, inplace=True)

        if args.create_columns:
            for column_name_expression in args.create_columns.split(","):
                column_name, expression = column_name_expression.split(":")
                df[column_name] = eval(expression)

        ## Sort dataframe if asked
        if args.sort:
            ascending = True if args.order=="+" else False
            df.sort_values(args.sort.split(","), inplace=True, ascending=ascending)

        ## Make columns
        csv_data = [ list(df.columns) ]
        csv_data = csv_data + [ [str(row[col]) for col in df.columns] for idx, row in df.iterrows() ]

    else:
        if args.sort:
            print("Could not import pandas, will not sort csv data")
        if args.create_columns:
            print("Could not import pandas, will not create columns")
        if args.drop_columns:
            print("Could not import pandas, will not drop columns")

        ## Read csv file
        with open (args.file, "r") as csv_file:
            csv_data = csv_file.readlines()
        csv_data = [ x.replace("\n", "").split(args.delimiter) for x in csv_data ]

    ## Add index
    if args.print_index:
        header = [ ["Index"] + csv_data[0] ]
        csv_data = [ [str(irow)] + row for irow, row in enumerate(csv_data[1:]) ]
        csv_data =  header + csv_data

    ## Get number of columns
    n_cols = len(csv_data[0])

    ## Compute max length of each column
    max_len = n_cols * [0] 
    for row in csv_data:
        for ic in range(n_cols):
            if max_len[ic] < len(row[ic]):
                max_len[ic] = len(row[ic])

    ## Print csv file
    if not args.no_columns:
        print_row(csv_data[0], max_len, n_cols)
        print((sum(max_len)+2*len(max_len))*"-")
        idx0 = 1
    else: idx0 = 0

    if not args.nrows:
        csv_to_print = csv_data[idx0:]
    else:
        csv_to_print = csv_data[idx0:int(args.nrows)]

    for row in csv_to_print:
        print_row(row, max_len, n_cols)

