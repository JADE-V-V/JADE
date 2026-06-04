.. _oktavian:

Oktavian
--------

Experimental results derived from Oktavian experiments are publicly accessible at the
`CoNDERC database <https://www-nds.iaea.org/conderc/oktavian>`_ which is mantained by the
IAEA Nuclear Data Section and built upon the
`database of shielding experiments <https://rsicc.ornl.gov/Benchmarks.aspx>`_ (SINBAD), hosted
by the RSICC and jointly mantained with the NEA data bank.

OKTAVIAN is an experimental facility located at the Osaka University which has been
operative since 1981. It consists of an intense deuterium-tritium (D-T) fusion
neutron source (up to 3E+12 n/s) that has been used during the years for
many experiments on high energy neutrons transport. Among them, many Time Of Flight
(TOF) experiments were conducted and their results have been
introduced in SINBAD. These experiments consists in placing the neutron source inside
a sphere composed only by a specific material of interest and measuring the leakage
photon spectra exiting from such sphere with the use of detectors. The photon energy
measure is performed indirectly measuring the time of flight, which is then converted
into a velocity.

Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /img/benchmarks/oktavian simplified.png
    :width: 600
    :align: center

    Simplified layout of the OKTAVIAN Fe experimental setup (not in scale).

An accelerated deuteron beam is led through a narrow tube to the centre of a sphere
(every time composed by a different material) where pulsed 14.1 MeV monochromatic 
neutrons were produced by the d-t fusion reaction. The source is regarded to be 14
MeV monochromatic. Neutron leakage current spectrum of neutrons was measured in 
"absolute values" by the time-of-flight technique between 10 keV and 14 MeV, about
9.5 m from the sphere centre. Because of the presence of the collimators the 
detectors could not see the entire surface of the sphere, but only the solid angle
of 17.28° from the sphere centre.

Tallies
^^^^^^^

Only two tallies are defined for each input:

Tally n. 21
  Neutron leakage current $[\#/cm^2]$ per source particle. 134 energy bins were defined spanning from 0.1 MeV to 20.6 MeV.
Tally n. 41
  Photon leakage current $[\#/cm^2]$ per source particle. 57 energy bins were defined spanning from 0.5 MeV to 10.5 MeV.

Since experimental results are provided as flux per unit lethargy, the tally results are manipulated as follows:

.. math::
    d\Phi_u = d\Phi/d(\log{E})

.. seealso:: **Related papers and contributions:**

    * A. Milocco, A. Trkov and I. A. Kodeli, 2010, "The OKTAVIAN TOF experiments in SINBAD: Evaluation of the
      experimental uncertainties", *Annals of Nuclear Energy*, **37** 443-449
    * I.Kodeli, E. Sartori and B. Kirk, “SINBAD - Shielding Benchmark Experiments - Status and Planned Activities”,
      *Proceedings of the ANS 14th Biennial Topical Meeting of Radiation Protection and Shielding Division*,
      Carlsbad, New Mexico (April 3-6, 2006)