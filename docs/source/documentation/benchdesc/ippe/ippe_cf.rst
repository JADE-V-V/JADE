(IPPE-CF) Institute of Physics and Power Engineering 252Cf 
----------------------------------------------------------

.. include:: /documentation/benchdesc/icbep_disclaimer.rst

In the 1980’s at the Institute of Physics and Power Engineering (IPPE) in Obninsk, Russia, several experiments were executed to study the spectra of neutrons and gamma-ray photons flowing away from iron spheres of different diameters with a 252Cf radionuclide source placed at the center of these spheres. Measurements of the spectra were made outside the spheres. For the measurements of spectra, the following spectrometers were used:
-	scintillation spectrometer of neutrons and gamma rays with a crystal of stilbene;
-	spectrometer of neutrons based on the hydrogen-recoil proportional counter;
-	multisphere spectrometer of neutrons, as a set of polyethylene spheres (so called Bonner spheres) with a semi-conductor detector of thermal neutrons at the center of these spheres.
The purpose of the experiments, which is taken from ICSBEP and identified as ALARM-CF-FE-SHIELD-001, was the research of neutron-physics characteristics of iron, which is the basis of the majority of construction materials and shielding of nuclear reactors. Besides this, the obtained experimental information could possibly be used to update and increase the accuracy of iron nuclear cross sections.


Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The experiment consists in measurement of the spectra of neutrons and gamma rays emitted from the surface of
the iron spheres with diameters 20.0, 30.0, 40.0, 50.0, 60.0, and 70.0 cm at whose centers the 252Cf
radionuclide source of neutrons has been placed. The uncertainty of the outer diameter of spheres was ± 0.1 cm.
The iron spheres were set-up on an aluminium support and steel frame.
The distance from the center of the spheres to the nearest wall of the experimental hall was more than 4 m.


.. figure:: /img/benchmarks/ippe-cf1.png
  :align: center
  :width: 600

  Iron Sphere with Plug and Cavity for the Source

For introduction of the californium source into the center of the spheres, a special radial channel 25 mm in
diameter had been drilled. This channel was closed by an iron plug at the end of which was a cylindrical cavity,
centered in the sphere, with depth 19 mm and 15 mm in diameter, for accommodation of the source.
Detectors of neutrons and gamma-ray photons were each fastened to a tripod which allowed the detectors
to be moved to different distances from the spheres.

.. figure:: /img/benchmarks/ippe-cf2.png
  :align: center
  :width: 600

  Iron Sphere with Plug and Cavity for the Source. 


MCNP modelling
^^^^^^^^^^^^^^
A surface tallies is employed to compute the neutron spectra at the external surface of the Iron sphere.
Tally 2 refers to the hydrogen-recoil proportional counter and Tally 12 to the stilbene scintillation spectrometer.

.. seealso:: **Related papers and contributions:**

    * ICBEP, NEA/NSC/DOC/(95)03/VIII, Volume VIII, ALARM-CF-FE-SHIELD-001,
      neutron and photon leakage spectra from cf-252 source at centers of six
      iron spheres of different diameters