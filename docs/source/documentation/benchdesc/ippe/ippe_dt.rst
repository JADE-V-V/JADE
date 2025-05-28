(IPPE-DT) Institute of Physics and Power Engineering DT Iron Sphere Experiment
------------------------------------------------------------------------------

.. include:: /documentation/benchdesc/sinbad_disclaimer.rst

The IPPE DT Iron Sphere Experiment was carried out at the Institute of Physics and Power Engineering (IPPE) in Obninsk,
Russia, to provide benchmark data for validating neutron transport codes and nuclear data libraries.
The experiment focused on measuring neutron leakage spectra from iron spheres irradiated by 14 MeV
neutrons produced at their center by a deuterium-tritium (DT) neutron generator.
It is part of the SINBAD database, which provides compilations of shielding and dosimetry benchmark experiments.
The IPPE iron experiments with the DT source were established as a benchmark problem within the EU CONRAD project
in year 2007. In such instance, attention was drawn on the simulation of the neutron spectra in time domain,
then converting those into the energy domain consistently with experimental method, since a direct analysis
in the energy domain would shift and jag multiple scattering effects, which is evident in the resonance region
of the leakage spectra from thick shells.


Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The experiment used a Cockcroft-Walton accelerator to produce 280 keV deuterons, which bombarded a
solid titanium-tritium target to generate 14 MeV neutrons. The neutron source was placed at the center of
a spherical iron assembly. The total iron thickness varied from 2.5 cm to 28.0 cm across different configurations.
A fast scintillation detector was positioned 6.8 meters from the source at 8-degree angle to measure neutron
leakage using the time-of-flight technique. The setup included lead shielding and collimation,
and alpha particle detection was used to monitor neutron yield. Room return was subtracted after
performing a measurement with a shadow bar.


.. figure:: /img/benchmarks/ippe-dt1.jpg
  :align: center
  :width: 600

  Experimental setup


MCNP modelling
^^^^^^^^^^^^^^
Two tallies are employed to compute the neutron leakage spectrum both in the energy (Tally 5)
and time domain (Tally 15) by means of a MCNP F5 point detector.

.. seealso:: **Related papers and contributions:**

    * S. Simakov, B.V. Devkin, M.G. Kobozev, V.A. Talalaev, U. Fischer, U. von Möllendorff,
      "Validation of evaluated data libraries against an iron shell transmission experiment and against the Fe(n,xn)
      reaction cross section with 14 MeV neutron source", Report EFF-DOC-747, NEA Data Bank, Dec. 2000, Paris
    * I. Kodeli, A. Milocco and A. Trkov, "Lessons learned from the TOF-benchmark intercomparison exercise
      within EU CONRAD project (how not to misinterpret a TOF-benchmark)", Nucl Technol 168 3 (2009) 965-969
    * I. Kodeli and E. Sartori, "SINBAD - Radiational shieding benchmark Experiments",
      Annals of Nuclear Energy, 159 (2021) 108254
