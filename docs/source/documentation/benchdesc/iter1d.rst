.. _iter1ddesc:

ITER 1D
-------

.. figure:: /img/benchmarks/iter1D.png
    :width: 600
    :align: center

    ITER 1D MCNP geometry (quarter)

The ITER 1D benchmark developed by Prof. Sawan M. is a popular 1-Dimensional neutronic model
used for nuclear data benchmarking in the fusion community. This consists of a 
simple but realistic model of the ITER TOKAMAK where the inboard and outboard 
portion of the machine and the plasma region are modelled by means of simple 
concentric cylindrical surfaces.

Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

As visible in the figure, the benchmarks geometry is uniquely composed by concentric
cylindrical surfaces. A detailed description of the different layers is reported
hereafter:

.. figure:: /img/benchmarks/materialsITER1D.png
    :width: 600
    :align: center

    Description of the layers composing the ITER 1D benchmark

The plasma region includes a 14.1 MeV isotropic neutron source
(characteristic of Deuterium-Tritium fusion reaction).

Tallies
^^^^^^^

Many quantities are tallied in the ITER 1D benchmark, the following is a thorough
description of them.

Tally n. 4
    Neutron flux [#/cm^2] (binned in Vitamin-J 175 energy groups) in 97 different MCNP cells located across the radial direction.
Tally n. 204
    Total neutron flux [#/cm^2] at the same locations as Tally n. 4.
Tally n. 14
    Photon flux [#/cm^2] (binned in energy) at the same locations as Tally n. 4. The energy bins limits are 0.1, 1, 5, 10 and 20.
Tally n. 214
    Total photon flux [#/cm^2] at the same locations as Tally n. 4.
Tally n.6
    Total nuclear heating [W/g], i.e., neutron plus photon heating at the same locations as Tally n. 4.
Tally n. 16
    Neutron heating [W/g] at the same locations as Tally n. 4.
Tally n. 26
    Photon heating [W/g] at the same locations as Tally n. 4.
Tally n. 34
    Helium production in steel.
Tally n. 44
    Hydrogen production in steel.
Tally n. 54
    Tritium production in steel.
Tally n. 64
    Displacement per atom (DPA) in Cu.
Tally n. 74
    Helium production in CuBeNi.
Tally n. 84
    Hydrogen production in CuBeNi.
Tally n. 94
    Tritium production in CuBeNi.
Tally n. 104
    DPA in Nickel.
Tally n. 114
    Helium production in Inconel.
Tally n. 124
    Hydrogen production in Inconel.
Tally n. 134
    Tritium production in Inconel.
Tally n. 144
    Helium production in Be.
Tally n. 154
    Hydrogen production in Inconel.
Tally n. 164
    Tritium production in Inconel.
Tally n. 174
    Fast (E>0.1 MeV) neutron fluence at magnets.


.. seealso:: **Related papers and contributions:**

    * M. Sawan, 1994,  "FENDL Neutronics Benchmark: Specifications for the calculational and shielding benchmark",
      (Vienna: INDC(NDS)-316)