class ConfigError(Exception):
    """Exception raised for errors in the configuration.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="There is an error in the configuration"):
        self.message = message
        super().__init__(self.message)
