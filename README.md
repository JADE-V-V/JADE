[![Testing windows](https://github.com/Radiation-Transport/F4Enix/actions/workflows/AutomatedTests_win.yml/badge.svg?branch=main)](https://github.com/Radiation-Transport/F4Enix/actions/workflows/AutomatedTests_win.yml)
[![Testing linux](https://github.com/Radiation-Transport/F4Enix/actions/workflows/AutomatedTests_linux.yml/badge.svg?branch=main)](https://github.com/Radiation-Transport/F4Enix/actions/workflows/AutomatedTests_linux.yml)
[![PyPi version](https://badgen.net/pypi/v/f4enix/)](https://pypi.org/project/f4enix)
[![Documentation Status](https://readthedocs.org/projects/f4enix/badge/?version=latest)](https://f4enix.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/Fusion4Energy/F4Enix/graph/badge.svg?token=P4A85K0ACG)](https://codecov.io/gh/Fusion4Energy/F4Enix)

# F4Enix
Parser for Monte Carlo simulations input and output files

**Python >3.9!**

Both Windows and Linux supported.

Go to [F4Enix official documentation](https://f4enix.readthedocs.io/en/latest/) to get
more information on the library capabilities, examples and much more.

## Install
The easiest way to install F4Enix is using pip:

```
pip install f4enix
```
See the [relevant section of the documentation](https://f4enix.readthedocs.io/en/stable/usage/installation.html#developer-mode-install) for developer mode installation

### Troubleshooting
If any unexpected issue is encountered during installation, the first step for
its resolution would be to create a new fresh virtual environment.
In conda this would be done with:
```
conda create -n <env_name> python=3.9
```
Please remember that python versions lower than 3.9 are not supported.