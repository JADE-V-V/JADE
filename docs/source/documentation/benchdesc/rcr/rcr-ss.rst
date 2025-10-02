(RCR-SS) RCR Stainless Steel Block Experiment with 252Cf source
----------------------------------------------------------

.. include:: /documentation/benchdesc/icbep_disclaimer.rst

In 2021 at the Research Centre Řež (RCR, Centrum Výzkumu Řež), a series of experiments were performed 
to study neutron activation and fast neutron leakage spectra from a large stainless-steel block (SST 321) 
with a 252Cf spontaneous fission neutron source placed at its geometric center. Multiple runs with and without 
a shielding cone (iron and borated polyethylene) to separate direct leakage from room-scattered background.

The experiment is identified as ALARM-CF-SST-SHIELD-001 in the ICSBEP database and was adopted by the 
International Nuclear Data Evaluation Network (INDEN) for the validation of Fe cross section above 1.5 MeV.

Benchmark structure
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The benchmark is organized into two experimental cases, each with a distinct measurement configuration and purpose:

Case 1: Fast Neutron Leakage and Spectrum Measurement & Surface Activation Foil Measurements
    Objective:
        #. Measure the direct fast neutron leakage and its energy spectrum from the stainless steel block.
        #. Measure the spatial distribution of neutron-induced reaction rates on the surface of the block.
    Method:
        #. Proton recoil method using hydrogen proportional counters (HPD, 0.1-1.3 MeV neutrons) and a stilbene 
           scintillation detector for 0.8-12 MeV neutrons, with digital pulse shape discrimination for neutron/gamma separation.
        #. Activation foils (58Ni(n, p)58Co, 115In(n, n')115m1) are placed at defined positions on the block surface and 
           irradiated during the neutron leakage measurements.
    Details
        #. The neutron fluence rate and spectrum are measured at a fixed distance (1 m from the block center, 74.8 cm from 
           the surface) with and without a shielding cone to separate direct leakage from background (room return).
        #. The reaction rates are determined by gamma spectrometry (HPGe detector) after irradiation, normalized per source 
           neutron and per target atom.

Case 2: Internal Activation Foil Measurements
    Objective
        Measure the spatial distribution of neutron-induced reaction rates inside the block.
    Method
        Activation foils (63Cu(n,g)64Cu, 197Au(n,g)198Au, 181Ta(n,g)182Ta, 93Nb(n,2n)92mNb, 58Ni(n,p)58Co, 
        97Au(n,2n)196Au) are placed between the plates at four depths (5.04, 10.08, 15.12, 20.16 cm from the surface) 
        inside the block.
    Details
        The block is disassembled, foils are inserted, and the block is reassembled and irradiated. Reaction rates are measured 
        by HPGe gamma spectrometry.

Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* **Block dimensions**: :math:`50.4\,\mathrm{cm} \times 50.2\,\mathrm{cm} \times 50.2\,\mathrm{cm}` (increased to 50.662 cm for 
    some configurations with foils inside).
* **Material**: Stainless steel (SST 321), composition determined by XRF analysis (Fe 67.8%, Cr 19.7%, Ni 9.3%, Mn 1.8%, Mo 0.4%, 
    Si 0.3%, Cu 0.3%, Ti 0.3%, V 0.06%, Sn 0.01%).
* **Density**: 7.9083 :math:`g/cm^3`
* **Source**: 252Cf oxide in a palladium matrix, encapsulated in double stainless-steel cladding.
* **Source position**: Geometric center of the block, placed in a 2.6 cm diameter, 28.1 cm deep hole drilled in a central 
    3 cm thick plate.
* **Experimental hall**: Room dimensions :math:`7.24\,\mathrm{m} \times 6.5\,\mathrm{m} \times 7.2\,\mathrm{m}` (height), 
    block center 2 m above floor.
* **Set-up of cases**
    * Case-1: It contains only the activation foils on the outside the stainless steel block (on the surface) 
      and the neutron detectors. 
    * Case-2: It contains only the activation foils within the stainless steel block.

.. figure:: /img/benchmarks/RCR-SS_1.png
    :width: 600
    :align: center

    Case 1: Neutron spectra measurement setup with shielding cones.

.. figure:: /img/benchmarks/RCR-SS_2.png
    :width: 600
    :align: center

    Case 2: Cross section of stainless steel block.

MCNP modelling
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Two MCNP inputs, corresponding to the two experimental cases were used:

**For case 1**
    *Detector tallies, Fn5 MCNP type*
        Two detector-flux tallies have been used to collect the energy-binned neutron spectra at the same detector position 
        with a course energy binning (F5) and a finer one (F15) which matches the measurement performed.
    *Track length flux tallies, Fn4 MCNP type*
        A track length flux tally has been used to collect results in the cells corresponding to the activation foils in MCNP 
        geometry. The tally has been multiplied in each input (with FM card) by the appropriate microscopic reaction cross section, 
        to obtain results in terms of number of reactions per unit neutron from the source. Energy binning was applied to half of 
        the tallies, while the other half recorded the total reaction rate in the same cells (see table below). Nuclear data 
        for tally collection was taken from IRDFF-II dosimetry libraries. In the following, a list of the reactions considered for 
        each activation foil material is reported:
    
.. list-table:: Tally Details
   :header-rows: 1
   :widths: 10 25 25 10

   * - Tally No.
     - Where
     - Foils Reactions
     - Energy binning
   * - 4
     - Outer block surface
     - 58Ni(n,p)58Co
     - Yes
   * - 14
     - Outer block surface
     - 115In(n,g)116m1In
     - Yes
   * - 24
     - Outer block surface
     - 115In(n,n')115m1 In
     - Yes
   * - 34
     - Outer block surface
     - 58Ni(n,p)58Co
     - No
   * - 44
     - Outer block surface
     - 115In(n,g)116m1In
     - No
   * - 54
     - Outer block surface
     - 115In(n,n')115m1 In
     - No

**For case 2**
    Track length flux tallies have been used to collect results in the cells corresponding to the activation foils in MCNP geometry 
    at different positions within the block. The tallies have been multiplied in each input (with FM card) by the appropriate 
    microscopic reaction cross section, to obtain results in terms of number of reactions per unit neutron from the source. No energy 
    bins were used. Nuclear data for tally collection was taken from IRDFF-II dosimetry libraries. In the following, a list of the 
    reactions considered for each activation foil material is reported.

.. list-table:: Tally Details (Within the Block)
   :header-rows: 1
   :widths: 8 35 30 10

   * - Tally No.
     - Where
     - Foils Reactions
     - Energy binning
   * - 4
     - Within the block - Plate No. 8
     - 197Au(n,g)198Au
     - Yes
   * - 14
     - (same as above)
     - 58Ni(n,p)58Co
     - Yes
   * - 24
     - (same as above)
     - 181Ta(n,g)182Ta
     - Yes
   * - 34
     - (same as above)
     - 63Cu(n,g)64Cu
     - Yes
   * - 44
     - Within the block - Plate No. 9
     - 197Au(n,g)198Au
     - Yes
   * - 54
     - (same as above)
     - 58Ni(n,p)58Co
     - Yes
   * - 64
     - (same as above)
     - 181Ta(n,g)182Ta
     - Yes
   * - 74
     - (same as above)
     - 93Nb(n,2n)92mNb
     - Yes
   * - 84
     - (same as above)
     - 63Cu(n,g)64Cu
     - Yes
   * - 94
     - Within the block - Plate No. 10
     - 197Au(n,g)198Au
     - Yes
   * - 104
     - (same as above)
     - 58Ni(n,p)58Co
     - Yes
   * - 114
     - (same as above)
     - 181Ta(n,g)182Ta
     - Yes
   * - 124
     - (same as above)
     - 63Cu(n,g)64Cu
     - Yes
   * - 134
     - Within the block - Plate No. 11
     - 197Au(n,g)198Au
     - Yes
   * - 144
     - (same as above)
     - 58Ni(n,p)58Co
     - Yes
   * - 154
     - (same as above)
     - 181Ta(n,g)182Ta
     - Yes
   * - 164
     - (same as above)
     - 63Cu(n,g)64Cu
     - Yes
   * - 174
     - Within the block - Plate No. 8
     - 197Au(n,g)198Au
     - No
   * - 184
     - (same as above)
     - 58Ni(n,p)58Co
     - No
   * - 194
     - (same as above)
     - 181Ta(n,g)182Ta
     - No
   * - 204
     - (same as above)
     - 63Cu(n,g)64Cu
     - No
   * - 214
     - Within the block - Plate No. 9
     - 197Au(n,g)198Au
     - No
   * - 224
     - (same as above)
     - 58Ni(n,p)58Co
     - No
   * - 234
     - (same as above)
     - 181Ta(n,g)182Ta
     - No
   * - 244
     - (same as above)
     - 93Nb(n,2n)92mNb
     - No
   * - 254
     - (same as above)
     - 63Cu(n,g)64Cu
     - No
   * - 264
     - Within the block - Plate No. 10
     - 197Au(n,g)198Au
     - No
   * - 274
     - (same as above)
     - 58Ni(n,p)58Co
     - No
   * - 284
     - (same as above)
     - 181Ta(n,g)182Ta
     - No
   * - 294
     - (same as above)
     - 63Cu(n,g)64Cu
     - No
   * - 304
     - Within the block - Plate No. 11
     - 197Au(n,g)198Au
     - No
   * - 314
     - (same as above)
     - 58Ni(n,p)58Co
     - No
   * - 324
     - (same as above)
     - 181Ta(n,g)182Ta
     - No
   * - 334
     - (same as above)
     - 63Cu(n,g)64Cu
     - No

Implemented broadening on Monte Carlo computed results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Following the ICSBEP documentation, MCNP neutron spectra are broadened with a Gaussian function using a constant 10% FWHM 
for all energy ranges for the hydrogen proportional counters while as per the table below for the stilbene scintillation detector. 

.. list-table:: Energy Resolution of the Stilbene Detector for Neutron Spectra Measurement 
   :header-rows: 1
   :widths: 15 15

   * - Elow (MeV)
     - FWHM (%)
   * - 17.02
     - 1
   * - 15.05
     - 1.35
   * - 13.63
     - 1.65
   * - 12.5
     - 1.92
   * - 11.42
     - 2.23
   * - 11.02
     - 2.35
   * - 10.97
     - 2.37
   * - 10.67
     - 2.47
   * - 9.96
     - 2.73
   * - 9.3
     - 3.01
   * - 8.05
     - 3.68
   * - 6.59
     - 4.97
   * - 5.91
     - 6.07
   * - 5.46
     - 7.41
   * - 5.25
     - 8.61
   * - 5.13
     - 10

.. seealso:: **Related papers and contributions:**

    * ICSBEP, NEA/NSC/DOC/(95)03/VIII, Volume VIII, ALARM-CF-SST-SHIELD-001.
    * M. Schulc et al., "Measuring neutron leakage spectra using spherical benchmarks with 252Cf source in its centers", 
      Nucl. Instrum. Methods Phys. Res. A 914 (2019) 53-56.  
    * M. Schulc et al., "Application of 252Cf neutron source for precise nuclear data experiments", Appl. Radiat. Isot. 
      151 (2019) 187-195.
    * M. Schulc et al., “Comprehensive stainless steel neutron transport libraries validation”, Annals of Nuclear 
      Energy 179 (2022) 109433.
    * https://www-nds.iaea.org/INDEN/