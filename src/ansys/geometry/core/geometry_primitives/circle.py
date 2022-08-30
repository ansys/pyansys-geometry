
from ansys.geometry.core.geometry_primitives.direction import Direction
from ansys.geometry.core.geometry_primitives.point3D import Point3D

class Circle:
    """
    Provides Circle geometry primitive representation.

    Parameters
    ----------
    origin : Point3D
        Centered origin of the circle.
    dirX: Direction,
        x plane direction.
    dirY: Direction,
        y plane direaction.
    radius: float
        Circle radius.
    """

    def __init__(
        self,
        origin: Point3D,
        dirX: Direction,
        dirY: Direction,
        radius: float,
    ):
        self._origin = origin
        self._dirX = dirX
        self._dirY = dirY
        self._radius = radius

    