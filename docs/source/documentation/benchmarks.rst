##################
Default Benchmarks
##################

This section describes more in detail all the default benchmarks
that have been implemented in JADE, dividing them between
computational and experimental benchmarks. It is strongly recommended
that the user reads this documentation carefully before using a specific 
benchmark in JADE. 

.. important::
    JADE benchmark inputs are not distributed with the software. 
    As explained in the :ref:`ecosystem` section, depending on their licensing
    policy, the benchmark inputs are stored in different GitHub/GitLab repositories.

Overview
========
The following tables summarise the computational and experimental benchmarks
that are included in JADE **(I)**, the ones that are currently under development
**(D)**, and a future wishlist **(W)**. A more detailed description of the implemented 
benchmarks can be found in the following sections.

**COMPUTATIONAL BENCHMARKS:**

.. csv-table::
    :file: computational_overview.csv
    :widths: 70 10 10 10
    :header-rows: 1

**EXPERIMENTAL BENCHMARKS:**

.. csv-table::
    :file: exp_overview.csv
    :widths: 70 10 10 10
    :header-rows: 1

Computational Benchmarks
========================

.. include:: benchdesc/sphere.rst

.. include:: benchdesc/iter1d.rst

.. include:: benchdesc/tbm.rst

.. include:: benchdesc/cmodel.rst

.. include:: benchdesc/sphereSDDR.rst

.. include:: benchdesc/itercylSDDR.rst

.. include:: benchdesc/simptokamak.rst

Experimental Benchmarks
=======================

.. include:: benchdesc/fng/fng-sddr.rst

.. include:: benchdesc/fng/fng-blk.rst

.. include:: benchdesc/fng/fng-w.rst

.. include:: benchdesc/fng/fng-sic.rst

.. include:: benchdesc/fng/fng-hcpb.rst

.. include:: benchdesc/fng/fng-ss.rst

.. include:: benchdesc/fng/tud-fng.rst

.. include:: benchdesc/fng/tud-w.rst

.. include:: benchdesc/aspis/aspis-fe88.rst

.. include:: benchdesc/aspis/aspis-pca-replica.rst

.. include:: benchdesc/oktavian.rst

.. include:: benchdesc/tiara.rst

.. include:: benchdesc/fns-tof.rst

.. include:: benchdesc/tud-fe.rst
