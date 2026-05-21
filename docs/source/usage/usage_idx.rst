##########
User Guide
##########

Once JADE is installed and properly configured, using JADE consists
in three main phases: generation/run of benchmarks, creation of the
raw post-processed files and generation of summary excel files and
atlases of plots. This section will guide the user through all these
phases.

This documentation describes what we usually refer as the "JADE engine". However,
this is only a part of the JADE V&V ecosystem.

The three repositories fully owned by the JADE team are:

- `JADE <https://github.com/JADE-V-V/JADE>`_: the main repository containing the engine.
- `JADE-RAW-RESULTS <https://github.com/JADE-V-V/JADE-RAW-RESULTS>`_: where the raw results processed by 
  JADE can be uploaded by the different users in order to have a centralized database and avoid duplication
  of efforts.
- `JADE-WEB-APP <https://github.com/JADE-V-V/JADE-WEB-APP>`_: which stores a web application that allows
  to interactively plot the benchmark results using the data contained in the JADE-RAW-RESULTS repository.
  This allows to easily compare the results of different benchmarks and different codes without the need
  to install JADE. The level of post-processing detail is lower than the one provided by JADE engine 
  processor, but it has the advantage of being interactive and easy to use.


Install and Configure
=====================
.. toctree::
   :maxdepth: 2
   :caption: Installation and Configuration

   ./installation
   ./user_configuration
   ./folders

JADE execution
==============
.. toctree::
   :maxdepth: 2
   :caption: JADE execution

   run
   postprocessing
   utilities
   tipstricks
   troubleshooting