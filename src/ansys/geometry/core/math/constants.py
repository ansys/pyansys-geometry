"""Mathematical constants for PyGeometry."""

from ansys.geometry.core.math.point import DEFAULT_POINT_VALUES, Point
from ansys.geometry.core.math.vector import UnitVector, Vector

DEFAULT_POINT = Point(DEFAULT_POINT_VALUES)
"""Default value for a 3D ``Point``."""

UNIT_VECTOR_X = UnitVector([1, 0, 0])
"""Unit vector in the cartesian traditional X direction."""

UNIT_VECTOR_Y = UnitVector([0, 1, 0])
"""Unit vector in the cartesian traditional Y direction."""

UNIT_VECTOR_Z = UnitVector([0, 0, 1])
"""Unit vector in the cartesian traditional Z direction."""

ZERO_VECTOR3D = Vector([0, 0, 0])
"""Zero-valued Vector object."""

ZERO_POINT3D = Point([0, 0, 0])
"""Zero-valued Point object."""

# Define the numpy.ndarrays as read-only - just for the sake of being "safe"
DEFAULT_POINT.setflags(write=False)
UNIT_VECTOR_X.setflags(write=False)
UNIT_VECTOR_Y.setflags(write=False)
UNIT_VECTOR_Z.setflags(write=False)
ZERO_VECTOR3D.setflags(write=False)
