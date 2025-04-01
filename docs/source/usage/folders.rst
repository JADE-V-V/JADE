.. _folders:

#################
Folder Structure
#################

The following is a scheme of the JADE folder structure:

::

    <JADE_root>
        |----- benchmark_templates
        |        |----- <Benchmark_name>
        |        |        |
        |        |        |-----<Benchmark run 1>
        |        |        |        |----- mcnp
        |        |        |        |        |----- <inputfile>.i
        |        |        |        |----- openmc
        |        |        |        |        |----- <inputgeometry>.i
        |        |        |        |        |----- <inputmaterials>.i
        |        |        |        |        |----- <inputtallies>.i
        |        |        |        |----- serpent
        |        |        |        |        |----- <inputfile>.i
        |        |        |        |----- benchmark_metadata.json
        |        |        |        
        |        |        |-----<Benchmark run 2>
        |        |        |         |----- ...
        |        |        |
        |        |        |----- metadata.json
        |        |   
        |        |----- ...
        |        |----- TypicalMaterials
        |
        |
        |----- cfg
        |        |----- batch_templates
        |        |        |----- <Job submission system 1 template>
        |        |        |----- [...]  
        |        |        
        |        |----- benchmarks
        |        |        |----- <Benchmark_name>
        |        |        |        |----- <custom files for run>
        |        |
        |        |----- benchmarks_pp
        |        |        |----- excel
        |        |        |        |----- <Benchmark name>.yml
        |        |        |
        |        |        |----- raw
        |        |        |        |----- <Benchmark name>.yml
        |        |        |
        |        |        |----- atlas
        |        |                 |----- <Benchmark name>.yml     
        |        |
        |        |----- exe_cfg
        |        |        |----- mcnp_config.sh
        |        |        |----- openmc_config.sh
        |        |        |----- serpent_config.sh
        |        |
        |        |----- env_vars_cfg.yml
        |        |----- libs_cfg.yml
        |        |----- pp_cfg.yml
        |        |----- run_cfg.yml
        |
        |-----logs
        |
        |----- post_processing
        |            |
        |            |----- <Benchmark name>
        |                          |----- <date>
        |                                   |----- atlas
        |                                   |----- excel
        |        
        |----- raw_data
        |        |
        |        |----- _exp_-_exp_
        |        |
        |        |----- _<code>_-_<library>_
        |                       |----- <Benchmark name>
        |                                   |----- metadata.json
        |                                   |----- <tally 1>.csv
        |                                   |----- [...].csv
        |        
        |----- simulations
                   |----- _<code>_-_<library>_
                                   |----- <Benchmark name>
                                                  |----- <Benchmark run 1>
                                                                 |----- metadata.json
                                                                 |----- <sim output file>


    
``<JADE_root>`` is the root folder chosen by the user where JADE has been installed 
as described in :ref:`install` section.

Hereafter, a general overview of the different JADE tree branches is presented.

benchmark_templates
===================
``<JADE_root>\benchmark_templates`` contains all the input decks of the default benchmarks available
in the JADE suite. This is the folder where eventual user defined benchmark inputs should be positioned.
Some benchmarks encompass more than one run/input, other only one. Nevertheless, to have a general input
representation, benchmarks composed by a single input/run are treated as degenerate multiple runs.
In each run folder, the actual input files for the different codes are stored in their corresponding sub-folders. 
The benchmark input metadata is stored in a JSON file which is common for all codes. The following
is an example of a metadata file:

.. code-block:: json

    {
        "name": "Sphere",
        "version": {
            "mcnp": "1.0",
            "openmc": "1.0",
            "serpent": "1.0"
            }
    }


``<JADE_root>\benchmark_templates\TypicalMaterials`` contains the typical materials used in the Sphere-like
benchmarks. If weight windows are available, they should be placed in same folder as the input. 

cfg
===
``<JADE_root>\cfg`` stores all the necessary configuration files to run JADE. These control both the run of
simulations and the post-processing of the results. The configuration files are divided in the following
sub-folders:

``<JADE_root>\cfg\batch_templates`` contains the templates for the job submission system. The user can add
new templates for different job submission systems.

``<JADE_root>\cfg\benchmarks`` contains the custom files for the benchmarks. These are the files that are
used to run the benchmarks. Normal users should not need to modify these files.

``<JADE_root>\cfg\benchmarks_pp`` contains the configuration files for the post-processing of the results.
When adding new benchmarks, suitable configuration files should be added here. to control its post-processing
(only for developers).

``<JADE_root>\cfg\exe_cfg`` contains the configuration files for the execution of the codes. These files
are used to set the paths to the executables of the codes.

``<JADE_root>\cfg\env_vars_cfg.yml`` contains the environment variables used by JADE. Every user will need
to modify this file after JADE installation

``<JADE_root>\cfg\libs_cfg.yml`` contains the configuration for the libraries used by JADE. Here all librarries
that are to be made available to JADE need to be listed

``<JADE_root>\cfg\pp_cfg.yml`` controls which benchmarks, code and libraries are to be post-processed.
This file is usually modified through GUI and not directly editing the YAML file.

``<JADE_root>\cfg\run_cfg.yml`` controls the run of the simulations. This file is usually modified through GUI
and not directly editing the YAML file.

.. seealso::
    :ref:`config` for additional description of the configuration files.

logs
====
``<JADE_root>\logs`` contains the log files of the JADE runs.

post-processing
===============
``<JADE_root>\post_processing`` is the folder where the post-processing (excel and atlas files)
are stored.

raw_data
========
``<JADE_root>\raw_data`` contains the raw data of the simulations. The data is stored in CSV files
and represents the interface between the part of JADE that is code-dependent and the part that is
code-independent.

simulations
===========
``<JADE_root>\simulations`` contains the output files of the simulations.
