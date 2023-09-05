"""Module providing default connection parameters."""

import os

DEFAULT_HOST = os.environ.get("ANSRV_GEO_HOST", "127.0.0.1")
"""
Default for the HOST name.

By default, PyAnsys Geometry searches for the environment variable ``ANSRV_GEO_HOST``,
and if this variable does not exist, PyAnsys Geometry uses ``127.0.0.1`` as the host.
"""

DEFAULT_PORT: int = int(os.environ.get("ANSRV_GEO_PORT", 50051))
"""
Default for the HOST port.

By default, PyAnsys Geometry searches for the environment variable ``ANSRV_GEO_PORT``,
and if this variable does not exist, PyAnsys Geometry uses ``50051`` as the port.
"""

MAX_MESSAGE_LENGTH = int(os.environ.get("PYGEOMETRY_MAX_MESSAGE_LENGTH", 256 * 1024**2))
"""
Default for the gRPC maximum message length.

By default, PyAnsys Geometry searches for the environment variable
``PYGEOMETRY_MAX_MESSAGE_LENGTH``, and if this variable does not exist,
it uses ``256Mb`` as the maximum message length.
"""

GEOMETRY_SERVICE_DOCKER_IMAGE = "ghcr.io/ansys/geometry"
"""
Default for the Geometry service Docker image location.

Tag is dependent on what OS service is requested.
"""

DEFAULT_PIM_CONFIG = os.path.join(os.path.dirname(__file__), "pim_configuration.json")
"""
Default for the PIM configuration when running PIM Light.

This parameter is only to be used when PIM Light is being run.
"""
