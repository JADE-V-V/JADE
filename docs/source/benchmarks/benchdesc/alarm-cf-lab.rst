(ALARM-CF-LAB) Concrete Labyrinth Benchmark Experiment
------------------------------------------------------------------

.. include:: /documentation/benchdesc/icbep_disclaimer.rst

The ICSBEP ALARM-CF-AIR-LAB is an experiment that was performed at the Institute of High Energy Physics of Protvino in 1982.
It consisted of a three-section concrete labyrinth with a 252Cf spontaneous decay neutron source at its doorway aperture.

Neutron count rates were measured by the Bonner sphere method at different points inside each section of the labyrinth. The influence 
of different coverings of the labyrinth concrete wall on the neutron flux in remote sections of the labyrinth was investigated. Six different 
labyrinth geometric configurations were studied:

1. Base case, completely bare concrete walls.
2. First corner of the labyrinth covered with a 6.1 cm thick layer of polyethylene and, on top, a 0.08 cm thick layer of cadmium.
3. First corner of the labyrinth covered with a 6.1 cm thick layer of polyethylene.
4. First and second corners of the labyrinth covered with a 10 cm thick layer of borated concrete.
5. Two 6.1 cm thick polyethylene plates are added perpendicularly to the second section of the labyrinth.
6. Addition of a dead end at the end of the first section of the labyrinth, two new Bonner spheres added in the dead end, and completely bare walls throughout all the labyrinth.

Configurations 1-5 included 10 Bonner Spheres along the labyrinth, while Case 6 introduced a modification to the geometry of the 
labyrinth and 2 additional detectors.

Each labyrinth geometric configuration was tested with “unfiltered” radiation from the bare source (case A) and with “filtered” radiation from the source 
surrounded by a 30.5-cm-diameter polyethylene sphere with a 4-cm-diameter spherical central cavity (case B).

From all described cases, only the following are included in JADE:

.. list-table::
   :widths: 20 35 20
   :header-rows: 1
   :align: center
   :class: center-table

   * - Labyrinth case
     - Labyrinth geometric configuration
     - Source
   * - Case 1A
     - 1
     - Unfiltered
   * - Case 1B
     - 1
     - Filtered
   * - Case 2A
     - 2
     - Unfiltered
   * - Case 2B
     - 2
     - Filtered
   * - Case 3A
     - 3
     - Unfiltered
   * - Case 3B
     - 3
     - Filtered
   * - Case 4A
     - 4
     - Unfiltered
   * - Case 4B
     - 4
     - Filtered
   * - Case 5A
     - 5
     - Unfiltered

Each labyrinth case constitutes a different computational model with its own geometry and materials. 
Therefore, 9 different sub-runs are included in this JADE benchmark.

Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. figure:: /img/benchmarks/alarm-cf-lab.png
    :width: 1100
    :align: center
    
    Computational model z-plane plots for different labyrinth geometric configurations

The labyrinth was built in an open place. Sand with thickness larger than 20 cm served as the primary
foundation. On top of the sand, 18-cm-thick steel-reinforced concrete plates, normally used for
roads, were laid. A 15-cm compact layer of special concrete was spread over the plates. Walls and
ceiling of the labyrinth were constructed from blocks of the same concrete. The total length of the 
labyrinth was 12.8 m and its total width was 7.2 m.

Measurements of the neutron fields in the labyrinth were made by Bonner spheres. The set
comprised six spheres with nominal diameters of 2, 3, 5, 8, 10, and 12 inches (reported diameters of
5.08 cm, 7.62 cm, 12.70 cm, 20.31 cm, 25.39 cm, and 30.47 cm). A 6LiI(Eu) crystal 1 cm in diameter and 
1 cm high was used as the thermal neutron detector.

The Bonner Sphere detectors were not explicitly modelled in the computational geometries. Instead, 
neutron flux was tallied at the detector locations and multiplied by the detectors' response functions 
to obtain the corresponding count rates:

.. math::
    N_{k,i}^{m} = S \cdot \sum_{g=1}^{30} \Phi_{k,g}^{i} r_{i,g'}

Where *N* is the count rate, *S* is the source intensity, *i* is the Bonner Sphere detector index, 
*m* is the case, *k* is the detector position, *g* is the energy bin, :math:`\Phi` is the neutron flux,
and *r* is the response function value.

While the importance-based variance reduction defined in the original ICSBEP benchmark inputs was used in MCNP, 
a set of mesh-based weight windows were developed for the OpenMC models employing the MAGIC method.

:math:`S(\alpha,\beta)` tables (thermal neutron scattering data) for hydrogen in polyethylene were used for
both codes (MCNP and OpenMC) for all labyrinth cases containing polyethylene.

Tallies
^^^^^^^
Three different magnitudes were tallied in MCNP and OpenMC calculations: neutron flux, neutron count rates, 
and the 1MeV Si equivalent fluence.

Accordingly, the following tallies were defined for each input:

Tally n. 4
  Neutron flux spectra at each detector position, units [:math:`n/cm^2`]
Tally n. 14
  Total neutron flux (no energy binning) at each detector position, units [:math:`n/cm^2`]
Tally n. 24
  Neutron count rates for the 2" Bonner Sphere detectors at each detector position, units [:math:`pulses/s`]
  Neutron flux was tallied and multiplied by the response function of the 2" Bonner Sphere detector using 
  an EM card in the case of MCNP and an *EnergyFunctionFilter()* in the case of OpenMC.
Tally n. 34
  Neutron count rates for the 3" Bonner Sphere detectors at each detector position, units [:math:`pulses/s`]
  Neutron flux was tallied and multiplied by the response function of the 3" Bonner Sphere detector using 
  an EM card in the case of MCNP and an *EnergyFunctionFilter()* in the case of OpenMC.
Tally n. 44
  Neutron count rates for the 5" Bonner Sphere detectors at each detector position, units [:math:`pulses/s`]
  Neutron flux was tallied and multiplied by the response function of the 5" Bonner Sphere detector using 
  an EM card in the case of MCNP and an *EnergyFunctionFilter()* in the case of OpenMC.
Tally n. 54
  Neutron count rates for the 5" Bonner Sphere (without Cd) detectors at each detector position, units [:math:`pulses/s`]
  Neutron flux was tallied and multiplied by the response function of the 5" Bonner Sphere (without Cd) detector using 
  an EM card in the case of MCNP and an *EnergyFunctionFilter()* in the case of OpenMC.
Tally n. 64
  Neutron count rates for the 8" Bonner Sphere detectors at each detector position, units [:math:`pulses/s`]
  Neutron flux was tallied and multiplied by the response function of the 8" Bonner Sphere detector using 
  an EM card in the case of MCNP and an *EnergyFunctionFilter()* in the case of OpenMC.
Tally n. 74
  Neutron count rates for the 10" Bonner Sphere detectors at each detector position, units [:math:`pulses/s`]
  Neutron flux was tallied and multiplied by the response function of the 10" Bonner Sphere detector using 
  an EM card in the case of MCNP and an *EnergyFunctionFilter()* in the case of OpenMC.
Tally n. 84
  Neutron count rates for the 12" Bonner Sphere detectors at each detector position, units [:math:`pulses/s`]
  Neutron flux was tallied and multiplied by the response function of the 12" Bonner Sphere detector using 
  an EM card in the case of MCNP and an *EnergyFunctionFilter()* in the case of OpenMC.
Tally n. 94
  1MeV Si equivalent fluence at each detector position, units [:math:`1/cm^2/source\ neutron`]

.. seealso:: **Related papers and contributions:**

    * 1.	Nikolaev, M., et al. Neutron Fields in Three-Section Concrete Labyrinth from Cf-252 Source, 
      ALARM-CF-AIR-LAB-001 in International Handbook of Evaluated Criticality Safety Benchmark Experiments. 
      Paris : NEA, OECD Nuclear Energy Agency, 2005.