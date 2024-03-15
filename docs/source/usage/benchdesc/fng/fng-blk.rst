.. _fngblk:

FNG Bulk Blanket and Shield Experiment
--------------------------------------

The aim of the experiment is to carry out a series of neutronics measurements, 
using 14 MeV neutrons, on a mockup of ITER inboard shielding system, with 
the purpose of validating the ITER shielding blanket design. 
To achieve the objective, mockup assembly configuration and material composition 
were chosen so that to replicate those of the ITER shielding system at the 
inboard side. The experiment was carried out at FNG facility, described in 
:ref:`fngsddr`, in the years 1995-97.

Geometry and run parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /img/benchmarks/FNGBLKT3.jpg
    :width: 500
    :align: center

    Photo of ITER Bulk Blanket mockup assembly.

 
The shield mockup is shown in the figure above. It consists of:

#. A 1 cm thick layer of copper simulating the first wall (FW),
#. A shielding block made of stainless steel AISI 316 type (SS) plates and 
   Perspex (a water equivalent material). The plates are arranged in such a way 
   as to reproduce blanket and vacuum vessel (VV) segment, including the 
   manifold region and the backplate,
#. A block made of alternate plates of SS316 and Cu 
   (both with thickness 2.2 cm), attached behind the shielding block, 
   simulating ITER Toroidal Field Coils (TFC).

The block is located at 5.3 cm from the neutron source. 
Of these 5.3 cm, 5 cm are in air and the remaining 0.3 cm are due to the 
target support structure ( 1 mm Cu, 1 mm H2O, and 1 mm SS). 
The block is positioned over an aluminium support and is surrounded by bunker
walls. The mockup is shielded in the rear side by a Polyethylene shield, 
to reduce to negligible levels the radiation backscattered from the bunker 
walls, with respect to the direct penetration flux.

In the experiment, activation foils were located in different locations along 
the block central (horizontal) axis, at different penetration depths.
Only foils of the same material were irradiated during every single irradiation.
Soon after each irradiation, the foils activities were recorded by a set of 
calibrated HPGe detectors.

Tallies
^^^^^^^^^^^^^^
The source angle/energy distribution was calculated with MCNP, taking into 
account the reaction kinematics and the slowing down of beam deuterons in the 
tritium/titanium target. Only one tally is defined for each input:

Tally n. 4
  A track length flux tally has been used to collect results in the cells
  corresponding to the activation foils in MCNP geometry. The tally has been
  multiplied in each input (with FM card) by the appropriate microscopic 
  reaction cross section, to obtain results in terms of number of reactions 
  per unit neutron from the source. No energy bins were used. Nuclear data for
  tally collection was taken from IRDFF dosimetry libraries. In the following,
  a list of the reactions considered for each activation foil material is
  reported:

  * Nb-93(n,2n)Nb-92
  * Ni-58(n,2n)Ni-57
  * Ni-58(n,p)Co-58
  * Fe-56(n,p)Mn-56
  * Al-27(n,a)Na-24
  * In-115(n,n')In-115m
  * Mn-55(n,g)Mn-56
  * Au-197(n,g)Au-198


.. seealso:: **Related papers and contributions:**

    * P. Batistoni, M. Angelone, W. Daenner, U. Fischer, L. Petrizzi, M. Pillon, A. santamarina, K. Seidel, "Neutronics Shield Experiment for ITER at the Frascati Neutron Generator FNG", 17th Symposium on Fusion Technology, Lisboa, Portugal, September 16-20, 1996.