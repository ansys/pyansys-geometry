"""``Point`` classes module."""

from typing import TYPE_CHECKING, Optional, Union

import numpy as np
from pint import Quantity, Unit

from ansys.geometry.core.misc import (
    UNIT_LENGTH,
    PhysicalQuantity,
    check_ndarray_is_float_int,
    check_type,
    check_type_equivalence,
)
from ansys.geometry.core.typing import RealSequence

DEFAULT_POINT2D_VALUES = [np.nan, np.nan]
"""Default values for a ``Point2D``."""

DEFAULT_POINT3D_VALUES = [np.nan, np.nan, np.nan]
"""Default values for a ``Point3D``."""

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.math.vector import Vector2D, Vector3D


class Point2D(np.ndarray, PhysicalQuantity):
    """
    Provides Point2D geometry primitive representation.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence], optional
        The direction arguments, either as a :class:`numpy.ndarray <numpy.ndarray>` ,
        or as a RealSequence.
        By default, ``[np.nan, np.nan, np.nan]``.
    unit : ~pint.Unit, optional
        Units employed to define the Point2D values, by default ``UNIT_LENGTH``.
    """

    def __new__(
        cls,
        input: Optional[Union[np.ndarray, RealSequence]] = DEFAULT_POINT2D_VALUES,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor for ``Point2D``."""
        # Build an empty np.ndarray object
        return np.zeros(len(input)).view(cls)

    def __init__(
        self,
        input: Union[np.ndarray, RealSequence] = DEFAULT_POINT2D_VALUES,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        # Call the PhysicalQuantity ctor
        super().__init__(unit, expected_dimensions=UNIT_LENGTH)

        # Check the inputs
        check_ndarray_is_float_int(input, "input") if isinstance(
            input, np.ndarray
        ) else check_ndarray_is_float_int(np.asarray(input), "input")

        # Check dimensions
        if len(input) != 2:
            raise ValueError("Point2D class must receive 2 arguments.")  # noqa: E501

        # Store values
        self.flat = [(elem * self.unit).to_base_units().magnitude for elem in input]

    def __eq__(self, other: "Point2D") -> bool:
        """Equals operator for ``Point2D``."""
        check_type_equivalence(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Point2D") -> bool:
        """Not equals operator for ``Point2D``."""
        return not self == other

    def __set_value(self, input: Quantity, idx: int) -> None:
        """General setter method for ``Point2D`` class."""
        self[idx] = self._base_units_magnitude(input)

    def __add__(self, other: Union["Point2D", "Vector2D"]) -> "Point2D":
        """Add operation for ``Point2D``."""
        from ansys.geometry.core.math.vector import Vector2D

        check_type(other, (Point2D, Vector2D))
        point = Point2D(np.add(self, other), self.base_unit)
        point.unit = self.unit
        return point

    def __sub__(self, other: "Point2D") -> "Point2D":
        """Subtraction operation for ``Point2D``."""
        from ansys.geometry.core.math.vector import Vector2D

        check_type(other, (Point2D, Vector2D))
        point = Point2D(np.subtract(self, other), self.base_unit)
        point.unit = self.unit
        return point

    @property
    def x(self) -> Quantity:
        """Returns the X plane component value."""
        return self._get_quantity(self[0])

    @x.setter
    def x(self, x: Quantity) -> None:
        """Set the X plane component value."""
        self.__set_value(x, 0)

    @property
    def y(self) -> Quantity:
        """Returns the Y plane component value."""
        return self._get_quantity(self[1])

    @y.setter
    def y(self, y: Quantity) -> None:
        """Set the Y plane component value."""
        self.__set_value(y, 1)


class Point3D(np.ndarray, PhysicalQuantity):
    """
    Provides Point3D geometry primitive representation.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence], optional
        The direction arguments, either as a :class:`numpy.ndarray <numpy.ndarray>` ,
        or as a RealSequence.
        By default, ``[np.nan, np.nan, np.nan]``.
    unit : ~pint.Unit, optional
        Units employed to define the Point3D values, by default ``UNIT_LENGTH``.
    """

    def __new__(
        cls,
        input: Optional[Union[np.ndarray, RealSequence]] = DEFAULT_POINT3D_VALUES,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor for ``Point3D``."""
        # Build an empty np.ndarray object
        return np.zeros(len(input)).view(cls)

    def __init__(
        self,
        input: Union[np.ndarray, RealSequence] = DEFAULT_POINT3D_VALUES,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        # Call the PhysicalQuantity ctor
        super().__init__(unit, expected_dimensions=UNIT_LENGTH)

        # Check the inputs
        check_ndarray_is_float_int(input, "input") if isinstance(
            input, np.ndarray
        ) else check_ndarray_is_float_int(np.asarray(input), "input")

        # Check dimensions
        if len(input) != 3:
            raise ValueError("Point3D class must receive 3 arguments.")  # noqa: E501

        # Store values
        self.flat = [(elem * self.unit).to_base_units().magnitude for elem in input]

    def __eq__(self, other: "Point3D") -> bool:
        """Equals operator for ``Point3D``."""
        check_type_equivalence(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Point3D") -> bool:
        """Not equals operator for ``Point3D``."""
        return not self == other

    def __add__(self, other: Union["Point3D", "Vector3D"]) -> "Point3D":
        """Add operation for ``Point3D``."""
        from ansys.geometry.core.math.vector import Vector3D

        check_type(other, (Point3D, Vector3D))
        point = Point3D(np.add(self, other), self.base_unit)
        point.unit = self.unit
        return point

    def __sub__(self, other: Union["Point3D", "Vector3D"]) -> "Point3D":
        """Subtraction operation for ``Point3D``."""
        from ansys.geometry.core.math.vector import Vector3D

        check_type(other, (Point3D, Vector3D))
        point = Point3D(np.subtract(self, other), self.base_unit)
        point.unit = self.unit
        return point

    def __set_value(self, input: Quantity, idx: int) -> None:
        """General setter method for ``Point3D`` class."""
        self[idx] = self._base_units_magnitude(input)

    @property
    def x(self) -> Quantity:
        """Returns the X plane component value."""
        return self._get_quantity(self[0])

    @x.setter
    def x(self, x: Quantity) -> None:
        """Set the X plane component value."""
        self.__set_value(x, 0)

    @property
    def y(self) -> Quantity:
        """Returns the Y plane component value."""
        return self._get_quantity(self[1])

    @y.setter
    def y(self, y: Quantity) -> None:
        """Set the Y plane component value."""
        self.__set_value(y, 1)

    @property
    def z(self) -> Quantity:
        """Returns the Z plane component value."""
        return self._get_quantity(self[2])

    @z.setter
    def z(self, z: Quantity) -> None:
        """Set the Z plane component value."""
        self.__set_value(z, 2)
