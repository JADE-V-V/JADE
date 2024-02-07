.. _aspispca:

Winfrith Water/Iron Benchmark Experiment (ASPIS-PCA-Replica)
------------------------------------------------------------

This experiment is part of the SINBAD database (`NEA-1517/104 <https://www.oecd-nea.org/science/wprs/shielding/sinbad/repl-abs.htm>`_). 
Users will need to show proof of licence and request the required input files to use this 
benchmark in JADE.

The experiment was designed to replicate the Oak Ridge Pool Critical Assembly (PCA) experiment with a highly enriched fission plate in 
place of the core source. Neutron spectra and reaction rate measurements were recorded through a water/iron shield as a model of the ex-core 
region of a pressurised water reactor (PWR). The experiment was performed in the early 1980's. 

Geometry 
^^^^^^^^

ASPIS occupies one of the four experimental caves on the NESTOR reactor as seen in the figure below with the iron/water assembly 
immersed in water within the shielding trolley. Further description of ASPIS and NESTOR is given :ref:`aspisfe88`. 

.. figure:: /img/benchmarks/ASPIS_pca_replica_NESTOR.JPG
    :width: 500
    :align: center

    View of the NESTOR reactor and ASPIS shield trolley in one of the four experimental caves. [:ref:`Reference 1 <referencesPCA>`]

.. figure:: /img/benchmarks/ASPIS_pca_replica_trolley.JPG
    :width: 500
    :align: center

    The ASPIS shield trolley containing the PCA replica experiment. [:ref:`Reference 1 <referencesPCA>`]

The shield assembly consists of layers of mild steel representing a PWR thermal shield and pressure vessel. Different zones are defined
through the different layers as reference for different material and detector locations as seen below.

.. figure:: /img/benchmarks/ASPIS_pca_replica_shield.JPG
    :width: 500
    :align: center

    Shielding assembly in ASPIS PCA replica. [:ref:`Reference 2 <referencesPCA>`]

The layers are comprised of the following:

* Planar neutron source (fission plate)
* Water gap (12 cm)
* Thermal shield sample (6 cm)
* Water gap (12 cm)
* Pressure vessel sample (22 cm)
* Void box
* Water pool

Measured data
^^^^^^^^^^^^^

Through the shield assembly illustrated above, activation foils were position at 10 different positions. The neutron flux was measured in
the energy range 1 to 10 MeV using NE213 organic scintillators and at lower energy with hydrogen filled proportional counters. T/4 and 3T/4
refer to different thicknesses of the pressure vessel, T. 

* **Reaction rates**: *103Rh(n,n')* at 1.91, 7.41, 12.41, 14.01, 19.91, 25.41, 30.41, 39.01 (T/4), 49.61 (3T/4) and 58.61 cm (rear void box). 
  *115In(n,n')* and *32S(n,p)* reaction rates were also measured at T/4, 3T/4 and in the void box.  
* **Neutron Spectra**: Spectral measurements were made at two locations, T/4 (position 8) and in the rear void box (position 10). The spectra 
  have been unfolded using the RADAK code for comparison to simulation. 

MCNP model
^^^^^^^^^^

The source term is included as an SDEF. A weight window produced using the DSA Technique is also included in the input file. 

All modifications necessary to the distributed input file are captured in a patch file.

S(:math:`{\alpha}`, :math:`{\beta}`) thermal treatment for graphite and water is required. The user should make sure these cross sections are available and if required
update the identifier on the *MTm* cards in the input file. 

MCNP tallies
^^^^^^^^^^^^^^

The reaction rates are calculated using the F4 tally in MCNP (*Tally n.4*). A tally multiplier has been applied to give results directly
comparable to the experimental data. 
 
The reaction *MT* numbers are by default assigned using the `convention for IRDFF-II <https://www-nds.iaea.org/IRDFF/IRDFF-II_ACE-LST.pdf>`_. 

The spectra have been calculated with an F4 tally with energy binning for comparison to the measured data. A multiplier is included using
the *FM* card (n/sec/NESTOR Watt) which following post processing performed by JADE to bin per unit lethargy, can be directly compared to 
the measured data. 

Patch file
^^^^^^^^^^
Coming soon... 

.. _referencesPCA:
.. seealso:: **Related papers and contributions:**

    #. Butler, J., Carter, M.D., Curl, I.J., March, M.R., McCracken, A.K., Murphy, M.F., Packwood, A., The PCA Replica Experiment PART I, Winfrith Measurements and Calculations, AEEW-R 1736, 1984
    #. Kodeli, I., van der Marck, S., Consistency Among the Results of the ASPIS Iron88, PCA Replica, and PCA ORNL Benchmark Experiments, Nuclear Science and Engineering, https://doi.org/10.1080/00295639.2023.2199673, 2023.
    #. Burn, K.W., Consul Camprini, P., Calculation of the NEA-SINBAD Experimental Benchmark: PCA-Replica, https://hdl.handle.net/20.500.12079/7957, 2017.