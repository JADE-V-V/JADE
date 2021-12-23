##################
JADE in a nutshell
##################

.. image:: img/scheme.png
    :width: 600

JADE is a new tool for nuclear libraries V&V.
Brought to you by NIER, University of Bologna (UNIBO) and Fusion For Energy (F4E).
JADE is an open source, Python 3 based software able to:

* automatically build a series of MCNP input file using different nuclear
  data libraries;
* sequentially run simulations on such inputs;
* automatically parse and post-process all the generated MCNP outputs
  (e.g. mctal and fmesh).

The benchmarks implemented by default are divided between computational
and experimental benchmarks. The post-processing output includes:

* raw data in .csv files containing the entire tallied output from the
  simulations;
* formatted Excel recap files;
* Word and PDF atlas collecting the plots generated during the post-processing.

Additional JADE features are:

* the possibility to implement user-defined benchmarks;
* operate on the material card of an MCNP input (e.g. create material mixtures, 
  translate it to a different nuclear data library or switch between atom and
  mass fraction);
* print a recap of the material composition of an MCNP input;
* modify the suffix of .ace library;
* produce default reaction file for D1S-UNED MCNP patch inputs.

When using JADE for scientific publications you are kindly encouraged to cite the following papers:

* Davide Laghi et al, 2020, "JADE, a new software tool for nuclear fusion data libraries verification & validation",
  Fusion Engineering and Design, **161** 112075, doi: https://doi.org/10.1016/j.fusengdes.2020.112075.
* D. Laghi, M. Fabbri, L. Isolan, M. Sumini, G. Shnabel and A. Trkov, 2021,
  "Application Of JADE V&V Capabilities To The New FENDL v3.2 Beta Release",
  *Nuclear Fusion*, **61** 116073. doi: https://doi.org/10.1088/1741-4326/ac121a

For additional information contact: d.laghi@nier.it

For additional information on future developments please check the issues list on the
GitHub repository [link].