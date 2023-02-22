####################
Modify documentation
####################

This documentation is written with
`Sphynx <https://www.sphinx-doc.org/en/master/index.html>`_ using a template
provided by `Read The Docs <https://readthedocs.org/>`_. Before attempting
to modify the documentation, the developer should familiarize with these tools
and with the RST language that is used to actually write the doc. 

Inside ``<JADE root>\Code\docs`` are located the *source* and *build* directories
of the documentation. To apply a modification, the user must simply modify/add one
or more files in the *source* tree and in the *docs* folder execute from terminal
the ``make html`` command.

Even if the documentation is not rebuilt locally, a new version is automatically
compiled by ReadTheDocs every time is performed a push to the main branch 
(similarly to what happens with automatic testing of the code).