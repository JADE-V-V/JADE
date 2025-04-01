C-Model
-------

.. important::

    This benchmark input cannot be distributed directly with JADE. The user must request to obtain it
    from ITER organization and insert it in the ``<JADE root>\Benchmarks inputs\C_Model\mcnp`` directory which 
    must be created by the user and the input renamed to 'C_Model.i'. If the user has OpenMC and Serpent inputs
    they should be added to openmc and serpent directories respectively. 

    The NPS card needs to be removed from the input. It is recommended to also delete total bins
    from standard tallies for a clearer post-processing results.

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
neutron current and nuclear heating at different locations.

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