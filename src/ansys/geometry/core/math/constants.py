"""Provides the ``Constants`` class for mathematical constants."""

import numpy as np

from ansys.geometry.core.math.matrix import Matrix33, Matrix44
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
"""Default value for a 2D point."""

IDENTITY_MATRIX33 = Matrix33(np.identity(3))
"""Identity ``Matrix33`` object."""

IDENTITY_MATRIX44 = Matrix44(np.identity(4))
"""Identity ``Matrix44`` object."""

UNITVECTOR3D_X = UnitVector3D([1, 0, 0])
"""Default 3D unit vector in the Cartesian traditional X direction."""

UNITVECTOR3D_Y = UnitVector3D([0, 1, 0])
"""Default 3D unit vector in the Cartesian traditional Y direction."""

UNITVECTOR3D_Z = UnitVector3D([0, 0, 1])
"""Default 3D unit vector in the Cartesian traditional Z direction."""

UNITVECTOR2D_X = UnitVector2D([1, 0])
"""Default 2D unit vector in the Cartesian traditional X direction."""

UNITVECTOR2D_Y = UnitVector2D([0, 1])
"""Default 2D unit vector  in the Cartesian traditional Y direction."""

ZERO_VECTOR3D = Vector3D([0, 0, 0])
"""Zero-valued ``Vector3D`` object."""

ZERO_VECTOR2D = Vector2D([0, 0])
"""Zero-valued ``Vector2D`` object."""

ZERO_POINT3D = Point3D([0, 0, 0])
"""Zero-valued ``Point3D`` object."""

ZERO_POINT2D = Point2D([0, 0])
"""Zero-valued ``Point2D`` object."""

# Define the numpy.ndarrays as read-only - just for the sake of being "safe"
DEFAULT_POINT3D.setflags(write=False)
DEFAULT_POINT2D.setflags(write=False)
IDENTITY_MATRIX33.setflags(write=False)
IDENTITY_MATRIX44.setflags(write=False)
UNITVECTOR3D_X.setflags(write=False)
UNITVECTOR3D_Y.setflags(write=False)
UNITVECTOR3D_Z.setflags(write=False)
UNITVECTOR2D_X.setflags(write=False)
UNITVECTOR2D_Y.setflags(write=False)
ZERO_VECTOR3D.setflags(write=False)
ZERO_VECTOR2D.setflags(write=False)
ZERO_POINT3D.setflags(write=False)
ZERO_POINT2D.setflags(write=False)
