.. _codemod:

####################
Contributing to JADE
####################

Thank you for considering contributing to JADE!

The purpose of this section is to document how the project is managed:
What is the procedure to be followed to contribute to JADE (bug fixes, enhancements, new features,
new benchmarks), how the JADE organization is structured and how you can be 
part of it.

These guidelines are inspired by what is being done in the
`OpenMC <https://docs.openmc.org/en/stable/devguide/index.html>`_ community.

Terminology
===========
There are different ways to contribute to JADE, and not all of them require you to code:

* A *Tester* is a JADE frequent user that helps the project giving detailed feedback on JADE stable and
  beta releases. This can also come in the form of opening issues.
* An *Expert* is a senior figure that provides knowledge in the field of nuclear data, Monte Carlo codes,
  and benchmarks, helping steering JADE priorities
* A *Contributor* is any individual creating or commenting on an issue or pull request.
* An *Approver* is a subset of contributors who are authorized to review and merge pull requests.
  We try to appoint at least one approver for each organization steadily contributing to JADE codebase.

A list of all the people contributing to JADE can be found at :ref:`contributor_list`.
The scope of the following section is to describe the procedure to be followed by *Contributors*.

Development Workflow
====================
Anyone wishing to make contributions to JADE should be fully acquainted and comfortable
working with git and GitHub. We assume here that you have git installed on your system,
have a GitHub account and that you are able to create/push to repositories on GitHub.
An easy wasy to approach the world of git actions and their integration with GitHub is to use
`GitHub Desktop <https://desktop.github.com/>`_.

Branching model
---------------
.. figure:: /img/dev_guide/branching_model.svg
    :width: 600
    :align: center

    Branching model showing Developing, Feature, Benchmark, Release and Hotfix branches

Development of JADE relies heavily on branching; specifically, we use a modified 
version of the branching model sometimes referred to as git flow. If you plan to 
contribute to JADE development, we highly recommend that you read this
`blog post <https://nvie.com/posts/a-successful-git-branching-model/>`_
to get a sense of how the branching model works. 

There are two primary branches that always exist: ``master`` and ``developing``. 
The ``master`` branch is a stable branch that contains the latest release of the 
code. The ``developing`` branch is where any ongoing development takes place 
prior to a release and is not guaranteed to be stable. 

Other branches will be created as required for different purposes which are 
listed below. When any of these branches need to be merged (e.g., into the 
``developing`` branch), a pull request (PR) should be initiated on GitHub that is 
then reviewed by an approver (see `Requirements for a successful merge`_). If the 
pull request is satisfactory, it is then merged into develop. Note that a 
committer may not review their own pull request (i.e., an independent code 
review is required). 

* **Feature** - All new features, enhancements, and bug fixes should be 
  developed on a ``Feature`` branch off ``developing``. Most branches on the 
  repository will be of this type and consist of work by the core JADE team.
* **Benchmark** - This type of branch is similar to that above, except it is 
  specifically for adding new benchmarks. This is branched off ``developing`` in
  the same way as ``Feature`` branches and will be the most frequently Pull 
  Requested (PR'd) from forks outside the core team.
* **Release** - This type of branch will come off ``developing`` when  the project 
  leader decides that a release should occur. This is solely for allowing further 
  testing and bug fixes for an upcoming release and will be merged into ``main`` 
  once completed.
* **Hotfix** - This is an exceptional type of branch that comes directly off ``main`` 
  and is merged directly back into it. This would used when there is a major bug
  needs fixing immediately.

Release Model
-------------

The JADE project uses semantic versioning in the format **Major.Minor.Patch** 
with the choice of versioning increment for a specific release using the 
following guidelines but the final decision beign discretionary.

* **Major** - Major or non-backwards compatible functionality additions such as a 
  new transport code being added, the class structure being modified or the 
  input/output directory structure is changed.
* **Minor** - Addition of new features that are additive/backward compatible with 
  the previous version. New Benchmarks will generally be at this level.
* **Patch** - Fixes for bugs, typos, tidying code, and other small changes that do
  not change or extend JADE's intended functionality.

Contribution steps
------------------
JADE follows the development process outlined in the diagram below, relying on 
Github Issues to track requests and delivery of new features, benchmarks, 
bugfixes and other developments. If there is a specific feature/benchmark or bug
fix you wish to work on, please initially submit an issue using the most 
suitable template.

.. figure:: /img/dev_guide/dev_process.svg
    :width: 600
    :align: center

    Development process flow diagram for JADE showing the processes for 
    accepting issues, planning releases, reviewing Pull Requests and releasing.

The general steps for contributing are as follows:

#. Fork the main JADE repository from `GitHub <https://github.com/JADE-V-V/JADE>`_. This will create a
   repository with the same name under your personal account. As such, you can commit
   to it as you please without disrupting other developers.
#. Clone locally your fork of JADE and create a new branch off of the ``developing`` one.
#. Setup your environment for developing JADE.
  #. Install JADE for development (see :ref:`installdevelop`.)
  #. Install and use `ruff https://docs.astral.sh/ruff/`_ for code style.
  #. Ensure you can run the tests (see :ref:`Testing In JADE <runtesting>`)
#. Make your changes on the new branch that you intend to have included in ``developing``.
#. Issue a pull request from GitHub and select the ``developing`` branch of JADE main
   repo as the target. You should then follow the fields in the PR template, but
   at a minimum, you should describe what the changes you've made are and why 
   you are making them. If the changes are related to an outstanding issue, make
   sure it is cross-referenced for its resolution to be properly tracked.
#. An approver will review your pull request based on the criteria above. Any issues with
   the pull request can be discussed directly on the pull request page itself.
#. After the pull request has been thoroughly vetted, it is merged back into the develop
   branch of JADE main repo.

Requirements for a successful merge
-----------------------------------

The following are minimum requirements necessary for the approval of a pull request:

* the python code should adhere to the `PEP 8 <https://peps.python.org/pep-0008/>`_ convention.
  This can be achieved for intance using `pycodestyle <https://pypi.org/project/pycodestyle/>`_
  as linter in your code editor of choice. The 
  `black formatter <https://github.com/psf/black>`_ should be run automatically
  as part of the pre-commit hooks (see `Contribution steps`_).
* if a new feature is developed, new test cases must be added to unit test suites.
  `pytest <https://docs.pytest.org/en>`_ must be used. Some additional 
  info on this can be found at :ref:`testing`.
* no conflicts are allowed with the ``developing`` branch, i.e., the original 
  ``developing`` branch should be pulled into the fork and all eventual 
  conflicts resolved prior to the submission of the pull request.
* the new code shall not break any pre-existing feature, i.e., all unit tests 
  and regression tests are passed.
* if a new feature is added, it should be properly reported in the sphinx 
  documentation (see `Modify documentation using Sphinx`_).

Modify documentation using Sphinx
=================================

This documentation is written with
`Sphinx <https://www.sphinx-doc.org/en/master/index.html>`_ using a template
provided by `Read The Docs <https://readthedocs.org/>`_. Before attempting
to modify the documentation, the developer should familiarize with these tools
and with the RST language that is used to write it. 

Inside the ``docs`` folder of JADE repo are located the *source* and *build* directories
of the documentation. To apply a modification, the user must simply modify/add one
or more files in the *source* tree and in the *docs* folder execute from terminal
the ``make html`` command to check that compilation works as intended.

Even if the documentation is not rebuilt locally, a new version is automatically
compiled by ReadTheDocs every time is performed a push to the main branch 
(similarly to what happens with automatic testing of the code).
