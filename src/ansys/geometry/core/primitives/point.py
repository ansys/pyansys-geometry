"""``Point3D`` and ``Point2D`` class module."""

from typing import List, Optional, Union

import numpy as np
from pint import Unit

from ansys.geometry.core import UNIT_LENGTH, UNITS, Real
from ansys.geometry.core.misc import (
    check_type_operation,
    check_is_float_int,
    check_is_pint_unit,
    check_ndarray_is_float_int,
    check_pint_unit_compatibility,
)

DEFAULT_POINT3D = [None, None, None]
"""Default value for ``Point3D``"""

DEFAULT_POINT2D = [None, None]
"""Default value for ``Point2D``"""


class Point3D(np.ndarray):
    """
    Provides Point3D geometry primitive representation.

    Parameters
    ----------
    input : Union[numpy.ndarray, List[Union[Real, None]]], optional
        The direction arguments, either as a :class:`numpy.ndarray`, or as a list.
        By default, ``DEFAULT_POINT3D``.
    unit : Unit, optional
        Units employed to define the Point3D values, by default ``UNIT_LENGTH``
    """

    def __new__(
        cls,
        input: Optional[Union[np.ndarray, List[Union[Real, None]]]] = DEFAULT_POINT3D,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor for ``Point3D``."""

        # Check if we are dealing with the default value
        if input is DEFAULT_POINT3D:
            obj = np.asarray(DEFAULT_POINT3D).view(cls)
            obj._unit = None
            _, obj._base_unit = UNITS.get_base_units(UNIT_LENGTH)
            return obj

        # Transform to numpy.ndarray
        obj = np.asarray([(elem * unit).to_base_units().magnitude for elem in input]).view(cls)
        obj._unit = unit
        _, obj._base_unit = UNITS.get_base_units(unit)

        # Check that the size is as expected
        if obj is None or len(obj) != 3:
            raise ValueError("Point3D must have three coordinates.")

        # Check that units provided (if any) are compatible
        check_pint_unit_compatibility(unit, UNIT_LENGTH)

        # If we are not dealing with the default value... check the inputs
        check_ndarray_is_float_int(obj, "input")

        # If all checks went through, return the Point3D
        return obj

    @property
    def x(self) -> Union[Real, None]:
        """Returns the X plane component value."""
        return UNITS.convert(self[0], self._base_unit, self._unit)

    @x.setter
    def x(self, x: Real) -> None:
        """Set the X plane component value."""
        check_is_float_int(x, "x")
        self[0] = (x * self._unit).to_base_units().magnitude

    @property
    def y(self) -> Union[Real, None]:
        """Returns the Y plane component value."""
        return UNITS.convert(self[1], self._base_unit, self._unit)

    @y.setter
    def y(self, y: Real) -> None:
        """Set the Y plane component value."""
        check_is_float_int(y, "y")
        self[1] = (y * self._unit).to_base_units().magnitude

    @property
    def z(self) -> Union[Real, None]:
        """Returns the Z plane component value."""
        return UNITS.convert(self[2], self._base_unit, self._unit)

    @z.setter
    def z(self, z: Real) -> None:
        """Set the Z plane component value."""
        check_is_float_int(z, "z")
        self[2] = (z * self._unit).to_base_units().magnitude

    @property
    def unit(self) -> Unit:
        """Returns the unit of the object."""
        return self._unit

    @unit.setter
    def unit(self, unit: Unit) -> None:
        """Sets the unit of the object."""
        check_is_pint_unit(unit, "unit")
        check_pint_unit_compatibility(unit, UNIT_LENGTH)
        self._unit = unit

    def __eq__(self, other: "Point3D") -> bool:
        """Equals operator for ``Point3D``."""
        check_type_operation(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Point3D") -> bool:
        """Not equals operator for ``Point3D``."""
        return not self == other


class Point2D(np.ndarray):
    """
    Provides Point2D geometry primitive representation.

    Parameters
    ----------
    input : Union[numpy.ndarray, List[Union[Real, None]]], optional
        The direction arguments, either as a :class:`numpy.ndarray`, or as a list.
        By default, ``DEFAULT_POINT3D``.
    unit : Unit, optional
        Units employed to define the Point3D values, by default ``UNIT_LENGTH``
    """

    def __new__(
        cls,
        input: Optional[Union[np.ndarray, List[Union[Real, None]]]] = DEFAULT_POINT2D,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor for ``Point2D``."""

        # Check if we are dealing with the default value
        if input is DEFAULT_POINT2D:
            obj = np.asarray(DEFAULT_POINT2D).view(cls)
            obj._unit = None
            _, obj._base_unit = UNITS.get_base_units(UNIT_LENGTH)
            return obj

        # Transform to numpy.ndarray
        obj = np.asarray([(elem * unit).to_base_units().magnitude for elem in input]).view(cls)
        obj._unit = unit
        _, obj._base_unit = UNITS.get_base_units(unit)

        # Check that the size is as expected
        if obj is None or len(obj) != 2:
            raise ValueError("Point2D must have two coordinates.")

        # Check that units provided (if any) are compatible
        check_pint_unit_compatibility(unit, UNIT_LENGTH)

        # If we are not dealing with the default value... check the inputs
        check_ndarray_is_float_int(obj, "input")

        # If all checks went through, return the Point2D
        return obj

    @property
    def x(self) -> Union[Real, None]:
        """Returns the X plane component value."""
        return UNITS.convert(self[0], self._base_unit, self._unit)

    @x.setter
    def x(self, x: Real) -> None:
        """Set the X plane component value."""
        check_is_float_int(x, "x")
        self[0] = (x * self._unit).to_base_units().magnitude

    @property
    def y(self) -> Union[Real, None]:
        """Returns the Y plane component value."""
        return UNITS.convert(self[1], self._base_unit, self._unit)

    @y.setter
    def y(self, y: Real) -> None:
        """Set the Y plane component value."""
        check_is_float_int(y, "y")
        self[1] = (y * self._unit).to_base_units().magnitude

    @property
    def unit(self) -> Unit:
        """Returns the unit of the object."""
        return self._unit

    @unit.setter
    def unit(self, unit: Unit) -> None:
        """Sets the unit of the object."""
        check_is_pint_unit(unit, "unit")
        check_pint_unit_compatibility(unit, UNIT_LENGTH)
        self._unit = unit

    def __eq__(self, other: "Point2D") -> bool:
        """Equals operator for ``Point2D``."""
        check_type_operation(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Point2D") -> bool:
        """Not equals operator for ``Point2D``."""
        return not self == other
