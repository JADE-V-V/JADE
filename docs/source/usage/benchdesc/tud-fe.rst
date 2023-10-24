TUD Iron Slab Benchmark Experiment
----------------------------------

TUD Iron Slab Benchmark Experiment consists in the determination of spectral 
neutron flux, spectral photon flux and neutron time-of-arrival (TOA) flux 
penetrating and leaking iron slab assemblies (thickness: 30 cm; solid and 
with gap) irradiated with 14 MeV neutrons

Experimental results derived from TUD Iron Slab Benchmark Experiment are available 
in SINBAD database.

Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The neutron source was a 14 MeV d-T neutron generator operated in pulsed
mode. The time distribution of the source neutrons was proportional to
:math:`exp[-(t/1.4 ns)^2]`.
The Fe slabs had a front area of 100 cm x 100 cm and a thickness of 30 cm
and were built up by bricks with dimensions of 20 cm x 10 cm x 5 cm.
Three assemblies were built up:
A0 - no gap,
A1 - vertical gap, distance: 10 cm from the centre, gap width: 5 cm, and
A2 - vertical gap, distance: 20 cm from the centre, gap width: 5 cm.
The three configurations are shown in the figure below:

.. figure:: /img/benchmarks/TUD-Fe_1.PNG
  :align: center
  :width: 600

  Geometries A0, A1, A2

The distance between neutron source and Fe slab was 19 cm. The distance
between Fe slab and detector was 300 cm. The distance between neutron
source and detector was 349 cm.
The angle between the d-beam of the neutron generator and an axis
crossing neutron source and centre of the slab was 74 degrees.
The detectors were positioned in a collimator shaped in such a way that
all neutrons and photons leaking from the slab in direction of the
detector could be observed.

A NE213 scintillator was employed for simultaneously measuring the
spectral neutron flux, the spectral photon flux, and the neutron time-
of-arrival spectrum for neutron energies of E>1 MeV and photon energies
of E>0.2 MeV. For each registered event the pulse-height, the
time-of-arrival, and a pulse-shape parameter were recorded to distinguish
between neutrons and photons.
Pulse-height distributions from three different hydrogen-filled
proportional detectors and a stilbene scintillator were used for
determining the neutron flux spectra for energies ranging from 30 keV
up to about 2.3 MeV, overlapping with the NE213 spectra.


MCNP modelling
^^^^^^^^^^^^^^
3 MCNP models corresponding to A0, A1 and A2 geometries were employed.
Point-flux-detectors for neutrons and photons were 
used as detector tallies in the locations corresponding to the detectors in the experiment:

Tally n. 5
    Neutron fluence (binned in energy groups)
Tally n. 15
    Neutron fluence (binned in time groups)
    For comparison with the experimental time-of-arrival spectrum, the
    calculated neutron fluence PHI(t,E) was folded with the neutron detection
    efficiency EPS(E) (DE/DF MCNP cards) of the NE213 detector in accordance with the
    measurement.

No FM card was used as the experimental results were given per unit source neutron.
During the post-processing the value of the fluence in each energy bin is divided by the bin width
so that to obtain the spectral fluence [#/cm^2/MeV/n] and spectral time-of-arrival fluence
[#/cm^2/shakes/n] to be compared with experimental data from
the detectors.

.. figure:: /img/benchmarks/TUD-Fe_2.PNG
    :align: center
    :width: 600

    Neutron detection efficiency of NE213 detector

Tally n. 25
    Photon spectral fluence [#/cm^2/MeV/n] (binned in energy groups)

.. seealso:: **Related papers and contributions:**

    * H. Freiesleben, W. Hansen, H. Klein, T. Novotny, D. Richter, R.
         Schwierz, K. Seidel, M. Tichy, S. Unholzer, Experimental results of
         an iron slab benchmark, Report Technische Universitaet Dresden,
         TUD-PHY-94/2, February 1995
    * H. Freiesleben, W. Hansen, D. Richter, K. Seidel, S. Unholzer,
         Experimental investigation of neutron and photon penetration and
         streaming through iron assemblies, Fusion Engineering and Design 28
         (1995) 545-550
    * H. Freiesleben, W. Hansen, D. Richter, K. Seidel, S. Unholzer,
         Shield Penetration Experiments, Report Technische Universitaet
         Dresden, Institut fuer Kern- und Teilchenphysik, TUD-IKTP-95/01,
         January 1995
    * H. Freiesleben, W. Hansen, D. Richter, K. Seidel, S. Unholzer,
         TUD experimental benchmarks of Fe nuclear data, Fusion Engineering
         and Design 37 (1997) 31-37
    * U. Fischer, H. Freiesleben, H. Klein, W. Mannhardt, D. Richter,
         D. Schmidt, K. Seidel, S. Tagesen, H. Tsige-Tamirat, S. Unholzer,
         H. Vonach, Y. Wu, Application of improved neutron cross-section data
         for Fe-56 to an integral fusion neutronics experiment, Int. Conf. on
         Nuclear Data for Science and Technology, Trieste (Italy), May 19-24,
         1997
    * M. Tichy, The DIFBAS Program - Description and User's Guide, Report
         PTB-7.2- 193-1, Braunschweig 1993
    * S. Guldbakke, H. Klein, A. Meister, J. Pulpan, U. Scheler, M. Tichy,
         S. Unholzer, Response Matrices of NE213 Scintillation Detectors for
         Neutrons, Reactor Dosimetry ASTM STP 1228, Ed. H. Farrar et al.,
         American Society for Testing Materials, Philadelphia, 1995, p. 310-322
    * L. Buermann, S. Ding, S. Guldbakke, S. Klein, H. Novotny, M. Tichy,
         Response of NE213 Liquid Scintillation Detectors to High-Energy
         Photons, Nucl. Instr. Methods A 332(1993)483
    * J. F. Briesmeister (Ed.), MCNP - A general Monte Carlo n-particle
         transport code, version 4A, Report, Los Alamos National Laboratory,
         LA-12625-M, November 1993
    * S. Ganesan and P. K. McLaughlin, FENDL/E - evaluated nuclear data
         library of neutron interaction cross-sections and photon production
         cross-sections and photon-atom interaction cross-sections for fusion
         applications, version 1.0, Report IAEA-NDS-128, Vienna, May 1994
    * J. Kopecky, H. Gruppelaar, H.A.J. Vanderkamp and D. Nierop,
         European Fusion File, Version-2, EFF-2, Final report on basic data
         files, Report, ECN-C-92-036, Petten, June 1992.
    * Y. Wu, Report FZKA-5953, Karlsruhe, 1997
    * A. Milocco, The Quality Assessment of the FNG/TUD Benchmark Experiments,
         IJS-DP-10216, April 2009