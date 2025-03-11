.. _uty:

#########
Utilities
#########

Apart from the main functionalities of JADE, the application provides a set of
utilities that can be used to perform specific tasks.

These can be executed using the utilities module of jade:

    | ``jade.utilities --<option>``

or 

    | ``python -m jade.utilitis --<option>``

The following is a list of the available utilities:

* ``--fetch``: re-download/sync benchmark inputs from the IAEA GitHub repository.
* ``--restore``: restore the default configuration settings.
* ``--runtpe``: remove the runtpe files (.r) from MCNP simulation folders. This helps in
  reducing the storage memory occupied by the simulation outputs.
* ``--addrmode``: This adds the "RMODE 0" card to all the MCNP input files. This is useful
  when running the benchmarks on a cluster with D1SUNED prompt version instead of vanilla MCNP.