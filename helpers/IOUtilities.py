import os
from pathlib import Path

from helpers import generalUtilities as gUtl


def has_redirector(file_name):

    if file_name.startswith("root://"):
        return True
    else:
        return False


def get_redirector(file_name):

    if has_redirector(file_name):
        return gUtl.list_to_str(file_name.split("/")[:3], "/")
    else:
        return None


def get_logical_file_name(file_name):

    if has_redirector(file_name):
        return gUtl.list_to_str(file_name.split("/")[3:], "/")
    else:
        return file_name


def get_file_name_without_directory(file_name):

    return file_name.split("/")[-1]


def make_directory(directory_name, check_exists=False):

    redirector = get_redirector(directory_name)
    logical_file_name = get_logical_file_name(directory_name)

    if check_exists:
        if file_exists(file_exists(file_name)):
            return

    print("Making directory %s " % directory_name)
    if redirector is None:
        Path(directory_name).mkdir(parents=True, exist_ok=check_exists)
    else:
        os.system("xrdfs %s mkdir -p %s" % (redirector, logical_file_name))


def file_exists(file_name):
    """Return True if file exists, else False.

    Args:
        file_name (str)

    Return:
        bool
    """

    # If file_name expansion
    if "{" in file_name or "[" in file_name or "*" in file_name or "?" in file_name:
        return True

    t3_psi_redirectors_outside_t3 = ["root://t3se01.psi.ch:1094"]
    t3_psi_redirectors_inside_t3 = ["root://t3dcachedb03.psi.ch", "root://t3dcachedb03.psi.ch:1094"]
    t3_psi_redirectors = t3_psi_redirectors_outside_t3 + t3_psi_redirectors_inside_t3
    path_to_t3_storage_element = "/pnfs/psi.ch/cms/trivcat"

    # Check only when there is no file name expansion
    redirector = get_redirector(file_name)
    logical_file_name = get_logical_file_name(file_name)

    if redirector is None:
        exit_code = gUtl.get_exit_code("ls %s > /dev/null 2>&1" % (logical_file_name))
      
    else:
        # If global redirector do not check if the file exists
        if redirector == "root://cms-xrd-global.cern.ch/":
            return True

        if redirector is None:
            exit_code = gUtl.get_exit_code("ls %s > /dev/null 2>&1" % (logical_file_name))
          
        else:
            exit_code = gUtl.get_exit_code("xrdfs %s ls %s > /dev/null 2>&1" % (redirector, logical_file_name))
            if exit_code == 2:
                print("Refresh your voms proxy by running the following command:")
                print("voms-proxy-init --rfc --voms cms -valid 192:00")
                exit(1)
        
            # It looks like this is an old version of xrootd
            # File existence cannot be checked via xrdfs ls
            # But files in a directory can be listed
            elif exit_code == 54:
                directory = os.path.dirname(logical_file_name)
                file_name_no_dir = get_file_name_without_directory(logical_file_name)
                files_list = gUtl.run_bash_command("xrdfs %s ls %s" % (redirector, directory)).split("\n")
                return logical_file_name in files_list

            # When running CMSSW, xrdfs returns code 50 with the following error message:
            # [ERROR] Internal error
            # Try to locate the file on T3 PSI storage element instead in that case
            # if the redirector is the T3 PSI redirector
            elif exit_code == 50 and redirector in t3_psi_redirectors:
                prefix = "" if redirector in t3_psi_redirectors_inside_t3 else path_to_t3_storage_element
                exit_code = gUtl.get_exit_code("ls %s/%s > /dev/null 2>&1" % (prefix, logical_file_name))
            
    if exit_code == 0:
        return True
    else:
        return False
