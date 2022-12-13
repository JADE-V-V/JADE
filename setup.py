import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

setuptools.setup(
    name="JADE",
    version="0.0.2",
    author="Steven Bradnam",
    author_email="steve.bradnam@ukaea.uk",
    description="Linux implimentation of a new tool for nuclear libraries V&V. Brought to you by NIER, University of Bologna (UNIBO), Fusion For Energy (F4E) and United Kingdom Atomic Energy Authority (UKAEA).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sbradnam/JADE",
    packages=setuptools.find_packages(),
    entry_points= dict(console_scripts=['jade=main:main']),
    install_requires=requirements,
    classifiers=["Programming Language :: Python :: 3",
                 "Operating System :: OS Independent"],
)
