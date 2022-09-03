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

from typing import Sequence, Union

import numpy as np

Real = Union[int, float]
"""Type used to refer to both ints and floats as possible values."""

RealSequence = Union[np.ndarray, Sequence[Real]]
"""Type used to refer to Real types as a Sequence.

Note
----
:class:`numpy.ndarrays` are also accepted, since they are
the overlaying data structure behind most PyGeometry objects.
"""
