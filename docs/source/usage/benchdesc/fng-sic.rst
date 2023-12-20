.. _fngsic:

FNG Silicon Carbide (FNG SiC)
-----------------------------

This experiment is part of the SINBAD database (NEA-1553/56). Users will need
to show proof of licence and request the required input files to use this benchamark
in JADE.

The purpose of this experiment is to validate Si and C cross sections through irradiation 
of a monolithc sintered SiC block placed in front of the FNG source. This is in important structural material that is being
explored for several differnt fusion concepts.  The experiment was carried out at the FNG
facility, described in :ref:`fngsddr`, in 2001.

Geometry 
^^^^^^^^

.. figure:: /img/benchmarks/FNGSiC.jpg
    :width: 500
    :align: center

    Illustration of the layout of the FNG SiC experiment.

 The SiC mock-up assembly consisted of a sintered SiC block of dimensions 45.72 cm x 
45.72 cm x 71.12 cm located 5.3 cm from the FNG source. 

Measured data
^^^^^^^^^^^^^

Four experimental locations were used through the centre of the mock used to measure reaction
rates and nuclear heating at different depths:

* **Reaction rates**: 197Au(n,g), 58Ni(n,g), 27Al(n,a), 93Nb(n,2n) at depths of 10.41 cm, 25.65 cm
  40.89 cm and 56.13 cm from the block surface. 
* **Nuclear heating**: Measured using TLDs at depths of 14.99 cm, 30.23 cm, 40.47 cm and 60.71 cm.

.. important::
    * There was a lack of reliable data on the concentration of boron in the SiC matrix therefoore 
      it is recommended that **data related to thermal interactions are used in relative comparison
      only between codes and cross section libraries**. This includes the nuclear heating measurements
      and 197Au(n,g) reaction rate. 

MCNP model
^^^^^^^^^^

There are two independent MCNP models in order to caputire the geoemetry of the TLD detectors. In 
both cass the SDEF source, 'SDEF_ENEA.txt' has been used and weight windows are included in each 
input file. 

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

JADE post processes the tally results by multiply by J/MeV=1.602E-13 and g/kg=1000 to give a direct
comparison to the experimental data given in Gy/source neutron.



Tally n. 4
  A track length flux tally has been used to collect results in the cells
  corresponding to the activation foils in MCNP geometry. The tally has been
  multiplied in each input (with FM card) by the appropriate microscopic 
  reaction cross section, to obtain results in terms of number of reactions 
  per unit neutron from the source. No energy bins were used. Nuclear data for
  tally collection was taken from IRDFF dosimetry libraries. In the following,
  a list of the reactions considered for each activation foil material is
  reported:

  * Nb-93(n,2n)Nb-92
  * Ni-58(n,2n)Ni-57
  * Ni-58(n,p)Co-58
  * Fe-56(n,p)Mn-56
  * Al-27(n,a)Na-24
  * In-115(n,n')In-115m
  * Mn-55(n,g)Mn-56
  * Au-197(n,g)Au-198

Patch file
^^^^^^^^^^
Coming soon... 

.. seealso:: **Related papers and contributions:**

    * P. Batistoni, M. Angelone, W. Daenner, U. Fischer, L. Petrizzi, M. Pillon, A. santamarina, K. Seidel, "Neutronics Shield Experiment for ITER at the Frascati Neutron Generator FNG", 17th Symposium on Fusion Technology, Lisboa, Portugal, September 16-20, 1996.