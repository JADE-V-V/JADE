.. _install:

############
Installation
############
The preferred way to install JADE is through a conda virtual environment, meaning that an
Anaconda or Miniconda installation is required. Please visit the
`Anaconda website <https://www.anaconda.com/products/individual>`_ for more detailed
information about the Anaconda products and virtual environments.

Once Anaconda is set up, proceed with the following steps to complete JADE installation:

#. Visit `JADE GitHub repository <https://github.com/dodu94/JADE>`_ and download the latest JADE release as a .zip folder; 
#. Extract the .zip into a folder of choice (from now on ``<JADE_root>``);
#. Rename the folder containing the different Python modules as 'Code' (``<JADE_root>\Code``);
   Your folders structure at this point should look like this:
   ::
      <JADE_root>
        |
        |--------- Code
        |            |----- default_settings
        |            |----- docs
        |            |----- install_files
        |            |----- templates
        |            |----- tests

#. Ensure that your conda version is up to date using:
   
  ``conda update conda``

#. Open an anaconda prompt shell and change directory to ``<JADE_root>\Code``.
   Here, create the JADE virtual environment typing:

   ``conda env create --name jade --file=environment.yml``
   
   This ensures that all JADE dependencies are satisfied. The environment can be activated using:

   ``conda activate jade``
   
   And deactivated simply using:

   ``conda deactivate``

#. With the environment active, type in the Anaconda prompt shell:
   
   ``python main.py``

   this will initialize the remaining part of JADE folders structure that now 
   should look like the one described in :ref:`folders`.
#. Open the global configuration file: ``<JADE_root>\Code\Configuration\Config.xlsx``;
   here you need to properly set the environment variables specified in the
   'MAIN Config.' sheet (i.e. xsdir Path, and multithread options);

The installation is now complete. JADE can now be started with the following
steps:

#. Open an Anaconda prompt shell;
#. activate the jade environment;
#. move to the ``<JADE_root>\Code`` folder;
#. type:

   ``python main.py``

.. seealso::
   check also :ref:`mainconfig` for additional information on the minimum environment variables
   to be set.

