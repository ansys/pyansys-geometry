"""Provides default connection parameters."""

import os

DEFAULT_HOST = os.environ.get("ANSRV_GEO_HOST", "127.0.0.1")
"""
Default HOST name used.

By default, it searches for the environment variable ``ANSRV_GEO_HOST``,
and if it does not exist, it falls back to ``127.0.0.1``.
"""

DEFAULT_PORT: int = int(os.environ.get("ANSRV_GEO_PORT", 50051))
"""
Default HOST port used.

By default, it searches for the environment variable ``ANSRV_GEO_PORT``,
and if it does not exist, it falls back to ``50051``.
"""

MAX_MESSAGE_LENGTH = int(os.environ.get("PYGEOMETRY_MAX_MESSAGE_LENGTH", 256 * 1024**2))
"""
Default gRPC message length.

By default, it searches for the environment variable ``PYGEOMETRY_MAX_MESSAGE_LENGTH``,
and if it does not exist, it falls back to ``256Mb``.
"""

GEOMETRY_SERVICE_DOCKER_IMAGE = "ghcr.io/ansys/geometry"
"""
Default Geometry service Docker image location.

Tag is dependent on what OS service is requested.
"""
