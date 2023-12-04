.. _install:

############
Installation
############

JADE can be installed both on Windows and Linux operating systems. The recommended method
for installation is to use virtual environments (see `the python website <https://docs.python.org/3/library/venv.html>`_ for more information). Currently, only MCNP can be run on the Windows installation. To use OpenMC
and Serpent in JADE, the user should install on Linux. 

Installation on Linux
---------------------

Firstly, create a virtual environment and activate it:

  | ``python -m venv jade``
  | ``source jade/bin/activate``

Visit the `JADE repository <https://github.com/JADE-V-V/jade>`_ and if you have `git <https://git-scm.com/>`_
you can clone the repository:

  | ``git clone https://github.com/JADE-V-V/JADE.git``
  | ``mv JADE Code``
  | ``cd Code``

The user can then checkout the relevant branch of the code. It is now recommended that you upgrade pip before performing
the installation:

  | ``pip install --upgrade pip``
  | ``pip install .``

If you are developing JADE, you can use the '-e' option when installing. JADE has now been installed as 
a command line tool and should now be initialised in the root directory as follows: 

  | ``cd ../``
  | ``jade``

The folder strucure should now look like the following:
::
      <JADE_root>
        | --------- Benchmark_Inputs
        | --------- Code
        | --------- Configuration
        | --------- Experimental_Results
        | --------- jade
        | --------- Quality
        | --------- Tests
        | --------- Utilities

The detailed folder structure should look like that illustrated in :ref:`folders`.

Once initialised, the user should configure JADE for their system. This can be done by editing 
``<jade_root>/Configuration/Config.xlsx.``

.. seealso::
   check also :ref:`mainconfig` for additional information on configuring JADE prior to running.

Following configuration, the user can run 'jade' within ``<JADE_root>`` to start JADE and the user
interface will appear. Each time a new window is launched, the user should remember to activate the
virtual environment. 

Installation on Windows
-----------------------

The steps for installation on windows are essentially the same as that described for Linux. 
Again, use of virtual envrionments is recommended. Note that if you are using PowerShell, you may need
to run PowerShell as an adminstrator and change the `Set-ExecutionPolicy <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-7.4>`_ 
cmdlet in order to be able to activate the virtual environment. 

  | ``python -m venv jade_venv``
  | ``.\jade_venv\Scripts\activate``

Once activated, the steps described above for Linux can be followed.

Currently, only the running of MCNP is supported on Windows and JADE should be configured accordingly.
This is further detailed in :ref:`mainconfig`. 

