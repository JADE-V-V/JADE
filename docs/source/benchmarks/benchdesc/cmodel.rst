C-Model
-------

.. important::

    This benchmark input cannot be distributed directly with JADE. The user must request to obtain it
    from ITER organization.

During the long life of the ITER project, many neutronics models have been generated to represent the
TOKAMAK machine. These are used to conduct neutronic analyses on the reactor in order to investigate
many direct and indirect effects induced by neutrons like heat generation, particle generation, DPA,
dose rate, etc. C-Model is an extremely detailed MCNP input of a 40° sector of ITER TOKAMAK. It was
the most complete neutronic model available for the ITER machine until 2021, when E-lite was released
which is a full 360° model of ITER that was conceived to overcome some limitation encountered using
the C-Model for specific application. Nevertheless, since E-lite is an extremely heavy model, C-model
is still considered a valid model to compute the possible impact on the nuclear responses over the ITER machine.

Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /img/benchmarks/cmodel.png
    :width: 600
    :align: center

    C-model R181031. Origin (1050,200,0). Basis (0.982339, 0.187112, 0.000000)
    (0,0,1). Extent (1000,1000)

Due to its complexity, a thorough description of the C-Model benchmark geometry is considered out of
the scope of this work and can be found, instead, in a dedicated F4E report.

Tallies
^^^^^^^
The C-model standard tallies have been used. They include neutron current,
neutron flux and nuclear heating at different locations. More precisely:

 - F11: Neutron current on plasma boundary (inboard BLK#1-6)
 - F21: Neutron current on plasma boundary (BLK#7)
 - F31: Neutron current on plasma boundary (BLK#8)
 - F41: Neutron current on plasma boundary (BLK#9)
 - F51: Neutron current on plasma boundary (BLK#10)
 - F61: Neutron current on plasma boundary (BLK#11)
 - F71: Neutron current on plasma boundary (BLK#12)
 - F81: Neutron current on plasma boundary (BLK#13)
 - F91: Neutron current on plasma boundary (BLK#14)
 - F101: Neutron current on plasma boundary (BLK#15)
 - F111: Neutron current on plasma boundary (BLK#16)
 - F121: Neutron current on plasma boundary (BLK#17)
 - F131: Neutron current on plasma boundary (BLK#18)

 - F12: Neutron flux on plasma boundary (inboard BLK#1-6)
 - F22: Neutron flux on plasma boundary (BLK#7)
 - F32: Neutron flux on plasma boundary (BLK#8)
 - F42: Neutron flux on plasma boundary (BLK#9)
 - F52: Neutron flux on plasma boundary (BLK#10)
 - F62: Neutron flux on plasma boundary (BLK#11)
 - F72: Neutron flux on plasma boundary (BLK#12)
 - F82: Neutron flux on plasma boundary (BLK#13)
 - F92: Neutron flux on plasma boundary (BLK#14)
 - F102: Neutron flux on plasma boundary (BLK#15)
 - F112: Neutron flux on plasma boundary (BLK#16)
 - F122: Neutron flux on plasma boundary (BLK#17)
 - F132: Neutron flux on plasma boundary (BLK#18)

 - F16: Nuclear heat in the blanket and divertor
 - F26: Nuclear heat in the vacuum vessel, port extension and port ducts
 - F36: Nuclear heat in thermal shields
 - F46: Nuclear heat in the cryostat
 - F56: Nuclear heat in port plugs
 - F66: Nuclear heat in PF coils
 - F76: Nuclear heat in TF coils
 - F86: Nuclear heat in correction coils
 - F96: Nuclear heat in Central solenoid

.. seealso:: **Related papers and contributions:**

    * D. Leichtle, B. Colling, M. Fabbri, R. Juarez, M. Loughlin,
      R. Pampin, E. Polunovskiy, A. Serikov, A. Turner and L. Bertalot, 2018,
      "The ITER tokamak neutronics reference model C-Model",
      *Fusion Engineering and Design*, **136** 742-746
    * R. Juarez, G. Pedroche, M. J. Loughlin, R. Pampin, P Martinez, M. De Pietri,
      J. Alguacil, F. Ogando, P. Sauvan, A. J. Lopez-Revelles, A. Kolšek,
      E. Pol-unovskiy, M. Fabbri, and J. Sanz. “A full and heterogeneous model of
      the ITERtokamak for comprehensive nuclear analyses”.
      In:Nature Energy 6 (2021), pp. 150–157
    * E. Polunovskiy. "Description of ITER Nuclear Analysis Tokamak Reference Model
      C-model R181031". Technical Report [ITER IDM XETSWC v1.5]. Iter Organization, 2019.