.. _tiara:
Tiara
--------

The TIARA (Takasaki Ion Accelerator for Advanced Radiation Application) 
shielding experiment is one among the several high quality experiments included in the
SINBAD database.
Like :ref:`oktavian` benchmark, experimental results derived from Tiara experiments are publicly accessible at
the `CoNDERC database <https://www-nds.iaea.org/conderc/oktavian>`_.

The shielding experiment was performed at JAERI (Japan Atomic Energy Research 
Institute). The neutron source was produced by bombarding a 99.9% Li-7 target 
with a high energy proton beam from a cyclotron. Two quasi-monoenergetic neutron
sources resulted from the bombardment, with peak energies at 43 MeV and 68 MeV. 
Three different detectors were used to collect data: the BC 501A liquid
scintillation detector, a series of Bonner sphere detectors and finally U-238 
and Th-232 fission cells to measure the reaction rates.



Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /img/benchmarks/Tiara.jpg
    :width: 500
    :align: center

    CAD model of Tiara Experiment. Dimensions in cm.

 
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