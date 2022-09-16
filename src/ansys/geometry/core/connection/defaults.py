"""Module containing default connection parameters."""

import os

DEFAULT_HOST = os.environ.get("ANSRV_GEO_HOST", "127.0.0.1")
"""
Default HOST name used.

By default it will search for the env variable ANSRV_GEO_HOST
and if it does not exist, it will fallback to ``127.0.0.1``.
"""

DEFAULT_PORT = os.environ.get("ANSRV_GEO_PORT", 50051)
"""
Default HOST port used.

By default it will search for the env variable ANSRV_GEO_PORT
and if it does not exist, it will fallback to ``50051``.
"""
