[![Testing](https://github.com/dodu94/JADE/actions/workflows/TestPy38.yml/badge.svg?branch=master)](https://github.com/dodu94/JADE/actions/workflows/TestPy38.yml)
[![Documentation Status](https://readthedocs.org/projects/jade-a-nuclear-data-libraries-vv-tool/badge/?version=latest)](https://jade-a-nuclear-data-libraries-vv-tool.readthedocs.io/en/latest/?badge=latest)

<img src="https://user-images.githubusercontent.com/25747626/118662537-5f124900-b7f0-11eb-8d69-282305f795c4.png" width="300" />

# JADE
A new tool for nuclear libraries V&V.
Brought to you by NIER, University of Bologna (UNIBO) and Fusion For Energy (F4E).

A more detailed documentation can be accessed from [\docs\build\html\index.html](./docs/build/html/index.html).

JADE is an open-source software licensed under the [GNU GPLv3](./LICENSE) license. When using JADE for scientific publications you are kindly encouraged to cite the following papers:
- Davide Laghi et al, 2020, "JADE, a new software tool for nuclear fusion data libraries verification & validation", Fusion Engineering and Design, doi: https://doi.org/10.1016/j.fusengdes.2020.112075.

For additional information contact: d.laghi@nier.it

## Requirements
- Windows operative system (Linux or MacOS compatibility has not been tested);
- Anaconda or Miniconda distribution (Python 3);
- Microsoft Office suite (Excel and Word);

## Installation
1) extract the zip into a folder of choice (from now on <JADE_root>);
2) rename the folder containing the Python scripts as 'Code' (<JADE_root>\Code);
3) open the global configuration file: <JADE_root>\Code\Configuration\Config.xlsx; here you need to properly set the environment variables specified in the 'MAIN Config.' sheet (i.e. xsdir Path, and multithread options);
4) Open an anaconda prompt shell and change directory to ``<JADE_root>\Code``. Then create a virtual
   environment specific for jade:

   ```
   conda env create --name jade --file=environment.yml
   ```
   
   This ensures that all dependencies are satisfied. The environment can be activated using:

   ```
   conda activate jade
   ```
   
   And deactivated simply using:

   ```
   conda deactivate
   ```

5) Finally, when the environment is activated, in order to start JADE type:

   ```
   python main.py
   ```

6) on the first usage the rest of the folders architecture is initialized.

## Usage!

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
- 'generate': select an MCNP input file (absolute full path is required); from this file, a number of materials can be selected and a new material will be created using user-specified fraction of them; the resulting material (in MCNP format) can be found in <JADE_root>\Utilities\Generated Materials;
- 'exit': leave the application freezing the log file that is saved in <JADE_root>\Utilities\Log Files
### Computational Benchmark Menu
- printlib: print to video all the libreries available in the xsdir file specified in the <JADE_root>\Code\Configuration\Config.xlsx file. Those are the libraries that can be assessed;
- assess: assess the selected library, the suite is run following the corresponding setup sheet in <JADE_root>\Code\Configuration\Config.xlsx; The MCNP input and output files can be found in <JADE_root>\Tests\MCNP simulations
- continue: continue an unfinished assessesment of the selected library;
- back: go back to the main menu;
- 'exit': leave the application freezing the log file that is saved in <JADE_root>\Utilities\Log Files
### Post Processing Menu
- printlib: print to video all the libreries that have been already assessed and can be post-processed.
- pp: post-process a single selected library, the results can be found in <JADE_root>\Tests\Post-Processing\Single Libraries;
- compare: compare two or more selected libraries, the first indicated will be considered as the reference one; the results can be found in <JADE_root>\Tests\Post-Processing\Comparisons
- back: go back to the main menu;
- 'exit': leave the application freezing the log file that is saved in <JADE_root>\Utilities\Log Files

## LICENSE
JADE is an open-source software licensed under the [GNU GPLv3](./LICENSE) license.
