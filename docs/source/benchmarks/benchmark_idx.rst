.. _benchmarks:

##########
Benchmarks
##########

This section describes more in detail all the default benchmarks
that have been implemented in JADE, dividing them between
computational and experimental benchmarks. It is strongly recommended
that the user reads this documentation carefully before using a specific 
benchmark in JADE. 

.. important::
    JADE benchmark inputs are not distributed with the software. 
    As explained in the :ref:`ecosystem` section, depending on their licensing
    policy, the benchmark inputs are stored in different GitHub/GitLab repositories.

.. important::
    For all FNG benchmarks in MCNP a SDEF source produced in 2021 by ENEA Frascati team (Davide Flammini et al.)
    was used. The source is parametrized at 260 keV and was generated using the following rdum parameters:

    "rdum    .260  1.6  0.0  0.001  0.0  0.001  1  1"

    For additional details on the source generation, the reader is referred to
    `Absolute experimental and numerical calibration of the 14 MeV neutron source at the Frascati neutron generator <https://doi.org/10.1063/1.1147035>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   computational
   experimental