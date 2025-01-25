.. _config_dev:

######################################
Additional config files for developers
######################################

Since JADE v4.0 to add a new banchmark to the JAD suite (being this computational or experimental) does
not require any additional code to be written but only the compilation of the benchmark configuration files.
These files control the run and post-processing of the benchmark.

Benchmark run configuration
===========================
These files are needed only for leakage-sphere like benchmarks. They can be found in
``<JADE_root>/cfg/benchmarks``. The vast majority of benchmarks will not require any kind
of configuration for their run.

Benchmark post-processing configuration
=======================================
Three configuration files are needed for each benchmark to be added to the JAD suite. These files
control the production of the raw data, the excel file production and plots atlas production.

Raw Data configuration
----------------------
Raw data processing can be different depending on the transport code that is used. The files are located
at ``<JADE_root>/cfg/benchmarks_pp/raw``. When contributing to the JADE codebase, developers should
add their files in ``jade/resources/default_cfg/benchmarks_pp/raw``.
The raw data processing configuration files are written in YAML format. The name of the file must be the 
same name of the benchmamrk.
The objective of the processed raw data (which will ultimately be a .csv table) is to be a strong interface 
towards JADE post-processing but also potentially towards other post-processing tools such as the
JAD web-app or third-party apps. This means that this is the endpoint of any transport code dependent coding.
After that, all logic will be transport code agnostic.

For this reason, the raw data processing introduces the concept of a *result*.
A *result* can be obtained from the concatenation of one or more tallies (i.e. transport code tallies) and these
tallies themselves can be modified through the use of *modifiers*. The currently supported modifiers are:

* ``no_action``: no action is taken on the tally. No arguments are expected.
* ``scale``: the tally is scaled by a factor. The *factor* is expected as key argument. 
* ``lethargy``: a neutron flux tally is expected and converted to a neutron flux per unit lethargy.
     No arguments are expected.
* ``by_energy``: a flux tally is expected and converted to a flux per unit energy.
     No arguments are expected.
* ``condense_groups``: takes a binned tallies and condenses into a coarser binning. Two keyargs needs to be passed:
     * *bins*: a list of floats representing the new bin edges.
     * *group_column*: the name of the binning column (e.g. 'Energy').

More than one modifiers can be applied in series to a single tally.
If your benchmark requires a new modifier, please refer to :ref:`add_tally_mod`.

Once the modifiers have been applied, if the *result** is composed by more than one tally,
a concatenation option needs to be provided. The currently supported concatenation options are:

* ``sum``: the tallies are summed.
* ``concat``: simple pd.concat() operation where the rows of one tally are added to the other.
* ``no_action``: perform no concatenation operation. (used when only one tally is present)
* ``subtract``: the tallies are substracted (in the order they are provided).
* ``ratio``: only two tallies are expected. The first is divided by the second.

If your benchmark requires a new way to combine tallies, please refer to :ref:`add_tally_concat`.

An example of a *result* configuration is shown below:

.. code-block:: yaml

  # Result configuration. the result name can contain spaces.
  result name:
    concat_option: sum  # The concatenation option 'sum' is used.
    44: [[no_action, {}]]  # Example of tally that is left untouched. 44 is the tally identifier used in the transport code.
    46: [[scale, {"factor": 1e5}], [lethargy, {}]]  # Example of tally that is scaled and converted to flux per unit lethargy.

Excel configuration
-------------------
The excel configuration files are located at ``<JADE_root>/cfg/benchmarks_pp/excel``. When contributing to the JADE codebase,
developers should add their files in ``jade/resources/default_cfg/benchmarks_pp/excel``.
These files are transport code independent and they act on the processed raw data. The configuration is written in YAML format.
The name of the file must be the same name of the benchmark. 
The excel configuration files are used to produce the excel file that will contain post-processed comparisons
between different code-lib simulation results.

The minimum unit for excel post-processing is the *table*. A table can be a single raw *result* or some kind of
combinations of them. In the configuration of each *table* the dev has to specify the *results* that are used
in the table, a type of comparisons (e.g. absolute difference), and then a number of options which will control
how the compared data is presented in the excel file.
When more than one *result* is used in a table, they all are combined in a single pandas dataframe and an 
extra column called "Result" is added to the dataframe to distinguish the different results.

The mandatory options to include in a *table* configurations are:

* ``results``: a list of *results* that are used in the table. These names must be the same as the ones used in
     the raw data configuration.
* ``comparison_type``: the type of comparison that is done between the *results* coming from two different lib-code couples.
     The currently supported comparisons are:
        * ``absolute``: the absolute difference between the two simulations.
        * ``percentage``: the percentage difference between the two simulations.
        * ``ratio``: the ratio between the two simulations.
* ``table_type``: the type of table that is produced. The currently supported types are:
        * ``pivot``: a pivot table is produced. This requires to specify also the ``value`` option.
* ``x``: the name of the column that will be used as the x-axis in the table.
* ``y``: the name of the column that will be used as the y-axis in the table.

The optional configurations that can be included in a *table* are:

* ``value``: to be provided only for pivot tables. This is the columns name that will be used for the pivot.
* ``add_error``: if True, the errors of both simulations will be added to the table.
* ``conditional_formatting``: a dictionary that specifies the values to be used as thresholds 
        for the conditional color formatting. As an example, if ``{"red": 20, "orange": 10, "yellow": 5}`` is
        provided, the table cells will be colored in red if the difference between the two simulations is greater than 20,
        in orange if it is greater than 10 and in yellow if it is greater than 5 and green otherwise.

An example of a *table* configuration is shown below:

.. code-block:: yaml

  comparison %:  # name that will appear in the excel sheet
    results:  # the list of raw *results* that are used in the table
        - Leakage neutron flux
        - Leakage photon flux
        - Neutron heating
        - Photon heating
        - T production
        - He ppm production
        - DPA production
    comparison_type: percentage
    table_type: pivot
    x: Case  # this is the column identify the different cases/runs in a multi-run benchmark
    y: [Result, Energy]  # note that also multi-index y axis are supported for pivot tables
    value: Value
    add_error: true
    conditional_formatting: {"red": 20, "orange": 10, "yellow": 5}