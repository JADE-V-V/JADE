##################
Default Benchmarks
##################
This section describe more in detail all the default benchmarks
that have been implemented in JADE dividing them between
computational and experimental benchmarks.

.. important::
    * Not all benchmark inputs and related files can be distributed
      toghether with JADE due to licensing reasons. In case the user
      provide evidence of licensing rights on specific benchmarks, the
      JADE team will provide the missing input which, once copied 
      in suitable JADE folders, allow to correctly run them.
    * For some of the benchmarks, weight windows (WW) have been produced and
      necessary for the benchmark run. Unfortunately, these WW are often too
      heavy for them to be distributed with Git. These files must be downloaded
      separately and inserted in a suitable folder in ``<JADE_root>\Benchmark inputs\VRT``.  
    * The benchmarks included in JADE can be also divided between
      **transport** benchmarks (ususally associated with classical
      MCNP) and **activation** benchmarks (usually associated with
      D1S-UNED). It is recommended to run these two benchmarks
      categories separately, mostly because they require a different
      input in terms of library to be assessed. If transport Benchmarks
      expect a single library (e.g. ``31c``), activation one require
      two: an activation library and a transport one for all zaids that
      cannot be activated (e.g. ``99c-31c``).
    * In activation benchmarks, the library that is considered the assessed one
      is always the activation library (i.e. the first provided). No track
      is kept during the post-processing of which was the transport library used
      and it is responsability of the user to make sure that comparisons between
      activation libraries results are done in a coherent way. That is, the
      same transport library should be always used.

Computational Benchmarks
========================

.. include:: benchdesc/sphere.rst

.. include:: benchdesc/iter1d.rst

.. include:: benchdesc/tbm.rst

.. include:: benchdesc/cmodel.rst

.. include:: benchdesc/sphereSDDR.rst

.. include:: benchdesc/itercylSDDR.rst

Experimental Benchmarks
=======================

.. include:: benchdesc/oktavian.rst

.. include:: benchdesc/fng.rst
