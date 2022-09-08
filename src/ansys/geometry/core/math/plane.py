"""``Plane`` class module."""

from typing import Union

import numpy as np

from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.typing import RealSequence


class Plane(Frame):
    """
    Provides primitive representation of a 2D plane in 3D space.

    Parameters
    ----------
    origin : Optional[Union[~numpy.ndarray, RealSequence, Point3D]]
        Centered origin of the ``Frame``. By default, cartesian origin.
    direction_x: Optional[Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]]
        X-axis direction. By default, ``UNIT_VECTOR_X``
    direction_y: Optional[Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]]
        Y-axis direction. By default, ``UNIT_VECTOR_Y``
    """

    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D] = [0, 0, 0],
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = [1, 0, 0],
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = [0, 1, 0],
    ):
        """Constructor method for ``Plane``."""
        super().__init__(origin, direction_x, direction_y)
