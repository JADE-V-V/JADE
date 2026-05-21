.. _add_benchmark:

###########
First steps
###########

The easiest way to contribute to JADE is to widen its benchmarks suite.

This section of the guide describes how to add custom benchmarks to the JADE suite.

The typical steps to add a new benchmark are the following:

- Prepare JADE yaml files (raw, excel and atlas)
- Add inputs to the correct repository (more on this in :ref:`where_inputs`)
- Add documentation, which includes a description of the benchmark as well as updating
  the overview table of implemented benchmarks in :ref:`benchmarks`.
- [OPTIONAL] Add support for your benchmark to JADE WebApp. More information on
  how to do so can be found in :ref:`webapp`.

.. _where_inputs:

Where should I put the benchmarks input files?
==============================================

The input files for the benchmarks do not reside in the JADE repository. If your benchmark can be freely
distributed please upload it to the the IAEA open-source repository 
`here <https://github.com/IAEA-NDS/open-benchmarks/tree/main/jade_open_benchmarks>`_. You will find 
more detailed instructions on where to position the files directly in the repository.
In case your benchmark is SINBAD derived and you are a SINBAD user, consider adding it to the
new SINBAD GitLab repository (coming soon).
If none of the above cases apply but you still would like to have some form of version
control on your benchmark (strongly recommended), you can upload your input files to the
privatly hosted GitLab of Fusion For Energy.
For any doubt regarding the upload of benchmark inputs please contact davide.laghi@f4e.europa.eu.

Different transport codes have different needs. Hereafter, the main requirements for each type
of inputs are specified.

MCNP
----

- The input name shall be ``<benchmark_name>.i``
- weight windows file (if present) should be named ``wwinp``

.. note:: 
  If the benchmark input uses special dosimetry libraries that should not be translated, their suffix
  should be added to the ``DOSIMETRY_LIBS`` list in ``jade/helper/constants.py``.

D1SUNED
-------

- MCNP requirements apply
- A ``<benchmark_name>_irrad`` and ``<benchmark_name>_react`` files should also be provided.
  If the reac file is not provided, the code will generate one automatically. All the isotopes
  contained in the input will be translated to the activation library if there is at least
  one decay pathway that can result into one of the daughters listed in the irrad file.
- The benchmark input should not contain any ``STOP`` parameters or ``NPS`` card.

OpenMC
------
- The names of the input files should be ``settings.xml``, ``geometry.xml``, ``tallies.xml`` and ``materials.xml``, 
  if the model uses an ``openmc.IndependentSource``.
- If the model uses an ``openmc.CompiledSource``, the ``settings.xml`` file is optional;
  if this is omitted, a ``settings.xml`` file is generated within JADE, assuming default options.
  A compiled library file, ``libsource.so`` must be provided, which has been compiled using ``gcc`` 
  with shared libraries enabled. An example of how to compile an OpenMC source is provided in the
  `OpenMC documentation <https://docs.openmc.org/en/stable/usersguide/settings.html#compiled-sources>`_.
- If the model uses weight windows, a weight windows file in HDF5 format should be provided.
  The file should be named ``weight_windows.h5``. This weight window will be used in simulation if it is provided.
- If dosimetry calculations are required, the IRDFF-II data library should be used and can be implemented using an ``openmc.EnergyFunctionFilter``
  which is outlined in this `notebook <https://nbviewer.org/gist/paulromano/842b1df9eb2003747e2fd6d95514129a>`.
- The tallies IDs should be explicitly fixed when creating the ``tallies.xml`` file. This prevents
  OpenMC from creating them automatically and, thus, potentially changing them between different runs
  of a same benchmark. If possible, the tallies identifiers should be the same as the ones used in the
  other transport codes.

Serpent
-------
TODO

Experimental Data
-----------------
Experimental data needs to be provided in the form of *.csv* files. These files should be named
exactly like the ones produced by the raw data processing and have the same structure. The Experimental
results are stored in the repository with the input files in an *exp_results* folder. E.g. for those
benchmarks in the IAEA repository, the experimental results can be found here: `here <https://github.com/IAEA-NDS/open-benchmarks/tree/main/jade_open_benchmarks/exp_results>`_ 

Modify the default run_cfg file
===============================

In order for the new benchmarks to appear among the available ones when running the JADE run
GUI, it needs to be added to the default run configuration file. The file can be
found at ``jade/resources/default_cfg/run_cfg.yaml``.

This is an example of yaml code to be added to the file in order to add a benchmark:

.. code-block:: yaml

  benchmark_name:  # this is the ID of the benchmark. Used in all cfg related files
    codes: # Leave empty like in the example
      d1s: []
      mcnp: []
      openmc: []
      serpent: []
    custom_input: # leave empty
    description: A short description of the benchmark
    nps: 5e7  # default value of number of histories to simulate
    only_input: false  # leave false