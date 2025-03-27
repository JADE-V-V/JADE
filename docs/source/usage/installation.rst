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
  | ``source jade/bin/activate``

Or if you are using Anaconda:

  | ``conda create -n jade python=3.11``
  | ``conda activate jade``

.. warning:: 
  JADE officially supports only Python 3.9, 3.10 and 3.11. There are known
  compatibility issues if Python 3.12 or later is used.

Install the JADE package
------------------------

User installation
^^^^^^^^^^^^^^^^^^

Jade is hosted on PyPi under the name of ``jadevv``. To install it, run:

  | ``pip install jadevv``

If the user wishes to use the OpenMC features within JADE, they can install the
additional dependency by running:

  | ``pip install jadevv[openmc]``

or 

  | ``pip install "jadevv[openmc]"``

Alternatively, the user can install OpenMC separately in the same python environment.

.. warning:: 
  Note that currently OpenMC is supported only up to version 0.14.0 and that the user
  will need to have git installed on their system if using the ``[openmc]`` option. 

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

A JADE instance has now been initialized and it is ready to be configured as discussed
in the :ref:`config` section.
