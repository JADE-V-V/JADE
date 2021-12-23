###################
Future developments
###################

Many interesting developments may be added to JADE to expand its potential and
usage. Some of them are listed hereafter:

Eliminate dependency from Microsoft Office suite
================================================
The need for Excel and Word may be a limiting factor for the use of JADE.
If substituing the excel configuration files with .csv ones or a GUI is 
definitely feasible, much harder would be to substitute the Excel use that is
at the core of JADE post-processing. Either those parts of code are rewritten
in order to use open-source equivalents (e.g. OpenOffice) or a simplified 
version of the post-processing must be developed.

Migration to Linux system
=========================
A great portion of science is nowadays run on Linux operative systems.
JADE is entirely written in Python, which should be easily portable to any
major OS system. Nevertheless,
key modules like ``xlwings`` or ``python-docx`` which are used respectively
to interact with Excel and Word do not fully support Linux operative systems.

Implementation of open-source Monte Carlo codes
===============================================
The science world is more and more going in the direction of open-source
software. Currently, in order to use JADE, a valid license of MCNP is
necessary, and this may be a huge limiting factor for its usage. Implementing
open-source MC code capabilities in JADE (such as OpenMC) would benefit
the JADE project in many ways like:

* extend JADE's potential users pool;
* give the possibility to JADE not only to compare libraries but also to
  compare different MC code results using the same library;
* allow JADE to be used more effectively in libraries continuous integration.