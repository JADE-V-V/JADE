[![Testing](https://github.com/dodu94/JADE/actions/workflows/TestPy38.yml/badge.svg?branch=master)](https://github.com/dodu94/JADE/actions/workflows/TestPy38.yml)
[![Documentation Status](https://readthedocs.org/projects/jade-a-nuclear-data-libraries-vv-tool/badge/?version=latest)](https://jade-a-nuclear-data-libraries-vv-tool.readthedocs.io/en/latest/?badge=latest)

<img src="https://user-images.githubusercontent.com/25747626/118662537-5f124900-b7f0-11eb-8d69-282305f795c4.png" width="300" />

# JADE
A new tool for nuclear libraries V&V.
Brought to you by NIER, University of Bologna (UNIBO), Fusion For Energy (F4E) and United Kingdom Atomic Energy Authority (UKAEA).

Check [JADE official documentation](https://jade-a-nuclear-data-libraries-vv-tool.readthedocs.io/en/latest/)
for more detailed information on how to use the tool. Linux installtion to be added. 

For additional information contact: d.laghi@nier.it

## Requirements
- Linux operative system (Windows or MacOS compatibility has not been tested);
- Python 3 installation;

## LICENSE
JADE is an open-source software licensed under the [GNU GPLv3](./LICENSE) license.

## LINUX INSTALLATION

Firstly, create a new JADE directory:

``` 
mkdir JADE
cd JADE
```

Then create a pip virtual environment and activate it:

```
python -m venv jade
source jade/bin/activate
```
Note that once the venv is created, only the source command is required in future use.
 
Next clone the repository, and rename it to Code, and cd into it:

```
git clone https://github.com/sbradnam/JADE.git
mv JADE Code
cd Code
```

Now upgrade pip, and install the pip requirements:

```
pip install --upgrade pip
pip install .
```

JADE has now been installed as a command line tool. JADE should now be initialised in the top level JADE folder. To do this, cd up one level and run jade:

```
cd ../
jade
```

Alternatively, JADE can be configured in any location on your system. Lets now refer to this as `<jade_root>`:

```
cd path/to/alternative/jade/location
jade
```

Once initialised, the user should configure jade for their system. This can be fone by editing `<jade_root>/Configuration/Config.xlsx`.

Following configuration, the user can run `jade` within `<jade_root>` to enter the JADE gui.






