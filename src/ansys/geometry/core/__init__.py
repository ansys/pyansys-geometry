"""
PyGeometry.

A Python wrapper for Ansys Geometry Service.
"""

# Version
# ------------------------------------------------------------------------------

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))

# Units
# ------------------------------------------------------------------------------

from pint import UnitRegistry

UNITS = UnitRegistry()
"""Unit manager."""

UNIT_LENGTH = UNITS.meter
"""Default unit length for PyGeometry."""

# Typing
# ------------------------------------------------------------------------------

from typing import Union

Real = Union[int, float]
