.. _futuredev:

###################
Future developments
###################

Many interesting developments may be added to JADE to expand its potential and
usage. Some of them are listed hereafter:

Eliminate dependency from Microsoft Office suite
================================================
The need for Excel and Word may be a limiting factor for the use of JADE.
Substituting the excel configuration files with .csv ones or a GUI is 
definitely feasible, much harder would be to substitute the Excel use that is
at the core of JADE post-processing. Either those parts of code are rewritten
in order to use open-source equivalents (e.g. OpenOffice) or a simplified 
version of the post-processing must be developed.

JADE may transition in the future to using an interactive web app for visualisation 
and analysis of results. This would remove the need for the office programs. 

Implementation of additional particle transport codes
=====================================================
Now that JADE has capability to run additional transport codes Serpent and OpenMC 
the framework is in theory available to expand this to other transport codes. 
This presents an opportunity to automate the running of the codes across the suite 
of benchmarks available in JADE. In the future cross-code comparison will be 
possible as part of the inherent post-processing.  

In particular, open source transport codes give significant additional 
benefits including:

* extend JADE's potential users pool;
* give the possibility to JADE not only to compare libraries but also to
  compare different MC code results using the same library;
* allow JADE to be used more effectively in libraries continuous integration.

Addition of benchmarks 
==============================
The number of computational and experimental benchmarks in the JADE suite is 
increasingly growing. This adds to the completeness of the JADE as a validation 
and verification tool. Benchmark contributions are welcomed and the code has been 
structured to facilitate additions in a straightforward manner. Guidance
for adding benchmarks to JADE is given in :ref:`customcompbench` and :ref:`customexpbench`.
General guidance for contributions to JADE is given in :ref:`codemod`.

Users wishing to add a benchmark to JADE should first raise an issue on the repository using 
the template for adding new benchmarks. 

Interface with benchmark repositories
======================================

Considerable work is often required to prepare experimental benchmarks for running in JADE.
This may include the modification of tallies or fixing small errors in input decks. These inputs 
are currently local to JADE. Ideally, there should exist a single reference database that permits
version control. Ways that JADE may interface with NEA and IAEA hosted repositories are currently being considered. 

**Further ideas for future development**

*	Development of an interactive web interface for plotting JADE post-processed data. 
*	Complete addition of OpenMC and Serpent for all benchmarks within JADE.
*	Integrating ACE file quality checks within JADE. Further JADE as a complete tool for both verification and validation. 
*	Production of weight windows required to run some of the benchmarks in JADE. This includes in MCNP, OpenMC and Serpent format. 
* Extend the suite of Utilities in JADE which are currently for MCNP to other transport codes. 

