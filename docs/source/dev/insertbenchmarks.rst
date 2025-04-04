.. _add_benchmark:

###################
Add a new benchmark
###################

The easiest way to contribute to JADE is to widen its benchmarks suite.

This section of the guide describes how to add custom benchmarks to the JADE suite.

Where should I put the benchmarks input files?
==============================================

The input files for the benchmarks do not reside in the JADE repository. If your benchmark can be freely
distributed please upload it to the the IAEA open-source repository 
`here <https://github.com/IAEA-NDS/open-benchmarks/tree/main/jade_open_benchmarks>`_. You will find 
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

.. note:: 
  If the benchmark input uses special dosimetry libraries that should not be translated, their suffix
  should be added to the ``DOSIMETRY_LIBS`` list in ``jade/helper/constants.py``.

D1SUNED
-------

- MCNP requirements apply
- A ``<benchmark_name>_irrad`` and ``<benchmark_name>_react`` files should also be provided.
  If the reac file is not provided, the code will generate one automatically. All the isotopes
  contained in the input will be translated to the activation library if there is at least
  one decay pathway that can result into one of the daughters listed in the irrad file.
- The benchmark input should not contain any ``STOP`` parameters or ``NPS`` card.

OpenMC
------
- The names of the input files should be ``settings.xml``, ``geometry.xml``, ``tallies.xml`` and ``materials.xml``.
- The tallies IDs should be explicitly fixed when creating the ``tallies.xml`` file. This prevents
  OpenMC from creating them automatically and, thus, potentially changing them between different runs
  of a same benchmark. If possible, the tallies identifiers should be the same as the ones used in the
  other transport codes.

Serpent
-------
TODO

Experimental Data
-----------------
Experimental data needs to be provided in the form of *.csv* files. These files should be named
exactly like the ones produced by the raw data processing and have the same structure. The Experimental
results are stored in the repository with the input files in an *exp_results* folder. E.g. for those
benchmarks in the IAEA repository, the experimental results can be found here: `here <https://github.com/IAEA-NDS/open-benchmarks/tree/main/jade_open_benchmarks/exp_results>`_ 

Modify the default run_cfg file
===============================

In order for the new benchmarks to appear among the available ones when running the JADE run
GUI, it needs to be added to the default run configuration file. The file can be
found at ``jade/resources/default_cfg/run_cfg.yaml``.

This is an example of yaml code to be added to the file in order to add a benchmark:

.. code-block:: yaml

  benchmark_name:  # this is the ID of the benchmark. Used in all cfg related files
    codes: # Leave empty like in the example
      d1s: []
      mcnp: []
      openmc: []
      serpent: []
    custom_input: # leave empty
    description: A short description of the benchmark
    nps: 5e7  # default value of number of histories to simulate
    only_input: false  # leave false

Add the raw config file
=======================

.. note::
  JADE makes significant use of YAML configuration file. In YAML it is possible to define aliases
  in order to avoid repetition of the same information. Here is an example:

  .. code-block:: yaml

    # Define the alias
    key_dict: &my_alias
      key1: value1
      key2: value2

    # Use the alias
    my_key: *my_alias
  
  JADE allows the use of aliases on condition that the name starts with un underscore or it is omitted.
  This is to avoid confusion with the other configuration keys. For instance, a correct use of aliases
  would look like:

  .. code-block:: yaml

    _key_dict: &my_alias
      key1: value1
      key2: value2

  or

  .. code-block:: yaml

    &my_alias
      key1: value1
      key2: value2

The raw processing configuration file contains the instructions to transition from a transport-code
dependent and tally-based output to a .csv *result* which will be completely transport-code independent.
The objective of the processed raw data is to be a strong interface 
towards JADE post-processing but also towards other post-processing tools such as the
JADE web-app or, possibly, third-party apps. 

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
        * - Cells-Segments
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
* ``scale``: the tally is scaled by a factor. The *factor* is expected as key argument and the provided value can 
  be either a float, and integer or a list (of floats or integers). 
* ``lethargy``: a neutron flux tally is expected and converted to a neutron flux per unit lethargy.
  No arguments are expected.
* ``by_energy``: a flux tally is expected and converted to a flux per unit energy.
  No arguments are expected.
* ``condense_groups``: takes a binned tallies and condenses into a coarser binning. 
  Errors are combined in squared root of sum of squares.
  Two keyargs needs to be passed:
  
  * *bins*: a list of floats representing the new bin edges.
  * *group_column*: the name of the binning column (e.g. 'Energy').
* ``replace``: replaces a column values based on a dictionary. Two keyargs needs to be passed:

  * *column*: the name of the column to be replaced.
  * *values*: a dictionary where the keys are the values to be replaced and the values are the new values.

* ``add_column``: adds a new column to the tally. Two keyargs needs to be passed:

  * *column*: the name of the new column.
  * *values*: a list of values to be added to the column. A single value can also be provided.

* ``keep_last_row``: keeps only the last row of the tally. No arguments are expected. 
* ``groupby``: this implements the pandas groupby method. The keyargs to provide are:
  
  * *by*: the name of the column to group by. If 'all' the operation is performed on the
    whole dataframe.
  * *action*: the aggregation function to be applied. The currently supported aggregations are 'sum', 'mean', 'max', 'min'.
  
  If the column *by* is not present in the tally, the modifier will not act and a logging.debug() message is
  registered.

* ``delete_cols``: deletes columns from the tally. The keyarg to provide is *cols* which expects a list
  of column names to be deleted.

* ``format_decimals``: formats the decimals of the data contained in specific columns. A 'decimals' dictionary is expected as a 
  keyarg, where the keys should be the column names to be formatted and the values should be the corresponding number of decimals 
  to keep. 

More than one modifiers can be applied in series to a single tally.
If your benchmark requires a new modifier, please refer to :ref:`add_tally_mod`.

Once the modifiers have been applied, if the *result* is composed by more than one tally,
a concatenation option needs to be provided. The currently supported concatenation options are:

* ``no_action``: perform no concatenation operation. (used when only one tally is present)
* ``sum``: the tallies are summed.
* ``concat``: simple pd.concat() operation where the rows of one tally are added to the other.
* ``subtract``: the tallies are subtracted (in the order they are provided).
* ``ratio``: only two tallies are expected. The first is divided by the second.

If your benchmark requires a new way to combine tallies, please refer to :ref:`add_tally_concat`.

An example of a *result* configuration is shown below:

.. code-block:: yaml

  # Result configuration. the result name can contain spaces.
  result name:
    concat_option: sum  # The concatenation option 'sum' is used.
    44: [[no_action, {}]]  # Example of tally that is left untouched. 44 is the tally identifier used in the transport code.
    46: [[scale, {"factor": 1e5}], [lethargy, {}]]  # Example of tally that is scaled and converted to flux per unit lethargy.

.. note:: 
  The *results* do not have to be present in all benchmark cases/runs. When they are not
  found, they are simply skipped.

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

The **mandatory options** to include in a *table* configurations are:

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

  Examples of the layout of these tables can be found in the :ref:`table_types` section.
  
  In case a new table type was needed, please refer to :ref:`add_table_type`.
* ``x``: the name of the column that will be used as the x-axis in the table.
* ``y``: the name of the column that will be used as the y-axis in the table.

The **optional configurations** that can be included in a *table* are:

* ``value``: to be provided only for pivot tables. This is the columns name that will be used for the pivot.
* ``add_error``: if True, the errors of both simulations will be added to the table.
* ``conditional_formatting``: a dictionary that specifies the values to be used as thresholds 
  for the conditional color formatting. As an example, if ``{"red": 20, "orange": 10, "yellow": 5}`` is
  provided, the table cells will be coloured in red if the difference between the two simulations is greater than 20,
  in orange if it is greater than 10 and in yellow if it is greater than 5 and green otherwise.
* ``change_col_names``: a dictionary that specifies the new names for the columns. The keys are the original column names
  and the values are the new names. This will be applied as a last operation before dumping the df.
* ``subsets``: it is used to select only certain results. It is a list of dictionary. One dictionary
  needs to be provided for each *result* for which only a subset needs to be selected. The keys
  of each dictionary are:

  * *result*: the name of the *result* for which the subset is selected.
  * *values*: a dictionary that will be used to select the subset. Keys are the colum names and items are
    the values that will be used to select the subset in that specific column.

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
The atlas configuration files are located at ``<JADE_root>/cfg/benchmarks_pp/atlas``. When contributing to the JADE codebase,
developers should add their files in ``jade/resources/default_cfg/benchmarks_pp/atlas``.
These files are transport code independent and they act on the processed raw data. The configuration is written in YAML format.
The name of the file must be the same name of the benchmark. 
The excel configuration files are used to produce the excel file that will contain post-processed comparisons
between different code-lib simulation results.

The minimum unit for atlas post-processing is the *plot*. A plot can be produced from a single raw *result* or some kind of
combinations of them.

The **mandatory options** for the *plot* configuration are:

* ``results``: a list of *results* that are used in the table.
  These names must be the same as the ones used in the raw data configuration.
  The effect of selection more than one results is that all *result* dataframe are combined thanks
  to an extra column called "Result" that is added to the global dataframe.
* ``plot_type``: the type of plot to be produced. You can check which type of plots are
  available in JADE in the :ref:`plot_types` section. In case a new plot is needed, please
  refer to :ref:`add_plot_type`.
* ``title``: title of the plot.
* ``x_label``: label of the x-axis.
* ``y_labels``: label of the y-axis (in some cases more than one label can be provided).
* ``x``: column name that will be used as the x-axis in the plot. Accepted names are listed in :ref:`allowed_binnings`.
* ``y``: column name that will be used as the y-axis in the plot. Accepted names are listed in :ref:`allowed_binnings`.

**Optional configuration** options are:

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
* ``recs``: This option allows to colour part of the plot with rectangles. A list of rectangles options 
  should be provided. Rectangle options must be a list/tuple of (in order), the name of the region (will
  appear in an additional legend), the colour of the rectangle, the x_min and x_max delimiting the region.
* ``subsets``: it is used to select only certain results. It is a list of dictionary. One dictionary
  needs to be provided for each *result* for which only a subset needs to be selected. The keys
  of each dictionary are:

  * *result*: the name of the *result* for which the subset is selected.
  * *values*: a dictionary that will be used to select the subset. Keys are the colum names and items are
    the values that will be used to select the subset in that specific column.

* ``select_runs``: This option allows
  to specify a regex pattern (in string format). Only the cases/runs that match the pattern will be plotted.

An example of plot configuration is shown below:

.. code-block:: yaml

  Wave plots (Isotopes):
    results:  
      - Leakage neutron flux (total)
      - Leakage photon flux
      - SDDR
    plot_type: waves
    title: Ratio wave plots
    x_label: Zaid and MT value
    y_labels: ''
    x: Case
    y: Value
    expand_runs: false
    plot_args:
      limits: [0.5, 1.5]
      shorten_x_name: 2
    select_runs: SphereSDDR_\d+_[A-Za-z]+-\d+_

Implement new functionalities
=============================

In the (hopefully) rare case that your new benchmarks requires either new modifiers, new concatenation options,
new table types or new plot types, you will need to implement new functionalities in the JADE codebase.
The bits of code to be added are well isolated from the rest of the framework. The following sections
describe how to implement these new features in JADE.

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

.. _add_table_type:

Implement a new table type
--------------------------

The following are the steps to add a new table type to JADE:

#. Go to ``jade/config/excel_config.py`` and add your new table type to the ``TableType`` enum class.
#. Extend the abstract ``Table`` class that can be found in ``jade/post/excel_routines.py``. The only method
   that needs to be re-implemented is the ``_get_sheet()`` one, which returns a list of pands dataframes.
   to be added to the excel. Have a look to the other table classes in the same file for inspirations and
   best practices.
#. Connect your new table class with the corresponded table type enum in the ``TableFactory`` class that
   can be found in the same file.
#. Add a test for your new table in ``jade/tests/post/test_excel_routines.py``.
#. Add your new table type to the available table types in the documentation.

.. _add_plot_type:

Implement a new plot type
-------------------------

The following are the steps to add a new plot type to JADE:

#. Go to ``jade/config/atlas_config.py`` and add your new plot type to the ``PlotType`` enum class.
   In case your new plot type requires specific plots arguments these can be passed to the plot
   through the ``plot_args`` dictionary.
#. Extend the abstract ``Plot`` class that can be found in ``jade/post/plotter.py``. The only method
   that needs to be re-implemented is the ``_get_figure()`` one, which returns the matplotlib figure.
   Have a look to the other plot classes in the same file for inspirations and best practices.
#. Connect your new plot class with the corresponded plot type enum in the ``PlotFactory`` class that
   can be found in the same file.
#. Add a test for your new plot in ``jade/tests/post/test_plotter.py``.
#. Add your new plot type to the available plot types in the documentation. 