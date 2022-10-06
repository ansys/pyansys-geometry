"""Mathematical constants for PyGeometry."""

from ansys.geometry.core.math.point import (
    DEFAULT_POINT2D_VALUES,
    DEFAULT_POINT3D_VALUES,
    Point2D,
    Point3D,
)
from ansys.geometry.core.math.vector import UnitVector2D, UnitVector3D, Vector2D, Vector3D

DEFAULT_POINT3D = Point3D(DEFAULT_POINT3D_VALUES)
"""Default value for a ``Point3D``."""

DEFAULT_POINT2D = Point2D(DEFAULT_POINT2D_VALUES)
"""Default value for a ``Point2D``."""

UNITVECTOR3D_X = UnitVector3D([1, 0, 0])
"""UnitVector3D in the cartesian traditional X direction."""

UNITVECTOR3D_Y = UnitVector3D([0, 1, 0])
"""UnitVector3D in the cartesian traditional Y direction."""

UNITVECTOR3D_Z = UnitVector3D([0, 0, 1])
"""Unit vector in the cartesian traditional Z direction."""

UNITVECTOR2D_X = UnitVector2D([1, 0])
"""UnitVector2D in the cartesian traditional X direction."""

UNITVECTOR2D_Y = UnitVector2D([0, 1])
"""UnitVector2D in the cartesian traditional Y direction."""

ZERO_VECTOR3D = Vector3D([0, 0, 0])
"""Zero-valued Vector3D object."""

ZERO_VECTOR2D = Vector2D([0, 0])
"""Zero-valued Vector2D object."""

ZERO_POINT3D = Point3D([0, 0, 0])
"""Zero-valued Point3D object."""

ZERO_POINT2D = Point2D([0, 0])
"""Zero-valued Point2D object."""

# Define the numpy.ndarrays as read-only - just for the sake of being "safe"
DEFAULT_POINT3D.setflags(write=False)
DEFAULT_POINT2D.setflags(write=False)
UNITVECTOR3D_X.setflags(write=False)
UNITVECTOR3D_Y.setflags(write=False)
UNITVECTOR3D_Z.setflags(write=False)
UNITVECTOR2D_X.setflags(write=False)
UNITVECTOR2D_Y.setflags(write=False)
ZERO_VECTOR3D.setflags(write=False)
ZERO_VECTOR2D.setflags(write=False)
ZERO_POINT3D.setflags(write=False)
ZERO_POINT2D.setflags(write=False)
