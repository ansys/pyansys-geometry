"""``Vector`` class module"""
from io import UnsupportedOperation
from typing import Union

import numpy as np
from pint import Quantity, Unit

from ansys.geometry.core.math.point import Point
from ansys.geometry.core.misc import (
    Accuracy,
    PhysicalQuantity,
    check_is_float_int,
    check_ndarray_is_float_int,
    check_pint_unit_compatibility,
    check_type,
    check_type_equivalence,
    only_for_3d,
)
from ansys.geometry.core.misc.measurements import UNIT_ANGLE
from ansys.geometry.core.typing import Real, RealSequence


class Vector(np.ndarray):
    """A 2- or 3-dimensional vector class.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence]
        2-/3-dimensional :class:`numpy.ndarray` with shape(X,).
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence]):
        """Constructor for ``Vector``"""

        obj = np.asarray(input).view(cls)

        # Check that the size is as expected
        obj = Vector._set_vector_dimensions(obj)

        # Check the input data
        check_ndarray_is_float_int(obj, "input")

        return obj

    @classmethod
    def _set_vector_dimensions(cls, obj: "Vector") -> "Vector":
        # Check that the size is as expected
        if len(obj) == 2:
            obj._is_3d = False
        elif len(obj) == 3:
            obj._is_3d = True
        else:
            raise ValueError(
                "Vector class can only receive 2 or 3 arguments, creating a 2D or 3D vector, respectively."  # noqa: E501
            )

        return obj

    @property
    def is_3d(self) -> bool:
        """Returns ``True`` if our ``Vector`` is defined in 3D space."""
        return self._is_3d

    @property
    def is_2d(self) -> bool:
        """Returns ``True`` if our ``Vector`` is defined in 2D space."""
        return not self.is_3d

    def same_dimension_as(self, other: "Vector") -> bool:
        """Returns ``True`` if both ``Vector`` objects have the same dimensions."""
        return self.is_3d == other.is_3d

    @property
    def x(self) -> Real:
        """X coordinate of ``Vector``."""
        return self[0]

    @x.setter
    def x(self, value: Real) -> None:
        """Sets the Y coordinate of ``Vector``."""
        check_is_float_int(value, "x")
        self[0] = value

    @property
    def y(self) -> Real:
        """Y coordinate of ``Vector``."""
        return self[1]

    @y.setter
    def y(self, value: Real) -> None:
        """Sets the Y coordinate of ``Vector``."""
        check_is_float_int(value, "y")
        self[1] = value

    @property
    @only_for_3d
    def z(self) -> Real:
        """Z coordinate of ``Vector``.

        Notes
        -----
        Only valid for ``Vector`` objects defined in 3D space.
        """
        return self[2]

    @z.setter
    @only_for_3d
    def z(self, value: Real) -> None:
        """Sets the Z coordinate of ``Vector``.

        Notes
        -----
        Only valid for ``Vector`` objects defined in 3D space.
        """
        check_is_float_int(value, "z")
        self[2] = value

    @property
    def norm(self) -> float:
        return np.linalg.norm(self)

    def is_perpendicular_to(self, other_vector: "Vector") -> bool:
        """Verifies if the two ``Vector`` instances are perpendicular."""
        if self.is_zero or other_vector.is_zero:
            return False

        angle_is_zero = Accuracy.angle_is_zero(self * other_vector)
        return angle_is_zero

    @property
    def is_zero(self) -> bool:
        """Confirms whether all components of the ``Vector`` are zero."""
        # TODO incorporate length accuracy in comparison
        return all([comp == 0 for comp in self])

    def normalize(self) -> "Vector":
        """Return a normalized version of the ``Vector``."""
        norm = self.norm
        if norm > 0:
            return Vector(self / norm)
        else:
            raise ValueError("The norm of the Vector is not valid.")

    def get_angle_between(self, v: "Vector") -> Quantity:
        if v.is_zero or self.is_zero:
            raise ValueError("Both vectors cannot be zero.")

        sine = (self % v).magnitude
        cosine = self * v

        if Accuracy.angle_is_zero(sine):
            if cosine > 0.0:
                return Quantity(0, UNIT_ANGLE)
            else:
                return Quantity(np.pi, UNIT_ANGLE)
        else:
            return Quantity(np.arctan2(sine, cosine), UNIT_ANGLE)

    @only_for_3d
    def cross(self, v: "Vector") -> "Vector":
        """Return cross product of 3D Vector objects"""
        check_type_equivalence(v, self)
        if self.same_dimension_as(v):
            return Vector(np.cross(self, v))
        else:
            raise ValueError("Invalid Vector dimensions for cross product.")

    def __eq__(self, other: "Vector") -> bool:
        """Equals operator for ``Vector``."""
        check_type_equivalence(other, self)
        return self.is_3d == other.is_3d and np.array_equal(self, other)

    def __ne__(self, other: "Vector") -> bool:
        """Not equals operator for ``Vector``."""
        return not self == other

    def __mul__(self, other: Union["Vector", Real]) -> Union["Vector", Real]:
        """Overload * operator with dot product.

        Note
        ----
        Also admits scalar multiplication.
        """
        if isinstance(other, (int, float)):
            return Vector(np.multiply(self, other))
        else:
            check_type_equivalence(other, self)
            if self.same_dimension_as(other):
                return self.dot(other)
            else:
                raise ValueError("Invalid Vector dimensions for dot product.")

    @property
    def magnitude(self) -> float:
        return self.norm

    @only_for_3d
    def __mod__(self, other: "Vector") -> "Vector":
        """Overload % operator with cross product."""
        return self.cross(other)

    @classmethod
    def from_points(
        cls,
        point_a: Union[np.ndarray, RealSequence, Point],
        point_b: Union[np.ndarray, RealSequence, Point],
    ):
        """Create a ``Vector3D`` from two distinct ``Point``.

        Parameters
        ----------
        point_a : Point
            A :class:`Point` representing the first point.
        point_b : Point
            A :class:`Point` representing the second point.

        Returns
        -------
        Vector3D
            A ``Vector3D`` from ``point_a`` to ``point_b``.
        """
        check_type(point_a, (Point, np.ndarray, list))
        check_type(point_b, (Point, np.ndarray, list))
        return Vector(point_b - point_a)


class UnitVector(Vector):
    """A 2-/3-dimensional ``UnitVector`` class.

    Parameters
    ----------
    input : ~numpy.ndarray, ``Vector``
        * One dimensional :class:`numpy.ndarray` with shape(X,)
        * Vector
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence, Vector]):
        obj = Vector(input) if not isinstance(input, Vector) else input
        obj = obj.normalize().view(cls)
        obj = Vector._set_vector_dimensions(obj)
        obj.setflags(write=False)
        return obj

    @Vector.x.setter
    def x(self, value: Real) -> None:
        raise UnsupportedOperation("UnitVector is immutable.")

    @Vector.y.setter
    def y(self, value: Real) -> None:
        raise UnsupportedOperation("UnitVector is immutable.")

    @Vector.z.setter
    def z(self, value: Real) -> None:
        raise UnsupportedOperation("UnitVector is immutable.")

    @classmethod
    def from_points(
        cls,
        point_a: Union[np.ndarray, RealSequence, Point],
        point_b: Union[np.ndarray, RealSequence, Point],
    ):
        """Create a ``UnitVector`` from two distinct ``Point``.

        Parameters
        ----------
        point_a : Point
            A :class:`Point` representing the first point.
        point_b : Point
            A :class:`Point` representing the second point.

        Returns
        -------
        UnitVector
            A ``UnitVector`` from ``point_a`` to ``point_b``.
        """
        check_type(point_a, (Point, np.ndarray, list))
        check_type(point_b, (Point, np.ndarray, list))
        return UnitVector(point_b - point_a)


class QuantityVector(Vector, PhysicalQuantity):
    def __new__(cls, vector: Union[np.ndarray, RealSequence, Vector], unit: Unit):
        """Constructor for ``QuantityVector``."""
        # Build an empty np.ndarray object
        return np.zeros(len(vector)).view(cls)

    def __init__(
        self,
        vector: Union[np.ndarray, RealSequence, Vector],
        unit: Unit,
    ):
        # Call the PhysicalQuantity ctor
        super().__init__(unit, expected_dimensions=None)

        # Check the inputs
        check_ndarray_is_float_int(vector, "vector") if isinstance(
            vector, np.ndarray
        ) else check_ndarray_is_float_int(np.asarray(vector), "vector")

        # Check dimensions
        if len(vector) == 2:
            self._is_3d = False
        elif len(vector) == 3:
            self._is_3d = True
        else:
            raise ValueError(
                "Vector class can only receive 2 or 3 arguments, creating a 2D or 3D vector, respectively."  # noqa: E501
            )

        # Store values
        self.flat = [(elem * self.unit).to_base_units().magnitude for elem in vector]

    @property
    def x(self) -> Quantity:
        """X coordinate of ``QuantityVector``."""
        return self._get_quantity(Vector.x.fget(self))

    @x.setter
    def x(self, x: Quantity) -> None:
        """Set X coordinate of ``QuantityVector``."""
        Vector.x.fset(self, self._base_units_magnitude(x))

    @property
    def y(self) -> Quantity:
        """Y coordinate of ``QuantityVector``."""
        return self._get_quantity(Vector.y.fget(self))

    @y.setter
    def y(self, y: Quantity) -> None:
        """Set Y coordinate of ``QuantityVector``."""
        Vector.y.fset(self, self._base_units_magnitude(y))

    @property
    @only_for_3d
    def z(self) -> Quantity:
        """Z coordinate of ``QuantityVector``."""
        return self._get_quantity(Vector.z.fget(self))

    @z.setter
    @only_for_3d
    def z(self, z: Quantity) -> None:
        """Set Z coordinate of ``QuantityVector``."""
        Vector.z.fset(self, self._base_units_magnitude(z))

    @property
    def norm(self) -> Quantity:
        """Norm of ``QuantityVector``."""
        return self._get_quantity(Vector.norm.fget(self))

    @property
    def magnitude(self) -> float:
        return self.norm.m

    def normalize(self) -> Vector:
        """Return a normalized version of the ``QuantityVector``.

        Notes
        -----
        This will return a simple ``Vector`` class. Units will
        be lost since they no longer hold any meaning.
        """
        norm = self.norm.to_base_units().magnitude
        if norm > 0:
            return Vector(self / norm)
        else:
            raise ValueError("The norm of the Vector is not valid.")

    @only_for_3d
    def cross(self, v: "QuantityVector") -> "QuantityVector":
        """Return cross product of ``QuantityVector``.

        Notes
        -----
        ``QuantityVector`` returned will hold the same units as self.
        """
        check_type_equivalence(v, self)
        check_pint_unit_compatibility(v.base_unit, self.base_unit)
        vec = QuantityVector(Vector.cross(self, v), self.base_unit)
        vec.unit = self.unit
        return vec

    def __eq__(self, other: "QuantityVector") -> bool:
        """Equals operator for ``QuantityVector``."""
        check_type_equivalence(other, self)
        return self.base_unit == other.base_unit and Vector.__eq__(self, other)

    def __ne__(self, other: "QuantityVector") -> bool:
        """Not equals operator for ``QuantityVector``."""
        return not self == other

    def __mul__(self, other: Union["QuantityVector", Real]) -> Union["QuantityVector", Real]:
        """Overload * operator with dot product."""
        if isinstance(other, QuantityVector):
            check_pint_unit_compatibility(other._base_unit, self._base_unit)
        return Vector.__mul__(self, other)

    @only_for_3d
    def __mod__(self, other: "QuantityVector") -> "QuantityVector":
        """Overload % operator with cross product."""
        return self.cross(other)

    @classmethod
    def from_points(cls, point_a: Point, point_b: Point):
        """Create a ``QuantityVector`` from two distinct ``Point``.

        Parameters
        ----------
        point_a : Point
            A :class:`Point` representing the first point.
        point_b : Point
            A :class:`Point` representing the second point.

        Returns
        -------
        QuantityVector
            A ``QuantityVector`` from ``point_a`` to ``point_b``.
        """
        check_type(point_a, Point)
        check_type(point_b, Point)
        return QuantityVector(Vector.from_points(point_a, point_b), point_a.base_unit)
