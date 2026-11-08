.. _uty:

#########
Utilities
#########

Apart from the main functionalities of JADE, the application provides a set of
utilities that can be used to perform specific tasks.

These can be executed using the utilities module of jade:

    | ``jade.utilities --<option>``

or 

    | ``python -m jade.utilities --<option>``

The following is a list of the available utilities:

* ``--fetch``: re-download/sync benchmark inputs from the IAEA GitHub repository and F4E GitLab (if access token
  was provided).
* ``--restore``: restore the default configuration settings.
* ``--runtpe``: remove the runtpe files (.r) from MCNP simulation folders. This helps in
  reducing the storage memory occupied by the simulation outputs.
* ``--addrmode``: This adds the "RMODE 0" card to all the MCNP input files. This is useful
  when running the benchmarks on a cluster with D1SUNED prompt version instead of vanilla MCNP.
* ``--unfinished``: Print to log the simulations that were not completed correctly or have not been run yet.
* ``--migrate-raw [RAW_ROOT]``: rename raw results folders produced by older JADE versions
  (``_<code>_-_<library>_``) to include the code version (``_<code>_-_<version>_-_<library>_``).
  The version is read from the ``code_version`` field of each benchmark ``metadata.json``.
  Folders whose code version is unknown, or whose destination already exists, are left
  untouched and reported in the log. By default the JADE ``raw_data`` folder is migrated; a
  different root (e.g. a local clone of the JADE raw results repository) can be provided.
  Add ``--dry-run`` to only print the planned changes.