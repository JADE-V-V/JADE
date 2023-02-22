.. _codemod:

################
Modify JADE code
################

The following are good practice steps that should be followed
when modifying JADE source code:

#. Identify a specific features that need to be introduced (e.g. a new experimental benchmark);
#. Create a dedicated branch from ``Developing`` and name it accordingly to the feature to be implemented
   (keep it short);
#. Work on the branch and be sure to frequently merge the ``Developing`` branch in your branch
   in order to prevent integration hell;
#. When the implementation of the feature is completed, merge the branch in ``Developing`` and
   delete the feature branch.

Be sure to always add automatic testing that covers all the added code (if possible).
To test your code check :ref:`testing`.