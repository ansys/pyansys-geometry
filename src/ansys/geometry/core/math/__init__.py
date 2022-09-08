"""PyGeometry math subpackage."""
from ansys.geometry.core.math.matrix import Matrix, Matrix33, Matrix44
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.math.vector import (
    QuantityVector2D,
    QuantityVector3D,
    UnitVector2D,
    UnitVector3D,
    Vector2D,
    Vector3D,
)

__all__ = [
    "Matrix",
    "Matrix33",
    "Matrix44",
    "Point2D",
    "Point3D",
    "QuantityVector2D",
    "QuantityVector3D",
    "UnitVector2D",
    "UnitVector3D",
    "Vector2D",
    "Vector3D",
]

UNIT_VECTOR_X = UnitVector3D([1, 0, 0])
"""Unit vector in the cartesian traditional X direction."""

UNIT_VECTOR_Y = UnitVector3D([0, 1, 0])
"""Unit vector in the cartesian traditional Y direction."""

UNIT_VECTOR_Z = UnitVector3D([0, 0, 1])
"""Unit vector in the cartesian traditional Z direction."""

ZERO_VECTOR3D = Vector3D([0, 0, 0])
"""Zero-valued Vector3D object."""
