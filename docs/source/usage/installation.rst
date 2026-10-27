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
  JADE officially supports only Python 3.11, 3.12, 3.13 and 3.14.
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
  Development cycles of OpenMC are quite fast. Be sure to install an OpenMC version
  that your python environment supports.  

ACTINV installation
~~~~~~~~~~~~~~~~~~~

Install the ACTINV CLI separately and configure its executable path as described
in :ref:`actinv_environment`. JADE runs
``actinv run <input>.json <output>.json`` as a subprocess, so no ACTINV Python
dependency is required. The initial adapter supports local, deterministic
neutron activation of one material per ``actinv-spec-1`` JSON input.

.. _installdevelop:

Developer Installation
^^^^^^^^^^^^^^^^^^^^^^

JADE source code is hosted at `JADE repository <https://github.com/JADE-V-V/JADE>`_.
You can either dowload the zip file or clone it using git with:

  | ``git clone https://github.com/JADE-V-V/JADE``

Moving into the downloaded folder, the user can install the ``jade`` python package
through a local pip install.

It is recommended to use the '-e' option when installing (editable mode),
together with the optional dependency groups needed for development:

  | ``pip install -e .[dev,ui,docs]``

The available optional dependency groups are:

- ``dev``: testing and formatting tools (``pytest``, ``pytest-cov``, ``pytest-xvfb``, ``ruff``).
- ``ui``: GUI dependencies (``ttkthemes``). Skip it on systems without Tkinter.
- ``docs``: tools needed to build this documentation locally (``sphinx`` and its extensions).

All dependencies are declared in ``pyproject.toml``, which is the single source of truth
(the documentation build on Read the Docs also installs from it). Most dependencies are capped
at their current major version (minor version for ``0.x`` packages); when bumping a cap,
make sure the test suite still passes.

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

