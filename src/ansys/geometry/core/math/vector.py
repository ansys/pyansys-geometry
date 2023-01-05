"""Provides ``Vector`` classes."""
from io import UnsupportedOperation

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np
from pint import Quantity

from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.misc import UNIT_ANGLE, Accuracy, check_ndarray_is_float_int
from ansys.geometry.core.typing import Real, RealSequence


class Vector3D(np.ndarray):
    """Provides a 3D vector class.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence]
        3D :class:`numpy.ndarray <numpy.ndarray>` class with shape(X,).
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence]):
        """Constructor method for the ``Vector3D`` class."""

        obj = np.asarray(input).view(cls)

        # Check that the size is as expected
        if len(obj) != 3:
            raise ValueError("Vector3D class must receive 3 arguments.")  # noqa: E501

        # Check the input data
        check_ndarray_is_float_int(obj, "input")

        return obj

    @property
    def x(self) -> Real:
        """X coordinate of the ``Vector3D`` class."""
        return self[0]

    @x.setter
    @check_input_types
    def x(self, value: Real) -> None:
        """Set the Y coordinate of the ``Vector3D`` class."""
        self[0] = value

    @property
    def y(self) -> Real:
        """Y coordinate of the ``Vector3D`` class."""
        return self[1]

    @y.setter
    @check_input_types
    def y(self, value: Real) -> None:
        """Set the Y coordinate of the ``Vector3D`` class."""
        self[1] = value

    @property
    def z(self) -> Real:
        """Z coordinate of the ``Vector3D`` class."""
        return self[2]

    @z.setter
    @check_input_types
    def z(self, value: Real) -> None:
        """Set the Z coordinate of the ``Vector3D`` class."""
        self[2] = value

    @property
    def norm(self) -> float:
        """Norm of the vector."""
        return np.linalg.norm(self)

    @property
    def magnitude(self) -> float:
        """Norm of the vector."""
        return self.norm

    @property
    def is_zero(self) -> bool:
        """Check if all components of the 3D vector are zero."""
        return all([comp == 0 for comp in self])

    @check_input_types
    def is_perpendicular_to(self, other_vector: "Vector3D") -> bool:
        """Check if this vector and another vector are perpendicular."""
        if self.is_zero or other_vector.is_zero:
            return False
        else:
            return Accuracy.angle_is_zero(self * other_vector)

    @check_input_types
    def is_parallel_to(self, other_vector: "Vector3D") -> bool:
        """Check if this vector and another vector are parallel."""
        if self.is_zero or other_vector.is_zero:
            return False
        else:
            return (self % other_vector).is_zero

    @check_input_types
    def is_opposite(self, other_vector: "Vector3D") -> bool:
        """Check if this vector and another vector are opposite."""
        return bool(self.is_parallel_to(other_vector) and self * other_vector < 0)

    def normalize(self) -> "Vector3D":
        """Return a normalized version of the 3D vector."""
        norm = self.norm
        if norm > 0:
            return (self / norm).view(Vector3D)
        else:
            raise ValueError("The norm of the 3D vector is not valid.")

    @check_input_types
    def get_angle_between(self, v: "Vector3D") -> Quantity:
        """Get the angle between this 3D vector and another 3D vector.

        Parameters
        ----------
        v : Vector3D
            Other 3D vector for computing the angle.

        Returns
        -------
        Quantity
            Angle between the two 3D vectors.
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

    @check_input_types
    def cross(self, v: "Vector3D") -> "Vector3D":
        """Return the cross product of ``Vector3D`` objects."""
        return np.cross(self, v).view(Vector3D)

    @check_input_types
    def __eq__(self, other: "Vector3D") -> bool:
        """Equals operator for the ``Vector3D`` class."""
        return np.array_equal(self, other)

    def __ne__(self, other: "Vector3D") -> bool:
        """Not equals operator for the ``Vector3D`` class."""
        return not self == other

    @check_input_types
    def __mul__(self, other: Union["Vector3D", Real]) -> Union["Vector3D", Real]:
        """Overload * operator with dot product.

        Notes
        -----
        Also admits scalar multiplication.
        """
        if isinstance(other, (int, float)):
            return np.multiply(self, other).view(Vector3D)
        else:
            return self.dot(other)

    def __mod__(self, other: "Vector3D") -> "Vector3D":
        """Overload % operator with cross product."""
        return self.cross(other)

    @check_input_types
    def __add__(self, other: Union["Vector3D", Point3D]) -> Union["Vector3D", Point3D]:
        """Addition operation overload for 3D vectors."""
        if isinstance(other, Point3D):
            return other + self
        else:
            return Vector3D(np.add(self, other))

    @check_input_types
    def __sub__(self, other: "Vector3D") -> "Vector3D":
        """Subtraction operation overload for 3D vectors."""
        return np.subtract(self, other).view(Vector3D)

    @classmethod
    @check_input_types
    def from_points(
        cls,
        point_a: Union[np.ndarray, RealSequence, Point3D],
        point_b: Union[np.ndarray, RealSequence, Point3D],
    ):
        """Create a 3D vector from two distinct 3D points.

        Parameters
        ----------
        point_a : Point3D
            :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
            class representing the first point.
        point_b : Point3D
            :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
            class representing the second point.

        Notes
        -----
        The resulting 3D vector is always expressed in ``Point3D``
        base units.

        Returns
        -------
        Vector3D
            3D vector from ``point_a`` to ``point_b``.
        """
        return Vector3D(point_b - point_a)


class Vector2D(np.ndarray):
    """Proves a 2D vector class.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence]
        2D :class:`numpy.ndarray <numpy.ndarray>` class with shape(X,).
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence]):
        """Constructor for the ``Vector2D`` class."""

        obj = np.asarray(input).view(cls)

        # Check that the size is as expected
        if len(obj) != 2:
            raise ValueError("Vector2D class must receive 2 arguments.")  # noqa: E501

        # Check the input data
        check_ndarray_is_float_int(obj, "input")

        return obj

    @property
    def x(self) -> Real:
        """X coordinate of the 2D vector."""
        return self[0]

    @x.setter
    @check_input_types
    def x(self, value: Real) -> None:
        """Set the X coordinate of the 2D vector."""
        self[0] = value

    @property
    def y(self) -> Real:
        """Y coordinate of the 2D vector."""
        return self[1]

    @y.setter
    @check_input_types
    def y(self, value: Real) -> None:
        """Set the Y coordinate of the 2D vector."""
        self[1] = value

    @property
    def norm(self) -> float:
        """Norm of the 2D vector."""
        return np.linalg.norm(self)

    @property
    def magnitude(self) -> float:
        """Norm of the 2D vector."""
        return self.norm

    @property
    def is_zero(self) -> bool:
        """Check if values for all components of the 2D vector are zero."""
        return all([comp == 0 for comp in self])

    @check_input_types
    def cross(self, v: "Vector2D"):
        """Return the cross product of ``Vector2D`` objects."""
        return np.cross(self, v)

    @check_input_types
    def is_perpendicular_to(self, other_vector: "Vector2D") -> bool:
        """Check if this 2D vector and another 2D vector are perpendicular."""
        if self.is_zero or other_vector.is_zero:
            return False
        else:
            return Accuracy.angle_is_zero(self * other_vector)

    @check_input_types
    def is_parallel_to(self, other_vector: "Vector2D") -> bool:
        """Check if this vector and another vector are parallel."""
        if self.is_zero or other_vector.is_zero:
            return False
        else:
            return bool((self % other_vector) == 0)

    @check_input_types
    def is_opposite(self, other_vector: "Vector2D") -> bool:
        """Check if this vector and another vector are opposite."""
        return bool(self.is_parallel_to(other_vector) and self * other_vector < 0)

    def normalize(self) -> "Vector2D":
        """Return a normalized version of the 2D vector."""
        norm = self.norm
        if norm > 0:
            return (self / norm).view(Vector2D)
        else:
            raise ValueError("The norm of the 2D vector is not valid.")

    @check_input_types
    def get_angle_between(self, v: "Vector2D") -> Quantity:
        """Getting the angle between this 2D vector and another 2D vector.

        Parameters
        ----------
        v : Vector2D
            Other 2D vector to compute the angle with.

        Returns
        -------
        Quantity
            Angle between both 2D vectors.
        """
        if v.is_zero or self.is_zero:
            raise ValueError("Vectors cannot be zero-valued.")

        angle = np.arctan2(v.y * self.x - v.x * self.y, v.x * self.x + v.y * self.y)

        if angle < 0:
            angle = angle + 2 * np.pi

        return Quantity(angle, UNIT_ANGLE)

    @check_input_types
    def __eq__(self, other: "Vector2D") -> bool:
        """Equals operator for the ``Vector2D`` class."""
        return np.array_equal(self, other)

    def __ne__(self, other: "Vector2D") -> bool:
        """Not equals operator for the ``Vector2D`` class."""
        return not self == other

    @check_input_types
    def __mul__(self, other: Union["Vector2D", Real]) -> Union["Vector2D", Real]:
        """Overload * operator with dot product.

        Notes
        -----
        Also admits scalar multiplication.
        """
        if isinstance(other, (int, float)):
            return np.multiply(self, other).view(Vector2D)
        else:
            return self.dot(other)

    @check_input_types
    def __add__(self, other: Union["Vector2D", Point2D]) -> Union["Vector2D", Point2D]:
        """Addition operation overload for 2D vectors."""
        if isinstance(other, Point2D):
            return other + self
        else:
            return Vector2D(np.add(self, other))

    @check_input_types
    def __sub__(self, other: "Vector2D") -> "Vector2D":
        """Subtraction operation overload for 2D vectors."""
        return np.subtract(self, other).view(Vector2D)

    def __mod__(self, other: "Vector2D") -> "Vector2D":
        """Overload % operator with cross product."""
        return self.cross(other)

    @classmethod
    @check_input_types
    def from_points(
        cls,
        point_a: Union[np.ndarray, RealSequence, Point2D],
        point_b: Union[np.ndarray, RealSequence, Point2D],
    ):
        """Create a 2D vector from two distinct 2D points.

        Parameters
        ----------
        point_a : Point2D
            :class:`Point2D <ansys.geometry.core.math.point.Point2D>`
            class representing the first point.
        point_b : Point2D
            :class:`Point2D <ansys.geometry.core.math.point.Point2D>`
            class representing the second point.

        Notes
        -----
        The resulting 2D vector is always expressed in ``Point2D``
        base units.

        Returns
        -------
        Vector2D
            2D vector from ``point_a`` to ``point_b``.
        """
        return Vector2D(point_b - point_a)


class UnitVector3D(Vector3D):
    """Provdes the 3D unit vector class.

    Parameters
    ----------
    input : ~numpy.ndarray, ``Vector3D``
        * 1D :class:`numpy.ndarray <numpy.ndarray>` class with shape(X,)
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
        """Create a 3D unit vector from two distinct 3D points.

        Parameters
        ----------
        point_a : Point3D
            :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
            class representing the first point.
        point_b : Point3D
            :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
            class representing the second point.

        Returns
        -------
        UnitVector3D
            A 3D unit vector from ``point_a`` to ``point_b``.
        """
        return UnitVector3D(Vector3D.from_points(point_a, point_b))


class UnitVector2D(Vector2D):
    """Provides the 2D unit vector class.

    Parameters
    ----------
    input : ~numpy.ndarray, ``Vector2D``
        * 1D :class:`numpy.ndarray <numpy.ndarray>` class with shape(X,)
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
        """Create a 2D unit vector from two distinct 2D points.

        Parameters
        ----------
        point_a : Point2D
            :class:`Point2D <ansys.geometry.core.math.point.Point2D>`
            class representing the first point.
        point_b : Point2D
            :class:`Point2D <ansys.geometry.core.math.point.Point2D>`
            class representing the second point.

        Returns
        -------
        UnitVector2D
            A 2D unit vector from ``point_a`` to ``point_b``.
        """
        return UnitVector2D(Vector2D.from_points(point_a, point_b))
