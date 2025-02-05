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

ratio
-----

plot_args

* ``split_x``: if True, the x-axis is split in two parts. This is useful if a portion of the x-axis results
     are not interesting and need to be omitted. It is a tuple/list of two values. The first value is
     interpreted as the x max limit of the left subplot while the second value is interpreted as the x min limit of the
     right subplot.