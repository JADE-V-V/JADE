.. _fngw:

FNG Benchmark Experiment on Tungsten
------------------------------------

The experiment was carried out in 2001 at FNG facility. The purpose is to validate tungsten cross sections as it is a candidate material for high 
flux components in ITER and its development is pursued in the 
European Fusion Technology Program. The experiment was carried out with the 14 MeV neutrons source 
used at FNG described in :ref:`fngsddr` and :ref:`fngblk`.

Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /img/benchmarks/fng-w.png
    :width: 500
    :align: center

    Layout of Benchmark Experiment on Tungsten.

 
The geometry of the mock-up consisted of a block of a tungsten alloy, DENSIMET, produced by PLANSEE,
in pieces of various shapes. The mock-up is assembled to obtain a size of about
42-47 cm (L) x 46.85 cm (H) and 49 cm in thickness. It was located in front
of the FNG target, 5.3 cm from the neutron source. Most of the material
(about 1.5 ton) is DENSIMET-176 type (92.3% W, 2.6% Fe, 4.2% Ni).
A layer of DENSIMET-180 (about 0.25 ton, 7 cm height, composition 95.0% W,
1.6% Fe, 3.4% Ni) was used in the central part of the block where the
measurements were done and contains the lateral access
channels (diameter 5.2 cm) for locating detectors of various types
(activation foils, TLD holders, active spectrometers)

.. The following quantities are measured:

.. * Neutron reaction rates by activation foils
.. * Nuclear heating by thermo-luminescent detectors (TLD-300)

The neutron reaction rates were measured by activation foils. Eight different reactions, listed in the following section, were used to
derive the neutron flux.
The reaction rates were measured in four experimental positions at different
depths from the block surface, using absolutely calibrated HPGe detectors. During the activation foil
measurements, the lateral access channels were completely closed by means of
4 ad hoc cylinders made of DENSIMET – 180, a thin slot was realised (4.4 mm)
to locate activation foils in position, using a thin Al holder. The foils
were irradiated in three irradiations: in the first one Zr, Al and Mn foils
were irradiated; in the second one Nb, Ni and Au foils were irradiated and in the last one
Fe and In foils were irradiated.

.. Gamma heating was measured using TLD-300 dosimeters (CaF2:Tm). TLDs
.. calibration was performed using Co-60 secondary standard, from 50 mGy up to
.. 4 Gy in air, converted into absorbed dose in TLD-300 using the photon energy
.. attenuation coefficients from Hubble.
.. Seven TLDs chips (3.2x3.2x0.9 mm3 each) were located in each experimental
.. position, using the same experimental arrangement as for the activation foils,
.. and enclosed in a perspex  holder 1 mm thick.

Tallies
^^^^^^^
The source angle/energy distribution was calculated with MCNP, taking into 
account the reaction kinematics and the slowing down of beam deuterons in the 
tritium/titanium target. Only one tally is defined for each input:

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
  * Zr-90(n,2n)Zr-89


.. seealso:: **Related papers and contributions:**

    * P. Batistoni, M. Angelone, L. Petrizzi, M. Pillon, Measurements
      and Analysis of Neutron Reaction Rates and of Gamma Heating in
      Tungsten, MA-NE-R-003, ENEA, Dec. 2002