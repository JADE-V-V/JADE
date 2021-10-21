.. _sphere:

Sphere Leakage
--------------
.. figure:: /img/benchmarks/sphere.png
    :align: center
    
    Sphere Leakage geometrical model

The Sphere Leakage benchmark is arguably the most important 
benchmark included in the JADE suite. Indeed, it allows to test
individually each single isotope of the nuclear data library under assessment
plus some typically used material in the ITER project namely:

* Water;
* Ordinary Concrete;
* Boron Carbide;
* SS316L(N)-IG;
* Natural Silicon;
* Polyethylene (non-borated).

Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^
The Sphere Lekage geometry consists of actually three
concentric spheres. The inner one is void and has a radius of 5 cm. Here
is located the uniform probability 0-14 MeV neutron point source. The second sphere
has a radius of 50 cm and it is composed entirely by a single isotope
or a typical ITER material. Finally,
the last 60 cm radius sphere acts as a graveyard where particles importance is
set to zero and the boundary of the model is defined.

Other two important settings that needed to be defined where the the choice of the sphere density
and of the MCNP STOP card parameters. Since to impose a
single density equal for all materials and  zaids was not a valid option, in order to keep some
kind of physical meaning in the results, as default densities the one computed using NTP
(Normal Temperature and Pressure) conditions were used. These are are defined at 20 °C and 
101325 Pa (1 atm). Even if these values work quite well with solids, they cause gases to perform 
poorly in terms of tally scoring. This happens due to the substantially lower density in NTP conditions 
for gases when compared to solids, resulting in too few interactions of the neutrons and secondary photons 
with the material. This has been proven to be especially true for hydrogen and helium, leading to the 
choice of selecting their liquid phase density instead. Another issue was encountered when simulating 
fissile isotopes like U235. A 1m diameter sphere containing a pure fissile isotopes at NTP density is
very much super-critical and the high number of secondary particles (i.e. other neutrons) produced 
caused the simulations to fail due to memory limitations. For this reason, the density of these isotopes 
was imposed equal to 1 g/cc as if an aerosol was considered.

Finally, the STOP card parameters were optimized. MCNP allows to stop a simulation based either on:
* the precision reached in a specified tally;
* the number of histories (NPS);
* the total elapsed computer time (i.e. the sum of computer time used by all CPUs).

The optimization of such parameters for each element was done through trial and error with the aim of
finding a good balance between computational cost and enough precise results.
These parameters are provided by default in JADE, but the user may modify them if necessary through
benchmark-specific configuration files. Density values can be modified too. The files are located in
``<JADE_root>\Configuration\Benchmarks Configuration\Sphere``.

Tallies
^^^^^^^
Both the transport of neutrons and of secondary photons are active and photons cut-off energy  is
left to the default value of 1 KeV.
The following MCNP tallies are defined in the Sphere Leakage benchmark:

Tally n. 2
    Fine neutron flux at the external surface of the filled sphere. The flux is binned in energy using the Vitamin-J \cite{Sartori:vitaminJ} 175 energy group structure.
Tally n. 12
    Coarse neutron flux at the external surface of the filled sphere. The flux is binned in 5 energy groups: 1e-6, 0.1, 1, 10 and 20 MeV.
Tally n. 32
    Fine photon flux at the external surface of the filled sphere. The flux is binned in energy using the 24 group structure described in the FISPACT manual \cite{manual:fispact}.
Tally n. 22
    Coarse photon flux at the external surface of the filled sphere. The flux is binned in 5 energy groups: 0.01, 0.1, 1, 10 and 20 MeV.
Tally n. 4
    Neutron heating computed in the filled sphere (F4+FM strategy).
Tally n. 44
    Photon heating computed in the filled sphere (F4+FM strategy).
Tally n. 6
    Neutron heating computed in the filled sphere (F6 strategy).
Tally n. 16
    Photon heating computed in the filled sphere (F6 strategy).
Tally n. 14
    Helium (He) ppm production in the filled sphere.
Tally n. 24
    Tritium (T) ppm production in the filled sphere.
Tally n. 34
    Displacement Per Atom (DPA) production in the filled sphere.

More details on the MCNP tally definition and especially on the difference between the heating computation
using the F6 or the F4+FM strategy can be found in §\ref{sec:tallies}.

.. seealso:: **Related papers and contributions:**

    * D. Laghi, M. Fabbri, L. Isolan, R. Pampin, M. Sumini, A. Portone and
      A. Trkov, 2020,
      "JADE, a new software tool for nuclear fusion data libraries verification &
      validation", *Fusion Engineering and Design*, **161** 112075