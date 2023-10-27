TUD Spectra Measurements (FNG Bulk Shield)
------------------------------------------

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
A MCNP model of the experimental assembly with the two detectors has been used, 
with track length flux type 4 tally for both neutron and photons:

Tally n. 504
  This track length flux tally has been used to collect the energy-binned neutron
  fluence at detector position A
Tally n. 514
  This track length flux tally has been used to collect the energy-binned photon
  fluence at detector position A
Tally n. 524
  This track length flux tally has been used to collect the energy-binned neutron
  fluence at detector position B
Tally n. 534
  This track length flux tally has been used to collect the energy-binned photon
  fluence at detector position B

No FM card was used as the experimental results were given per unit source neutron.
During the post-processing the value in each energy bin is divided by the bin width
so that to obtain the spectral fluence to be compared with experimental data from
the detectors.

.. seealso:: **Related papers and contributions:**

    *    M. Martone, M. Angelone, M. Pillon, The 14 MeV Frascati Neutron
         Generator, Journal of Nuclear Materials 212-215 (1994) 1661-1664;
    *    M. Pillon, M. Angelone, A. V. Krasilnikov, 14 MeV Neutron Spectra
         Measurements with 4% Energy Resolution using Type IIa Diamond Detector,
         Nucl. Instr. Meth. in Phys. Res. B101 (1995) 473-485.
    *    H. Freiesleben, W. Hansen, D. Richter, K. Seidel, S. Unholzer, P.
         Batistoni, M. Pillon, M. Angelone, Investigation of Neutron and
         Gamma-ray Spectra in a Blanket Mock-up of the International
         Thermonuclear Experimental Reactor (ITER), Proc. of the 9th Intern.
         Symp. on Reactor Dosimetry, Prague, Czech Republic, 2-6 September
         1996, Editors: H. Ait Abderrahim, P. D'hondt and B. Osmera,
         World Scientific, Singapore, 1998, p. 391-396.
    *    H. Freiesleben, W. Hansen, D. Richter, K. Seidel, S. Unholzer, U.
         Fischer, Y. Wu, M. Angelone, P. Batistoni, M. Pillon,
         Measurement and Analysis of Spectral Neutron and Photon Fluxes in an
         ITER Shield Mock-Up, Fusion Technology 1996, Proc. of the 19th. Symp.
         on Fusion Technology, Lisbon, Portugal, 16-20 September 1996,
         C. Varandas and F. Serra (editors), Elsevier Science B.V., Amsterdam,
         1997, p. 1571-1574.
    *    H. Freiesleben, W. Hansen, D. Richter, K. Seidel, S. Unholzer, U.
         Fischer, Y. Wu, M. Angelone, P. Batistoni, M. Pillon, Measurement
         of Neutron and Gamma Spectral Fluxes in the Shielding Assembly,
         Report TU Dresden, Institut fuer Kern- und Teilchenphysik,
         TUD-IKTP/96-04, November 1996.
    *    H. Freiesleben, W. Hansen, D. Richter, K. Seidel, S. Unholzer, U.
         Fischer, Y. Wu, M. Angelone, P. Batistoni, M. Pillon, Neutron and
         Photon Flux Spectra in a Mock-up of the ITER Shielding System,
         Fusion Engineering and Design 42 (1998), Proc. of the Fourth Intern.
         Symp. on Fusion Nuclear Technology, Tokyo, April 6-11, 1997,
         M.A. Abdou (Ed.), Elsevier Science B.V., Part C, p. 247-253.
    *    U. Fischer, H. Freiesleben, W. Hansen, D. Richter, K. Seidel, S.
         Unholzer, Y. Wu, Test of evaluated data from libraries for fusion
         applications in an ITER shield mock-up experiment, International
         Conference on Nuclear Data for Science and Technology, Trieste,
         May 19-24, 1997, Conference Proceedings Vol. 59, p. 1215-1217,
         G. Reffo, A. Ventura and C. Grandi (Eds.), SIF, Bologna, 1997.
    *    M. Tichy, The DIFBAS Program - Description and User's Guide, Report
         PTB-7.2- 193-1, Braunschweig 1993.
    *    U. Fischer, Y. Wu, W. Hansen, D. Richter, K. Seidel, S. Unholzer,
         Benchmark Analyses for the ITER Bulk Shield Experiment with EFF-3.0,
         -3.1 and FENDL-1, -2 Nuclear Cross-Section Data, IAEA FENDL-2
         Consultants' Meeting, October 12-14, 1998, Vienna.
    *    I. Kodeli, Report on 1999 Activity on ND-1.2.1 (extracts),
         EFF/DOC-698, EFF Meeting, Issy-les-Moulineaux NEA-DB (Nov. 1999)
    *    P. Batistoni, M. Angelone, U. Fischer, H. Freiesleben, W. Hansen,
         M. Pillon, L. Petrizzi, D. Richter, K. Seidel, S. Unterholzer:
         Neutronics Experiment on a Mock-up of the ITER Shielding Blanket at the
         Frascati Neutron Generator, Fusion Engineering Design 47 (1999) 25-60
    *    A. Milocco, The Quality Assessment of the FNG/TUD Benchmark Experiments,
         IJS-DP-10216, April 2009
