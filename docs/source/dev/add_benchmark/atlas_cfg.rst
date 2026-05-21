Add the atlas config file
=========================
The atlas configuration files are located at ``<JADE_root>/cfg/benchmarks_pp/atlas``. When contributing to the JADE codebase,
developers should add their files in ``jade/resources/default_cfg/benchmarks_pp/atlas``.
These files are transport code independent and they act on the processed raw data. The configuration is written in YAML format.
The name of the file must be the same name of the benchmark. 
The excel configuration files are used to produce the excel file that will contain post-processed comparisons
between different code-lib simulation results.

The *plot* concept
-------------------

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
* ``xlimits`` : a tuple with the lower and upper limits for the x-axis to apply.
  If not set, the limits will be set automatically (preferred option).
* ``ylimits`` : a tuple with the lower and upper limits for the y-axis to apply.
  If not set, the limits will be set automatically (preferred option).


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