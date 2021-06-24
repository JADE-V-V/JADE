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
   when launching the simulation in order to obtain consistently named outputs;
#. once the simulation is completed, copy all MCNP outputs to the same 
   ``<JADE root>\Tests\MCNP simulation\<lib suffix>\<Benchmark name>`` folder;
#. normally run the post-processing.