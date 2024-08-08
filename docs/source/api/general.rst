##################
General OOP scheme
##################

.. figure:: /img/OOPscheme.png
    :align: center
    :width: 600

    General OOP scheme for the JADE code

All user interactions that happen through the command console are handled
by the ``gui.py module``. When JADE is started, a Session object
is intialized which is a container for a series of information and tools
that many parts of the code may need to access. In particular it contains:

Paths
    through Session it is possible to recover many paths to the
    different folders that constitutes the JADE tree (see also :ref:`folders`).
Status
    the Status object has information on which libraries have
    been assessed or post-processed.
Configuration
    the Configuration object is the one that handles the
    parsing of the :ref:`mainconfig` file.
Library Manager
    the libmanager is responsible for all operations related
    to nuclear data libraries. It is now included in f4enix here: `f4enix documentation <https://f4enix.readthedocs.io/en/latest/_autosummary/f4enix.input.libmanager.html#module-f4enix.input.libmanager>`_
    These include for instance checking the
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
In JADE the object representing a benchmark is the Test object (or MultipleTest object
in case the benchmark is composed by more than one run). This object is responsible
for the creation of the MCNP input and for its run. A vital attribute of the benchmark
is its associated Input object (`Input object <https://f4enix.readthedocs.io/en/latest/_autosummary/f4enix.input.MCNPinput.html>`_) or one of its children. In case the benchmark is run
with d1s code, an irradiation file and a reaction file (`D1S files <https://f4enix.readthedocs.io/en/latest/_autosummary/f4enix.input.d1suned.html>`_) are also associated with the
test.

Post-processing
===============
Operations for the post-processing of benchmark run results are handled by the
``postprocessing.py`` module.
All objects representing outputs of a benchmark run must be a child of the abstract class
AbstractOutput. These classes always include an MCNPoutput which collect
the results coming from the parsers of the different MCNP outputs.

    