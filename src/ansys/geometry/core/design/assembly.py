
from logging import Logger

class Assembly:
    """
    Provides Assembly class for building 3D design elements.

    Synchronizes to a server

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
        self._design_geometries = [] # DesignGeometry[] maintaining reference to all geometries within the current assembly
