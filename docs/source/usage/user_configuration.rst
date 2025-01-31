.. _config:

##############
Configure JADE
##############

All configuration files are included in the ``<JADE_root>/cfg`` directory.
This folder contains many files but most of them are of no interest of normal users (i.e. not developers).

Set environmental variables
===========================
The first thing that should be done after jade installation is to have a look at the
``<JADE_root>/cfg/env_vars_cfg.yml`` file.
This file contains the environmental variables that are used by JADE to run the different codes.
Here is an example:

.. code-block:: yaml

    # parameters related to parallel run
    mpi_tasks: 0  # this controls the number of MPI tasks to be used on a cluster
    openmp_threads: 8  # this controls the number of OpenMP threads to be used during execution

    # paths to the code executables. If the codes are not installed, just leave the field empty.
    executables:
        - mcnp: path/to/mcnp6/executable  # it can also be just 'mcnp6' if the executable is in the PATH
        - openmc:  path/to/openmc/executable  # it can also be just 'openmc' if the executable is in the PATH
        - serpent: path/to/serpent/executable  # it can also be just 'sss2' if the executable is in the PATH
        - d1s: path/to/d1s/executable  # it can also be just 'd1s' if the executable is in the PATH

    # run mode is either "serial" to run locally or "job" to submit to a cluster
    run_mode: serial
    
    # These need to be non-empty only if submitting a job to a cluster
    batch_template: batch_template/Slurmtemplate.sh  # batch template. Both relative and absolute paths should work.
    batch_system: sbatch  # the command to submit a job to the cluster (e.g. llsubmit, sbatch, etc.)
    mpi_prefix: srun  # the command to run jobs, it prepends your executable (e.g. mpirun, srun, etc.)
    code_configurations: # You can either modify the files at these (relative) paths that already exist or provide your own
        - mcnp: exe_config/mcnp_config.sh
        - openmc: exe_config/openmc_config.sh
        - serpent: exe_config/serpent_config.sh
        - d1s: exe_config/d1s_config.sh

It can be seen that in order to submit a job to a cluster, the user needs to provide the path to the batch template
file and a config file for the code(s) to be run.
The batch template file is the job submission script to be utilised on the users chosen system.
This should match the command provided for the batch system variable.
Several default job submission scripts are provided in the ``cfg/batch_template`` folder.
The config file for the code is a shell script containing environment variables required for running
a specific code on UNIX.
By default these files should exist already in the ``cfg/exe_config`` folder.

Configure the libraries
=======================
Another mandatory configuration is the one of nuclear data libraries. The user should provide the path to
libraries he intends to use in the ``<JADE_root>/cfg/libs_cfg.yml`` file. Two different kind of libraries
are supported for the moment, normal transport libraries and D1S libraries.
The following is an example of the settings of a transport library:

.. code-block:: yaml

    FENDL 3.2c:  # this is the name of the library. It will be used in all outputs
        mcnp:
            path: /path/to/xsdir  # path to the xsdir file
            suffix: 32c  # correspondent suffix in the xsdir file
        openmc:
            path: pathtolib  # path to the library file
        serpent:  # TODO
            path: pathtolib

There is no need to provide paths for the codes that the user does not intend to use.

Finally, an example of a D1S library settings:

.. code-block:: yaml

    D1SUNED (FENDL 3.1d+EAF2007):
        d1s:
            path: /path/to/xsdir  # path to the xsdir file for the D1SUNED lib
            suffix: 99c  # correspondent suffix in the xsdir file for the D1SUNED lib
            # To run simulations, also a normal transport library is needed as not all
            # isotopes will be set to be activated (i.e. will use the D1S library)
            transport_library_path: /path/to/xsdir  # path to the xsdir file for the transport lib
            transport_suffix: 32c  # correspondent suffix in the xsdir file for the transport lib


   
