#######################
Post-Processing Gallery
#######################


Table types
===========


.. _plot_types:

Plot types
==========

binned
------

plot_args:

* ``show_error``: if True, an additional subplot is added that includes the statistical error associated to
  the plotted values.
* ``show_error``: if True, an additional subplot is added that includes the statistical error associated to
  the plotted values.
* ``show_CE``: if True, an additional subplot is added that includes the C/E values associated to the plotted values.
* ``subcases``: a list of subcases to be plotted. The first value is the name of the column that identify the
  subcasese while the second value is a list of the subcases to be plotted. The different cases will be plotted
  all in the same subplot.
* ``scale_subcases``: if true and subcases are present, it scale each subsequent subcase bu 1e-1 to fit them all
  in the same subplot. Default is false.
* ``xscale``: The scale of the x-axis. Every argument that could be passed to the matplotlib function
  ``set_xscale()`` is accepted. Common ones are 'linear' or 'log'. Default is 'log'.

ratio
-----

plot_args

* ``split_x``: if True, the x-axis is split in two parts. This is useful if a portion of the x-axis results
  are not interesting and need to be omitted. It is a tuple/list of two values. The first value is
  interpreted as the x max limit of the left subplot while the second value is interpreted as the x min limit of the
  right subplot.

C/E
---

plot_args

* ``style``: either 'step' or 'point'. If 'step', the plot is a step plot. If 'point', the plot is a scatter plot.
* ``ce_limits``: define a minimum and maximum limit for the C/E plot. The first value is interpreted as the y min limit
  of the plot while the second value is interpreted as the y max limit of the plot. Triangles are plotted on the
  limit line in case the data exceeds it.
* ``subcases``: a list of subcases to be plotted. The first value is the name of the column that identify the
  subcasese while the second value is a list of the subcases to be plotted. This will cause the plot to be split
  in as many rows as the number of subcases.
* ``shorten_x_name``: this type of plots can be categorical. In the event of using the 
  cases as x axis, the long names of the benchmark runs can become problematic. This option
  will split the name of the benchmark run on the '_' symbols and retain only the last N chunks
  where N is the specified *shorten_x_name* value.
* ``rotate_ticks`` if set to True, the x-axis ticks are rotated by 45 degrees. default is False.
* ``xscale``: The scale of the x-axis. Every argument that could be passed to the matplotlib function
  ``set_xscale()`` is accepted. Common ones are 'linear' or 'log'. Default is 'linear'.

Waves
-----

plot_args

* ``limits``: a tuple of two values that define the limits of the plot. The first value is the y min limit while the
  second value is the y max limit.
* ``shorten_x_name``: this type of plots are often categorical. In the event of using the 
  cases as x axis, the long names of the benchmark runs can become problematic. This option
  will split the name of the benchmark run on the '_' symbols and retain only the last N chunks
  where N is the specified *shorten_x_name* value.

Barplot
-------

plot_args

* ``maxgroups``: indicates the maximum number of values that are plotted in a single row (to avoid overcrowding).
  by default it is set to 20.
* ``log``: if True, the y-axis is set to log scale. Default is False. The code also analyses the data to be plotted
  and if the values span in less than 2 order of magnitude the log scale is not applied.