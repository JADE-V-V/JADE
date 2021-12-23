############
JADE Testing
############

Following software developing best practices, JADE supports automating testing
of its code and continuous integration on GitHub.

Unit testing is performed through ``pytest`` while the code test coverage is
monitored through ``coverage``.

The automatic testing is performed each time there is a merge operation on the
main JADE branch on GitHub but at anytime the user may test the code throgh the
following steps:

#. Open an Anaconda prompt and activate jade environment;
#. Change directory to ``<JADE_root>\Code``;
#. run:
   
   ``pytest --cov-report html --cov=.``

This will automatically collect and run all tests contained in 
``<JADE_root>\Code\tests`` while also providing an html index with detailed
information about the code coverage that can be found in
``<JADE_root>\Code\htmlcov\index.html``.

The routine for continuous integration in GitHub are specified in
``<JADE_root>\Code\.github\workflows``.