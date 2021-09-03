import argparse

try:
    import pandas as pd
    pandasImported = True
except:
    pandasImported = False


def printRow(row, maxLen, nCols):

    line = ""
    for ic in range(nCols-1):
        N = maxLen[ic] - len(row[ic])
        line = line + row[ic] + N*" " + " | "
    N = maxLen[nCols-1] - len(row[nCols-1])
    line = line + row[nCols-1]

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
        "-nc", "--noColumns",
        help="csv file does not have column names in 1st row",
        action="store_true"
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
        "-i", "--printIndex",
        help="print index column",
        action="store_true"
        )

    args = parser.parse_args()


    if pandasImported:
        ## Read csv file
        df = pd.read_csv(args.file, delimiter=args.delimiter)

        ## Sort dataframe if asked
        if args.sort:
            ascending = True if args.order=="+" else False
            df.sort_values(args.sort.split(","), inplace=True, ascending=ascending)

        ## Make columns
        csvData = [ list(df.columns) ]
        csvData = csvData + [ [str(row[col]) for col in df.columns] for idx, row in df.iterrows() ]

    else:
        if args.sort:
            print("Could not import pandas, will not csv data")

        ## Read csv file
        with open (args.file, "r") as csvFile:
            csvData = csvFile.readlines()
        csvData = [ x.replace("\n", "").split(args.delimiter) for x in csvData ]

    ## Add index
    if args.printIndex:
        header = [ ["Index"] + csvData[0] ]
        csvData = [ [str(irow)] + row for irow, row in enumerate(csvData[1:]) ]
        csvData =  header + csvData

    ## Get number of columns
    nCols = len(csvData[0])

    ## Compute max length of each column
    maxLen = nCols * [0] 
    for row in csvData:
        for ic in range(nCols):
            if maxLen[ic] < len(row[ic]):
                maxLen[ic] = len(row[ic])

    ## Print csv file
    if not args.noColumns:
        printRow(csvData[0], maxLen, nCols)
        print((sum(maxLen)+2*len(maxLen))*"-")
        idx0 = 1
    else: idx0 = 0

    if not args.nrows:
        csvToPrint = csvData[idx0:]
    else:
        csvToPrint = csvData[idx0:int(args.nrows)]

    for row in csvToPrint:
        printRow(row, maxLen, nCols)
