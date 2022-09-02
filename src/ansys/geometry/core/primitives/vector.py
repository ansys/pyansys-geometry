"""``Vector`` class module"""
from io import UnsupportedOperation
from typing import List, Union

import numpy as np

from ansys.geometry.core import Real
from ansys.geometry.core.misc import (
    check_is_float_int,
    check_ndarray_is_float_int,
    check_type_operation,
)


class Vector3D(np.ndarray):
    """A three-dimensional vector with Cartesian coordinates.

    Parameters
    ----------
    input : Union[numpy.ndarray, List[Real]]
        One dimensional :class:`numpy.ndarray` with shape(3,)
    """

    def __new__(cls, input: Union[np.ndarray, List[Real]]):
        """Constructor for ``Vector3D``"""

        obj = np.asarray(input).view(cls)

        # Check that the size is as expected
        if len(obj) != 3:
            raise ValueError("Vector3D must have three coordinates.")

        # Check the input data
        check_ndarray_is_float_int(obj, "input")

        return obj

    @property
    def x(self) -> Real:
        """X coordinate of ``Vector3D``"""
        return self[0]

    @x.setter
    def x(self, value: Real) -> None:
        check_is_float_int(value, "x")
        self[0] = value

    @property
    def y(self) -> Real:
        """Y coordinate of ``Vector3D``"""
        return self[1]

    @y.setter
    def y(self, value: Real) -> None:
        check_is_float_int(value, "y")
        self[1] = value

    @property
    def z(self) -> Real:
        """Z coordinate of ``Vector3D``"""
        return self[2]

    @z.setter
    def z(self, value: Real) -> None:
        check_is_float_int(value, "z")
        self[2] = value

    @property
    def norm(self) -> float:
        return np.linalg.norm(self)

    def normalize(self) -> "Vector3D":
        """Return a normalized version of the ``Vector3D``"""
        norm = self.norm
        if norm > 0:
            return self / norm
        else:
            raise ValueError("The norm of the Vector3D is not valid.")

    def cross(self, v: "Vector3D") -> "Vector3D":
        """Return cross product of Vector3D"""
        return Vector3D(np.cross(self, v))

    def __eq__(self, other: "Vector3D") -> bool:
        """Equals operator for ``Vector3D``."""
        check_type_operation(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Vector3D") -> bool:
        """Not equals operator for ``Vector3D``."""
        return not self == other

    def __mul__(self, other: "Vector3D") -> Real:
        """Overload * operator with dot product."""
        check_type_operation(other, self)
        return self.dot(other)

    def __mod__(self, other: "Vector3D") -> "Vector3D":
        """Overload % operator with cross product."""
        check_type_operation(other, self)
        return self.cross(other)


class Vector2D(np.ndarray):
    """A two-dimensional vector with Cartesian coordinates.

    Parameters
    ----------
    input : Union[numpy.ndarray, List[Real]]
        One dimensional :class:`numpy.ndarray` with shape(2,)
    """

    def __new__(cls, input: Union[np.ndarray, List[Real]]):

        obj = np.asarray(input).view(cls)

        # Check that the size is as expected
        if len(obj) != 2:
            raise ValueError("Vector2D must have two coordinates.")

        # Check the input data
        check_ndarray_is_float_int(obj, "input")

        return obj

    @property
    def x(self) -> Real:
        """X coordinate of ``Vector2D``"""
        return self[0]

    @x.setter
    def x(self, value: Real) -> None:
        check_is_float_int(value, "x")
        self[0] = value

    @property
    def y(self) -> Real:
        """Y coordinate of ``Vector2D``"""
        return self[1]

    @y.setter
    def y(self, value: Real) -> None:
        check_is_float_int(value, "y")
        self[1] = value

    @property
    def norm(self) -> float:
        return np.linalg.norm(self)

    def normalize(self) -> "Vector2D":
        """Return a normalized version of the ``Vector2D``"""
        norm = self.norm
        if norm > 0:
            return self / norm
        else:
            raise ValueError("The norm of the Vector2D is not valid.")

    def __eq__(self, other: "Vector2D") -> bool:
        """Equals operator for ``Vector2D``."""
        check_type_operation(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Vector2D") -> bool:
        """Not equals operator for ``Vector2D``."""
        return not self == other

    def __mul__(self, other: "Vector2D") -> Real:
        """Overload * operator with dot product."""
        check_type_operation(other, self)
        return self.dot(other)


class UnitVector3D(Vector3D):
    """A three-dimensional ``UnitVector`` class.

    Parameters
    ----------
    input : numpy.ndarray, ``Vector3D``
        * One dimensional :class:`numpy.ndarray` with shape(3,)
        * Vector3D
    """

    def __new__(cls, input: Union[np.ndarray, List[Real], Vector3D]):
        obj = Vector3D(input) if not isinstance(input, Vector3D) else input
        obj = obj.normalize().view(cls)
        obj.setflags(write=False)
        return obj

    @Vector3D.x.setter
    def x(self, value: Real) -> None:
        raise UnsupportedOperation("UnitVector3D is immutable.")

    @Vector3D.y.setter
    def y(self, value: Real) -> None:
        raise UnsupportedOperation("UnitVector3D is immutable.")

    @Vector3D.z.setter
    def z(self, value: Real) -> None:
        raise UnsupportedOperation("UnitVector3D is immutable.")


class UnitVector2D(Vector2D):
    """A two-dimensional ``UnitVector`` with Cartesian coordinates.

    Parameters
    ----------
    input : numpy.ndarray, Vector2D
        * One dimensional :class:`numpy.ndarray` with shape(2,)
        * Vector2D
    """

    def __new__(cls, input: Union[np.ndarray, List[Real], Vector2D]):
        obj = Vector2D(input) if not isinstance(input, Vector2D) else input
        obj = obj.normalize().view(cls)
        obj.setflags(write=False)
        return obj

    @Vector2D.x.setter
    def x(self, value: Real) -> None:
        raise UnsupportedOperation("UnitVector2D is immutable.")

    @Vector2D.y.setter
    def y(self, value: Real) -> None:
        raise UnsupportedOperation("UnitVector2D is immutable.")
