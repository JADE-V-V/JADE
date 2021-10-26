##################
General OOP scheme
##################

.. figure:: /img/OOPscheme.png
    :align: center
    :width: 600

    General OOP scheme for the JADE code

All user interactions that happen through the command console are handled
by the ``gui.py module``. When JADE is started, a ``main.Session()`` object
is intialized which is a container for a series of information and tools
that many parts of the code may need to access. In particular it contains:

Paths
    through ``main.Session()`` it is possible to recover many paths to the
    different folders that constitutes the JADE tree (see also :ref:`folders`).
Status
    the ``state.Status()`` object has informations on which libraries have
    been assessed or post-processed.
Configuration
    the ``configuration.Configuration()`` object is the one that handles the
    parsing of the :ref:`mainconfig` file.
Library Manager
    the ``libmanager.LibManager()`` is responsible for all operations related
    to nuclear data libraries. These include for instance checking the
    availability of a library, or handling the translation of a single isotope.

Generally speaking, the user can request three types of thing to the gui:

* use one of the utilities, that will trigger the call of the ``utilitiesgui.py``;
* run the benchmark suite on a library through the ``computational.py`` module;
* perform the pst-processing on one or more libraries calling the ``postprocess.py``
  module.

Utilities
=========
The ``utilitiesgui.py`` simply contains a number of functions associated to the
different utilities available in JADE.

.. seealso::
    :ref:`uty`

Benchmarks generation and run
=============================
In JADE the object representing a benchmark is the :ref:`testob` (or :ref:`multitestob`
in case the benchmark is composed by more than one run). This object is responsible
for the creation of the MCNP input and for its run. In order to build the input
it uses the following auxiliary classes:



    