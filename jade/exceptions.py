import sys
import logging


def fatal_exception(message=None):
    """
    Use this function to exit with a code error from a handled exception

    Parameters
    ----------
    message : str, optional
        Message to display. The default is None.

    Returns
    -------
    None.

    """
    if message is None:
        message = "A Fatal exception have occured"

    message = message + ", the application will now exit"
    logging.critical(" FATAL EXCEPTION: \n%s", message)
    sys.exit()
