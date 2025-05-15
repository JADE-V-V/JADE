import logging

# Handle OpenMC optional dependency with global flag.
try:
    import openmc

    OMC_AVAIL = True
except ImportError:
    OMC_AVAIL = False
    logging.warning(
        "OpenMC has not been installed - see JADE installation instructions"
    )

try:
    import tkinter as tk

    import ttkthemes

    TKINTER_AVAIL = True
except ImportError:
    TKINTER_AVAIL = False
    logging.warning("'tkinter' is not installed. GUI functionality will be disabled.")
