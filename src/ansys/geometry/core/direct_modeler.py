from logging import Logger

class DirectModeler:
    """
    Provides DirectModeler class for building CAD designs.

    Parameters
    ----------
    logger : Logger
        Client-side logging resource.
    """

    def __init__(
        self,
        logger: Logger
    ):
        self._logger = logger
    