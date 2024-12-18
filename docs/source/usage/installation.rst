.. _install:

############
Installation
############

JADE can be installed both on Windows and Linux operating systems. The recommended method
for installation is to use virtual environments (see `the python website <https://docs.python.org/3/library/venv.html>`_ for more information).
Currently, only MCNP can be run on the Windows installation. To use OpenMC
and Serpent in JADE, the user should install on Linux. 

jade package installation
-------------------------

Firstly, create a virtual environment and activate it:

  | ``python -m venv jade_venv``
  | ``source jade/bin/activate``

Visit the `JADE repository <https://github.com/JADE-V-V/jade>`_ and if you have `git <https://git-scm.com/>`_
installed you can clone the repository:

  | ``git clone https://github.com/JADE-V-V/JADE.git``
  | ``mv JADE Code``
  | ``cd Code``

The folder structure should now look like the following:
::
      <JADE_root>
        | --------- Code
                      | ------ jade
                      | ------ setup.cfg
                      | ------ pyproject.toml
                      | ------ ...


The user can then checkout the relevant branch of the code. It is now recommended that you upgrade pip before performing
the installation:

  | ``pip install --upgrade pip``
  | ``pip install .``

If the user wishes to use the OpenMC features within JADE, they should alternatively install JADE with OpenMC as follows:

  | ``pip install .[openmc]``

Note that currently version 0.14.0 of OpenMC is supported. The user will need to have git installed on their system. 

.. _installdevelop:

Development Installation
^^^^^^^^^^^^^^^^^^^^^^^^

If you are developing JADE, you can use the '-e' option when installing and you should install the additional dev dependencies. 

  | ``pip install -e .[dev]``

Create a jade folder tree
-------------------------

JADE has now been installed as a command line tool.
To complete the installation, create a new folder where you prefer. This is going to to be the
 <JADE_root> folder. You can have as many JADE tree as you prefer in your machine.
 Now Move into the root directory and run the following command: 

  | ``jade``

If permissions errors are encountered, you may also run:

  | ``python -m jade``

The folder structure should now look like the following:
::
      <JADE_root>
        | --------- benchmark_templates
        | --------- cfg
        | --------- logs
        | --------- post-processing
        | --------- raw_data
        | --------- simulations

The detailed folder structure should look like that illustrated in :ref:`folders`.

Complete the initial configuration
----------------------------------

Inside the `<JADE_root/cfg>` folder there are a few files that must be configured before
running jade. More information on this can be found at :ref:`configuration`.

