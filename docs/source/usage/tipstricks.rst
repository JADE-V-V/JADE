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

#. Set the ``OnlyInput`` during the run configuration for the benchmark that needs to
   be run externally. This
   will generate the input files of the benchmark that can be found in
   ``<JADE root>/simulations/<code-lib>/<benchmark_name>``
   without running it;
#. Once the simulation is completed, copy all the outputs to the same folder;
#. Tun the post-processing as normal.

Add a new material to the spherical benchmarks
==============================================
To add a new material to both the Sphere Leakage and Sphere SDDR is fairly simple.
The steps to follow are the following:

* Add the material card defining the material to the MCNP input named
  **TypicalMaterials** in the ``JADE_root>/benchmark_templates`` folder.
  Chose a material number that has not been already used.
* Modify the ``<JADE_root>\cfg\benchmarks\Sphere\MaterialSettings.csv``
  and the ``<JADE_root>\cfg\benchmarks\SphereSDDR\MaterialSettings.csv``
  to specify the run parameters for the new materials. See :ref:`runconf` for
  additional details on such files.

Compare design solutions instead of libraries
=============================================
It is possible to "inappropriately" use JADE to compare different
design solution or in general different version of a same benchmark input instead 
of libraries and still exploit JADE automatic post-processing. For instance
let us imagine to test which is the effect of different level of impurities 
in a specific material inside a particular geometry. Then the following steps
would allow to use JADE post-processing features to obtain comparisons of results
at different impurities:

* :ref:`customcompbench` containing the problem of interest;
* run the first version of the benchmark with a library of choice;
* rename the obtained output folder (e.g. "_mcnp_-_test1_");
* change the impurity level in the MCNP template and run again the bechmark;
* rename the obtained folder (e.g. "_mcnp_-_test2_");
* repeat the previous steps for all the different benchmark versions;
* map the fake library names to more significant ones using the ``<root>/cfg/libs_cfg.yml`` file;
* run a comparison post-processing listing all the fake libraries.

Note that the benchmarks could also be run on different hardware and only the simulation
results be brought in JADE. Clearly, all benchmarks should be run using the same
nuclear data library.
