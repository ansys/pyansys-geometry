"""PyAnsys Geometry is a Python wrapper for the Ansys Geometry service."""

# Version
# ------------------------------------------------------------------------------

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata  # type: ignore

__version__ = importlib_metadata.version(__name__.replace(".", "-"))
"""PyAnsys Geometry version."""

# Ease import statements
# ------------------------------------------------------------------------------

from ansys.geometry.core.connection.launcher import (
    launch_local_modeler,
    launch_modeler,
    launch_modeler_with_discovery,
    launch_modeler_with_discovery_and_pimlight,
    launch_modeler_with_geometry_service,
    launch_modeler_with_geometry_service_and_pimlight,
    launch_modeler_with_spaceclaim,
    launch_modeler_with_spaceclaim_and_pimlight,
    launch_remote_modeler,
)
from ansys.geometry.core.logger import LOG
from ansys.geometry.core.modeler import Modeler

# Global config constants
# ------------------------------------------------------------------------------

USE_TRAME = False
"""Global constant for checking whether to use `trame <https://kitware.github.io/trame/>`_
for visualization."""
