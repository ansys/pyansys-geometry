"""Provides the PyGeometry ``math`` subpackage."""

from ansys.geometry.core.math.bbox import BoundingBox2D
from ansys.geometry.core.math.constants import (
    DEFAULT_POINT2D,
    DEFAULT_POINT3D,
    IDENTITY_MATRIX33,
    IDENTITY_MATRIX44,
    UNITVECTOR2D_X,
    UNITVECTOR2D_Y,
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    UNITVECTOR3D_Z,
    ZERO_POINT2D,
    ZERO_POINT3D,
    ZERO_VECTOR2D,
    ZERO_VECTOR3D,
)
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.matrix import Matrix, Matrix33, Matrix44
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.math.vector import UnitVector2D, UnitVector3D, Vector2D, Vector3D
