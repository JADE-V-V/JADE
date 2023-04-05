.. _testing:

#############################
JADE CI and automatic testing
#############################

Brief introduction
------------------

Following software developing best practices, JADE supports automating testing
of its code and Continuous Integration (CI) on GitHub. These concepts are briefly
described hereafter.

There are many ways to perform automatic testing on code.
The choice fell upon **unit testing** which is commonly used in software development
and consists of stress-testing single units of code, i.e., the minimal portion
of the software that have an autonomous operation like single classes or methods.
These set of tests are usually defined with the help of specific libraries and
are automated in order to be executed frequently. 

This approach guarantees a series of advantages:

* it is easier to accept new features from new developers because the risk of
  them breaking the code will be way lower if it passed the tests;
* it generally improves the reliability of the code;
* it enhances the stability of the code through the years, since, when a bug is
  found, it is good practice to add a specific test able to catch it and ensure
  that it will never present itself again in the future;
* it generally improves the quality of the code since unit testing forces
  developers to write code in a more schematic and clear way (retrofitting unit
  testing to code already written, on the contrary, can cause a bit of an
  headache);
* if done correctly, it can actually speed up the development of new features
  when the complexity of the code is high due to a more easy identification of
  the issues (i.e. the failed tests).

Unit testing is also a key component of the so-called Continuous Integration (CI)
which is needed when many developers start to collaborate to the same project.
In order to do so, each of them will work on a local copy of the code which will
gradually become less representative of the master repository due to the
constant modifications applied by others. If a single developer waits too much
before committing his modifications to the master repository, the main code
could have become so different that trying to merge a commitment with success
(i.e. without conflicts) could become more time consuming than just restart the
development of the new feature from scratch. This situation is usually referred
to as “integration hell” or “merge hell”. In short, continuous integration
consists of committing your code modifications fast and often, trying to avoid
at all costs integration hell and save effort and time. Tools like GitHub are
instrumental to the diffusion of the CI philosophy thanks to it many
collaborative features and robust version control. Nevertheless, key principles
of the process are considered to be the automatic build and automatic testing
of the code which need to be performed each time the master code is adjourned.

Testing in JADE
---------------
Unit testing in JADE is defined and run with the help of the ``pytest`` module
while the code test coverage is monitored through the ``coverage`` one.

The automatic testing is performed each time there is a merge operation on the
main JADE branch on GitHub although, at any time, the user may test the code throgh the
following steps:

#. Open an Anaconda prompt and activate jade environment;
#. Change directory to ``<JADE_root>\Code``;
#. run:
   
   ``pytest --cov=. --cov-report html -cov-config=.coveragerc``

This will automatically collect and run all tests contained in 
``<JADE_root>\Code\tests`` while also providing an html index with detailed
information about the code coverage that can be found in
``<JADE_root>\Code\htmlcov\index.html``.

The routine for continuous integration in GitHub are specified in
``<JADE_root>\Code\.github\workflows``.