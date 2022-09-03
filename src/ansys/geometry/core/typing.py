"""Typing module for PyGeometry."""

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
