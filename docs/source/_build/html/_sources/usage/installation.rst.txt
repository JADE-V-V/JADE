.. _install:

############
Installation
############
The preferred way to install JADE is through a conda virtual environment, meaning that an
Anaconda or Miniconda installation is required.

#. Extract the zip into a folder of choice (from now on ``<JADE_root>``);
#. Rename the folder containing the Python scripts as 'Code' (``<JADE_root>\Code``);
#. Open the global configuration file: ``<JADE_root>\Code\Configuration\Config.xlsx``;
   here you need to properly set the environment variables specified in the 'MAIN Config.' sheet (i.e. xsdir Path, and multithread options);
#. Open an anaconda prompt shell and change directory to ``<JADE_root>\Code``. Then create a virtual
   environment specific for jade:

   ``conda env create --name jade --file=environment.yml``
   
   This ensures that all dependencies are satisfied. The environment can be activated using:

   ``conda activate jade``
   
   And deactivated simply using:

   ``conda deactivate``

#. Finally, when the environment is activated, in order to start JADE type:

   ``python main.py``

#. On the first usage the rest of the folders architecture is initialized.

.. seealso::
   check also :ref:`mainconfig` for additional information on the minimum environment variables
   to be set.

