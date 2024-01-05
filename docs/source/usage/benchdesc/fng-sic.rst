.. _fngsic:

FNG Silicon Carbide (FNG SiC)
-----------------------------

This experiment is part of the SINBAD database (`NEA-1553/56 <https://www.oecd-nea.org/science/wprs/shielding/sinbad/fng_sic/fngsic-a.htm>`_). 
Users will need to show proof of licence and request the required input files to use this 
benchamark in JADE.

The purpose of this experiment is to validate Si and C cross sections through irradiation 
of a monolithc sintered SiC block placed in front of the FNG source. This is in important 
structural material that is being explored for several differnt fusion concepts.  The 
experiment was carried out at the FNG facility, described in :ref:`fngsddr`, in 2001.

Geometry 
^^^^^^^^

The SiC mock-up assembly consisted of a sintered SiC block of dimensions 45.72 cm x 
45.72 cm x 71.12 cm located 5.3 cm from the FNG source. 

.. figure:: /img/benchmarks/fng-sic.jpg
    :width: 500
    :align: center

    Layout of FNG-SiC experiment. Figure taken from the SINBAD repository. 

Measured data
^^^^^^^^^^^^^

Four experimental locations were used through the centre of the mock used to measure reaction
rates and nuclear heating at different depths:

* **Reaction rates**: 197Au(n,g), 58Ni(n,g), 27Al(n,a), 93Nb(n,2n) at depths of 10.41 cm, 25.65 cm
  40.89 cm and 56.13 cm from the block surface. 
* **Nuclear heating**: Measured using TLDs at depths of 14.99 cm, 30.23 cm, 40.47 cm and 60.71 cm.

.. important::
    * There was a lack of reliable data on the concentration of boron in the SiC matrix therefore 
      it is recommended that **data related to thermal interactions are used in relative comparison
      only between codes and cross section libraries**. This includes the nuclear heating measurements
      and 197Au(n,g) reaction rate. 

MCNP model
^^^^^^^^^^

There are two independent MCNP models in order to caputire the geoemetry of the TLD detectors. In 
both cases the the most recently developed SDEF source from ENEA has been used and weight windows 
are included in each input file. 

Further modifications necessary to the distributed input file are captured in the patch file.

MCNP tallies
^^^^^^^^^^^^^^

The total dose in the TLDs is calculated by summation of the neutron and photon dose. The neutron
dose has an associated sensitivity coefficient that varies as a function of depth. The total dose
is then calculated as: 

D\ :sub:`t`\ = D\ :sub:`n`\ * K\ :sub:`n`\ + D\ :sub:`g`\

where K\ :sub:`n`\ is the neutron sensitivity coefficient, D\ :sub:`n`\ the neutron dose and
D\ :sub:`g`\ the photon dose.

Neutron and photon energy deposition are calculated through F6 type tallies. Here, Tally n.16 is 
used for the neutron energy deposition and Tally n. 26 for photon energy deposition. 

JADE post processes the tally results by multiplying by J/MeV=1.602E-13 and g/kg=1000 to give a direct
comparison to the experimental data given in Gy/source neutron.

Reaction rates were calcualted using an F4 type tally - Tally n.4 is used in all cases. The reaction MT numbers
are by default assigned using the `convention for IRDFF-II <https://www-nds.iaea.org/IRDFF/IRDFF-II_ACE-LST.pdf>`_. 
The raw output from MCNP can be compared directly the reported measured data.

Patch file
^^^^^^^^^^
Coming soon... 

.. seealso:: **Related papers and contributions:**

    * Angelone, M., Batistoni, P., Kodeli, I., Petrizzi, L., Pillon, M., Benchmark analysis of neutronics performances of a SIC block irradiated with 14 MeV neutrons, Fusion Engineering and Design, 63-64, 2002. 