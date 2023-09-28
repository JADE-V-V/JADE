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
  beta releases. This can also come in the form of openining issues.
* An *Expert* is a senior figure that provides knowledge in the field of nuclear data, Monte Carlo codes,
  and benchmarks, helping steering JADE priorities
* A *Contributor* is any individual creating or commenting on an issue or pull request.
* An *Approver* is a subset of contributors who are authorized to review and merge pull requests.
* The *Technical Leader* is currently Davide Laghi (davide.laghi01@gmail.com) who has the authority
  to tag new releases.

A list of all the people contributing to JADE can be found at :ref:`contributor_list`.
The scope of the following section is to describe the procedure to be followed by *Contributors*.

Development Workflow
====================
Anyone wishing to make contributions to JADE should be fully acquainted and comfortable
working with git and GitHub. We assume here that you have git installed on your system,
have a GitHub account and that you are able to create/push to repositories on GitHub.
An easy wasy to approach the world of git actions and their integration with GitHub is to use
`GitHub Desktop <https://desktop.github.com/>`_.

Development of JADE relies heavily on branching; specifically, we use a branching model
sometimes referred to as git flow. If you plan to contribute to JADE development,
we highly recommend that you read this
`blog post <https://nvie.com/posts/a-successful-git-branching-model/>`_
to get a sense of how the branching
model works. There are two main branches that always exist: ``master`` and ``Developing``.
The master branch is a stable branch that contains the latest release of the code.
The develop branch is where any ongoing development takes place prior to a release and is
not guaranteed to be stable. When the project leader decides that a release should occur,
the ``Developing`` branch is merged into master.

All new features, enhancements, and bug fixes should be developed on a branch that branches off
of Developing. When the feature is completed, a pull request is initiated on GitHub that is
then reviewed by an approver. If the pull request is satisfactory, it is then merged into develop.
Note that a committer may not review their own pull request
(i.e., an independent code review is required).

Contribution steps
------------------
These steps apply to both new features and bug fixes. The general steps for contributing
are as follows:

#. Fork the main JADE repository from `GitHub <https://github.com/JADE-V-V/JADE>`_. This will create a
   repository with the same name under your personal account. As such, you can commit
   to it as you please without disrupting other developers.
#. Clone locally your fork of JADE and create a new branch off of the ``Developing`` one.
#. Make your changes on the new branch that you intend to have included in ``Developing``.
#. Issue a pull request from GitHub and select the ``Developing`` branch of JADE main
   repo as the target.
   At a minimum, you should describe what the changes you’ve made are and why you are
   making them. If the changes are related to an outstanding issue, make sure it is
   cross-referenced for its resolution to be properly tracked.
#. An approver will review your pull request based on the criteria above. Any issues with
   the pull request can be discussed directly on the pull request page itself.
#. After the pull request has been thoroughly vetted, it is merged back into the develop
   branch of JADE main repo.

Requirements for a successful merge
-----------------------------------

The following are minimum requirements necessary for the approval of a pull request:

* the python code should adhere to the `PEP 8 <https://peps.python.org/pep-0008/>`_ convention.
  This can be achieved for intance using `pycodestyle <https://pypi.org/project/pycodestyle/>`_
  as linter in your code editor of choice. Another (automatic) way, is to use the `black formatter 
  <https://github.com/psf/black>`_
* if a new feature is developed, new test cases must be added to unit test suites.
  `pytest <https://docs.pytest.org/en/7.4.x/>`_ must be used. Some additional info on this can be 
  found at :ref:`testing`.
* no conflicts are allowed with the ``Developing`` branch, i.e., the original ``Developing`` branch
  should be pulled into the fork and all eventual conflicts resolved prior to the submission
  of the pull request.
* the new code shall not break any pre-existing feature, i.e., all unit tests and regression tests
  are passed.
* if a new feature is added, it should be properly reported in the sphinx documentation.

Modify documentation using Sphinx
=================================

This documentation is written with
`Sphynx <https://www.sphinx-doc.org/en/master/index.html>`_ using a template
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
