import logging

logger = logging.getLogger(__name__)

# Handle OpenMC optional dependency with global flag.
try:
    import openmc  # noqa: F401

    OMC_AVAIL = True
except ImportError:
    OMC_AVAIL = False
    logger.warning("OpenMC has not been installed - see JADE installation instructions")

try:
    import tkinter as tk  # noqa: F401

    import ttkthemes  # noqa: F401

    TKINTER_AVAIL = True
except ImportError:
    TKINTER_AVAIL = False
    logger.warning("'tkinter' is not installed. GUI functionality will be disabled.")
