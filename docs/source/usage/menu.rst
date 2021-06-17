.. _menu:

#######################
Usage
#######################
Once JADE is correctly configured
(for additional details see :ref:`config`), the application can be started
with:

``python main.py``

The main menu is loaded at this point:

.. image:: ../img/main_menu.png
    :width: 400

This menu allows users to interact with the tool directly from the
command prompt via pre-defined commands.
The following main option are available typing from the main menu:

* ``qual`` not currently supported;
* ``comp`` opens the :ref:`compmenu`;
* ``exp`` opens the :ref:`expmenu`;
* ``post`` opens the :ref:`postmenu`;
* ``exit`` exit the application.

Additionaly to these main options, a series of "utilities" can be also accessed
from the main menu. These are a collection of side-tools initially developed
for JADE that nevertheless can be useful also as stand-alone tools.
A detailed description of these functionalities can be found in :ref:`uty`.

Quality check menu
==================
Not implemented.

.. _compmenu:

Computational Benchmark menu
============================

.. image:: ../img/compmenu.png
    :width: 400

The following options are available in the computational benchmark menu:

* ``printlib`` print to video all the available nuclear data libraries
  in the xsdir file selected during JADE configuration;
* ``assess`` start the assessment of a selected library. The library is
  specified directly from the console when the selection is prompted to
  video. The library must be contained in the xsdir file (available libraries
  can be explored using ``printlib``);
* ``continue`` continue a previously interrupted assessment for a selected
  library. Currently, this option is implemented only for the Sphere Leakage
  benchmark.
* ``back`` go back to the main menu;
* ``exit`` exit the application;

.. _expmenu:

Experimental Benchmark menu
===========================

.. image:: ../img/expmenu.png
    :width: 400

The following option are available in the experimental benchmark menu:

.. _postmenu:

Post-processing menu
====================

.. image:: ../img/postmenu.png
    :width: 400