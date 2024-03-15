FNG/TUD Tungsten Experiment
---------------------------

The purpose of the experiment is transport data benchmark by determination of spectral neutron flux and
spectral photon flux at four positions in a thick block of W irradiated
with 14 MeV neutrons.

The same experimental setup used in :ref:`fngw` was used

Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Neutron and photon flux spectra were measured on the central axis of
the assembly in four positions (P1,...,P4) at z = 5, 15, 25 and 35 cm:

.. figure:: /img/benchmarks/TUD-W_2.PNG
    :width: 600
    :align: center

Neutron and photon pulse-height spectra were measured simultaneously
using an NE 213 scintillation spectrometer. The dimensions of the
cylindrical active volume of the detector were 3.8 cm in both height
and diameter. Its material had a mass density of 0.874 g/cm3 and an
elemental composition of 54.8 at-% H and 45.2 at-% C.
The scintillator was coupled to a photomultiplier by means of a 50 cm
long light guide. When the detector was located at one of the
positions, the other ones were filled with rods of W
alloy.



Tallies
^^^^^^^^^^^^^^
The calculations were performed taking into account the precise geometry of
the mock-up as well as the complete surroundings, to model correctly each 
measurement 4 MCNP inputs were used, with two tallies each at detector position
for neutron and photon flux (energy-binned):

Tally n. 4
  This track length flux tally has been used to collect the energy-binned neutron
  fluence
Tally n. 14
  This track length flux tally has been used to collect the energy-binned photon
  fluence

No FM card was used as the experimental results were given per unit source neutron.
During the post-processing the value in each energy bin is divided by the bin width
so that to obtain the spectral fluence to be compared with experimental data from
the detectors.

.. seealso:: **Related papers and contributions:**

    *   M. Angelone, M. Pillon, P. Batistoni, M. Martini, M. Martone, V.
        Rado, "Absolute experimental and numerical calibration of the 14
        MeV neutron source at the Frascati Neutron Generator", Rev. Sci.
        Instr. 67(1996)2189.
    *   H. Freiesleben, C. Negoita, K. Seidel, S. Unholzer, U. Fischer, D.
        Leichtle, M. Angelone, P. Batistoni, M. Pillon, "Measurement and
        analysis of neutron and gamma-ray flux spectra in Tungsten",
        Report TUD-IKTP/01-03, Dresden, EFFDOC-857 (2003)
    *   U. Fischer et al., Monte Carlo Transport and Sensitivity Analyses
        for the TUD Neutron Transport Benchmark Experiment on Tungsten,
        EFFDOC-860 (2002)
    *   A. Milocco, The Quality Assessment of the FNG/TUD Benchmark Experiments,
        IJS-DP-10216, April 2009
