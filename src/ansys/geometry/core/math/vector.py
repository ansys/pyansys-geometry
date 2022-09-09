"""``Vector`` class module"""
from io import UnsupportedOperation
from typing import Union

import numpy as np
from pint import Unit

from ansys.geometry.core import UNITS
from ansys.geometry.core.accuracy import Accuracy
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.misc import (
    check_is_float_int,
    check_is_pint_unit,
    check_ndarray_is_float_int,
    check_pint_unit_compatibility,
    check_type,
    check_type_equivalence,
)
from ansys.geometry.core.typing import Real, RealSequence


class Vector3D(np.ndarray):
    """A three-dimensional vector with Cartesian coordinates.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence]
        One dimensional :class:`numpy.ndarray` with shape(3,)
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence]):
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

    def is_perpendicular_to(self, other_vector: "Vector3D") -> bool:
        """Verifies if the two ``Vector3D`` instances are perpendicular."""
        if self.is_zero or other_vector.is_zero:
            return False

        angle_is_zero = Accuracy.angle_is_zero(self * other_vector)
        return angle_is_zero

    @property
    def is_zero(self) -> bool:
        """Confirms whether all components of ``Vector3D`` are zero."""
        return self.x == 0 and self.y == 0 and self.z == 0

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
        check_type_equivalence(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Vector3D") -> bool:
        """Not equals operator for ``Vector3D``."""
        return not self == other

    def __mul__(self, other: Union["Vector3D", Real]) -> Union["Vector3D", Real]:
        """Overload * operator with dot product.

        Note
        ----
        Also admits scalar multiplication.
        """
        if isinstance(other, (int, float)):
            return np.multiply(self, other).view(self.__class__)
        else:
            check_type_equivalence(other, self)
            return self.dot(other)

    def __mod__(self, other: "Vector3D") -> "Vector3D":
        """Overload % operator with cross product."""
        check_type_equivalence(other, self)
        return self.cross(other).view(self.__class__)

    @classmethod
    def from_points(
        cls,
        point_a: Union[np.ndarray, RealSequence, Point3D],
        point_b: Union[np.ndarray, RealSequence, Point3D],
    ):
        """Create a ``Vector3D`` from two distinct ``Point3D``.

        Parameters
        ----------
        point_a : Point3D
            A :class:`Point3D` representing the first point.
        point_b : Point3D
            A :class:`Point3D` representing the second point.

        Returns
        -------
        Vector3D
            A ``Vector3D`` from ``point_a`` to ``point_b``.
        """
        if point_a == point_b:
            raise ValueError("The two points cannot have the exact same coordinates.")

        x = point_b[0] - point_a[0]
        y = point_b[1] - point_a[1]
        z = point_b[2] - point_a[2]
        return Vector3D([x, y, z])


class Vector2D(np.ndarray):
    """A two-dimensional vector with Cartesian coordinates.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence]
        One dimensional :class:`numpy.ndarray` with shape(2,)
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence]):

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
        check_type_equivalence(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Vector2D") -> bool:
        """Not equals operator for ``Vector2D``."""
        return not self == other

    def __mul__(self, other: Union["Vector2D", Real]) -> Union["Vector2D", Real]:
        """Overload * operator with dot product.

        Note
        ----
        Also admits scalar multiplication.
        """
        if isinstance(other, (int, float)):
            return np.multiply(self, other).view(self.__class__)
        else:
            check_type_equivalence(other, self)
            return self.dot(other)

    @classmethod
    def from_points(
        cls,
        point_a: Union[np.ndarray, RealSequence, Point2D],
        point_b: Union[np.ndarray, RealSequence, Point2D],
    ):
        """Create a ``Vector2D`` from two distinct ``Point2D``.

        Parameters
        ----------
        point_a : Point2D
            A :class:`Point2D` representing the first point.
        point_b : Point2D
            A :class:`Point2D` representing the second point.

        Returns
        -------
        Vector2D
            A ``Vecto2D`` from ``point_a`` to ``point_b``.
        """
        if point_a == point_b:
            raise ValueError("The two points cannot have the exact same coordinates.")

        return Vector2D([point_b[0] - point_a[0], point_b[1] - point_a[1]])


class UnitVector3D(Vector3D):
    """A three-dimensional ``UnitVector`` class.

    Parameters
    ----------
    input : ~numpy.ndarray, ``Vector3D``
        * One dimensional :class:`numpy.ndarray` with shape(3,)
        * Vector3D
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence, Vector3D]):
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
    input : ~numpy.ndarray, Vector2D
        * One dimensional :class:`numpy.ndarray` with shape(2,)
        * Vector2D
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence, Vector2D]):
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


class QuantityVector3D(Vector3D):
    def __new__(cls, vector: Union[np.ndarray, RealSequence, Vector3D], unit: Unit):
        """Constructor for ``QuantityVector3D``."""

        # Transform to base units
        check_is_pint_unit(unit, "unit")
        vector_base_units = [(elem * unit).to_base_units().magnitude for elem in vector]

        # Build the Vector3D object
        obj = Vector3D(vector_base_units)
        obj = obj.view(cls)

        # Store the units
        obj._unit = unit
        _, obj._base_unit = UNITS.get_base_units(unit)

        return obj

    @property
    def x(self) -> Real:
        """X coordinate of ``QuantityVector3D``."""
        return UNITS.convert(Vector3D.x.fget(self), self._base_unit, self._unit)

    @x.setter
    def x(self, x: Real) -> None:
        """Set X coordinate of ``QuantityVector3D``."""
        check_is_float_int(x, "x")
        Vector3D.x.fset(self, (x * self._unit).to_base_units().magnitude)

    @property
    def y(self) -> Real:
        """Y coordinate of ``QuantityVector3D``."""
        return UNITS.convert(Vector3D.y.fget(self), self._base_unit, self._unit)

    @y.setter
    def y(self, y: Real) -> None:
        """Set Y coordinate of ``QuantityVector3D``."""
        check_is_float_int(y, "y")
        Vector3D.y.fset(self, (y * self._unit).to_base_units().magnitude)

    @property
    def z(self) -> Real:
        """Z coordinate of ``QuantityVector3D``."""
        return UNITS.convert(Vector3D.z.fget(self), self._base_unit, self._unit)

    @z.setter
    def z(self, z: Real) -> None:
        """Set Z coordinate of ``QuantityVector3D``."""
        check_is_float_int(z, "z")
        Vector3D.z.fset(self, (z * self._unit).to_base_units().magnitude)

    @property
    def norm(self) -> float:
        """Norm of ``QuantityVector3D``."""
        return UNITS.convert(Vector3D.norm.fget(self), self._base_unit, self._unit)

    @property
    def unit(self) -> Unit:
        """Returns the unit of the ``QuantityVector3D``."""
        return self._unit

    @unit.setter
    def unit(self, unit: Unit) -> None:
        """Sets the unit of the ``QuantityVector3D``."""
        check_is_pint_unit(unit, "unit")
        check_pint_unit_compatibility(unit, self._base_unit)
        self._unit = unit

    @property
    def base_unit(self) -> Unit:
        """Returns the base unit of the ``QuantityVector3D``."""
        return self._base_unit

    def normalize(self) -> "QuantityVector3D":
        """Return a normalized version of the ``QuantityVector3D``"""
        vec = Vector3D.normalize(self).view(QuantityVector3D)
        vec._unit = self._unit
        vec._base_unit = self._base_unit
        return vec

    def cross(self, v: "QuantityVector3D") -> "QuantityVector3D":
        """Return cross product of ``QuantityVector3D``"""
        check_pint_unit_compatibility(v._base_unit, self._base_unit)
        vec = Vector3D.cross(self, v).view(QuantityVector3D)

        # At this point, data is stored as base_unit^2
        factor, _ = UNITS.get_base_units(self._unit)
        vec /= factor

        vec._unit = self._unit
        vec._base_unit = self._base_unit
        return vec

    def __eq__(self, other: "QuantityVector3D") -> bool:
        """Equals operator for ``QuantityVector3D``."""
        check_type_equivalence(other, self)
        return np.array_equal(self, other) and self._base_unit == other._base_unit

    def __ne__(self, other: "QuantityVector3D") -> bool:
        """Not equals operator for ``QuantityVector3D``."""
        return not self == other

    def __mul__(self, other: "QuantityVector3D") -> Real:
        """Overload * operator with dot product."""
        check_type_equivalence(other, self)
        check_pint_unit_compatibility(other._base_unit, self._base_unit)
        return self.dot(other)

    def __mod__(self, other: "QuantityVector3D") -> "QuantityVector3D":
        """Overload % operator with cross product."""
        check_type_equivalence(other, self)
        check_pint_unit_compatibility(other._base_unit, self._base_unit)
        return self.cross(other)

    @classmethod
    def from_points(cls, point_a: Point3D, point_b: Point3D):
        """Create a ``QuantityVector3D`` from two distinct ``Point3D``.

        Parameters
        ----------
        point_a : Point3D
            A :class:`Point3D` representing the first point.
        point_b : Point3D
            A :class:`Point3D` representing the second point.

        Returns
        -------
        QuantityVector3D
            A ``QuantityVector3D`` from ``point_a`` to ``point_b``.
        """

        check_type(point_a, Point3D)
        check_type(point_b, Point3D)

        if point_a == point_b:
            raise ValueError("The two points cannot have the exact same coordinates.")

        x = point_b[0] - point_a[0]
        y = point_b[1] - point_a[1]
        z = point_b[2] - point_a[2]
        return QuantityVector3D([x, y, z], point_a.base_unit)


class QuantityVector2D(Vector2D):
    def __new__(cls, vector: Union[np.ndarray, RealSequence, Vector3D], unit: Unit):
        """Constructor for ``QuantityVector2D``."""

        # Transform to base units
        check_is_pint_unit(unit, "unit")
        vector_base_units = [(elem * unit).to_base_units().magnitude for elem in vector]

        # Build the Vector2D object
        obj = Vector2D(vector_base_units)
        obj = obj.view(cls)

        # Store the units
        obj._unit = unit
        _, obj._base_unit = UNITS.get_base_units(unit)

        return obj

    @property
    def x(self) -> Real:
        """X coordinate of ``QuantityVector2D``."""
        return UNITS.convert(Vector2D.x.fget(self), self._base_unit, self._unit)

    @x.setter
    def x(self, x: Real) -> None:
        """Set X coordinate of ``QuantityVector2D``."""
        check_is_float_int(x, "x")
        Vector2D.x.fset(self, (x * self._unit).to_base_units().magnitude)

    @property
    def y(self) -> Real:
        """Y coordinate of ``QuantityVector2D``."""
        return UNITS.convert(Vector2D.y.fget(self), self._base_unit, self._unit)

    @y.setter
    def y(self, y: Real) -> None:
        """Set Y coordinate of ``QuantityVector2D``."""
        check_is_float_int(y, "y")
        Vector2D.y.fset(self, (y * self._unit).to_base_units().magnitude)

    @property
    def norm(self) -> float:
        """Norm of ``QuantityVector2D``."""
        return UNITS.convert(Vector2D.norm.fget(self), self._base_unit, self._unit)

    @property
    def unit(self) -> Unit:
        """Returns the unit of the ``QuantityVector2D``."""
        return self._unit

    @property
    def base_unit(self) -> Unit:
        """Returns the base unit of the ``QuantityVector2D``."""
        return self._base_unit

    @unit.setter
    def unit(self, unit: Unit) -> None:
        """Sets the unit of the ``QuantityVector2D``."""
        check_is_pint_unit(unit, "unit")
        check_pint_unit_compatibility(unit, self._base_unit)
        self._unit = unit

    def normalize(self) -> "QuantityVector2D":
        """Return a normalized version of the ``QuantityVector2D``"""
        vec = Vector2D.normalize(self).view(QuantityVector2D)
        vec._unit = self._unit
        vec._base_unit = self._base_unit
        return vec

    def __eq__(self, other: "QuantityVector2D") -> bool:
        """Equals operator for ``QuantityVector2D``."""
        check_type_equivalence(other, self)
        return np.array_equal(self, other) and self._base_unit == other._base_unit

    def __ne__(self, other: "QuantityVector2D") -> bool:
        """Not equals operator for ``QuantityVector2D``."""
        return not self == other

    def __mul__(self, other: "QuantityVector2D") -> Real:
        """Overload * operator with dot product."""
        check_type_equivalence(other, self)
        check_pint_unit_compatibility(other._base_unit, self._base_unit)
        return self.dot(other)

    @classmethod
    def from_points(cls, point_a: Point2D, point_b: Point2D):
        """Create a ``QuantityVector2D`` from two distinct ``Point2D``.

        Parameters
        ----------
        point_a : Point2D
            A :class:`Point2D` representing the first point.
        point_b : Point2D
            A :class:`Point2D` representing the second point.

        Returns
        -------
        QuantityVector2D
            A ``QuantityVector2D`` from ``point_a`` to ``point_b``.
        """

        check_type(point_a, Point2D)
        check_type(point_b, Point2D)

        if point_a == point_b:
            raise ValueError("The two points cannot have the exact same coordinates.")

        return QuantityVector2D(
            [point_b[0] - point_a[0], point_b[1] - point_a[1]], point_a.base_unit
        )
