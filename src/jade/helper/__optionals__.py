import logging

logger = logging.getLogger(__name__)

# Handle OpenMC optional dependency with global flag.
try:
    import openmc

    OMC_AVAIL = True
except ImportError:
    OMC_AVAIL = False
    logger.warning(
        "OpenMC has not been installed - see JADE installation instructions"
    )

# Handle serpentTools optional dependency with global flag. serpentTools still
# imports distutils, which on Python >= 3.12 is only provided by setuptools.
try:
    import serpentTools  # noqa: F401

    SERPENT_AVAIL = True
except ImportError:
    SERPENT_AVAIL = False
    logger.warning(
        "serpentTools has not been installed - see JADE installation instructions"
    )

try:
    import tkinter as tk

    import ttkthemes

    TKINTER_AVAIL = True
except ImportError:
    TKINTER_AVAIL = False
    logger.warning("'tkinter' is not installed. GUI functionality will be disabled.")
