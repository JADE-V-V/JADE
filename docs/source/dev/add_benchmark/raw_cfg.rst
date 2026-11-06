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
* ``cooling_time``: converts elapsed time to seconds after shutdown. The required
  *shutdown_time* argument is a finite, non-negative time in seconds. The tally's
  *time* column must be finite and strictly increasing, and include the shutdown
  endpoint within ``1e-6`` seconds. Rows at or before that endpoint are removed;
  the remaining times have *shutdown_time* subtracted. Values and errors are
  unchanged, and no interpolation is performed. This modifier checks the
  endpoint, not whether irradiation actually ends there.

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

* ``gaussian_broadening``: applies Gaussian broadening to the 'Value' column. 
  Three parameters, two of which are mandatory, are expected:

    * *column* (*str*): the name of the column to be used as a reference for the broadening (e.g., "Energy" or "Time").
    * *integral* (Optional, *bool*): boolean indicating whether the provided spectra ('Value' column in the tally) is bin-integrated (equivalently, non-normalized previously using either the *by_energy* or 
      *by_bin* tally modifiers). Default is false (differential). If integral spectra is provided, it will be normalized, the broadening will be applied, and the result will be bin-integrated before being returned.
      The broadening will be applied to the bin-integrated values.
    * *bins* (*dict*): dictionary specifying the broadening scaling factor to be applied for each *column* bin range. The keys are the 
      successive upper *column* range limits (*str*), and the values are dictionaries which require a key indicating the type of scaling (``no_scaling``, ``linear``, 
      ``square``, or ``square_root``) and two values: the first one is ``fwhm_frac`` (the full width at half maximum fraction, *float* or *list[float]*), and the second one is ``Ref`` (in the units of ``column``). The ``Ref`` value is only required 
      if a scaling option different from ``no_scaling`` is used. The definition of this dictionary allows to assign different scaling
      factors to different *column* ranges independently.
    
  For example:

  .. code-block:: yaml

    - [gaussian_broadening, {
        'column': 'Energy',
        'bins':{
        '1.0':{'no_scaling':{'fwhm_frac': 0.0}}, 
        '4.97':{'no_scaling':{'fwhm_frac': [0.035, 0.0805]}},
        '10.00':{'square':{'fwhm_frac': 0.0525, 'Ref': 8.0}},
        },
        'integral': false
        }]

  In the example above, the response broadening is applied to differential energy spectra.
  For energies lower or equal than 1.0 MeV, no gaussian broadening is applied (because ``fwhm_frac`` is 0.0).
  For energies between 1.0 MeV and 4.97 MeV (included), no scaling is applied during the gaussian broadening. In this energy range, there are 2 energy bins in the tally: the lower one gets a FWHM of 3.5% 
  and the upper one gets a FWHM of 8.05%.
  For energies higher than 4.97 MeV and up to 10.0 MeV, a square scaling with a reference energy of 8.0 MeV (peak maximum) is applied in the broadening (with FWHM of 5.25%).

  The experimental spectra are affected by the resolution of the measurements. This tally modifier allows for the inclusion of resolution broadening effects using a 
  gaussian approximation. The resolution broadening is governed by the following convolution integral:
  
.. math::

  F(x) = \int F_m(x-u)\,p(u)\,du
  \tag{4}

where:

  * :math:`F`: resolution-broadened spectrum,
  * :math:`F_m`: calculated spectrum,
  * :math:`p(u)`: resolution-broadening function.

In this case, :math:`p(u)` is a gaussian function, which can include a scaling factor to account for the resolution dependence on the reference variable (e.g., energy or time):

.. math::

   p(u) = \frac{1}{\sqrt{2\pi}\,\sigma\,s}
          \exp\left[-\frac{u^2}{2(s\sigma)^2}\right]

where :math:`s` is the scaling factor. This tally modifier allows for three
different types of scaling:

* ``linear``: :math:`s = \frac{x}{\text{Ref}}`,
* ``square``: :math:`s = \left(\frac{x}{\text{Ref}}\right)^2`,
* ``square_root``: :math:`s = \sqrt{\frac{x}{\text{Ref}}}`,

where :math:`x` is the reference variable (e.g., energy or time) and
:math:`\text{Ref}` is the reference value (peak maximum) used for scaling.

* ``response_broadening``: broadens differential spectra ('Value' column in tallies) using a user-defined response function. 
  Five parameters, two of which are mandatory, are expected:

  * *column* (*str*): the name of the column to be used as a reference for the broadening (e.g., "Energy" or "Time").
  * *response_bins* (Optional, *list* or *np.ndarray*): list of bins of the response function (corresponding to the values provided in *response_values*). The bins must be expressed relative 
    to the peak maximum of the spectra (negative values indicate bins below the peak, positive values indicate bins above the peak). These bins don't need to be the same as the tally bins.
  * *response_values* (*list* or *np.ndarray*): list of response function values corresponding to the bins specified in *response_bins*. 
  * *integral* (Optional, *bool*): boolean indicating whether the provided spectra ('Value' column in the tally) is bin-integrated (equivalently, non-normalized previously using either the *by_energy* or 
    *by_bin* tally modifiers). Default is false (differential). If integral spectra is provided, it will be normalized, the broadening will be applied, and the result will be bin-integrated before being returned.
    The broadening will be applied to the bin-integrated values.
  * *scaling* (Optional, *dict*): dictionary specifying the broadening scaling factor to be applied for each *column* bin range. The keys are the 
    successive upper *column* range limits (*str*), and the values are dictionaries which require a key indicating the type of scaling (``no_scaling``, ``linear``, 
    ``square``, or ``square_root``) and a value ``Ref`` (*float*, in the units of ``column``) if a scaling option different from ``no_scaling`` is used. If this parameter
    is not provided, no scaling factor is applied anywhere in the broadening of the spectra. The definition of this dictionary allows to assign different scaling
    factors to different *column* ranges independently.
  
  For example:

  .. code-block:: yaml

     - [response_broadening, {column: Energy, integral: true,
                              response_bins: [5.6, 9.3, 11.7],
                              response_values: [0.234, 0.657, 0.456],
                              scaling: {4.0: {"no_scaling": {}}, 12.0: {"linear": {"Ref": 8.0}}}}]

  In the example above, the response broadening is applied to non-normalized energy spectra.
  The response function is provided using the *response_bins* and *response_values* parameters.
  For energies lower or equal than 4.0 MeV, no scaling is applied during the broadening. 
  For energies higher than 4.0 MeV and up to 12.0 MeV, a linear scaling with a reference energy of 8.0 MeV 
  (peak maximum) is applied in the broadening.

  The same convolution integral as the one described for the *gaussian_broadening* tally modifier is applied when using this 
  tally modifier as well. However, in this case, the resolution-broadening function :math:`p(u)`: is the
  response function provided by the user. The scaling factors available are the same as for the *gaussian_broadening* tally modifier.

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
