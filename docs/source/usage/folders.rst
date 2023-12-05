.. _folders:

#################
Folder Structure
#################

The following is a scheme of the JADE folder structure:

::

    <JADE_root>
        |----- Benchmark inputs
        |        |----- <Inputfolder>
        |        |        |----- mcnp
        |        |        |        |----- <inputfile>.i
        |        |        |----- openmc
        |        |        |        |----- <inputgeometry>.i
        |        |        |        |----- <inputmaterials>.i
        |        |        |        |----- <inputtallies>.i
        |        |        |----- serpent
        |        |        |        |----- <inputfile>.i
        |        |----- ...
        |        |----- TypicalMaterials
        |
        |----- Code
        |        |----- docs
        |        |----- jade
        |        |        |----- default_settings
        |        |        |----- install_files
        |        |        |----- resources
        |        |        |----- templates
        |        |        |----- <JADE_modules>.py
        |        |        |----- ...
        |        |----- tests
        |
        |----- Configuration
        |        |----- Benchmarks Configuration
        |        |        |----- <Benchmark 1 config>.xlsx
        |        |        |----- [...]    
        |        |        
        |        |----- Job_Script_Templates
        |        |        |----- <Job submission system 1 template>.cmd
        |        |        |----- [...]      
        |        |
        |        |----- Config.xlsx
        |        |----- mcnp_config.sh
        |        |----- openmc_config.sh
        |        |----- serpent_config.sh
        |
        |----- Experimental results
        |        |----- <Benchmark name 1>
        |        |----- [...]
        |
        |-----[Quality]
        |
        |----- Tests
        |        |----- Simulations
        |        |        |----- <Lib suffix 1>
        |        |        |        |----- <Benchmark name 1>
        |        |        |        |        |----- <Code 1>
        |        |        |        |        |        |----- <output>
        |        |        |        |        |----- [...]
        |        |        |        |----- [...]
        |        |        |----- [...]
        |        |
        |        |----- Post-Processing
        |                 |----- Comparisons
        |                 |        |----- <lib 1>_Vs_<lib 2>_Vs....
        |                 |        |        |----- <Benchmark name 1>
        |                 |        |        |        |----- Atlas
        |                 |        |        |        |----- Excel
        |                 |        |        |
        |                 |        |        |----- [...]
        |                 |        |
        |                 |        |----- [...]
        |                 |             
        |                 |----- Single Libraries
        |                          |----- <Lib suffix 1>
        |                          |        |----- <Benchmark name 1>
        |                          |        |        |----- <Code 1>                                            
        |                          |        |        |        |----- Atlas
        |                          |        |        |        |----- Excel
        |                          |        |        |        |----- Raw Data
        |                          |        |        |----- [...] 
        |                          |        |----- [...]
        |                          |----- [...]
        |    
        |----- Utilities

    
``<JADE_root>`` is the root folder chosen by the user. As described in :ref:`install` section,
the JADE GitHub repo should be renamed and placed inside the root directory as ``<JADE_root>\Code``.

All folders parallel to the ``<JADE_root>\Code`` will be created after the first JADE run.

Hereafter, a general overview of the different JADE tree branches is presented.

Benchmark inputs
================
``<JADE_root>\Benchmark inputs`` contains all the inputs of the default benchmarks avaialble in the JADE suite.
This is the folder where eventual user defined benchmark inputs should be positioned.
In case of benchmarks that are composed by more than one run, all the inputs are reunited in a sub-folder
(e.g. ``<JADE_root>\Benchmark inputs\Oktavian``.

``<JADE_root>\Benchmark inputs\VRT`` folder is especially important. Here, in specific subfolders, can be found
all additional files required by the benchmark inputs (e.g. weight window files, irradiation files, reactions file,
etc.)

Code
====
``<JADE_root>\Code`` contains the JADE GitHub repo itself. Various git files and license information is contained here together with the
following subfolders:



docs
   Contains all files related to this documentation. Here, local version of the documentations can be found.

jade
   Contains all source code, as well as the following folders:

    default_settings
        Contains all JADE default settings. On the first JADE instance these are copied to the ``<JADE_root>\Configuration``
        folder. They can be restored by a dedicated utility function available from the main menu.

    install_files
        Contains files to be used during the first JADE run. They do have not any appeal to the general user.

    resources
        Miscelaneous resources, currently information on natural isotope abundances and atomic masses.
        

tests
    Contains all the .py files to be run with pytest and folders containing files useful for the testing activity.

Configuration
=============
``<JADE_root>\Configuration`` stores the main JADE configuration file ``Config.xlsx`` and all benchmark-specific configuration
files that are stored in ``<JADE_root>\Code\Benchmarks Configuration``. For users running on UNIX systems, this folder also 
contains templates for several common job submission systems (Slurm, LoadLeveler), and config shell scripts for configuring 
modules and environment variables at runtime.

.. seealso::
    :ref:`config` for additional description of the configuration files.

Experimental results
====================
``<JADE_root>\Experimental results`` stores all the experimental results needed for the post-processing of
experimental benchmarks. In case of benchmarks that are composed by more than one run, all the inputs are reunited in a sub-folder
(e.g. ``<JADE_root>\Experimental results\Oktavian``.

Quality
=======
This space has been reserved but Quality branch is **not being implemented**
for the time being.

Tests
=====
``<JADE_root>\Tests`` reunites all the outputs of the benchmarks assessments. 

Simulations
    contains the results of the transport simulations.

Post-Processing
    contains all the results coming from the post-processing of results. These are divided between
    *Comparisons* and *Single Libraries*.

Utilities
=========
``<JADE_root>\Tests`` is where all outputs coming from the :ref:`uty` are reunited. Each utility generates
a dedicated sub-folder when is used for the first time. Upon installation, the only sub-folder is
``<JADE_root>\Tests\Log Files`` that contains all log files produced by each JADE session.