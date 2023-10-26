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

.. _calloutput:

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

.. _insbin:

Insert binned-value plot experimental benchmarks
------------------------------------------------
Experimental results often come as quantities like spectra, leakage fluxes, etc.
binned in energy or time. For this reason, a standard way of post-processing this kind
of data has been introduced in JADE, to speed-up the insertion process and to remove the need 
of adding code. The idea is to organize the benchmark by means of an Excel configuration file,
which is way more user-friendly than writing new code. The main steps to follow to
introduce a binned-value data benchmark are the following:

* All steps mentioned above for the insertion of a generic benchmark are still valid
  and should be followed also in this case. Also the folder structure is the usual one.
* As a general rule, to each tally of each in put file it corresponds a .csv file in Experimental Results
  data folder.
* Benchmark input filepath should be ``<JADE_root>\Benchmarks inputs\<BenchmarkName>``.
* For multiple run benchmarks, the filepath should be ``<JADE_root>\Benchmarks inputs\<BenchmarkName>\<BenchmarkName>_<InputName>.i``.
* The name of the experimental data file corresponding to a given tally in a given benchmark
  is supposed to be: BenchmarkName_TallyNumber.csv, and it must be put in
  ``<JADE_root>\Experimental Results\<BenchmarkName>``.
* If the benchmark foresees multiple runs, the filename must be set as: BenchmarkName_InputName_TallyNumber.csv
  and must be put in ``<JADE_root>\Experimental Results\<BenchmarkName>\<InputName>``
* Tallies in MCNP input should be binned only on one variable, e.g. only energy or
  only time (JADE doesn't foresee dependency on more than one independent variable)
  and should not include total bins (they are eventually ignored by JADE).
* In ``expoutput.py`` there is the global variable (dictionary) ``TALLY_NORMALIZATION`` which
  is used to select the normalization type of the MCNP results (e.g. in terms of
  lethargy or energy bins width).
* Data in .csv experimental data files should follow some standard rules:
    #. The name of the first column should be equal to: ``X Quantity [unit]``, where 
       ``X Quantity`` can be both ``Energy`` or ``Time``. The code could be easily
       updated to include also other binnings, e.g. Cosine bins. ``unit`` should correspond
       to the MCNP standard unit of the binned quantity.
    #. Data in first column should correspond to the upper values of the bins of the quantity
       and should be in ascending order.
    #. The second column name should be ``Y Quantity [unit]``, e.g. ``Fluence``, ``Leakage flux``, etc.
    #. Data in the second column should be the final data which is to be printed
       in the plot. No further processing and normalizations are foreseen by the code.
    #. The last column should be named ``Relative error [-]`` and should contain 
       the values of the total relative experimental error of that bin, not in percentage.
* Do the things explained in :ref:`calloutput` by using the ``SpectrumOutput`` class.
* Setup the benchmark configuration file in ``<JADE_root>\Configuration\Benchmarks Configuration`` folder
  as explained in :ref:`spectrumconfig`.
* In case of multiple runs, the same tally number should be used for the same quantity in all
  MCNP input files, e.g. tally number 14 in :ref:`tiara` benchmark should correspond
  for the sake of simplicity to the on-axis neutron flux in all MCNP inputs.

Here an example of a .csv experimental data file structure is reported:

.. figure:: /img/dev_guide/Example_exp_data.PNG
    :width: 600
    :align: center
    
    Example of .csv experimental file for SpectrumOutput class

.. _insbinmul:

Insert multiple tallies in plot
------------------------------------------------
In order to visualize data in a more compact way and to have a direct comparison of
the differences between different cases, it is often useful to show more than one 
plot in the same figure. For instance, the following picture is taken from :ref:`fnstof` ``Atlas``
and shows how the spectra acquired in the 5 different detectors' locations are grouped
in the same plot: 

.. figure:: /img/dev_guide/FNS-TOF_atlas.jpg
    :width: 600
    :align: center

    Leakage lethargy fluxes from 5 different detetors' locations in FNS-TOF experiment

To avoid the overlapping of the plots, both the tally results and experimental data
can also be multiplied by a factor. C/E comparisons are then printed for each tally
in the following page of the ``Atlas``.

To get this kind of plots is enough to follow the same steps mentioned in :ref:`insbin`,
but the class ``MultipleSpectrumOutput`` must be used. All the other parameters are set in
the related configuration file (see :ref:`multspectrumconfig`)