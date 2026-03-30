class ConfigError(Exception):
    """Exception raised for errors in the configuration."""

    def __init__(self, message="There is an error in the configuration"):
        self.message = message
        super().__init__(self.message)


class VersionInconsistencyError(ConfigError):
    """Exception raised for version inconsistencies in the configuration."""

    def __init__(self, message="There is a version inconsistency in the sims"):
        self.message = message
        super().__init__(self.message)


class PostProcessConfigError(Exception):
    """Exception raised for errors in the configuration of post processing."""

    def __init__(
        self, message="There is an error in the JADE post-processing configuration"
    ):
        self.message = message
        super().__init__(self.message)
