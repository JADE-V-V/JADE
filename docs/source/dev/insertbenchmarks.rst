########################
Insert Custom Benchmarks
########################

The easiest way to contribute to JADE is to widen its benchmarks suite.

This section of the guide describes how to add custom benchmarks to the JADE suite. The procedures
necessary to implement new computational and experimental benchmarks are different and are
described respectively in :ref:`customcompbench` and :ref:`customexpbench`.

.. _customcompbench:

Insert Custom Computational Benchmark
=====================================
Implementing a new computational benchmark is relatively easy and, theoretically, no additional
code is required. The procedure is composed by the following steps:

#. Once the benchmark input has been finalized, save it as ``<JADE_root>\Benchmark inputs\<name>.i``. 
#. Add the benchmark to the main configuration file in the computational sheet. See :ref:`compsheet`
   for additional information on this.
#. [OPTIONAL] if external weight windows (WW) are used, the WW file must be named *wwinp* and inserted in
   ``<JADE_root>\Benchmark inputs\VRT\<name>\``.
#. Create a custom post-processing configuration file as described in :ref:`ppconf` and save it in
   ``<JADE_root>\Configuration\Benchmarks Configuration\<name>.xlsx``

.. note::
    The benchmark input should not contain any STOP paramaters or NPS card (this is regulated by the
    main configuration file).
.. note::
    It is recommended to provide a comment card (FC) for each tally. These comments are considered the
    extended tally names and are used during post-processing.
.. warning::
    benchmark input file name cannot end with 'o' or 'm'.

.. _customexpbench:

Insert Custom Experimental Benchmark
====================================
Inserting a custom experimental benchmark is slightly more complex, but a significant higher order
of customization is guaranteed.
Steps 1) and 2) of the computational benchmarks procedure still need to be followed but then some
additional coding needs to be performed, specifically, a new child of the :ref:`expoutputclass`
class needs to be defined inside ``<JADE_root>\Code\expoutput.py``.
In order to do that, at least the three abstract methods ``_processMCNPdata()``, ``_pp_excel_comparison()``
and ``_build_atlas()`` need to be implemented in the new class.
Once this has been done, a few other adjustments need to be done to the code.

Call the right Output class
---------------------------
In ``<JADE_root>\Code\postprocess.py``, the function ``_get_output()`` controls the creation of the
benchmark object during post-processing depending on the benchmark. Here an *elif* statement needs
to be added to ensure that the newly created custom class is called when generating the output for
the custom added experimental benchmark. Here is an example of how the FNG benchmark was added:

.. code-block:: python

    ...

    elif testname == 'FNG':
        if action == 'compare':
            out = expo.FNGOutput(lib, testname, session, multiplerun=True)
        elif action == 'pp':
            print(exp_pp_message)
            return False
    
    ...

The user should just substitute ``FNG`` with the name of the benchmark input and ``FNGOutput`` with
the newly created class. Attention should be paid also to the ``multiplerun`` keyword, set True if
the benchmark is actually composed by more than one input (i.e. multiple MCNP/D1S runs).

Additional actions for multi-run benchmarks
-------------------------------------------
.. warning::
    these next actions need to be performed **only** if the benchmark is composed by more than one input.

In ``<JADE_root>\Code\status.py`` the name of the benchmark input needs to be added to the MULTI_TEST

.. code-block:: python

    MULTI_TEST = ['Sphere', 'Oktavian', 'SphereSDDR', 'FNG']

In ``<JADE_root>\Code\computational.py`` the function ``executeBenchmarksRoutines`` is responsible for
the generation and run of the benchmarks during a JADE session. The modification here is to be performed
in the part that is responsible for choosing the Test object to be used depending on the benchmark.
Here is the code snippet of interest: 

.. code-block:: python

    ...

    # Handle special cases
    if testname == 'Sphere Leakage Test':
        test = testrun.SphereTest(*args)

    elif testname == 'Sphere SDDR':
        test = testrun.SphereTestSDDR(*args)

    elif fname == 'Oktavian':
        test = testrun.MultipleTest(*args)

    elif fname == 'FNG':
        test = testrun.MultipleTest(*args, TestOb=testrun.FNGTest)

    else:
        test = testrun.Test(*args)
    
    ...

The default option is to simply create a ``Test`` object. Clearly, if a children was defined
specifically for the new experimental benchmark, an option would need to be added here.
If the benchmark is a multirun one, an additional *elif* statement needs to be added similarly
to what has been done for the FNG benchmark.

.. seealso::
     see also :ref:`testrunmodule` for a better description of the Test object and his children