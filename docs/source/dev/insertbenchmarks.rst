###################
Add a new benchmark
###################

The easiest way to contribute to JADE is to widen its benchmarks suite.

This section of the guide describes how to add custom benchmarks to the JADE suite.

Where should I put the benchmarks input files?
==============================================

The input files for the benchmarks do not reside in JADE repository. If your benchmark can be freely
distributed please upload it to the the IAEA open-source repository 
`here https://github.com/IAEA-NDS/open-benchmarks/tree/main/jade_open_benchmarks`_. You will find 
more detailed instructions on where to position the files directly in the repository.
In case your benchmark is SINBAD derived and you are a SINBAD user, consider adding it to the
new SINBAD GitLab repository (coming soon).
If none of the above cases apply but you still would like to have some form of version
control on your benchmark (strongly recommended), you can upload your input files to the
privatly hosted GitLab of Fusion For Energy.
For any doubt regarding the upload of benchmark inputs please contact davide.laghi@f4e.europa.eu.

Different transport codes have different needs. Hereafter, the main requirements for each type
of inputs are specified.

MCNP
----

- The input name shall be ``<benchmark_name>.i``
- weight windows file (if present) should be named ``wwinp``

D1SUNED
-------

- MCNP requirements apply
- A ``<benchmark_name>_irrad`` and ``<benchmark_name>_react`` files should also be provided.
  If the reac file is not provided, the code will generate one automatically. All the isotopes
  contained in the input will be translated to the activation library if there is at least
  one decay pathway that can result into one of the daughters listed in the irrad file.
- The benchmark input should not contain any ``STOP`` paramaters or ``NPS`` card.

OpenMC
------
TODO

Serpent
-------
TODO

Experimental Data
-----------------
Experimental data needs to be provided in the form of .csv files. These files should be named
exactly like the ones produced by the raw data processing and have the same structure.

Add the raw config file
=======================

The raw processing configuration file contains the instructions to transition from a transport-code
dependent and tally-based output to a .csv *result* which will be completely transport-code independent.
The objective of the processed raw data is to be a strong interface 
towards JADE post-processing but also towards other post-processing tools such as the
JAD web-app or, possibly, third-party apps. 

The starting point for the processing of the raw data is a number of parsed tallies. JADE processes the
different codes outputs and produces a pandas DataFrame for each tally of the simulation.
Only a fixed number of possible binnings are accepted and their name has been standardadized
across the different transport codes. The binnings are the following:

.. _allowed_binnings:

.. list-table:: Allowed binnings
        :widths: 50
        :header-rows: 1

        * - **Admissible column names**
        * - Energy
        * - Cells
        * - time
        * - tally
        * - Dir
        * - User
        * - Segments
        * - Cosine
        * - Cor A (not fully supported)
        * - Cor B (not fully supported)
        * - Cor C (not fully supported)

Raw data processing can be different depending on the transport code that is used. The files are located
at ``<JADE_root>/cfg/benchmarks_pp/raw``. When contributing to the JADE codebase, developers should
add their files in ``jade/resources/default_cfg/benchmarks_pp/raw``.
The raw data processing configuration files are written in YAML format. The name of the file must be the 
same name of the benchmark.

A *result* can be obtained from the concatenation of one or more tallies (i.e. DataFrames)
and the tallies themselves can be modified through the use of *modifiers*.
The currently supported modifiers are:

* ``no_action``: no action is taken on the tally. No arguments are expected.
* ``scale``: the tally is scaled by a factor. The *factor* is expected as key argument. 
* ``lethargy``: a neutron flux tally is expected and converted to a neutron flux per unit lethargy.
  No arguments are expected.
* ``by_energy``: a flux tally is expected and converted to a flux per unit energy.
  No arguments are expected.
* ``condense_groups``: takes a binned tallies and condenses into a coarser binning. Two keyargs needs to be passed:
  * *bins*: a list of floats representing the new bin edges.
  * *group_column*: the name of the binning column (e.g. 'Energy').
* ``replace``: replaces a column values based on a dictionary. Two keyargs needs to be passed:
  * *column*: the name of the column to be replaced.
  * *values*: a dictionary where the keys are the values to be replaced and the values are
    the new values.

More than one modifiers can be applied in series to a single tally.
If your benchmark requires a new modifier, please refer to :ref:`add_tally_mod`.

Once the modifiers have been applied, if the *result** is composed by more than one tally,
a concatenation option needs to be provided. The currently supported concatenation options are:

* ``no_action``: perform no concatenation operation. (used when only one tally is present)
* ``sum``: the tallies are summed.
* ``concat``: simple pd.concat() operation where the rows of one tally are added to the other.
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


.. _add_tally_mod:

Implement new tally modifier
----------------------------

It may be that your new benchmark requires a new tally modifier. Adding a new modifier to JADE is pretty simple.

#. Go to ``jade/config/raw_config.py`` and add your new modifier option to the ``TallyModOption`` enum class.
#. Add a function to modify the tally in ``jade/post/manipulate_tally.py``. This function should take as
    the only positional argument a dataframe (the tally). Keyword arguments can be added if needed. return type
    must be a pandas dataframe.
#. Link the function to the enum adding it to the ``MOD_FUNCTIONS`` dictionary that can be found in the same file.
#. Add a test for your new modifier in ``jade/tests/post/test_manipulate_tally.py``.
#. Add your new option to the available modifiers in the documentation.

.. _add_tally_concat:

Implement new tallies combinator
--------------------------------
If instead you need to add a new way to combine tallies, you should:

#. Go to ``jade/config/raw_config.py`` and add your new concat option to the ``TallyConcatOption`` enum class.
#. Add a function to concat the tallies in ``jade/post/manipulate_tally.py``. This function should take as
    the only positional argument a list of dataframes (the tallies). Return type must be a pandas dataframe.
#. Link the new function to the enum adding it to the ``CONCAT_FUNCTIONS`` dictionary that can be found in the same file.
#. Add a test for your new modifier in ``jade/tests/post/test_manipulate_tally.py``.
#. Add your new option to the available concat options in the documentation.

Add the excel config file
=========================

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
        * ``simple``: The starting data is simply the dataframe itself.
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
* ``change_col_names``: a dictionary that specifies the new names for the columns. The keys are the original column names
        and the values are the new names. This will be applied as a last operation before dumping the df.

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


Add the atlas config file
=========================

mandatory:

* ``results``: a list of *results* that are used in the table.
    These names must be the same as the ones used in the raw data configuration.
    The effect of selection more than one results is that all *result* dataframe are combined thanks
    to an extra column called "Result" that is added to the global dataframe.
* ``plot_type``: the type of plot to be produced. You can check which type of plots are
    available in JADE in the :ref:`plot_types` section.
* ``title``: title of the plot.
* ``x_label``: label of the x-axis.
* ``y_labels``: label of the y-axis (in some cases more than one label can be provided).
* ``x``: column name that will be used as the x-axis in the plot. Accepted names are listed in :ref:`allowed_binnings`.
* ``y``: column name that will be used as the y-axis in the plot. Accepted names are listed in :ref:`allowed_binnings`.

Optional:

* ``expand_runs``: By default true. If the benchmark consisted of more than one run, the results have been combined in the
  global results dataframe adding a 'Case' column. If expand_runs is set to true, the plot will be produced for each
  case/run separately.
* ``additional_labels``: a dictionary that specifies additional text boxes to be superimposed to the plot.
  It is a dictionary that can accept only two keys: 'major' and 'minor'. Major labels are bigger and placed
  inside a box. Major labels appear above the minor labels. The item associated to each key is a list of 
  tuples that have two elements. The first element is the text to be displayed and the second is the x position
  of the left corner of the text. Units are the ones of the x-axis of the plot.
* ``v_lines``: allows to add vertical lines to the plot. It is a dictionary that accepts only two keys:
  'major' and 'minor'. Major lines are thicker. The item associated to each key is a list of floats that
  indicate the x position of the line. Units are the ones of the x-axis of the plot.
* ``plot_args``: a dictionary that specifies the arguments to be passed to a specific plot type. The keys are the arguments
  names and the values are the arguments values. The list of plot_args parameters available in each plot
  are described in the plot gallery.
* ``rectangles``: TODO