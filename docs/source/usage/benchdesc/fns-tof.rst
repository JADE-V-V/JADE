.. _fnstof:
FNS Time-of-Flight Experiment
-----------------------------

Two types of integral experiments for nuclear data benchmark tests with DT 
neutrons have been performed for more than 30 years at JAEA/FNS for the purpose
of validation of nuclear data for fusion reactors materials: an in-situ 
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
The neutron yield at the target was monitored by detecting the 
associated alpha-particles with a silicon surface-barrier detector (SSD) emplaced
in the beam line. 

The detector-collimator system determined the area on the rear surface of slab 
and the solid angle by which the angular neutron flux was defined. The area was 
designed to be about 50 mm in diameter by choosing the sizes of the detector and
the collimator opening. The detector-collimator system was placed on the dual 
rotating deck. The system consisted of an upper and a lower deck to perform the 
experiments on different thick slabs with combination of their rotation. 
The lower deck moves centering around the target (neutron source), and then the 
upper deck rotates slightly relative to the lower deck to adjust the axis to the
measured direction, i.e., the center of rear-face of the slab. 
The detector-collimator axis can be adjusted to any point around the neutron 
source by these two motions. 

.. figure:: /img/benchmarks/FNS-TOF_3.PNG
    :width: 700
    :align: center
    
    Experimental configuration of the TOF experiment and definition of useful parameters

The angular flux measurement is performed in foreground-background mode.
The background is measured by blocking the collimator hole with a plug of type 
304 stainless steel of 0.6 min length and polyethylene of 0.4 min length. 
Background data are subtracted from the foreground data. 
Measured time spectra are then transformed to energy spectra.

The measured data are reduced to the angular flux by the following equation:
 
.. math::
    \Phi(\Omega, E_n) = C(E_n)/(\epsilon(E_n)·A_s·\Delta\Omega·S_n·T(E_n))

where:
  * :math:`\Phi(\Omega, E_n)`: neutrons with energy :math:`E_n` per unit lethargy 
    and emitting solid angle :math:`\Delta\Omega` per unit source neutron at the
    rear surface center of the assembly
  * :math:`C(E_n)`: counts per unit lethargy for neutrons of energy :math:`E_n`
  * :math:`\epsilon(E_n)`:	efficiency of neutron detector at energy :math:`E_n`
  * :math:`\Delta\Omega`: solid angle subtended by the detector to the target, 
    i.e., :math:`\Delta\Omega=A_d/L^2`, where:
    :math:`A_d`: counting area of the detector;
    L:	distance from the target to the detector,
  * :math:`A_s`:	effective measured area defined by the detector collimator system
    on the plane perpendicular to the axis at the assembly surface. It is 
    determined from an experimental detector-collimator response function and
    it is given by the equation: :math:`A_s = 0.2304·L - 84.16`,
    where L is the flight path length in cm
  * :math:`S_n`	total source neutrons obtained by the associated alpha particle monitor,
  * :math:`T(E_n)`: attenuation due to air in neutron flight path:
    :math:`e^{-\Sigma_{air}(E_n)·L}`, :math:`\Sigma_{air}(E_n)` : macroscopic total cross section of air.

The dependence of flight path length on mesuring angle is given in the following
table:

.. figure:: /img/benchmarks/Table.PNG
    :width: 700
    :align: center


MCNP modelling
^^^^^^^^^^^^^^
A point Monte Carlo method is adopted for a nuclear data test, for each tested slab. The point detector
estimator is used and five detector locations are taken into account 
corresponding to the measured angles. The example of calculational model is 
shown in the figure below 

.. figure:: /img/benchmarks/MCNP_FNS_TOF.PNG
    :width: 700
    :align: center
    
    Representation of 3D model for MCNP calculations of FNS-TOF experiment

In this model, the collimator is simulated by cylindrical hole with the radius 
of effective measured area :math:`A_s`. This cylindrical hole is surrounded by 
no-importance regions in which neutron histories are immediately terminated. 


One point detector tally has been used for each detector position:

Tally n. 5
  This detector-flux tally has been used to collect the energy-binned neutron
  leakage flux at 0 degrees
Tally n. 15
  This detector-flux tally has been used to collect the energy-binned neutron
  leakage flux at 12.2 degrees
Tally n. 25
  This detector-flux tally has been used to collect the energy-binned neutron
  leakage flux at 24.9 degrees
Tally n. 35
  This detector-flux tally has been used to collect the energy-binned neutron
  leakage flux at 41.8 degrees
Tally n. 45
  This detector-flux tally has been used to collect the energy-binned neutron
  leakage flux at 66.8 degrees

No FM card was used as the experimental results were given per unit source neutron.
During the post-processing the value in each energy bin is divided by the lethargy bin width.
The calculated leakage lethargy flux are reduced to the measured quantity by multiplying by 
:math:`L^2/A_s` for each detector position.

.. seealso:: **Related papers and contributions:**

    * Oyama, Y., Yamaguchi, S., Maekawa, H., Experimental results of angular neutron flux spectra leaking
      from slabs of fusion reactor candidate materials, I, JAERI-M 90-092, 124p. (1990).
    * Sub Working Group of Fusion Reactor Physics Subcommittee (Ed.), “Collection of Experimental Data
      for Fusion Neutronics Benchmark”, JAERI-M 94-014 (1994) 302p.