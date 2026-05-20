###############
Troubleshooting
###############

libGl.so.1 error
================

When you install on linux it may happen that after installation, the first
time you call jade there may be some missing libraries that ``vtk`` needs
to run properly.

If you get one of the following errors:

.. code-block:: bash

    Traceback (most recent call last):
    File "/home/laghida/.conda/envs/jade/bin/jade", line 5, in <module>
        from jade.main import main
    File "/home/laghida/jade_repo/JADE/jade/main.py", line 34, in <module>
        import jade.gui as gui
    File "/home/laghida/jade_repo/JADE/jade/gui.py", line 35, in <module>
        import jade.computational as cmp
    File "/home/laghida/jade_repo/JADE/jade/computational.py", line 29, in <module>
        import jade.testrun as testrun
    File "/home/laghida/jade_repo/JADE/jade/testrun.py", line 40, in <module>
        import f4enix.input.MCNPinput as ipt
    File "/home/laghida/.conda/envs/jade/lib/python3.11/site-packages/f4enix/__init__.py", line 6, in <module>
        from .output.meshtal import Meshtal
    File "/home/laghida/.conda/envs/jade/lib/python3.11/site-packages/f4enix/output/meshtal.py", line 36, in <module>
        import vtk
    File "/home/laghida/.conda/envs/jade/lib/python3.11/site-packages/vtk.py", line 5, in <module>
        from vtkmodules.vtkWebCore import *

or 

.. code-block:: bash

    Traceback (most recent call last):
    File "/home/laghida/.conda/envs/jade/bin/jade", line 5, in <module>
        from jade.main import main
    File "/home/laghida/jade_repo/JADE/jade/main.py", line 34, in <module>
        import jade.gui as gui
    File "/home/laghida/jade_repo/JADE/jade/gui.py", line 35, in <module>
        import jade.computational as cmp
    File "/home/laghida/jade_repo/JADE/jade/computational.py", line 29, in <module>
        import jade.testrun as testrun
    File "/home/laghida/jade_repo/JADE/jade/testrun.py", line 40, in <module>
        import f4enix.input.MCNPinput as ipt
    File "/home/laghida/.conda/envs/jade/lib/python3.11/site-packages/f4enix/__init__.py", line 6, in <module>
        from .output.meshtal import Meshtal
    File "/home/laghida/.conda/envs/jade/lib/python3.11/site-packages/f4enix/output/meshtal.py", line 36, in <module>
        import vtk
    File "/home/laghida/.conda/envs/jade/lib/python3.11/site-packages/vtk.py", line 5, in <module>
        from vtkmodules.vtkWebCore import *

you can solve the issue installing the following libraries:

.. code-block:: bash
    conda install -c conda-forge libgl
    conda install -c conda-forge xorg-libxrender


ImportError: urllib3 v2 only supports OpenSSL 1.1.1+
====================================================

There are a few systems where the installation may fail while fetching the benchmark
data from the internet due to old version installed of OpenSSL.
The drop in support is described `here <https://github.com/urllib3/urllib3/issues/2168>`_.

If this error is encountered either the openSSL can be upgraded:

.. code-block:: bash

    brew install openssl@1.1

or the urllib3 version (jade dependency) can be downgraded:

.. code-block:: bash

    pip install urllib3==1.26.6

see `here <https://stackoverflow.com/questions/76187256/importerror-urllib3-v2-0-only-supports-openssl-1-1-1-currently-the-ssl-modu>`_ for additional info on the fix.


