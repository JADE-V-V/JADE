Add the excel config file
=========================

The excel configuration files are located at ``<JADE_root>/cfg/benchmarks_pp/excel``. When contributing to the JADE codebase,
developers should add their files in ``jade/resources/default_cfg/benchmarks_pp/excel``.
These files are transport code independent and they act on the processed raw data. The configuration is written in YAML format.
The name of the file must be the same name of the benchmark. 
The excel configuration files are used to produce the excel file that will contain post-processed comparisons
between different code-lib simulation results.

The *table* concept
-------------------

The minimum unit for excel post-processing is the *table*. A table can be a single raw *result* or some kind of
combinations of them. In the configuration of each *table* the dev has to specify the *results* that are used
in the table, a type of comparisons (e.g. absolute difference), and then a number of options which will control
how the compared data is presented in the excel file.
When more than one *result* is used in a table, they all are combined in a single pandas dataframe and an 
extra column called "Result" is added to the dataframe to distinguish the different results.
Additionally, when a benchmark consists of more than one run, the results are combined in a single dataframe
and an extra column called "Case" is added to the dataframe to distinguish the different runs.

The **mandatory options** to include in a *table* configurations are:

* ``results``: a list of *results* that are used in the table. These names must be the same as the ones used in
  the raw data configuration.
* ``comparison_type``: the type of comparison that is done between the *results* coming from two different lib-code couples.
  The currently supported comparisons are:
  
  * ``absolute``: the absolute difference between the two simulations.
  * ``percentage``: the percentage difference between the two simulations.
  * ``ratio``: the ratio between the two simulations.
  * ``chi_squared``: the chi-squared difference between computational and experimental results.
* ``table_type``: the type of table that is produced. The currently supported types are:
  
  * ``simple``: The starting data is simply the dataframe itself.
  * ``pivot``: a pivot table is produced. This requires to specify also the ``value`` option.
  * ``chi_squared``: a specific implementation of the *simple* table type that is used to
    report the chi-squared value of a C/E result.

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