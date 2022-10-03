"""``Vector`` class module"""
from io import UnsupportedOperation
from typing import Union

import numpy as np
from pint import Quantity, Unit

from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.misc import (
    Accuracy,
    PhysicalQuantity,
    check_is_float_int,
    check_ndarray_is_float_int,
    check_pint_unit_compatibility,
    check_type,
    check_type_equivalence,
)
from ansys.geometry.core.misc.measurements import UNIT_ANGLE
from ansys.geometry.core.typing import Real, RealSequence


class Vector3D(np.ndarray):
    """A 3-dimensional vector class.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence]
        3-dimensional :class:`numpy.ndarray` with shape(X,).
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence]):
        """Constructor for ``Vector3D``"""

        obj = np.asarray(input).view(cls)

        # Check that the size is as expected
        if len(obj) != 3:
            raise ValueError("Vector3D class must receive 3 arguments.")  # noqa: E501

        # Check the input data
        check_ndarray_is_float_int(obj, "input")

        return obj

    @property
    def x(self) -> Real:
        """X coordinate of ``Vector3D``."""
        return self[0]

    @x.setter
    def x(self, value: Real) -> None:
        """Sets the Y coordinate of ``Vector3D``."""
        check_is_float_int(value, "x")
        self[0] = value

    @property
    def y(self) -> Real:
        """Y coordinate of ``Vector3D``."""
        return self[1]

    @y.setter
    def y(self, value: Real) -> None:
        """Sets the Y coordinate of ``Vector3D``."""
        check_is_float_int(value, "y")
        self[1] = value

    @property
    def z(self) -> Real:
        """Z coordinate of ``Vector3D``."""
        return self[2]

    @z.setter
    def z(self, value: Real) -> None:
        """Sets the Z coordinate of ``Vector3D``."""
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
        """Confirms whether all components of the ``Vector3D`` are zero."""
        # TODO incorporate length accuracy in comparison
        return all([comp == 0 for comp in self])

    def normalize(self) -> "Vector3D":
        """Return a normalized version of the ``Vector3D``."""
        norm = self.norm
        if norm > 0:
            return Vector3D(self / norm)
        else:
            raise ValueError("The norm of the Vector3D is not valid.")

    def get_angle_between(self, v: "Vector3D") -> Quantity:
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

    def cross(self, v: "Vector3D") -> "Vector3D":
        """Return cross product of Vector3D objects"""
        check_type_equivalence(v, self)
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

        Notes
        -----
        Also admits scalar multiplication.
        """
        if isinstance(other, (int, float)):
            return Vector3D(np.multiply(self, other))
        else:
            check_type_equivalence(other, self)
            return self.dot(other)

    @property
    def magnitude(self) -> float:
        return self.norm

    def __mod__(self, other: "Vector3D") -> "Vector3D":
        """Overload % operator with cross product."""
        return self.cross(other)

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
        check_type(point_a, (Point3D, np.ndarray, list))
        check_type(point_b, (Point3D, np.ndarray, list))
        return Vector3D(point_b - point_a)


class Vector2D(np.ndarray):
    """A 2-dimensional vector class.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence]
        2-dimensional :class:`numpy.ndarray` with shape(X,).
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence]):
        """Constructor for ``Vector2D``"""

        obj = np.asarray(input).view(cls)

        # Check that the size is as expected
        if len(obj) != 2:
            raise ValueError("Vector2D class must receive 2 arguments.")  # noqa: E501

        # Check the input data
        check_ndarray_is_float_int(obj, "input")

        return obj

    @property
    def x(self) -> Real:
        """X coordinate of ``Vector2D``."""
        return self[0]

    @x.setter
    def x(self, value: Real) -> None:
        """Sets the X coordinate of ``Vector2D``."""
        check_is_float_int(value, "x")
        self[0] = value

    @property
    def y(self) -> Real:
        """Y coordinate of ``Vector2D``."""
        return self[1]

    @y.setter
    def y(self, value: Real) -> None:
        """Sets the Y coordinate of ``Vector``."""
        check_is_float_int(value, "y")
        self[1] = value

    @property
    def norm(self) -> float:
        return np.linalg.norm(self)

    def is_perpendicular_to(self, other_vector: "Vector2D") -> bool:
        """Verifies if the two ``Vector2D`` instances are perpendicular."""
        if self.is_zero or other_vector.is_zero:
            return False

        angle_is_zero = Accuracy.angle_is_zero(self * other_vector)
        return angle_is_zero

    @property
    def is_zero(self) -> bool:
        """Confirms whether all components of the ``Vector2D`` are zero."""
        return all([comp == 0 for comp in self])

    def normalize(self) -> "Vector2D":
        """Return a normalized version of the ``Vector2D``."""
        norm = self.norm
        if norm > 0:
            return Vector2D(self / norm)
        else:
            raise ValueError("The norm of the Vector2D is not valid.")

    def get_angle_between(self, v: "Vector2D") -> Quantity:
        if v.is_zero or self.is_zero:
            raise ValueError("Both vectors cannot be zero.")

        angle = np.arctan2(v.y * self.x - v.x * self.y, v.x * self.x + v.y * self.y)

        if angle < 0:
            angle = angle + np.pi

        return Quantity(angle, UNIT_ANGLE)

    def __eq__(self, other: "Vector2D") -> bool:
        """Equals operator for ``Vector2D``."""
        check_type_equivalence(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Vector2D") -> bool:
        """Not equals operator for ``Vector2D``."""
        return not self == other

    def __mul__(self, other: Union["Vector2D", Real]) -> Union["Vector2D", Real]:
        """Overload * operator with dot product.

        Notes
        -----
        Also admits scalar multiplication.
        """
        if isinstance(other, (int, float)):
            return Vector2D(np.multiply(self, other))
        else:
            check_type_equivalence(other, self)
            return self.dot(other)

    @property
    def magnitude(self) -> float:
        return self.norm

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
            A :class:`Point` representing the first point.
        point_b : Point2D
            A :class:`Point` representing the second point.

        Returns
        -------
        Vector2D
            A ``Vector2D`` from ``point_a`` to ``point_b``.
        """
        check_type(point_a, (Point2D, np.ndarray, list))
        check_type(point_b, (Point2D, np.ndarray, list))
        return Vector2D(point_b - point_a)


class UnitVector3D(Vector3D):
    """A 2-/3-dimensional ``UnitVector3D`` class.

    Parameters
    ----------
    input : ~numpy.ndarray, ``Vector3D``
        * One dimensional :class:`numpy.ndarray` with shape(X,)
        * Vector3D
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence, Vector3D]):
        obj = Vector3D(input) if not isinstance(input, Vector3D) else input
        obj = obj.normalize().view(cls)
        obj.setflags(write=False)
        return obj

    @Vector3D.x.setter
    def x(self, value: Real) -> None:
        raise UnsupportedOperation("UnitVector is immutable.")

    @Vector3D.y.setter
    def y(self, value: Real) -> None:
        raise UnsupportedOperation("UnitVector is immutable.")

    @Vector3D.z.setter
    def z(self, value: Real) -> None:
        raise UnsupportedOperation("UnitVector is immutable.")

    @classmethod
    def from_points(
        cls,
        point_a: Union[np.ndarray, RealSequence, Point3D],
        point_b: Union[np.ndarray, RealSequence, Point3D],
    ):
        """Create a ``UnitVector3D`` from two distinct ``Point3D``.

        Parameters
        ----------
        point_a : Point3D
            A :class:`Point3D` representing the first point.
        point_b : Point3D
            A :class:`Point3D` representing the second point.

        Returns
        -------
        UnitVector3D
            A ``UnitVector3D`` from ``point_a`` to ``point_b``.
        """
        check_type(point_a, (Point3D, np.ndarray, list))
        check_type(point_b, (Point3D, np.ndarray, list))
        return UnitVector3D(point_b - point_a)


class UnitVector2D(Vector2D):
    """A 2-dimensional unit vector class.

    Parameters
    ----------
    input : ~numpy.ndarray, ``Vector2D``
        * One dimensional :class:`numpy.ndarray` with shape(X,)
        * Vector2D
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence, Vector2D]):
        obj = Vector2D(input) if not isinstance(input, Vector2D) else input
        obj = obj.normalize().view(cls)
        obj.setflags(write=False)
        return obj

    @Vector2D.x.setter
    def x(self, value: Real) -> None:
        raise UnsupportedOperation("UnitVector is immutable.")

    @Vector2D.y.setter
    def y(self, value: Real) -> None:
        raise UnsupportedOperation("UnitVector is immutable.")

    @classmethod
    def from_points(
        cls,
        point_a: Union[np.ndarray, RealSequence, Point2D],
        point_b: Union[np.ndarray, RealSequence, Point2D],
    ):
        """Create a ``UnitVector2D`` from two distinct ``Point2D``.

        Parameters
        ----------
        point_a : Point2D
            A :class:`Point2D` representing the first point.
        point_b : Point2D
            A :class:`Point2D` representing the second point.

        Returns
        -------
        UnitVector2D
            A ``UnitVector2D`` from ``point_a`` to ``point_b``.
        """
        check_type(point_a, (Point2D, np.ndarray, list))
        check_type(point_b, (Point2D, np.ndarray, list))
        return UnitVector2D(point_b - point_a)


class QuantityVector3D(Vector3D, PhysicalQuantity):
    def __init__(
        self,
        vector: Union[np.ndarray, RealSequence, Vector3D],
        unit: Unit,
    ):
        # Call the PhysicalQuantity ctor
        super().__init__(unit, expected_dimensions=None)

        # Check the inputs
        check_ndarray_is_float_int(vector, "vector") if isinstance(
            vector, np.ndarray
        ) else check_ndarray_is_float_int(np.asarray(vector), "vector")

        # Check dimensions
        if len(vector) != 2:
            raise ValueError("QuantityVector3D class must receive 3 arguments.")  # noqa: E501

        # Store values
        self.flat = [(elem * self.unit).to_base_units().magnitude for elem in vector]

    @property
    def x(self) -> Quantity:
        """X coordinate of ``QuantityVector3D``."""
        return self._get_quantity(Vector3D.x.fget(self))

    @x.setter
    def x(self, x: Quantity) -> None:
        """Set X coordinate of ``QuantityVector3D``."""
        Vector3D.x.fset(self, self._base_units_magnitude(x))

    @property
    def y(self) -> Quantity:
        """Y coordinate of ``QuantityVector3D``."""
        return self._get_quantity(Vector3D.y.fget(self))

    @y.setter
    def y(self, y: Quantity) -> None:
        """Set Y coordinate of ``QuantityVector3D``."""
        Vector3D.y.fset(self, self._base_units_magnitude(y))

    @property
    def z(self) -> Quantity:
        """Z coordinate of ``QuantityVector3D``."""
        return self._get_quantity(Vector3D.z.fget(self))

    @z.setter
    def z(self, z: Quantity) -> None:
        """Set Z coordinate of ``QuantityVector3D``."""
        Vector3D.z.fset(self, self._base_units_magnitude(z))

    @property
    def norm(self) -> Quantity:
        """Norm of ``QuantityVector3D``."""
        return self._get_quantity(Vector3D.norm.fget(self))

    @property
    def magnitude(self) -> float:
        return self.norm.m

    def normalize(self) -> Vector3D:
        """Return a normalized version of the ``QuantityVector3D``.

        Notes
        -----
        This will return a simple ``Vector3D`` class. Units will
        be lost since they no longer hold any meaning.
        """
        norm = self.norm.to_base_units().magnitude
        if norm > 0:
            return Vector3D(self / norm)
        else:
            raise ValueError("The norm of the QuantityVector3D is not valid.")

    def cross(self, v: "QuantityVector3D") -> "QuantityVector3D":
        """Return cross product of ``QuantityVector3D``.

        Notes
        -----
        ``QuantityVector3D`` returned will hold the same units as self.
        """
        check_type_equivalence(v, self)
        check_pint_unit_compatibility(v.base_unit, self.base_unit)
        vec = QuantityVector3D(Vector3D.cross(self, v), self.base_unit)
        vec.unit = self.unit
        return vec

    def __eq__(self, other: "QuantityVector3D") -> bool:
        """Equals operator for ``QuantityVector3D``."""
        check_type_equivalence(other, self)
        return self.base_unit == other.base_unit and Vector3D.__eq__(self, other)

    def __ne__(self, other: "QuantityVector3D") -> bool:
        """Not equals operator for ``QuantityVector3D``."""
        return not self == other

    def __mul__(self, other: Union["QuantityVector3D", Real]) -> Union["QuantityVector3D", Real]:
        """Overload * operator with dot product."""
        if isinstance(other, QuantityVector3D):
            check_pint_unit_compatibility(other._base_unit, self._base_unit)
        return Vector3D.__mul__(self, other)

    def __mod__(self, other: "QuantityVector3D") -> "QuantityVector3D":
        """Overload % operator with cross product."""
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
        return QuantityVector3D(Vector3D.from_points(point_a, point_b), point_a.base_unit)


class QuantityVector2D(Vector2D, PhysicalQuantity):
    def __init__(
        self,
        vector: Union[np.ndarray, RealSequence, Vector2D],
        unit: Unit,
    ):
        # Call the PhysicalQuantity ctor
        super().__init__(unit, expected_dimensions=None)

        # Check the inputs
        check_ndarray_is_float_int(vector, "vector") if isinstance(
            vector, np.ndarray
        ) else check_ndarray_is_float_int(np.asarray(vector), "vector")

        # Check dimensions
        if len(vector) != 2:
            raise ValueError("QuantityVector2D class must receive 2 arguments.")  # noqa: E501

        # Store values
        self.flat = [(elem * self.unit).to_base_units().magnitude for elem in vector]

    @property
    def x(self) -> Quantity:
        """X coordinate of ``QuantityVector2D``."""
        return self._get_quantity(Vector2D.x.fget(self))

    @x.setter
    def x(self, x: Quantity) -> None:
        """Set X coordinate of ``QuantityVector2D``."""
        Vector2D.x.fset(self, self._base_units_magnitude(x))

    @property
    def y(self) -> Quantity:
        """Y coordinate of ``QuantityVector2D``."""
        return self._get_quantity(Vector2D.y.fget(self))

    @y.setter
    def y(self, y: Quantity) -> None:
        """Set Y coordinate of ``QuantityVector2D``."""
        Vector2D.y.fset(self, self._base_units_magnitude(y))

    @property
    def norm(self) -> Quantity:
        """Norm of ``QuantityVector2D``."""
        return self._get_quantity(Vector2D.norm.fget(self))

    @property
    def magnitude(self) -> float:
        return self.norm.m

    def normalize(self) -> Vector2D:
        """Return a normalized version of the ``QuantityVector2D``.

        Notes
        -----
        This will return a simple ``Vector2D`` class. Units will
        be lost since they no longer hold any meaning.
        """
        norm = self.norm.to_base_units().magnitude
        if norm > 0:
            return Vector2D(self / norm)
        else:
            raise ValueError("The norm of the Vector2D is not valid.")

    def __eq__(self, other: "QuantityVector2D") -> bool:
        """Equals operator for ``QuantityVector2D``."""
        check_type_equivalence(other, self)
        return self.base_unit == other.base_unit and Vector2D.__eq__(self, other)

    def __ne__(self, other: "QuantityVector2D") -> bool:
        """Not equals operator for ``QuantityVector2D``."""
        return not self == other

    def __mul__(self, other: Union["QuantityVector2D", Real]) -> Union["QuantityVector2D", Real]:
        """Overload * operator with dot product."""
        if isinstance(other, QuantityVector2D):
            check_pint_unit_compatibility(other._base_unit, self._base_unit)
        return Vector2D.__mul__(self, other)

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
        return QuantityVector2D(Vector2D.from_points(point_a, point_b), point_a.base_unit)
