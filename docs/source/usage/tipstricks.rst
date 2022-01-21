#############
Tips & Tricks
#############

This section reunites a series of tips and tricks that can be used to *unlock*
JADE additional capabilities.

.. _externalrun:

External Run of a benchmark
===========================
It may be useful for particularly computational-intensive benchmark to be
run on a separate hardware (e.g. a server) with respect to the one used for JADE.
This can be achieved quite easily with the following steps:

#. set the ``OnlyInput`` option in the ``<JADE root>\Configuration\Conf.xlsx``
   file to ``True`` for the benchmark that needs to be run externally. This
   will generate the MCNP input file of the benchmark that can be found in
   ``<JADE root>\Tests\MCNP simulation\<lib suffix>\<Benchmark name>``
   without running it;
#. copy the generated input file into the hardware selected for the run and start the
   MCNP simulation. The only requirement is to use the MCNP keyword  ``name=``
   when launching the simulation in order to obtain consistently named outputs,
   for instance:

   ``mcnp6 name=FNG tasks 32``

#. once the simulation is completed, copy all MCNP outputs to the same 
   ``<JADE root>\Tests\MCNP simulation\<lib suffix>\<Benchmark name>`` folder;
#. normally run the post-processing.

Change the plots fontsizes
==========================
Font size in plots is hardcoded in JADE. Nevertheless to change these value globally
for all plots it is quite easy since they are all defined at the beginning of the
``<JADE root>\Code\plotter.py`` file trough the matplotlib.pyplot.rc attribute:

.. code-block:: python

   import matplotlib.pyplot as plt
   # ============================================================================
   #                   Specify parameters for plots
   # ============================================================================
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


Add a new material to the spherical benchmarks
==============================================
To add a new material to both the Sphere Leakage and Sphere SDDR is fairly simple.
The steps to follow are the following:

* Add the material card defining the material to the MCNP input named
  **TypicalMaterials** in the ``JADE_root>\Benchmarks inputs`` folder.
  Chose a material number that has not been already used.
* Modify the ``<JADE_root>\Configuration\Benchmarks Configuration\Sphere\MaterialSettings.csv``
  and the ``<JADE_root>\Configuration\Benchmarks Configuration\SphereSDDR\MaterialSettings.csv``
  to specify the run parameters for the new materials. See :ref:`runconf` for
  additional details on such files.
