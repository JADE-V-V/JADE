from enum import Enum


class CODE(Enum):
    MCNP = "mcnp"
    OPENMC = "openmc"
    SERPENT = "serpent"
    D1S = "d1s"
    EXPERIMENT = "exp"


EXP_TAG = "_exp_-_exp_"  # tag for the experiment folder

# get all possile code tags in a list
CODE_TAGS = [code.value for code in CODE]

JADE_TITLE = """
       8888888       oo       888oo       o8888o
           88      o8 8o      88  8oo    88     8
           88     o8   8o     88    8o   88     8
           88    o8=====8o    88    8o   88====°
       88  88   o8       8o   88  8oo    8o
       °°8888  o8         8o  888oo       oo88888

      Welcome to JADE, a nuclear libraries V&V test suite

      This is the log file, all main events will be recorded here
-------------------------------------------------------------------------------
###############################################################################
"""

# Long messages
FIRST_INITIALIZATION = """
 Welcome to JADE
 During this first run the entire JADE tree has been initialized.
 The application will be now closed. Before restarting the application, please
 follow the instructions in the documentation on how to configure JADE.

"""

DEFAULT_SETTINGS_RESTORATION = """
 Default configurations were restored successfully.
 The application will be now closed. Before restarting the application, please
 follow the instructions in the documentation on how to configure JADE.
"""

ALLOWED_COLUMN_NAMES = [
    "Energy",
    "Cells",
    "time",
    "tally",
    "Dir",
    "User",
    "Segments",
    "Multiplier",
    "Cosine",
    "Cor A",
    "Cor B",
    "Cor C",
]

DOSIMETRY_LIBS = ["34y"]
