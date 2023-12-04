import sys

# colors
CRED = '\033[91m'
CORANGE = '\033[93m'
CEND = '\033[0m'

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
        message = 'A Fatal exception have occured'

    message = message+', the application will now exit'
    print(CRED+' FATAL EXCEPTION: \n'+message+CEND)
    sys.exit()