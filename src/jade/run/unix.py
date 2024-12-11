import os
import re
import subprocess
import sys

if "MODULESHOME" in os.environ:
    if "MODULEPATH" not in os.environ and "win" not in sys.platform:
        f = open(os.environ["MODULESHOME"] + "/init/.modulespath")
        path = []
        for inline in f.readlines():
            line = re.sub("#.*$", "", inline)
            if line != "":
                path.append(line)
        os.environ["MODULEPATH"] = ":".join(path)

    if "LOADEDMODULES" not in os.environ and "win" not in sys.platform:
        os.environ["LOADEDMODULES"] = ""


def module(*args: list) -> None:
    """Runs the module command using subprocess"""
    if type(args[0]) == type([]):
        args = args[0]
    else:
        args = list(args)
    (output, _) = subprocess.Popen(
        ["/usr/bin/modulecmd", "python"] + args, stdout=subprocess.PIPE
    ).communicate()
    exec(output)


def export(*args: list) -> None:
    """Export environment variables based on input values."""
    if type(args[0]) == type([]):
        args = args[0]
    else:
        args = list(args)
    args = "".join(args)
    environ, value = args.split("=")
    if environ not in os.environ:
        os.environ[environ] = ""
    value = value.replace("$" + environ, os.environ[environ])
    if "$" in value:
        parts = value.split("$")
        for string in parts[1:]:
            parent = string[: string.find("/")]
            value = value.replace("$" + parent, os.environ[parent])
    os.environ[environ] = value


def configure(config_file: str) -> None:
    """Perform configuration based on contents of configuration file.

    Parameters
    ----------
    config_file : str
        The configuration file path.
    """
    with open(config_file) as f:
        for line in f:
            if line.startswith("module"):
                args = line.split()
                module(args[1:])
            if line.startswith("export"):
                args = line.split()
                export(args[1:])
