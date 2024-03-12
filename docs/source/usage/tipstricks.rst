#############
Tips & Tricks
#############

This section reunites a series of tips and tricks that can be used to *unlock*
JADE additional capabilities.

.. _externalrun:

External Run of a benchmark
===========================
Although submission is parallel is now possible in JADE, it may be useful for 
particularly computational-intensive benchmark to be run on a separate hardware
(e.g. a server) with respect to the one used for JADE. This can be achieved quite easily
with the following steps:

#. Set the ``OnlyInput`` option in the ``<JADE root>\Configuration\Conf.xlsx``
   file to ``True`` for the benchmark that needs to be run externally. This
   will generate the input files of the benchmark that can be found in
   ``<JADE root>\Tests\Simulations\<lib suffix>\<benchmark_name>\<code>\``
   without running it;
#. Once the simulation is completed, copy all the outputs to the same 
   ``<JADE root>\Tests\Simulation\<lib suffix>\<benchmark name>\<code>\`` folder;
#. Tun the post-processing as normal. 

Change the plots parameters
===========================
Font size in plots is hardcoded in JADE. Nevertheless to change these value globally
for all plots it is quite easy since they are all defined at the beginning of the
``<JADE root>\Code\plotter.py`` file trough the matplotlib.pyplot.rc attribute:

.. code-block:: python

   import matplotlib.pyplot as plt
   # ============================================================================
   #                   Specify parameters for plots
   # ============================================================================
   DEFAULT_EXTENSION = '.png'

   SMALL_SIZE = 22
   MEDIUM_SIZE = 26
   BIGGER_SIZE = 30

   plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
   plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
   plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
   plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
   plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
   plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
   plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
   plt.rc('lines', markersize=12)          # Marker default size

Also the default extension of the plots can be changed in this way (it needs
to be supported by ``matplotlib`` though).

Add a new material to the spherical benchmarks
==============================================
To add a new material to both the Sphere Leakage and Sphere SDDR is fairly simple.
The steps to follow are the following:

* Add the material card defining the material to the MCNP input named
  **TypicalMaterials** in the ``JADE_root>\Benchmarks inputs`` folder.
  Chose a material number that has not been already used.
* Modify the ``<JADE_root>\Configuration\Benchmarks_Configuration\Sphere\MaterialSettings.csv``
  and the ``<JADE_root>\Configuration\Benchmarks_Configuration\SphereSDDR\MaterialSettings.csv``
  to specify the run parameters for the new materials. See :ref:`runconf` for
  additional details on such files.

Compare design solutions instead of libraries
=============================================
It is possible to "inappropriately" use JADE to compare different
design solution or in general different version of a same MCNP input instead 
of libraries and still exploit JADE automatic post-processing. For instance
let us imagine to test which is the effect of different level of impurities 
in a specific material inside a particular geometry. Then the following steps
would allow to use JADE post-processing features to obtain comparisons of results
at different impurities:

* :ref:`customcompbench` containing the problem of interest;
* run the first version of the benchmark with a library of choice;
* rename the obtained output folder (e.g. "01.d");
* change the impurity level in the MCNP template and run again the bechmark;
* rename the obtained folder (e.g. "02.d");
* repeat the previous steps for all the different benchmark versions;
* map the fake library names to more significant ones using the :ref:`mainconfig` file;
* run a comparison post-processing listing all the fake libraries (e.g. 01.d-02.d-...).

Note that the benchmarks could also be run separately and only the simulation
results be brought in JADE. Clearly, all benchmarks should be run using the same
nuclear data library.
