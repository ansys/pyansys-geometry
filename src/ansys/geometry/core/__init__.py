"""
PyGeometry is a Python wrapper for the Ansys Geometry service.
"""

# Version
# ------------------------------------------------------------------------------

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata  # type: ignore

__version__ = importlib_metadata.version(__name__.replace(".", "-"))

# Logger
# ------------------------------------------------------------------------------

import logging

from ansys.geometry.core.logger import Logger

LOG = Logger(level=logging.ERROR, to_file=False, to_stdout=True)
LOG.debug("Loaded logging module as LOG")

# Ease import statements
# ------------------------------------------------------------------------------

from ansys.geometry.core.connection import launch_modeler
from ansys.geometry.core.modeler import Modeler
