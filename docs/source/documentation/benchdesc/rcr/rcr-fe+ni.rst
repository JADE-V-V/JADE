(RCR-Fe+Ni) RCR Iron/Nickel Sphere Experiment with 252Cf source
------------------------------------------------------------------

.. include:: /documentation/benchdesc/icbep_disclaimer.rst

This benchmark was designed to evaluate fast neutron leakage spectra and neutron activation 
from an Iron and Nickel sphere of 50cm of diameter and with a 252Cf (spontaneous fission) 
neutron source placed in its centre. The experimental measurements were carried out in 2021 
at the Neutron Source Laboratory (NSL) in the Research Centre Řež (RCR, Centrum Výzkumu Řež) 
by the proton recoil method and by evaluating the reaction rates in irradiated activation foils. 

The experiment is identified as ALARM-CF-Fe-SHIELD-002 in the ICSBEP database. 

Benchmark structure
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The benchmark is organized into two single experimental case which just differs by the sphere material. 

**Material** 
    * Case-1: Iron 
    * Case-2: Nickel
**Objective**
    #. measure the direct fast neutron leakage and its energy spectrum from the Fe sphere. 
    #. measure the spatial distribution of neutron-induced reaction rates on the surface of the sphere. 
**Method**
    #. Proton recoil method using hydrogen proportional counters (HPD, 0.1-1.3 MeV neutrons) and a stilbene 
    scintillation detector for 0.8-12 MeV neutrons, with digital pulse shape discrimination for neutron/gamma separation. 
    #. Activation foils (58Ni(n, p)58Co, 115In(n, n')115m1) are placed at defined positions on the sphere surface and 
    irradiated during the neutron leakage measurements. 

Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**Sphere dimensions and materials**
    * Case-1: 50 cm Fe sphere
    * Case-2: 50 cm Ni Sphere
**Density**
    * Case-1 Iron sphere: 7.85 :math:`g/cm^3`
    * Case-2 Nickel sphere: 8.89 :math:`g/cm^3`
**Material**
    Composition determined by XRF analysis:
    * Case-1 Iron sphere: Fe 99.737%, Mn 0.075%, P 0. 025%, C 0.04%, S 0.026%, Al 0.005%, Mo 0. 01%, Cr 0.02%, Cu 0.062%. 
    * Case-2 Nickel sphere: Ni 99.631%, Mo 0.007%, Fe 0.21%, W 8.45E-05%, Al 0.102%, Gd 7.40E-07%, Cr 0.022%, B 5.00E-06%, 
    Mn 0.019%, Cd 8.32E-06%, Cu 0.01%.
**Source**
    252Cf oxide in a palladium matrix, encapsulated in double stainless-steel cladding.
**Source position**
    Geometric center of the sphere, placed in a 2.6 cm diameter, 28 cm deep hole drilled in a central 3 cm thick plate.
**Experimental hall**
    Room dimensions :math:`7.24\,\mathrm{m} \times 6.5\,\mathrm{m} \times 7.2\,\mathrm{m}` (height), sphere center 
    2 m above floor.
**Set-up of case**
    It contains only the activation foils on the outside the Fe sphere (on the surface) and the neutron detectors at 
    1 m from the sphere center. 

.. figure:: /img/benchmarks/RCR-Fe+Ni_1.png
    :width: 600
    :align: center

    Figure 1. Scheme of Iron/Nickel Sphere - Side View. Dimensions in cm.

.. figure:: /img/benchmarks/RCR-Fe+Ni_2.png
    :width: 600
    :align: center

    Figure 2. Photo of Iron Sphere with Shadow Cone and Stilbene Detector.

MCNP modelling
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Two independent MCNP inputs are employed, one for each case, just with different sphere material and with the hereinafter 
described tallies: 

*Detector tallies, Fn5 MCNP type* 
    Two detector-flux tallies have been used to collect the energy-binned neutron spectra at the same detector position 
    with a course energy binning (F5, for the Stilbene detector) and a finer one (F15 for the hydrogen proportional 
    counters, HPD) which matches the measurement performed. 
*Track length flux tallies, Fn4 MCNP type*
    A track length flux tally has been used to collect results in the cells corresponding to the activation foils in MCNP 
    geometry. The tally has been multiplied in each input (with FM card) by the appropriate microscopic reaction cross 
    section, to obtain results in terms of number of reactions per unit neutron from the source. Energy binning was applied 
    to half of the tallies, while the other half recorded the total reaction rate in the same cells (see table below). Nuclear 
    data for tally collection was taken from IRDFF-II dosimetry libraries and experimental values averaged when multiplies 
    values where present. In the following, a list of the reactions considered for each activation foil material is reported: 

.. list-table:: Tally Details
   :header-rows: 1
   :widths: 10 25 25 10

   * - Tally No.
     - Where
     - Foils Reactions
     - Energy binned
   * - 4
     - Outer sphere surface
     - 58Ni(n,p)58Co
     - Yes
   * - 14
     - Outer sphere surface
     - 115In(n,n')115m1 In
     - Yes
   * - 24
     - Outer sphere surface
     - 58Ni(n,p)58Co
     - No
   * - 34
     - Outer sphere surface
     - 115In(n,n')115m1 In
     - No

Implemented broadening on Monte Carlo computed results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Following the ICSBEP documentation, MCNP neutron spectra are broadened with a Gaussian function using a constant 10% FWHM 
for all energy ranges for the hydrogen proportional counters while as per the table below for the stilbene scintillation detector. 

.. list-table:: Energy Resolution of the Stilbene Detector for Neutron Spectra Measurement 
   :header-rows: 1
   :widths: 15 15

   * - Elow (MeV)
     - FWHM (%)
   * - 17.02
     - 1
   * - 15.05
     - 1.35
   * - 13.63
     - 1.65
   * - 12.5
     - 1.92
   * - 11.42
     - 2.23
   * - 11.02
     - 2.35
   * - 10.97
     - 2.37
   * - 10.67
     - 2.47
   * - 9.96
     - 2.73
   * - 9.3
     - 3.01
   * - 8.05
     - 3.68
   * - 6.59
     - 4.97
   * - 5.91
     - 6.07
   * - 5.46
     - 7.41
   * - 5.25
     - 8.61
   * - 5.13
     - 10

.. seealso:: **Related papers and contributions:**

    * ICSBEP, NEA/NSC/DOC/(95)03/VIII, Volume VIII, ALARM-CF-Fe-SHIELD-002. 
    * https://www-nds.iaea.org/INDEN/  
    * M. Schulc et al., "Measuring neutron leakage spectra using spherical benchmarks with 252Cf source in its centers",
      Nucl. Instrum. Methods Phys. Res. A 914 (2019) 53-56. 
    * M. Schulc et al., "Application of 252Cf neutron source for precise nuclear data experiments", Appl. Radiat. 
      Isot. 151 (2019) 187-195. 