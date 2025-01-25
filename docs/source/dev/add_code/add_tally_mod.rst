.. _custom_raw_process:

###########################################
Add new raw data processing functionalities
###########################################


.. _add_tally_mod:

Implement new tally modifier
============================

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
===============================
If instead you need to add a new way to combine tallies, you should:

#. Go to ``jade/config/raw_config.py`` and add your new concat option to the ``TallyConcatOption`` enum class.
#. Add a function to concat the tallies in ``jade/post/manipulate_tally.py``. This function should take as
    the only positional argument a list of dataframes (the tallies). Return type must be a pandas dataframe.
#. Link the new function to the enum adding it to the ``CONCAT_FUNCTIONS`` dictionary that can be found in the same file.
#. Add a test for your new modifier in ``jade/tests/post/test_manipulate_tally.py``.
#. Add your new option to the available concat options in the documentation.