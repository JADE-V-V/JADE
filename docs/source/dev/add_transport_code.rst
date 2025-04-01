########################
Add a new transport code
########################

The following steps are required to add a new transport code to JADE:

#. Go to ``src/jade/helper/constants.py`` and add the new code tag to the the :class:`CODE` enum.
#. Go to ``src/jade/config/run_config.py`` and extend the :class:`Library` class to support the
   parsing of nuclear data libraries for the new transport code. Then, add that new library class to the
   :class:`LibraryFactory` in order to link it with the new code tag.
#. The next step is at ``src/jade/run/benchmark.py``. Here, you need to extend the :class:`SingleRun` and
   :class:`Input` (``src/jade/run/input.py``) abstract classes to support the new transport code. Then, add the new classes to the
   :class:`SingleRunFactory`. Childrens of :class:`SingleRun` only needs to implement a couple of methods to get the 
   executable command for the transport code.
   Childrens of :class:`Input` needs to implement methods that allow to read an input, modify the
   number of NPS to be run, translate the input to use a specific nuclear data library and write
   the input back.
   This will introduce the necessary logic to generate and execute all JADE supported benchmarks
   with the exception of the Sphere and SphereSDDR benchmarks.
   These benchmarks are the only ones that require an ad hoc children of :class:`Input`. For these
   benchmarks, you will need to connect this additional class directly in the ``_run_sub_benchmarks()``
   method of the :class:`SphereBenchmarkRun` or :class:`SphereSDDRBenchmarkRun` classes.
#. Finally, the :class:`AbstractSimOutput` abstract class at ``src/jade/post/sim_output.py``)
   needs to be extended. This class is responsible for parsing the output files of the transport code
   simulation and store the results of each single tally in a separate DataFrame of which the columns
   name are standardized. The list of accepted column names can be found at :ref:`allowed_binnings`.
   This new class can be connected with its ENUM tag in the ``__init__()`` method of the
   :class:`RawProcessor` class at  ``src/jade/post/raw_processor.py``.

Clearly, suitable tests should also be added to ensure the correct functioning of the newly implemented
classes.