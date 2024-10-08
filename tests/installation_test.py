import shutil
import os
import runpy
from jade.main import main

cp = os.path.dirname(os.path.abspath(__file__))
# TODO change this using the files and resources support in Python>10
root = os.path.dirname(cp)


def test_install(tmpdir):
    original_dir = os.getcwd()  # Store the original working directory
    os.chdir(tmpdir)
    try:
        main()
    except SystemExit:
        assert len(os.listdir(os.path.join(tmpdir, "Benchmarks_Inputs"))) > 0
        assert len(os.listdir(os.path.join(tmpdir, "Experimental_Results"))) > 0
    finally:
        os.chdir(original_dir)  # Change back to the original directory
