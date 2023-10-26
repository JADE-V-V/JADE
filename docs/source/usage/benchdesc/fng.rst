.. _fngsddr:

Frascati Neutron Generator SDDR Experiment
------------------------------------------

.. important::
  This benchmark input cannot be distributed directly with JADE. The user must have a valid SINBAD
  license and contact the JADE team in order to obtain the instructions on how to modify
  the inputs in order for them to be used in JADE.

The Frascati Neutron Generator (FNG) is an experimental facility designed and built by ENEA
(the italian New Technology, Energy and Ambient Body) in Frascati, Italy. The installation
is able to produce 14 MeV neutrons based on the T(d,n)α fusion reaction and it is able to
produce up to 5E+11 n/s.

One of the key experiments that have been conducted at the FNG is the neutron irradiation
experiment, where a mock-up of the outer vacuum vessel region of ITER was irradiated by
means of 14 MeV neutrons for a sufficiently long time in order to achieve achieve significative
activation levels. Two
distinct irradiation campaigns were conducted in May and August 2000 and, among other
things, the SDDR values after different cooling time intervals were measured.
Many benchmarks activities have been performed using the experiment in the past, and the
benchmark is also included in the SINBAD database (listed as fng_dose).

Geometry
^^^^^^^^
.. figure:: /img/benchmarks/fng.jpg
    :width: 600
    :align: center

    FNG SDDR experiment layout

At the FNG, a deuterium beam is accelerated up to 300 KeV by means of a linear electro-static
tube towards a target rich in tritium generating a 14 MeV neutron source. These are the
neutrons that were used to irradiate the experimental assembly which consisted of a block of
stainless steel and water equivalent material (perspex) with total thickness of 71.4 cm, and
a lateral size of 100 cm x 100 cm. A cavity was obtained within the block (12.6 cm in the beam
direction, 11.98 cm high) behind a 22.47 cm thick shield. A void channel (2.7 cm inner diameter)
was included in front of the cavity to study the effect of streaming paths in the bulk shield.
A squared box was used to locate detectors inside the cavity, with 2 mm thick bottom and lateral walls.
Measurements were taken in the cavity, during the irradiation and after shut-down, to obtain the
local neutron flux, the decay gamma-ray spectra and the dose rates for different cooling times.

JADE MCNP input template was realized starting from the MCNP inputs provided in the SINBAD database
and, for this reason, it cannot be freely distributed together with the JADE source code.
Cell and surface card were left untouched as well as the material composition. D1S-UNED specific
cards were also added.

SDDR Parameters
^^^^^^^^^^^^^^^

The next two tables describe the equivalent schedules considered for respectively the 1st and 2nd
irradiation campaign conducted at the FNG.

.. list-table:: Equivalent schedule of the 1st FNG irradiation campaign
    :header-rows: 1

    * - Δt [s]
      - Δt [min]
      - Neutron Intensity [n/s]
    * - 19440
      - 324
      - 2.32E+10
    * - 61680
      - 1028
      - 0       
    * - 32940
      - 549
      - 2.87E+10
    * - 54840
      - 914
      - 0        
    * - 15720
      - 262
      - 1.90E+10 
    * - 6360
      - 106
      - 0       
    * - 8940
      - 149
      - 1.36E+10 

.. list-table:: Equivalent schedule of the 2nd FNG irradiation campaign
    :header-rows: 1

    * - Δt [s]
      - Δt [min]
      - Neutron Intensity [n/s]
    * - 1748
      - 29
      - 3.04E+10
    * - 7820
      - 130
      - 4.28E+10
    * - 54140
      - 902
      - 0
    * - 22140
      - 369
      - 4.29E+10
    * - 900
      - 15
      - 0
    * - 3820
      - 64
      - 3.38E+10
    * - 420
      - 7
      - 0
    * - 140
      - 2
      - 2.86E+10

The experimentally measured SDDR values at different cooling times are reported in
the next tables for the 1st and 2nd irradiation campaigns.

.. list-table:: Experimental measure of the SDDR during 1st FNG irradiation campaign
    :header-rows: 1

    * - Cooldown Time [d]
      - Cooldown Time [s]
      - Experimental SDDR [Sv/h]
      - Relative Error
    * - 1
      - 86400
      - 2.46E-06
      - 0.1
    * - 7
      - 604800
      - 6.99E-07
      - 0.1
    * - 15
      - 1296000
      - 4.95E-07
      - 0.1
    * - 30
      - 2592000
      - 4.16E-07
      - 0.1
    * - 60
      - 5184000
      - 3.16E-07
      - 0.1
                     
.. list-table:: Experimental measure of the SDDR during 2nd FNG irradiation campaign
    :header-rows: 1

    * - Cooldown Time [s]
      - Cooldown Time [h]
      - Cooldown Time [d]
      - Experimental SDDR [Sv/h]
      - Relative Error
    * - 4380
      - 1.22
      - 0.05
      - 4.88E-04
      - 3.89E-02
    * - 6180
      - 1.72
      - 0.07
      - 4.15E-04
      - 3.86E-02
    * - 7488
      - 2.08
      - 0.09
      - 3.75E-04
      - 4.00E-02
    * - 11580
      - 3.22
      - 0.13
      - 2.68E-04
      - 3.73E-02
    * - 17280
      - 4.80
      - 0.20
      - 1.73E-04
      - 4.05E-02
    * - 24480
      - 6.80
      - 0.28
      - 1.01E-04
      - 3.96E-02
    * - 34080
      - 9.47
      - 0.39
      - 5.06E-05
      - 3.95E-02
    * - 45780
      - 12.72
      - 0.53
      - 2.30E-05
      - 3.91E-02
    * - 57240
      - 15.90
      - 0.66
      - 1.17E-05
      - 4.27E-02
    * - 72550
      - 20.15
      - 0.84
      - 5.80E-06
      - 3.97E-02
    * - 90720
      - 25.20
      - 1.05
      - 3.56E-06
      - 3.93E-02
    * - 132000
      - 36.67
      - 1.53
      - 2.43E-06
      - 3.70E-02
    * - 212400
      - 59.00
      - 2.46
      - 1.78E-06
      - 3.93E-02
    * - 345600
      - 96.00
      - 4.00
      - 1.22E-06
      - 4.10E-02
    * - 479300
      - 133.14
      - 5.55
      - 9.52E-07
      - 3.89E-02
    * - 708500
      - 196.81
      - 8.20
      - 7.59E-07
      - 3.95E-02
    * - 1050000
      - 291.67
      - 12.15
      - 6.67E-07
      - 3.90E-02
    * - 1670000
      - 463.89
      - 19.33
      - 6.13E-07
      - 3.92E-02
    * - 1710000
      - 475.00
      - 19.79
      - 6.14E-07
      - 3.91E-02

When simulating with the D1S approach, in order to reduce the computation time it is good practice
to individuate the subset of decay isotopes which contribute the most to the dose rate. This
subset will depend from the unirradiated material composition and the cool-down time that are considered.
In order to do so, preliminary activation calculation are usually performed with the help of
activation codes like FISPACT or ACAB. These studies have been already conducted
both during the D1S libraries initial V&V procedure and when the experimental results were tested for
the first time. The next plot lists the isotopes
contributing cumulatively to more than 95% of the dose rate during the first irradiation campaign.

.. figure:: /img/benchmarks/daughtersFNG.png
  :align: center
  :width: 600

  Isotope contribution to the the dose during the first FNG irradiation campaign

At this point, the D1S reaction file can be generated: it will include all reactions that can
originate in the material (i.e. that are also available in the activation library) which result
in the creation of one of the daughters of interest. The D1S irradiation file will simply
contain those daughters which are generated by at least one reaction. All of this implies that
a comparison between two different libraries can often not be an exact one. Indeed, it is quite
common that to a new library release corresponds an increase in the number of available reactions.
Nevertheless, this is in line with the philosophy of JADE. If the Sphere benchmarks are the
primary tools that should be used to identify specific inconsistencies at the single cross section
level among libraries, all other benchmarks have a slightly different scope which is to show how
big is the impact of these inconsistencies on more realistic applications.

Tallies
^^^^^^^

The only tallied result for the FNG benchmark is the dose rate at the dosimeter location inside the cavity (tally n.4).

.. seealso::
  **Related papers:**

  * M. Martone, M. Angelone, and M. Pillon. “The 14 MeV Frascati neutron generator”.
    In: Journal of Nuclear Materials 212-215 (1994). Fusion Reactor Materials, pp. 1661–1664
  * P. Batistoni, M. Angelone, L. Petrizzi, and M. Pillon. “Benchmark Experiment for the
    Validation of Shut Down Activation and Dose Rate in a Fusion Device”. In: Journal of Nuclear
    Science and Technology 39.sup2 (2002), pp. 974–977.
  * K. Seidel, Y. Chen, U. Fischer, H. Freiesleben, D. Richter, and S. Unholzer.“Measurement
    and analysis of dose rates and gamma-ray fluxes in an ITER shut-down dose rate experiment”.
    In:Fusion Engineering and Design 63-64 (2002), pp. 211–215.
  * R. Pampin, A. Davis, R.A. Forrest, D.A. Barnett, I. Davis, and M.Z. Youssef.“Status of novel
    tools for estimation of activation dose”. In: Fusion Engineering and Design 85.10 (2010).
    Proceedings of the Ninth International Symposiumon Fusion Nuclear Technology, pp. 2080–2085.
  * J. Sanz, O. Cabellos, and N. Garcia-Herranz. Inventory Code for Nuclear Applications:
    User’s Manual V. 2008. RSICC. 2008.