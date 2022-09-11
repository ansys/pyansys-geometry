"""``Plane`` class module."""

from typing import Union

import numpy as np

from ansys.geometry.core.math.constants import UNIT_VECTOR_X, UNIT_VECTOR_Y, ZERO_POINT3D
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.point import Point
from ansys.geometry.core.math.vector import UnitVector, Vector
from ansys.geometry.core.typing import RealSequence


class Plane(Frame):
    """
    Provides primitive representation of a 2D plane in 3D space.

    Parameters
    ----------
    origin : Optional[Union[~numpy.ndarray, RealSequence, Point]]
        Centered origin of the ``Frame``. By default, cartesian origin.
    direction_x: Optional[Union[~numpy.ndarray, RealSequence, UnitVector, Vector]]
        X-axis direction. By default, ``UNIT_VECTOR_X``
    direction_y: Optional[Union[~numpy.ndarray, RealSequence, UnitVector, Vector]]
        Y-axis direction. By default, ``UNIT_VECTOR_Y``
    """

    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point] = ZERO_POINT3D,
        direction_x: Union[np.ndarray, RealSequence, UnitVector, Vector] = UNIT_VECTOR_X,
        direction_y: Union[np.ndarray, RealSequence, UnitVector, Vector] = UNIT_VECTOR_Y,
    ):
        """Constructor method for ``Plane``."""
        super().__init__(origin, direction_x, direction_y)
