###############
Troubleshooting
###############

Unable to post-process a libray
===============================

It may happen that the request to post-process a library fails, prompting to
video that the library in question has not been run.

.. image:: /img/troubleshooting/notrun.png

This may puzzle the user who is sure to have run the library instead.

This may happen if:

* in the :ref:`mainconfig` file, not all the benchmark that are currently set 
  as active for the post-processing have been actually run;
* MCNP was run for the benchmarks but there were errors in the Monte Carlo
  simulations. JADE considers a benchmark to have been "run" only if a mctal or
  fmesh file has been produced for each of the MCNP run foreseen by the benchmark.
