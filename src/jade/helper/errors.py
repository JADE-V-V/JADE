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


class PlotIndexMismatchError(Exception):
    """Exception raised when the indices of the dataframes do not match."""

    def __init__(
        self,
        index1,
        index2,
        codelib,
    ):
        self.message = (
            f"Indices do not match between reference and {codelib}: {index1}, {index2}"
        )
        super().__init__(self.message)
