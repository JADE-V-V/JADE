################
Developers Guide
################

With the release of JADE v4.0.0 the architecture of the software has been substantially revisited
in order to make it easier for new contributors to onboard the project.

A new feature from a developer can essentially be categorized into one of the following categories: 

1) adding a new benchmark only through configuration files (vast majority of case)
2) adding a new benchmark that require a new types of plots/tables (should be a reduced number of cases)
3) adding a new transport code (quite rare event)

In case 1) no additional code whatsoever is required. The developer only need to provide suitable 
configuration files to control the run and post-processing of the benchmark.
In case 2) some isolated functions will need to be added to the codebase to handle the new types of plots/tables.
In case 3) a new transport code will need to be added to the codebase. This is a more complex task
but it should still be much easier than it was in the past as only extension of already existing
classes are required.

.. toctree::
    :maxdepth: 2
    :caption: General guidelines
    
    ./workflow
    ./testing

.. toctree::
    :maxdepth: 2
    :caption: Add a new benchmark
    
    ./architecture_overview
    ./insertbenchmarks
    ./pp_gallery
    ./add_transport_code
