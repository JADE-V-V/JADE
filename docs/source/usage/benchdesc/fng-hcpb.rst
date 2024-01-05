.. _fnghcpb:

FNG Helium Cooled Pebble Bed (HCPB) Tritium Breeder Module (TBM) Mock-up
------------------------------------------------------------------------

This experiment is part of the SINBAD database (`NEA-1553/71 <hhttps://www.oecd-nea.org/science/wprs/shielding/sinbad/fng_hcpb/fnghcpb-a.htm>`_). 
Users will need to show proof of licence and request the required input files to use this 
benchamark in JADE.

The purpose of this experiment was to validate transport through a mockup of the Helium 
Cooled Pebble Bed (HCPB) blanket concept. This is one of the concepts anticipated for 
the ITER test blanket module (TBM) programme and in future fusion power plants. The accurate
prediction of the tritium production, one of the primary functions of the blanket is therefore 
very important. The experiment was carried out at the FNG facility, described in :ref:`fngsddr`,
in 2005.

Geometry 
^^^^^^^^

The geoemtry of the mockup has external dimensions of 31.0 cm x 29.0 cm x 30.9 cm. The bulk of the 
geometry consists of beryllium with two layers symmetric across the central plane consisting of 
Li2CO3 containing natural Li. Stacks of 12 pellets of Li2C03 encased in Al were assemebled for measuring
the tritium production rate. At the rear is a steel box filled with Li2CO3. 

.. figure:: /img/benchmarks/fng-hcpb.jpg
    :width: 500
    :align: center

    Layout of the FNG-HCPB experiment.

Measured data
^^^^^^^^^^^^^

Activation foils were placed at increasing distance from the source through the centre of the
geometry to measure reaction rates. The tritium production rate was measured at four different 
depths a the locations of each of the pellet stacks above and below the central axis. 

* **Reaction rates**: 197Au(n,g), 58Ni(n,g), 27Al(n,a), 93Nb(n,2n) at depths of 4.055 cm, 10.355 cm, 
  16.655 cm and 22.955 cm from the block surface. There is an additional measurement at depth 0 cm 
  for 93Nb(n,2n). 
* **Tritium Activity**: Measured for each of the stacks of 12 pellets as shown in the above Figure. The 
  tritium specific activity is available in units of Bq/g.

MCNP model
^^^^^^^^^^

A single MCNP geometry is used for calculating the reaction rates and tritium activity. The 
most recently developed SDEF source from ENEA has been used and a weight window
is included in the input file. 

All modifications necessary to the distributed input file are captured in a patch file.

MCNP tallies
^^^^^^^^^^^^^^

The reaction rates are calculated using the F4 tally in MCNP and can be directly compared to 
the experimental data set which are presented per source neutron. Tally n.4 is used in all cases. 
The reaction MT numbers are by default assigned using the `convention for IRDFF-II <https://www-nds.iaea.org/IRDFF/IRDFF-II_ACE-LST.pdf>`_. 
The raw output from MCNP can be compared directly the reported measured data.

The tritium production is tallied for 6Li and 7Li using the reaction MT number 205 for total 
triton production. No energy binning is required. The specific activitiy is then calculated as:

.. math::
    Specific \; activity (Bq/g) = (MCNP\_result (RR) \times \lambda (s^{-1}) \times n_{tot})/ mass (g)

where :math:`{\lambda}` is the decay constant, :math:`n_{tot}` is the total neutron production and the 
mass is for an individual pellet. 

Patch file
^^^^^^^^^^
Coming soon... 

.. seealso:: **Related papers and contributions:**

    * Batistoni, P., Villari, R., TBM - HCPB Neutronics Experiments: Comparisonand Check Consistency among Results Obtained by the Different Teams Implications for ITER TBM Nuclear Design and Final Assessment, FUS-TEC–MA–NE-R-019, ENEA, Dec. 2006.
    * Batistoni, P., Carconi, P., Villari, R., Angelone, M., Pillon, M., Zappa, G., Measurements and Analysis of Tritium Production Rate (TPR) in Ceramic Breeder and of Neutron Flux by Activation Rates in Beryllium in TBM Mock-up, FUS-TEC-MA-NE-R-014, Dec. 2005