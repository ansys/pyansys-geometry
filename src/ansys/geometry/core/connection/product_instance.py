"""Module containing the ``ProductInstance`` class."""
import logging
import os
import signal


class ProductInstance:
    """
    ``ProductInstance`` class.

    This class is used as a handle for a local session of Ansys Product's backend: Discovery, Windows Geometry Service 
    or SpaceClaim.

    Parameters
    ----------    
    pid : int
        The local instance's proccess identifier. This allows to  keep track of the process and close it if need be.
    """
    def __init__(
        self,
        pid: int
    ):
        self._pid = pid

    def close(self) -> bool:
        """
        Closes the process associated to the pid.
        """
        try:
            os.kill(self._pid, signal.SIGTERM)
        except OSError as oserr:
            logging.error(str(oserr))
            return False
        return True