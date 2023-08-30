"""Provides typing of values for PyAnsys Geometry."""

from beartype.typing import Sequence, Union
import numpy as np

Real = Union[int, float, np.integer, np.floating]
"""Type used to refer to both integers and floats as possible values."""

RealSequence = Union[np.ndarray, Sequence[Real]]
"""
Type used to refer to ``Real`` types as a ``Sequence`` type.

Notes
-----
:class:`numpy.ndarrays <numpy.ndarray>` are also accepted because they are
the overlaying data structure behind most PyAnsys Geometry objects.
"""
