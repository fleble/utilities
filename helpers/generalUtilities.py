import re
import subprocess

from helpers import IOUtilities as ioUtl


def run_bash_command(bash_command):
    """Returns the output of a bash command.

    Args:
        bash_command (str)

    Returns:
        str
    """

    return subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8")[:-1]


def get_exit_code(bash_command):
    """Returns the exit code of a bash command.

    Args:
        bash_command (str)

    Returns:
        int
    """

    bash_command = bash_command + "; echo $?"
    output = run_bash_command(bash_command)
    return int(output)


def make_slice(slice_text):
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

    split = slice_text.split(":")
    if len(split) == 1:
        return int(slice_text)
    else:
        return slice(*map(lambda x: int(x.strip()) if x.strip() else None, slice_text.split(':')))


def list_to_str(list_, str_for_concatenation=""):
    """Concatenate elements of a list into an str.

    Args:
        list_ (list): List of elements convertible to str
        str_for_concatenation (str, optional, default=""): Text to be placed
            in between concatenated elements

    Returns: 
        str

    """

    if len(list_)==0:
        text = ""
    else:
        text = list_[0]
        for el in list_[1:]: text = text + str_for_concatenation + str(el)

    return text


def get_file_names_from_file_name_expansion(file_name_expansion):
    """Return list of files matching the file name expansion.

    Args:
        file_name_expansion (str)

    Returns:
        list[str]
    """

    file_names = []

    re_search = re.search("(.*)\{([0-9]+)(\.\.|,)([0-9]+)\}(.*)", file_name_expansion)
    file_name_start = re_search.group(1)
    file_name_end = re_search.group(5)
    part_start = int(re_search.group(2))
    part_end = int(re_search.group(4))
    how = re_search.group(3)

    if how == "..":
        parts = range(part_start, part_end+1)
    elif how == ",":
        parts = (part_start, part_end)
    else:
        raise NotImplementedError

    for part in parts:
        file_name = file_name_start + str(part) + file_name_end
        exists = ioUtl.file_exists(file_name)
        if exists:
            file_names.append(file_name)

    return file_names


def make_file_list(files_argument):
    """Make list of ROOT files to merge.

    Args:
        files_argument (str):
            Comma separated ROOT file names e.g. file1.root,file2.root or
            text file name with a ROOT file name on each line or filename
            expension. Can combine several syntaxes separated by +.

    Returns:
        list[str]
    """

    root_files = []
    for files_arg in files_argument.split("+"):
        # If the file argument has file name expansion (not really a regex, ls does not support regex)
        if "*" in files_arg or "!" in files_arg or "?" in files_arg or "^" in files_arg \
        or "[" in files_arg or "{" in files_arg:

            redirector = ioUtl.get_redirector(files_arg)

            if redirector is None:
                root_files += gUtl.run_bash_command("ls %s 2>/dev/null" %files_arg).split("\n")
            else:
                if "{" in files_arg:
                    root_files += get_file_names_from_file_name_expansion(files_arg)
                else:
                    raise NotImplementedError

        # If list of ROOT files in txt file
        elif files_arg.endswith(".txt"):
            with open (files_arg, "r") as txt_file:
                root_files += [ x.replace("\n", "") for x in txt_file.readlines() ]
        # Else we assume coma separated list of ROOT files
        else:
            root_files += files_arg.split(",")

    # In case there were empty lines in txt file or extra comas, remove empty strings
    root_files = [ x for x in root_files if x != "" ]
    
    return root_files

