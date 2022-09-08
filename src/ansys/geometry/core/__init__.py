"""
PyGeometry.

A Python wrapper for Ansys Geometry Service.
"""

# Version
# ------------------------------------------------------------------------------

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))
"""The installed version of PyGeometry."""


# Units
# ------------------------------------------------------------------------------

from pint import UnitRegistry

UNITS = UnitRegistry()
"""Unit manager."""

UNIT_LENGTH = UNITS.meter
"""Default length unit for PyGeometry."""

UNIT_ANGLE = UNITS.radian
"""Default angle unit for PyGeometry."""
