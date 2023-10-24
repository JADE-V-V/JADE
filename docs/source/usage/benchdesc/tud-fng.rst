FNG Bulk Blanket and Shield Experiment
--------------------------------------

The purpose of the experiment is the determination of neutron and photon spectra
in a neutronic mock-up of the ITER shielding system, irradiated with 14-MeV neutrons.

The same experimental setup used in :ref:`fngblk` was used

Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Neutron and photon spectra were determined in the mock-up on the central
axis of the assembly at two positions:

Position A: Measurement behind the 6 cm thick Perspex layer inside a SS316
            slab, at a total penetration depth 41.5 cm from the front of
            the assembly (Cu 1 cm, SS316 26.08 cm, and Perspex 14.42 cm).

Position B: Measurement in a SS316 layer at the total penetration depth
            87.6 cm from the front of the assembly (Cu 1 cm, SS316 59.82 cm,
            and Perspex 26.78 cm).

The detectors were placed on the axis of the d-beam of the neutron generator.
A NE213 scintillator was employed for simultaneously measuring the neutron
spectra for energies E>1 MeV and the photon spectra for energies E>0.2 MeV.
For each registered event both the pulse-height and a pulse-shape parameter
were recorded to distinguish between neutrons and photons.
Pulse-height distributions from three different hydrogen-filled
proportional detectors, one methane-filled proportional detector and a
stilbene scintillator were used for determining the neutron flux spectra
for energies ranging from 20 keV up to about 3.6 MeV, overlapping
with the NE213 spectra.

.. figure:: /img/benchmarks/TUD-FNG_2.PNG
    :width: 600
    :align: center

    Photo of ITER Bulk Blanket mockup assembly with detectors' positions.

Tallies
^^^^^^^^^^^^^^
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


.. seealso:: **Related papers and contributions:**

    * P. Batistoni, M. Angelone, W. Daenner, U. Fischer, L. Petrizzi, M. Pillon, A. 
      Santamarina, K. Seidel, "Neutronics Shield Experiment for ITER at the 
      Frascati Neutron Generator FNG", 17th Symposium on Fusion Technology, 
      Lisboa, Portugal, September 16-20, 1996.