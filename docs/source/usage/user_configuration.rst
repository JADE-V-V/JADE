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
    # if both mpi_tasks and openmp_threads are set to 0 or 1, the code will run in serial mode.
    mpi_tasks: 0  # this controls the number of MPI tasks to be used on a cluster
    openmp_threads: 8  # this controls the number of OpenMP threads to be used during execution

    # paths to the code executables. If the codes are not installed, just leave the field empty.
    executables:
        mcnp: path/to/mcnp6/executable  # it can also be just 'mcnp6' if the executable is in the PATH
        openmc:  path/to/openmc/executable  # idem
        serpent: path/to/serpent/executable  # idem
        d1s: path/to/d1s/executable  # idem

    # run mode is either "local", "job" or "global_job"
    # local: the code will be run locally on the machine where JADE is running
    # job: the code will be submitted as a job to a cluster. Each simulation will be sent as a separate job
    # global_job: the code will be submitted as a job to a cluster but all simulations will be sent as a single job
    run_mode: local
    # scheduler command (needed only if run_mode is "job" or "global_job")
    scheduler_command: sbatch  # e.g. 'sbatch' for slurm, 'qsub' for torque, 'bsub' for lsf

    # Not needed for a windows run.
    # These templates are used for job submission on a cluster.
    code_job_template: # You can either modify the files at these (relative) paths that already exist or provide your own
        mcnp: cfg/exe_config/mcnp_template.sh
        openmc: cfg/exe_config/openmc_template.sh
        serpent: cfg/exe_config/serpent_template.sh
        d1s: cfg/exe_config/d1s_template.sh
    # Optional prefix to be added before the executable command (it can also be null)
    exe_prefix: srun  # e.g. 'srun' or 'aprun' or 'ibrun' or 'mpirun' depending on the system

It can be seen that in order to submit a job to a cluster, the user needs to provide the path to the batch template
file for the code(s) to be run.
The batch template file is the job submission script to be utilised on the users chosen system.
Several default job submission scripts are provided in the ``cfg/exe_config`` folder.

.. important::
    In case of a ``global_job``, in addition to the modules, the bash template should also contain
    the export command to load the cross sections (different command depending on the code).
    This is automatically handled by JADE in case of ``job`` mode.

These file should contain all the necessary job submission options (e.g. slurm directives) and
all the necessary commands to load the modules required by the different transport codes.
Some placeholder are defined and will be substituted by JADE at runtime when submitting the job. They
are all optional:
- ``INITIAL_DIR``: the directory where the job is submitted from (i.e. the simulation folder)
- ``OUT_FILE``: the file where the standard output will be written
- ``ERROR_FILE``: the file where the standard error will be written
- ``MPI_TASKS``: the number of MPI tasks to be used
- ``OMP_THREADS``: the number of OpenMP threads to be used
- ``USER``: the user who submitted the job



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


   
