import subprocess


def run_bash_command(bash_command):
    """Execute a bash command line.

    Args:
        bash_command (str)

    Returns:
        str
    """

    return subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8")[:-1]
