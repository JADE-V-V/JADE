.. _fngss:

FNG Stainless Steel (FNG SS)
-----------------------------

This experiment is part of the SINBAD database (`NEA-1553/57 <https://www.oecd-nea.org/science/wprs/shielding/sinbad/FNG_SS/FNGSS_A.HTM>`_). 
Users will need to show proof of licence and request the required input files to use this 
benchmark in JADE.

The purpose of this benchmark was to improve understanding of neutron transport in
structural materials, specifically, stainless steel. This is a common material for many
components in a fusion device. The experiment was carried out at the FNG facility, described
in :ref:`fngsddr`, in 1989.

Geometry 
^^^^^^^^

A block of AISI 316 type stainless steel measuring 100 cm x 100 cm x 70 cm was placed 5.3 cm
from the FNG source. The assembly can be seen below.

.. figure:: /img/benchmarks/fng-ss.jpg
    :width: 450
    :align: center

    Layout of FNG-SS experiment. [:ref:`Reference 1 <referencesfngss>`]

Measured data
^^^^^^^^^^^^^

Activation foils were placed at different depths through the stainless steel. Only foils of the
same material were irradiation in a single irradiation.  Foil activities were then determined 
using HPGe detectors and standard radiometric techniques. 

* **Reaction rates**: *58Ni(n,p)*, *27Al(n,a)*, *56Fe(n,p)*, *115In(n,n')* at depths of 4.95, 10.05,
  20.15, 30.30, 40.50, 50.70 and 60.90 cm. *197Au(n,g)*, *55Mn(n,g)* were measured at
  5.0, 10.0, 20.0, 30.0, 40.0, 50.0 and 60.0 cm. *58Ni(n,2n)* was measured at 4.95,
  10.05, 20.15 and 30.30 cm. All measurements are from the front surface of the assembly. 


MCNP model
^^^^^^^^^^

The MCNP model includes the source, SS assembly and shielding wall around the facility. Different
foils have different thicknesses which also varies with depth therefore 7 independent MCNP models were
created for calculating each of the reactions above. 

The ENEA SDEF source has been included as for FNG SiC and FNG HCPB models in JADE. No variance reduction 
is used in this benchmark. 

Further modifications necessary to the distributed input file are captured in the patch file.

MCNP tallies
^^^^^^^^^^^^^^

Reaction rates for each of the different foils in the experiment have been calculated using an *F4* tally.
*Tally n.4* is used in all cases. The reaction *MT* numbers are by default assigned using the `convention for IRDFF-II <https://www-nds.iaea.org/IRDFF/IRDFF-II_ACE-LST.pdf>`_. 
The raw output from MCNP can be compared directly the reported measured data available in SINBAD which is given 
in units of 10\ :sup:`24`/(source neutron). 

Patch file
^^^^^^^^^^
Coming soon... 

.. _referencesfngss:
.. seealso:: **Related papers and contributions:**

    #. Martone, M., Angelone, M., Batistoni, P., Pillon, M., Rado, V., FENDL Neutronics Benchmark: Stainless Steel Bulk Shield Experiment Perfomed at Frascati Neutron Generator, INDC(NDS)-315, 1994. 