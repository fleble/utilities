import argparse
import re
from os import listdir
from os.path import isfile, join


def pre_process_file(file_):
    file_ = file_.readlines()
    return [line.replace("\n", "") for line in file_]


def get_packages_in_file(file_name):

    packages_list = []

    with open (file_name, "r") as file_:
        file_ = pre_process_file(file_)
        for line in file_:
            package = None
            if "import" in line:
                re_search = re.search(r'^\s*import ([a-zA-Z0-9]+)', line)
                if re_search:
                    package = re_search.group(1)
                else:
                    re_search = re.search(r'from ([a-zA-Z0-9]+)\.?(.*)? import .+', line)
                    if re_search:
                        package = re_search.group(1)
            if package is not None:
                packages_list.append(package)
                
        return packages_list


def get_packages_in_repo(path, packages_list=[]):

    for item in listdir(path):
        full_path = join(path, item)
        if isfile(full_path):
            packages_list += get_packages_in_file(full_path)
        else:
            packages_list += get_packages_in_repo(full_path)

    return sorted(set(packages_list))


def get_package_version(package_name):

    package = __import__(package_name)
    if hasattr(package, "__version__"):
        version = package.__version__
        return version
    else:
        return None


def print_packages_and_version(packages):

    for package in packages:
        version = get_package_version(package)
        if version is not None:
            print("%s==%s" %(package, version))

    return


if (__name__ == "__main__"):

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r", "--repository",
        help="Repo to analyse",
        required=True,
        )

    args = parser.parse_args()

    packages = get_packages_in_repo(args.repository)
    print_packages_and_version(packages)

