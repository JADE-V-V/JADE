Sphere SDDR
-----------

The Sphere SDDR benchmark is a variation of the the :ref:`spheredesc`
which is focused on isotopes activation and dose rate measurement.
Once again, these kind of benchmarks allows to test all available
isotopes in the library under assessment (this time being a D1S activation
library) together with a few typical ITER materials. In particular, each 
single reaction channel (MT) of every isotope will be tested separately while,
for the typical materials, all possible reactions foreseen by the library will
be considered.

Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. figure:: /img/benchmarks/sphereSDDRgeom.png
    :width: 600
    :align: center

    Schematic view of the Sphere SDDR model

The geometry of the Sphere SDDR benchmarks, is practically the same as the one 
of the Sphere Leakage benchmark. The only difference is that externally to the filled
sphere, a void spherical shell has been defined having a 10 cm radial thickness.
This is the cell used to tally the contact shut down dose rate.

Similarly to what was done for the Sphere Leakage benchmark, the user have control on
the densities to be applied for each element and material (default is set to NTP
conditions with few exceptions) and control on the STOP parameters to be used.
The same 0-14 MeV uniform neutron point source is also defined.

In addition to the parameters that can be set for the Sphere Leakage benchmark, the D1S-UNED
irradiation files must also be provided for each activation library that needs to be tested.
These irradiation files contain the D1S time factors related to the SA-2 scenarios (see next paragraph) for all 
available daughter nuclides in the library. The file must be named as ``irrad_<library>`` where
``<library>`` is the suffix of the activation library the time factor refers to. This should be
the same as the one used in the :ref:`activationfile`. The file must be placed in the same folder
as the ``MaterialsSettings.csv`` and the ``ZaidSettings.csv`` files.

SDDR parameters
^^^^^^^^^^^^^^^

The cool-down times that have been considered are 0 s, 2.7 h, 24 h, 11.6 d, 30 d
and 10 y. For the isotopes simulations, since only one reaction is considered, relative
comparisons at different cool-down times will not lead to different results, hence,
during post-processing operations only the results at 0 s are elaborated. This does
not apply to materials simulations, where many different reactions are included.

The irradiation schedule considered for the Sphere SDDR benchmark is reported hereafter
and represents an actual equivalent irradiation scenario foreseen for ITER blanket (SA2):

.. list-table:: Irradiation schedule (ITER SA2 irradiation scenario)
    :header-rows: 1

    * - Source Intensity [n/s]
      - Δt irr.
      - Multiplicity
    * - 1.0714E+17
      - 2 y
      - 1
    * - 8.2500E+17
      - 10 y
      - 1
    * - 0
      - 9 m
      - 1
    * - 1.6667E+18
      - 15 m
      - 1
    * - 0
      - 3290 s
      - ->
    * - 2.0000E+19
      - 400 s
      - 17
    * - 0
      - 3290 s
      - ->
    * - 2.8000E+19
      - 400 s
      - 4

As previously discussed, the irradiation file and reaction file provided together with the
MCNP input file are generated in two different ways depending on if the simulation is
conducted on a single isotope or on a typical ITER material. In the first case, a single
reaction is considered and the irradiation file will only contain the daughter of such irradiation.
In the second case, all possible reactions that are available in the library and that can be
originated in the material will be included. The irradiation file will be then generated accordingly.

Tallies
^^^^^^^
All neutron and photon related tallies defined in Sphere Leakage benchmark have also been imported
in the Sphere SDDR benchmark. For photons, the time binning necessary to cover all the cool-down
times of interest have been added. Tally n. 104 have been also defined to tally the shut
down dose rate at all cool-down times in the additional spherical shell added for this
specific purpose [Sv/h].

.. seealso:: 
  For additional information on SA2 irradiation scenario
  and ITER irradiation scenarios in general the reader is
  referred to Loughlin M. and Taylor N., 2009, "Recommendation on Plasma scenarios",
  [ITER IDM 2V3V8G v1.2].