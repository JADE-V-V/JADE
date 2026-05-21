=======================
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

The *result* concept
--------------------

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

Tally modifiers
---------------

The currently supported modifiers are:

* ``no_action``: no action is taken on the tally. No arguments are expected.
* ``volume``: a volume divisor is applied to the tally, obtained from a ``volumes.json`` file supplied with the bechmark inputs. No arguments are expected.
* ``mass``: a mass divisor is applied to the tally, obtained from a ``volumes.json`` file supplied with the bechmark inputs, and OpenMC ``xml`` files. No arguments are expected.
* ``scale``: the tally is scaled by a factor. The *factor* is expected as key argument and the provided value can 
  be either a float, and integer or a list (of floats or integers). 
* ``lethargy``: a neutron flux tally is expected and converted to a neutron flux per unit lethargy.
  No arguments are expected.
* ``by_energy``: a flux tally is expected and converted to a flux per unit energy.
  No arguments are expected.
* ``by_bin``: a flux tally is expected and converted to a flux per unit bin.
  The *column_name* is expected as key argument and the provided value has to be the name of the binning column in 
  the form of a string.
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

* ``add_column_with_dict``: adds new columns to the tally. Three keyargs needs to be passed:

  * *ref_column*: the name of the column used as reference to create the new columns.
  * *values*: a dictionary of values to be added to the new columns, taking as keys the values of ref_column with the same order.
  * *new_columns*: the names of the new columns.
  
* ``keep_last_row``: keeps only the last row of the tally. No arguments are expected. 
* ``groupby``: this implements the pandas groupby method. The keyargs to provide are:
  
  * *by*: the name of the column to group by. If 'all' the operation is performed on the
    whole dataframe.
  * *action*: the aggregation function to be applied. The currently supported aggregations are 'sum', 'mean', 'max', 'min'.
  
  If the column *by* is not present in the tally, the modifier will not act and a logging.debug() message is
  registered.

* ``delete_cols``: deletes columns from the tally. The keyarg to provide is *cols* which expects a list
  of column names to be deleted.

* ``format_decimals``: formats the decimals of the data contained in specific columns. A *decimals* dictionary is expected as a
  keyarg, where the keys should be the column names to be formatted and the values should be the corresponding number of decimals
  to keep.

* ``tof_to_energy``: converts the time-of-flight to energy. The tally is expected
  to be binned in time and a new column *Energy* will be created. 
  The used formula is:

  .. math::
  
    E = m \cdot \dfrac{1}{\sqrt{1-\dfrac{L}{\left( c \cdot t\right)^2}} - 1}

  where *E* is the energy in MeV, *m* is the mass of the particle in MeV/c^2, *L* is the distance between source and detector in meters,

  Two optional keyargs that can be passed are:

  * ``m``: mass of the particle in MeV/c^2. Default is the neutron one, 939.5654133.
  * ``L``: distance between source and detector in meters. Default is 1.0.

* ``select_subset``: selects a subset of the data. The keyargs to provide are:

  * *column*: the name of the column to be used for the subset selection.
  * *values*: list of values in *column* identifying the rows to be retained.

* ``cumulative_sum``: computes the cumulative sum of a specific column. The optional keyargs to provide are *column*, the name of the column
  to be used for the cumulative sum, and *norm*, a boolean indicating whether to normalize the result with respect to the total sum (a percentage is returned).
  If no *column* argument is provided, the cumulative sum is computed on the 'Value' column by default. The argument *norm* is True by default.

* ``gaussian_broadening``: applies Gaussian broadening to the 'Value' column. The optional keyarg to provide is *fwhm_frac*, 
  which specifies the fraction of the FWHM (Full Width at Half Maximum) to use for Gaussian broadening. This can be provided either 
  as a single float value, which will be applied uniformly to all energy bins, or as a list of float values with the same length as the 
  'Energy' column, allowing for a different broadening parameter for each energy bin. If not specified, the default value is 0.1 (10%).

More than one modifiers can be applied in series to a single tally.
If your benchmark requires a new modifier, please refer to :ref:`add_tally_mod`.

Concatenation options
---------------------

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
  The *results* do not have to be present in all benchmark cases/runs/transport codes. When they are not
  found, they are simply skipped.

.. note:: 
  To get an equivalent result to photon heating in MCNP, the photon, electron and positron heating must be 
  summed in OpenMC. This is all handled by the code and only the id of the *photon* heating tally needs to be provided
  in the raw config file.

In some cases it may be useful to produce certain results only from some cases/runs and
not from others. Or maybe different modifiers need to be applied in different runs.
An example may be the case of having a benchmark composed by two runs with the same tallies.
Nevertheless, in one run the geometry is slightly different from the other or the irradiation
scenario is different and a distinction is needed in the applied modifiers. In this case,
an optional parameter can be specified in the *result* config to specify a list of runs/cases
to which the configuration is applicable:

.. code-block:: yaml

  # Result configuration. the result name can contain spaces.
  result name specific for a run1:
    apply_to: [run1] # A list of runs/cases to which the configuration is applicable.
    concat_option: sum  # The concatenation option 'sum' is used.
    44: [[no_action, {}]]  # Example of tally that is left untouched. 44 is the tally identifier used in the transport code.
    46: [[scale, {"factor": 1e5}], [lethargy, {}]]  # Example of tally that is scaled and converted to flux per unit lethargy.

The *yaml* raw configuration file is read as a dictionary, which results in all *result names* (keys of the dictionary)
having to be different. However, if the *apply_to* option is specified, the string *apply_to#n*, where n is an integer, can be appended to the result name
to make it unique. JADE will delete this suffix when creating the .csv files, which allows to have the same *result name* for different subcases:

.. code-block:: yaml

  result name apply_to#1:
    apply_to: [run1]
    concat_option: sum  
    44: [[no_action, {}]]
    46: [[scale, {"factor": 1e5}], [lethargy, {}]]

  result name apply_to#2: # The result name is the same as the previous one, except for the suffix 'apply_to#2'.
    apply_to: [run2] 
    concat_option: sum 
    44: [[scale, {"factor": 1e5}]]  # Different modifiers are applied with respect to run1.
    46: [[lethargy, {}]]  # Different modifiers are applied with respect to run1.

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
