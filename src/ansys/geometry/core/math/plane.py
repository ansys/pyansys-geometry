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
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Centered origin of the ``Frame``.
    direction_x: Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-plane direction.
    direction_y: Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Y-plane direction.
    """

    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D],
    ):
        """Constructor method for ``Plane``."""
        super().__init__(origin, direction_x, direction_y)
