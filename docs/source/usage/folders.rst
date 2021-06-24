.. _folders:

#################
Folder Structure
#################

The following is a scheme of the JADE folder structure:

::

    <JADE_root>
        |--------- Benchmark inputs
        |
        |--------- Code
        |            |----- Default Settings
        |            |----- docs
        |            |----- Installation Files
        |            |----- Templates
        |
        |--------- Configuration
        |                |----------- Benchmarks Configuration
        |                |----------- Config.xlsx
        |
        |--------- Experimental results
        |                    |------------ <Benchmark name 1>
        |                    |------------ [...]
        |
        |--------- [Quality]
        |
        |--------- Tests
        |            |--------- MCNP simulations
        |            |                 |----------- <Lib suffix 1>
        |            |                 |                  |---------- <Benchmark name 1>
        |            |                 |                  |---------- [...]
        |            |                 |----------- [...]
        |            |
        |            |--------- Post-Processing
        |                             |------------ Comparisons
        |                             |                  |-------- <lib 1>_Vs_<lib 2>_Vs....
        |                             |                  |                  |------------------ <Benchmark name 1>
        |                             |                  |                  |                            |----------- Atlas
        |                             |                  |                  |                            |----------- Excel
        |                             |                  |                  |
        |                             |                  |                  |------------------ [...]
        |                             |                  |
        |                             |                  |------- [...]
        |                             |             
        |                             |------------ Single Libraries
        |                                                 |----------- <Lib suffix 1>
        |                                                 |                  |---------- <Benchmark name 1>
        |                                                 |                  |                   |----------- Atlas
        |                                                 |                  |                   |----------- Excel
        |                                                 |                  |                   |----------- Raw Data
        |                                                 |                  |            
        |                                                 |                  |---------- [...]
        |                                                 |
        |                                                 |----------- [...]
        |            
        |-------- Utilities

    
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

Code
====
``<JADE_root>\Code`` contains the JADE GitHub repo itself. All the source code is contained here toghether with the
following subfolders:

Default Settings
   Contains all JADE default settings. On the first JADE instance these are copied to the ``<JADE_root>\Configuration``
   folder. They can be restored by a dedicated utility function available from the main menu.

docs
   Contains all files related to this documentation. Here, local version of the documentations can be found.

Installation Files
    Contains files to be used during the first JADE run. They have not any appeal to the general user.

Templates
    Contains all the Microsoft Office and Word templates to be used during post-processing. In case of user-defined
    benchmarks that are based on specific templates, these need to be added here. 

Configuration
=============
``<JADE_root>\Configuration`` stores the main JADE configuration file ``Config.xlsx`` and all benchmark-specific configuration
files that are stored in ``<JADE_root>\Code\Benchmarks Configuration``.

.. seealso::
    :ref:`config` for additional description of the configuration files.

Experimental results
====================
``<JADE_root>\Experimental results`` stores all the experimental results needed for the post-processing of
experimental benchmarks. In case of benchmarks that are composed by more than one run, all the inputs are reunited in a sub-folder
(e.g. ``<JADE_root>\Experimental results\Oktavian``.

Quality
=======
**NOT IMPLEMENTED**

Tests
=====
``<JADE_root>\Tests`` reunites all the outputs of the benchmarks assessments. 

MCNP simulations
    contains the results of the transport simulations.

Post-Processing
    contains all the results coming from the post-processing of results. These are divided between
    *Comparisons* and *Single Libraries*.

Utilities
=========
``<JADE_root>\Tests`` is where all outputs coming from the :ref:`uty` are reunited. Each utility generates
a dedicated sub-folder when is used for the first time. Upon installation, the only sub-folder is
``<JADE_root>\Tests\Log Files`` that contains all log files produced by each JADE session.