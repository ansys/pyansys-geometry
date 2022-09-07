"""``Polygon`` class module."""

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.typing import Real


class PolygonShape(BaseShape):
    """A class for modelling polygon."""

    def __init__(
        self,
        origin: Point3D,
        dir_1: UnitVector3D([1, 0, 0]),
        dir_2: UnitVector3D([0, 1, 0]),
        radius: Real,
        sides: int,
    ):
        """Initializes the polygon shape.

        Parameters
        ----------
        radius : Real
            The radius of the polygon.
        sides : int
            Number of sides of the polygon
        origin : Point3D
            A :class:``Point3D`` representing the origin of the shape.
        dir_1 : UnitVector3D
            A :class:``UnitVector3D`` representing the first fundamental direction
            of the reference plane where the shape is contained.
        dir_2 : UnitVector3D
            A :class:``UnitVector3D`` representing the second fundamental direction
            of the reference plane where the shape is contained.

        """
        super().__init__(origin, dir_1, dir_2, is_closed=True)
        self._radius = radius
        self._sides = sides
