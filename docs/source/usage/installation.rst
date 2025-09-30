.. _install:

############
Installation
############

JADE can be installed both on Windows and Linux operating systems. The recommended method
for installation is to use virtual environments (see `the python website <https://docs.python.org/3/library/venv.html>`_ for more information).
Currently, only MCNP can be run on the Windows installation. To use OpenMC
and Serpent in JADE, the user should install on Linux. 

Create a virtual environment
----------------------------

Firstly, create a virtual environment and activate it:

  | ``python -m venv jade_venv``
  | ``source jade_venv/bin/activate``

Or if you are using Anaconda:

  | ``conda create -n jade python=3.11``
  | ``conda activate jade``

.. warning:: 
  JADE officially supports only Python 3.10, 3.11 and 3.12.
  It may work with other versions, but they are untested.

Install the JADE package
------------------------

User installation
^^^^^^^^^^^^^^^^^^

Jade is hosted on PyPi under the name of ``jadevv``. To install it, run:

  | ``pip install jadevv[ui]``

It is responsibility of the user to install OpenMC in the same python environment 
in case they are planning to use it. This guarantees better visibility for the users
on which version of OpenMC is being run.

.. note:: 
  By using the ``[ui]`` option, the user will also install the GUI dependencies, in
  particular ``tkinter``. This may not be desirable if installing on clusters as
  often the module is not available in these systems. In this case, the recommended
  installation is to use simply ``pip install jadevv``. Ubuntu users should note
  that the default python installation does not come with Tkinter, and should run
  ``sudo apt-get install python3-tk`` before installing JADE.

.. warning:: 
  Development cycles of OpenMC are quite fast. For instance, after version 0.15.0
  OpenMC does not support anymore python 3.10. Be sure to install an OpenMC version
  that your python environment supports.  

.. _installdevelop:

Developer Installation
^^^^^^^^^^^^^^^^^^^^^^

JADE source code is hosted at `JADE repository <https://github.com/JADE-V-V/JADE>`_.
You can either dowload the zip file or clone it using git with:

  | ``git clone https://github.com/JADE-V-V/JADE``

Moving into the downloaded folder, the user can install the ``jade`` python package
through a local pip install.

It is recommeded to use the '-e' option when installing (editable mode)
and you should also install the additional 'dev' dependencies. 

  | ``pip install -e .[dev]``

If your dev system allows it, install also openmc in the same python environment.

Instantiate a JADE folder tree
------------------------------

JADE has now been installed as a command line tool at this point.

Many JADE instances (i.e. JADE folder structures) can be created on the same machine.

To use JADE, select a new root folder of your choice (different from where the JADE code clone
has been saved). This is going to to be the <root> folder.

Now Move into the root directory and run the following command: 

  | ``jade``

If permissions errors are encountered, try:

  | ``python -m jade``

The folder structure should now look like the one described in :ref:`folders`.
During this operation the benchmark inputs contained at `IAEA repository <https://github.com/IAEA-NDS/open-benchmarks>`_
are fetched.

A JADE instance has now been initialized and it is ready to be configured as discussed
in the :ref:`config` section.

In case the user possesses a valid access token for the F4E GitLab, they can add an environment
variable to their system named `F4E_GITLAB_TOKEN` with such token. JADE will automatically fetch
inputs also from the F4E GitLab. Alternatively, the token can be added later and
additional inputs can be recovered using the JADE utility:

  | ``python -m jade.utilities --fetch``

