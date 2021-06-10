Installation
============
The procedure to install JADE is the following:

#. install/update Anaconda, you can update all packages in your current environment using:
``
conda update --all
``
However, if bugs or problems are encuntered, a fresh Anaconda re-installation may solve the issues
#. install additional packages. It may be necessary to activate the conda-forge channel. It can be done typing in an anaconda prompt shell:
``
conda config --add channels conda-forge
``
then use:
``
conda install python-docx
``
#. extract the zip into a folder of choice (from now on <JADE_root>);
#. rename the folder containing the Python scripts as 'Code' (<JADE_root>\Code);
#. open the global configuration file: <JADE_root>\Code\Configuration\Config.xlsx; here you need to properly set the environment variables specified in the 'MAIN Config.' sheet (i.e. xsdir Path, and multithread options);
#. open an anaconda prompt shell and change directory to <JADE_root>\Code. Then type:
``
python main.py
``
#. on the first usage the rest of the folders architecture is initialized.
