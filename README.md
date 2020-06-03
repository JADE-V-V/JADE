# JADE
Version: 0.4.3
A new tool for nuclear libraries V&V.
Brought to you by NIER, University of Bologna (UNIBO) and Fusion For Energy (F4E).

For additional information contact: d.laghi@niering.it

## Requirements
- Windows operative system (Linux compatibility has not been tested);
- Up-to-date Anaconda distribution (Python 3);
- Microsoft Office suite (Excel and Word);
- Addtional Python packages to Anaconda distribution:
  - python-docx.

## Installation
The procedure to install JADE is the following:
1) install/update Anaconda;
2) install additional packages. It may be necessary to activate the conda-forge channel. It can be done typing in an anaconda prompt shell:
  ```
  conda config --add channels conda-forge
  ```
  then use:
  ```
  conda install python-docx
  ```
3) extract the zip into a folder of choice (from now on <JADE_root>);
4) rename the folder containing the Python scripts as 'Code' (<JADE_root>\Code);
5) copy and paste the 'Benchmarks Inputs' folder into <JADE_root>;
6) open the global configuration file: <JADE_root>\Code\Configuration\Config.xlsx; here you need to properly set the environment variables specified in the 'MAIN Config.' sheet (i.e. xsdir Path, and multithread options);
7) open an anaconda prompt shell and change directory to <JADE_root>\Code. Then type:
  ```
  python main.py
  ```
8) on the first usage the rest of the folders architecture is initialized.

###### N.B.
A limitator has been inserted in the code in order to test it before using JADE for production (this will be eliminated when a proper function testing the installation will be produced). To remove it, open <JADE_root>\Code\testrun.py and comment out line 239 and 279 while de-commenting line 238 and 278.

## Usage
JADE is a consolle based software where different menu can be accessed through direct typing into the shell.
### Main Menu
The main menu is divided into two sections, the first one let the user open the specific 2nd level menus of one of the main JADE functions, while the second one allows to directly execute some auxiliary functions.
#### Main Functions
- 'qual': open the quality checks menu (not implemented);
- 'comp': open the computational benchmarks menu;
- 'exp': open the experimental benchmark menu (not implemented);
- 'post': open the post-processing menu.
#### Utilities
- 'printlib': print to video all the libreries available in the xsdir file specified in the <JADE_root>\Code\Configuration\Config.xlsx file. Those are the libraries that can be assessed;
- 'trans': select an MCNP input file (absolute full path is required) and translate it to a selected library among the available ones; the results can be found in <JADE_root>\Utilities\Translations;
- 'printmat': select an MCNP input file (absolute full path is required) and print an excel that summarizes its material cards information; the results can be found in <JADE_root>\Utilities\Materials Infos;
- 'generate':
