"""Provides the PyGeometry ``typing`` class."""

from beartype.typing import Sequence, Union
import numpy as np

Real = Union[int, float, np.integer, np.floating]
"""Type used to refer to both integers and floats as possible values."""

RealSequence = Union[np.ndarray, Sequence[Real]]
"""Type used to refer to ``Real`` types as a ``Sequence``.

Notes
-----
:class:`numpy.ndarrays <numpy.ndarray>` are also accepted because they are
the overlaying data structure behind most PyGeometry objects.
"""
