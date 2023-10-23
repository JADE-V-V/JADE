FNS Time-of-Flight Experiment
-----------------------------

Two types of integral experiments for nuclear data benchmark tests with DT 
neutrons have been performed for more than 30 years at JAEA/FNS: an in-situ 
experiment and a Time-of-flight (TOF) experiment.

Deuteron beams were accelerated to 350 keV by the 
electrostatic accelerator of the FNS (Fusion Neutronics Source) facility at JAERI
on a tritium-metal targert and 14 MeV neutrons were produced by DT fusion reaction.
In the TOF experiment, an assembly was placed 200 mm from the DT neutron source and 
leakage angular neutron spectra from the assembly above 100 keV were measured at
angles of 0, 12.2, 24.9, 41.8 and 66.8 degrees with the TOF method.

.. figure:: /img/benchmarks/FNS-TOF_1.PNG
    :width: 600
    :align: center

    Experimental configuration of the TOF experiment

Experimental assemblies with different size and materials were used:

.. list-table:: FNS TOF experiment experimental assemblies details
    :header-rows: 1

    * - Material
      - Shape
      - Size
    * - Be
      - Quasi-cylinder
      - 630 mm in effective diameter;
        51, 152 mm in thickness
    * - C
      - Quasi-cylinder
      - 630 mm in effective diameter;
        51, 203, 406 mm in thickness      
    * - Liquid :math:`N_2`
      - Cylinder tank
      - 600 mm in diameter;
        200 mm in thickness
    * - Liquid :math:`O_2`
      - Cylinder tank
      - 600 mm in diameter;
        200 mm in thickness      
    * - Fe
      - Cylinder
      - 1000 mm in diameter;
        50, 200, 400, 600 mm in thickness
    * - Pb
      - Quasi-cylinder
      - 630 mm in effective diameter;
        51, 203, 406 mm in thickness       

Experimental results derived from FNS TOF experiment are publicly accessible at
the `CoNDERC database <https://nds.iaea.org/conderc/shield-fns>`_.



Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Deuteron beams were accelerated to 350 keV and driven towards the target. The 14
MeV DT neutrons were generated at a 3.7x :math:`10^2` GBq (10 Ci) tritium-metal target. 
The tritium was adsorbed in a 40 g/m^2 titanium layer, evaporated on a 1 mm-thick
copper backing. The neutron yield at the target was monitored by detecting the 
associated alpha-particles with a silicon surface-barrier detector (SSD) emplaced
in the beam line. The conversion factor of alpha counts to total neutron. yield 
was calculated from kinematics considering slowing-down of deuterons in the 
titanium-tritium layer. The neutron source spectrum from the target is measured 
and presented as follows:
 
.. math::
    \Psi(\Omega, E_n) = C(E_n)/(\epsilon(E_n)·\Delta\Omega·S_n·T(E_n))

where:
  * :math:`\Psi(\Omega, E_n)`: neutrons with energy :math:`E_n` per unit lethargy 
    and emitting solid angle :math:`\Delta\Omega` per unit source neutron
  * :math:`C(E_n)`: counts per unit lethargy for neutrons of energy :math:`E_n`
  * :math:`\epsilon(E_n)`:	efficiency of neutron detector at energy :math:`E_n`
  * :math:`\Delta\Omega`: solid angle subtended by the detector to the target, 
    i.e., :math:`\Delta\Omega=A_d/L^2`, where:
    :math:`A_d`: counting area of the detector;
    L:	distance from the target to the detector
  * :math:`S_n`	total source neutrons obtained by the associated alpha particle monitor,
  * :math:`T(E_n)`: attenuation due to air in neutron flight path:
    :math:`e^{-\Sigma_{air}(E_n)·L}`, :math:`\Sigma_{air}(E_n)` : macroscopic total cross section of air].



The neutron source for the benchmark experiment is produced by 43 MeV and
68 MeV protons incident on a 99.9 % enriched Li-7 target. The neutrons generated
in the target pass through a 225 cm long iron collimator, placed in a 
thick concrete wall which surrounds the accelerator. 
The neutron source spectra are measured 14 m from the target with an organic
scintillator by the time-of-flight measurement technique and is normalized per 
1 microC of source proton charge.
After the collimator, different shieldings of two different materials - iron and
concrete - are placed. Iron shielding thickness ranges from 0 cm to 130 cm,
while concrete shielding thickness ranged from 0 cm to 200 cm. Additional 
collimators of different thicknesses can be placed before the shielding.
Energy spectra are obtained by unfolding the resulting recoil spectra produced
in a 12.7 cm by 12.7 cm BC 501A scintillator.
Additionally to spectra measurements with the BC 501A scintillator, 
measurements with a series of Bonner sphere counters are performed. On and
off axis measurements of reaction rates are also performed with U-238 fission 
cell and Th-232 fission cell.


MCNP modelling
^^^^^^^^^^^^^^
Because three different types of detectors are used, with different type of 
output data, TIARA benchmark is divided into three separated benchmarks. 
For each detector benchmark, measurements with different neutron source energies,
shielding material, shield thickness and additional collimator thickness are 
made. 
Because TIARA is a deep shielding problem, variance reduction is needed to perform
effective and fast simulations. The variance reduction is performed at the source,
with its geometry being limited to a conical shape, and with energy
dependant weight windows determined by the ADVANTG hybrid deterministic/Monte
Carlo code. The weight windows files can be provided on request.
The three cases with three different detectors were modelled with 3 
different tallies:

BC 501A scintillators:
  The BC 501A liquid scintillator tally is modelled as a F4 volume tally. 
  In MCNP geometry the actual detectors are modelled as a cylinder with a height of h = 12.7 cm 
  and a diameter of d = 12.7 cm. The cylinders are filled with a liquid 
  scintillator material, defined in the technical documentation of the detector,
  and positioned on-axis and/or off-axis, tih offsets of 20 cm and 40 cm,
  depending on the case. The tally results are then normalized according to the
  SINBAD documentation, by a normalization factor calculated with the following
  equation:

  .. math::
    \Phi_{normalized} = \Phi_{MCNP}^{F4}*PtC*PF*4\pi

  Where the factors in the equation are:

  • PtC = Peak to continuum normalization factor (2.17 for the 43 MeV neutron source and 2.61 for the 43 MeV neutron source).
  
  • PF = peak flux of source neutrons which differs from case to case.
  
  • solid angle factor
  
  Finally, tallies are divided into energy bins according to experimental 
  results, for easier comparison with the latters.
  Since experimental results are provided as flux per unit lethargy, tally 
  results are manipulated as follows:

  .. math::
    d\Phi_u = d\Phi/d(\log{E})


Bonner spheres detectors:
  The Bonner sphere detectors are modelled as simple spheres with diameters 
  which correspond to the diameters of the different polyethylene moderators 
  (bare, 15 mm, 30 mm, 50 mm, 90 mm). The F4 tallies have volumes which 
  correspond to the volumes of the spheres. The spheres are filled with air, but 
  the responses are modified with linearly interpolated energy response 
  functions. Then, the result of the tally is multiplied by the same
  normalization factor applied for scintillators.

Fission cells detectors:
  The fission cells are modelled as cylinders (height: h = 10.1 cm, diameter: 
  d = 3.81 cm). The cylinders are filled with air, but the responses are 
  modified with linearly interpolated fission cross sections. Then, the result 
  of the tally is multiplied by the same normalization factor applied for 
  scintillators.


.. seealso:: **Related papers and contributions:**

    * Bor Kos and I. A. Kodeli, "MCNP modelling of the TIARA 
      SINBAD shielding benchmark", September 2018