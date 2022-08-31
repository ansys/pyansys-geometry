from logging import Logger


class DirectModeler:
    """
    Provides DirectModeler class for building CAD designs.

    Should have methods like:
    AddDesign(...) - Adds a new design that is synchronized to the server

    Parameters
    ----------
    logger : Logger
        Client-side logging resource.
    """

    def __init__(self, logger: Logger):
        self._logger = logger
