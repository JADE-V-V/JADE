[![Testing](https://github.com/dodu94/JADE/actions/workflows/TestPy38.yml/badge.svg?branch=master)](https://github.com/dodu94/JADE/actions/workflows/TestPy38.yml)
[![Documentation Status](https://readthedocs.org/projects/jade-a-nuclear-data-libraries-vv-tool/badge/?version=latest)](https://jade-a-nuclear-data-libraries-vv-tool.readthedocs.io/en/latest/?badge=latest)

<img src="https://user-images.githubusercontent.com/25747626/118662537-5f124900-b7f0-11eb-8d69-282305f795c4.png" width="300" />

# JADE
A new tool for nuclear libraries V&V.
Brought to you by NIER, University of Bologna (UNIBO) and Fusion For Energy (F4E).

Check [JADE official documentation](https://jade-a-nuclear-data-libraries-vv-tool.readthedocs.io/en/latest/)
for more detailed information on how to use the tool.

For additional information contact: d.laghi@nier.it

## Requirements
- Windows operative system (Linux or MacOS compatibility has not been tested);
- Anaconda or Miniconda distribution (Python 3);
- Microsoft Office suite (Excel and Word);

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
pip install -r requirements.txt
```

From here, the user can follow the instructions from step 5 in:

https://jade-a-nuclear-data-libraries-vv-tool.readthedocs.io/en/latest/usage/installation.html




