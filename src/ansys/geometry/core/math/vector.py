"""``Vector`` classes module"""
from io import UnsupportedOperation
from typing import Union

import numpy as np
from pint import Quantity

from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.misc import (
    UNIT_ANGLE,
    Accuracy,
    check_is_float_int,
    check_ndarray_is_float_int,
    check_type,
    check_type_equivalence,
)
from ansys.geometry.core.typing import Real, RealSequence


class Vector3D(np.ndarray):
    """A 3-dimensional vector class.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence]
        3-dimensional :class:`numpy.ndarray <numpy.ndarray>` with shape(X,).
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence]):
        """Constructor for ``Vector3D``."""

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
        """The norm of the vector."""
        return np.linalg.norm(self)

    @property
    def magnitude(self) -> float:
        """The norm of the vector."""
        return self.norm

    @property
    def is_zero(self) -> bool:
        """Confirms whether all components of the ``Vector3D`` are zero."""
        # TODO incorporate length accuracy in comparison
        return all([comp == 0 for comp in self])

    def is_perpendicular_to(self, other_vector: "Vector3D") -> bool:
        """Verifies if the two ``Vector3D`` instances are perpendicular."""
        if self.is_zero or other_vector.is_zero:
            return False

        angle_is_zero = Accuracy.angle_is_zero(self * other_vector)
        return angle_is_zero

    def normalize(self) -> "Vector3D":
        """Return a normalized version of the ``Vector3D``."""
        norm = self.norm
        if norm > 0:
            return (self / norm).view(Vector3D)
        else:
            raise ValueError("The norm of the Vector3D is not valid.")

    def get_angle_between(self, v: "Vector3D") -> Quantity:
        """Method for getting the angle between two ``Vector3D`` objects.

        Parameters
        ----------
        v : Vector3D
            The other vector to compute the angle with.

        Returns
        -------
        Quantity
            The angle between both vectors.
        """
        if v.is_zero or self.is_zero:
            raise ValueError("Vectors cannot be zero-valued.")

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
        return np.cross(self, v).view(Vector3D)

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
            return np.multiply(self, other).view(Vector3D)
        else:
            check_type_equivalence(other, self)
            return self.dot(other)

    def __mod__(self, other: "Vector3D") -> "Vector3D":
        """Overload % operator with cross product."""
        return self.cross(other)

    def __add__(self, other: Union["Vector3D", Point3D]) -> Union["Vector3D", Point3D]:
        """Addition operation overload for ``Vector3D`` objects."""
        try:
            check_type_equivalence(other, self)
        except TypeError:
            if isinstance(other, Point3D):
                return other + self
            else:
                raise NotImplementedError(
                    f"Vector3D addition operation not implemented for {type(other)}"
                )
        return Vector3D(np.add(self, other))

    def __sub__(self, other: "Vector3D") -> "Vector3D":
        """Subtraction operation overload for ``Vector3D`` objects."""
        check_type_equivalence(other, self)
        return np.subtract(self, other).view(Vector3D)

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
            A :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
            representing the first point.
        point_b : Point3D
            A :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
            representing the second point.

        Notes
        -----
        The resulting ``Vector3D`` is expressed in `Point3D``
        base units, no matter what.

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
        2-dimensional :class:`numpy.ndarray <numpy.ndarray>` with shape(X,).
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence]):
        """Constructor for ``Vector2D``."""

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
        """Sets the Y coordinate of ``Vector2D``."""
        check_is_float_int(value, "y")
        self[1] = value

    @property
    def norm(self) -> float:
        """The norm of the vector."""
        return np.linalg.norm(self)

    @property
    def magnitude(self) -> float:
        """The norm of the vector."""
        return self.norm

    @property
    def is_zero(self) -> bool:
        """Confirms whether all components of the ``Vector2D`` are zero."""
        return all([comp == 0 for comp in self])

    def is_perpendicular_to(self, other_vector: "Vector2D") -> bool:
        """Verifies if the two ``Vector2D`` instances are perpendicular."""
        if self.is_zero or other_vector.is_zero:
            return False

        angle_is_zero = Accuracy.angle_is_zero(self * other_vector)
        return angle_is_zero

    def normalize(self) -> "Vector2D":
        """Return a normalized version of the ``Vector2D``."""
        norm = self.norm
        if norm > 0:
            return (self / norm).view(Vector2D)
        else:
            raise ValueError("The norm of the Vector2D is not valid.")

    def get_angle_between(self, v: "Vector2D") -> Quantity:
        """Method for getting the angle between two ``Vector2D`` objects.

        Parameters
        ----------
        v : Vector2D
            The other vector to compute the angle with.

        Returns
        -------
        Quantity
            The angle between both vectors.
        """
        if v.is_zero or self.is_zero:
            raise ValueError("Vectors cannot be zero-valued.")

        angle = np.arctan2(v.y * self.x - v.x * self.y, v.x * self.x + v.y * self.y)

        if angle < 0:
            angle = angle + 2 * np.pi

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
            return np.multiply(self, other).view(Vector2D)
        else:
            check_type_equivalence(other, self)
            return self.dot(other)

    def __add__(self, other: Union["Vector2D", Point2D]) -> Union["Vector2D", Point2D]:
        """Addition operation overload for ``Vector2D`` objects."""
        try:
            check_type_equivalence(other, self)
        except TypeError:
            if isinstance(other, Point2D):
                return other + self
            else:
                raise NotImplementedError(
                    f"Vector2D addition operation not implemented for {type(other)}"
                )
        return Vector2D(np.add(self, other))

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        """Subtraction operation overload for ``Vector2D`` objects."""
        check_type_equivalence(other, self)
        return np.subtract(self, other).view(Vector2D)

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
            A :class:`Point2D <ansys.geometry.core.math.point.Point2D>`
            representing the first point.
        point_b : Point2D
            A :class:`Point2D <ansys.geometry.core.math.point.Point2D>`
            representing the second point.

        Notes
        -----
        The resulting ``Vector2D`` is expressed in `Point2D``
        base units, no matter what.

        Returns
        -------
        Vector2D
            A ``Vector2D`` from ``point_a`` to ``point_b``.
        """
        check_type(point_a, (Point2D, np.ndarray, list))
        check_type(point_b, (Point2D, np.ndarray, list))
        return Vector2D(point_b - point_a)


class UnitVector3D(Vector3D):
    """A 3-dimensional unit vector class.

    Parameters
    ----------
    input : ~numpy.ndarray, ``Vector3D``
        * One dimensional :class:`numpy.ndarray <numpy.ndarray>` with shape(X,)
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
            A :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
            representing the first point.
        point_b : Point3D
            A :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
            representing the second point.

        Returns
        -------
        UnitVector3D
            A ``UnitVector3D`` from ``point_a`` to ``point_b``.
        """
        return UnitVector3D(Vector3D.from_points(point_a, point_b))


class UnitVector2D(Vector2D):
    """A 2-dimensional unit vector class.

    Parameters
    ----------
    input : ~numpy.ndarray, ``Vector2D``
        * One dimensional :class:`numpy.ndarray <numpy.ndarray>` with shape(X,)
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
            A :class:`Point2D <ansys.geometry.core.math.point.Point2D>`
            representing the first point.
        point_b : Point2D
            A :class:`Point2D <ansys.geometry.core.math.point.Point2D>`
            representing the second point.

        Returns
        -------
        UnitVector2D
            A ``UnitVector2D`` from ``point_a`` to ``point_b``.
        """
        return UnitVector2D(Vector2D.from_points(point_a, point_b))
