##################
General OOP scheme
##################

.. figure:: /img/OOPscheme.png
    :align: center
    :width: 600

    General OOP scheme for the JADE code

All user interactions that happen through the command console are handled
by the ``gui.py module``. When JADE is started, a :ref:`sessionob` object
is intialized which is a container for a series of information and tools
that many parts of the code may need to access. In particular it contains:

Paths
    through :ref:`sessionob` it is possible to recover many paths to the
    different folders that constitutes the JADE tree (see also :ref:`folders`).
Status
    the :ref:`statusob` object has informations on which libraries have
    been assessed or post-processed.
Configuration
    the :ref:`confob` object is the one that handles the
    parsing of the :ref:`mainconfig` file.
Library Manager
    the :ref:`libmanagerob` is responsible for all operations related
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
Operations for the benchmarks generation and run are handled by the ``computational.py``
module.
In JADE the object representing a benchmark is the :ref:`testob` (or :ref:`multitestob`
in case the benchmark is composed by more than one run). This object is responsible
for the creation of the MCNP input and for its run. A vital attribute of the benchmark
is its associated :ref:`inputob` or one of its children. In case the benchmark is run
with d1s code, an :ref:`irradfileob` and a :ref:`reacfileob` are also associated with the
test. A fundamental attribute of inputs is the :ref:`matcardob` which handles all operations
related to the materials (including library translations).

Post-processing
===============
Operations for the post-processing of benchmark run results are handled by the
``postprocessing.py`` module.
All objects representing outputs of a benchmark run must be a child of the abstract class
:ref:`abstractoutputob`. These classes always include an :ref:`mcnpoutputob` which collect
the results coming from the parsers of the different MCNP outputs.

    