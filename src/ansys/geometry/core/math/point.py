"""Provides ``Point`` classes."""

from beartype import beartype as check_input_types
from beartype.typing import TYPE_CHECKING, Optional, Union
import numpy as np
from pint import Quantity, Unit

from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.misc import (
    DEFAULT_UNITS,
    UNITS,
    PhysicalQuantity,
    check_ndarray_is_float_int,
    check_type,
)
from ansys.geometry.core.typing import RealSequence

DEFAULT_POINT2D_VALUES = [np.nan, np.nan]
"""Default values for a 2D point."""

DEFAULT_POINT3D_VALUES = [np.nan, np.nan, np.nan]
"""Default values for a 3D point."""

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.math.vector import Vector2D, Vector3D

BASE_UNIT_LENGTH = UNITS.get_base_units(DEFAULT_UNITS.LENGTH)[1]
"""Default value for the length of the base unit."""


class Point2D(np.ndarray, PhysicalQuantity):
    """
    Provides ``Point2D`` geometry primitive representation.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence], default: DEFAULT_POINT2D_VALUES
        Direction arguments, either as a :class:`numpy.ndarray <numpy.ndarray>` class
        or as a ``RealSequence``.
    unit : ~pint.Unit, optional
        Units for defining 2D point values. By default, ``DEFAULT_UNITS.LENGTH``
    """

    def __new__(
        cls,
        input: Optional[Union[np.ndarray, RealSequence]] = DEFAULT_POINT2D_VALUES,
        unit: Optional[Unit] = None,
    ):
        """Initialize the ``Point2D`` class."""
        # Build an empty np.ndarray object
        return np.zeros(len(input)).view(cls)

    def __init__(
        self,
        input: Union[np.ndarray, RealSequence] = DEFAULT_POINT2D_VALUES,
        unit: Optional[Unit] = None,
    ):
        """Initialize ``Point2D`` class."""
        # Call the PhysicalQuantity ctor
        unit = unit if unit else DEFAULT_UNITS.LENGTH
        super().__init__(unit, expected_dimensions=DEFAULT_UNITS.LENGTH)

        # Check the inputs
        check_ndarray_is_float_int(input, "input") if isinstance(
            input, np.ndarray
        ) else check_ndarray_is_float_int(np.asarray(input), "input")

        # Check dimensions
        if len(input) != 2:
            raise ValueError("Point2D class must receive two arguments.")  # noqa: E501

        # Store values
        self._quantities = [Quantity(elem, units=unit) for elem in input]
        self.flat = [elem.to_base_units().m for elem in self._quantities]

    @check_input_types
    def __eq__(self, other: "Point2D") -> bool:
        """Equals operator for the``Point2D`` class."""
        return np.array_equal(self, other)

    def __ne__(self, other: "Point2D") -> bool:
        """Not equals operator for the ``Point2D`` class."""
        return not self == other

    @check_input_types
    def __set_value(self, input: Quantity, idx: int) -> None:
        """General setter method for the ``Point2D`` class."""
        self[idx] = self._base_units_magnitude(input)
        self._quantities[idx] = input.to(self.unit)

    def __add__(self, other: Union["Point2D", "Vector2D"]) -> "Point2D":
        """Add operation for the ``Point2D`` class."""
        from ansys.geometry.core.math.vector import Vector2D

        check_type(other, (Point2D, Vector2D))
        point = np.add(self, other).view(Point2D)
        point._unit = self.unit
        point._base_unit = self.base_unit
        point._quantities = [np.nan, np.nan]
        return point

    def __sub__(self, other: "Point2D") -> "Point2D":
        """Subtraction operation for the ``Point2D`` class."""
        from ansys.geometry.core.math.vector import Vector2D

        check_type(other, (Point2D, Vector2D))
        point = np.subtract(self, other).view(Point2D)
        point._unit = self.unit
        point._base_unit = self.base_unit
        point._quantities = [np.nan, np.nan]
        return point

    @property
    def x(self) -> Quantity:
        """X plane component value."""
        if self._quantities[0] is np.nan:
            self._quantities[0] = Quantity(self[0], units=self.base_unit).to(self.unit)
        return self._quantities[0]

    @x.setter
    def x(self, x: Quantity) -> None:
        """Set the X plane component value."""
        self.__set_value(x, 0)

    @property
    def y(self) -> Quantity:
        """Y plane component value."""
        if self._quantities[1] is np.nan:
            self._quantities[1] = Quantity(self[1], units=self.base_unit).to(self.unit)
        return self._quantities[1]

    @y.setter
    def y(self, y: Quantity) -> None:
        """Set the Y plane component value."""
        self.__set_value(y, 1)

    @PhysicalQuantity.unit.getter
    def unit(self) -> Unit:
        """Get the unit of the object."""
        if hasattr(self, "_unit"):
            return self._unit
        else:
            self._unit = DEFAULT_UNITS.LENGTH
            return self._unit

    @PhysicalQuantity.base_unit.getter
    def base_unit(self) -> Unit:
        """Get the base unit of the object."""
        if hasattr(self, "_base_unit"):
            return self._base_unit
        else:
            self._base_unit = BASE_UNIT_LENGTH
            return self._base_unit


class Point3D(np.ndarray, PhysicalQuantity):
    """
    Provides ``Point3D`` geometry primitive representation.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence], default: DEFAULT_POINT3D_VALUES
        Direction arguments, either as a :class:`numpy.ndarray <numpy.ndarray>` class
        or as a ``RealSequence``.
    unit : ~pint.Unit, optional
        Units for defining 3D point values. By default, ``DEFAULT_UNITS.LENGTH``
    """

    def __new__(
        cls,
        input: Optional[Union[np.ndarray, RealSequence]] = DEFAULT_POINT3D_VALUES,
        unit: Optional[Unit] = None,
    ):
        """Initialize ``Point3D`` class."""
        # Build an empty np.ndarray object
        return np.zeros(len(input)).view(cls)

    def __init__(
        self,
        input: Union[np.ndarray, RealSequence] = DEFAULT_POINT3D_VALUES,
        unit: Optional[Unit] = None,
    ):
        """Initialize ``Point3D`` class."""
        # Call the PhysicalQuantity ctor
        unit = unit if unit else DEFAULT_UNITS.LENGTH
        super().__init__(unit, expected_dimensions=DEFAULT_UNITS.LENGTH)

        # Check the inputs
        check_ndarray_is_float_int(input, "input") if isinstance(
            input, np.ndarray
        ) else check_ndarray_is_float_int(np.asarray(input), "input")

        # Check dimensions
        if len(input) != 3:
            raise ValueError("Point3D class must receive 3 arguments.")  # noqa: E501

        # Store values
        self._quantities = [Quantity(elem, units=unit) for elem in input]
        self.flat = [elem.to_base_units().m for elem in self._quantities]

    @check_input_types
    def __eq__(self, other: "Point3D") -> bool:
        """Equals operator for the ``Point3D`` class."""
        return np.array_equal(self, other)

    def __ne__(self, other: "Point3D") -> bool:
        """Not equals operator for the ``Point3D`` class."""
        return not self == other

    def __add__(self, other: Union["Point3D", "Vector3D"]) -> "Point3D":
        """Add operation for the ``Point3D`` class."""
        from ansys.geometry.core.math.vector import Vector3D

        check_type(other, (Point3D, Vector3D))
        point = np.add(self, other).view(Point3D)
        point._unit = self.unit
        point._base_unit = self.base_unit
        point._quantities = [np.nan, np.nan, np.nan]
        return point

    def __sub__(self, other: Union["Point3D", "Vector3D"]) -> "Point3D":
        """Subtraction operation for the ``Point3D`` class."""
        from ansys.geometry.core.math.vector import Vector3D

        check_type(other, (Point3D, Vector3D))
        point = np.subtract(self, other).view(Point3D)
        point._unit = self.unit
        point._base_unit = self.base_unit
        point._quantities = [np.nan, np.nan, np.nan]
        return point

    @check_input_types
    def __set_value(self, input: Quantity, idx: int) -> None:
        """General setter method for the ``Point3D`` class."""
        self[idx] = self._base_units_magnitude(input)
        self._quantities[idx] = input.to(self.unit)

    @property
    def x(self) -> Quantity:
        """X plane component value."""
        if self._quantities[0] is np.nan:
            self._quantities[0] = Quantity(self[0], units=self.base_unit).to(self.unit)
        return self._quantities[0]

    @x.setter
    def x(self, x: Quantity) -> None:
        """Set the X plane component value."""
        self.__set_value(x, 0)

    @property
    def y(self) -> Quantity:
        """Y plane component value."""
        if self._quantities[1] is np.nan:
            self._quantities[1] = Quantity(self[1], units=self.base_unit).to(self.unit)
        return self._quantities[1]

    @y.setter
    def y(self, y: Quantity) -> None:
        """Set the Y plane component value."""
        self.__set_value(y, 1)

    @property
    def z(self) -> Quantity:
        """Z plane component value."""
        if self._quantities[2] is np.nan:
            self._quantities[2] = Quantity(self[2], units=self.base_unit).to(self.unit)
        return self._quantities[2]

    @z.setter
    def z(self, z: Quantity) -> None:
        """Set the Z plane component value."""
        self.__set_value(z, 2)

    @PhysicalQuantity.unit.getter
    def unit(self) -> Unit:
        """Get the unit of the object."""
        if hasattr(self, "_unit"):
            return self._unit
        else:
            self._unit = DEFAULT_UNITS.LENGTH
            return self._unit

    @PhysicalQuantity.base_unit.getter
    def base_unit(self) -> Unit:
        """Get the base unit of the object."""
        if hasattr(self, "_base_unit"):
            return self._base_unit
        else:
            self._base_unit = BASE_UNIT_LENGTH
            return self._base_unit

    def transform(self, matrix: "Matrix44") -> "Point3D":
        """
        Transform the current Point3D with a transformation matrix.

        Notes
        -----
        Transform the current Point3D object by applying the specified 4x4
        transformation matrix and returns a new Point3D object representing the
        transformed point.

        Parameters
        ----------
        matrix : Matrix44
            The 4x4 transformation matrix to apply to the point.

        Returns
        -------
        Point3D
            A new Point3D object that is the transformed copy of the original point after applying
            the transformation matrix.
        """
        point_4x1 = np.append(self, 1)
        result_4x1 = matrix * point_4x1
        result_point = Point3D(result_4x1[0:3])
        result_point.unit = self.unit
        return result_point
