"""``Point3D`` and ``Point2D`` class module."""

from typing import List, Optional, Union

import numpy as np
from pint import Unit

from ansys.geometry.core import UNITS

DEFAULT_POINT3D = [None, None, None]
"""Default value for ``Point3D``"""

DEFAULT_POINT2D = [None, None]
"""Default value for ``Point2D``"""


class Point3D(np.ndarray):
    """
    Provides Point3D geometry primitive representation.

    Parameters
    ----------
    input : Union[np.ndarray, List[Union[float, int, None]]], optional
        The direction arguments, either as a np.ndarray, or as a list.
        By default, ``DEFAULT_POINT3D``.
    units : Unit, optional
        Units employed to define the Point3D values, by default ``UNITS.meter``
    """

    def __new__(
        cls,
        input: Optional[Union[np.ndarray, List[Union[float, int, None]]]] = DEFAULT_POINT3D,
        units: Optional[Unit] = UNITS.meter,
    ):
        """Constructor for ``Point3D``."""

        # Transform to numpy.ndarray
        obj = np.asarray([(elem * units).to_base_units().magnitude for elem in input]).view(cls)
        obj._units = units
        _, obj._base_units = UNITS.get_base_units(units)

        # Check that the size is as expected
        if obj is None or len(obj) != 3:
            raise ValueError("Point3D must have three coordinates.")

        # Check if we are dealing with the default value
        if input is DEFAULT_POINT3D:
            return obj

        # If we are not dealing with the default value... check the inputs
        if not np.issubdtype(obj.dtype, np.number) or not all(
            isinstance(value, (int, float)) for value in obj.data
        ):
            raise TypeError("The input parameters should be integer or float.")

        # If all checks went through, return the Point3D
        return obj

    @property
    def x(self) -> Union[float, int, None]:
        """Returns the X plane component value."""
        return UNITS.convert(self[0], self._base_units, self._units)

    @x.setter
    def x(self, x: Union[float, int]) -> None:
        """Set the X plane component value."""
        if not isinstance(x, (int, float)):
            raise TypeError("The parameter 'x' should be a float or an integer value.")
        self[0] = (x * self._units).to_base_units().magnitude

    @property
    def y(self) -> Union[float, int, None]:
        """Returns the Y plane component value."""
        return UNITS.convert(self[1], self._base_units, self._units)

    @y.setter
    def y(self, y: Union[float, int]) -> None:
        """Set the Y plane component value."""
        if not isinstance(y, (int, float)):
            raise TypeError("The parameter 'y' should be a float or an integer value.")
        self[1] = (y * self._units).to_base_units().magnitude

    @property
    def z(self) -> Union[float, int, None]:
        """Returns the Z plane component value."""
        return UNITS.convert(self[2], self._base_units, self._units)

    @z.setter
    def z(self, z: Union[float, int]) -> None:
        """Set the Z plane component value."""
        if not isinstance(z, (int, float)):
            raise TypeError("The parameter 'z' should be a float or an integer value.")
        self[2] = (z * self._units).to_base_units().magnitude

    @property
    def units(self) -> Unit:
        """Returns the units of the object."""
        return self._units

    @z.setter
    def units(self, units: Unit) -> None:
        """Sets the units of the object."""
        if not isinstance(units, Unit):
            raise TypeError("The parameter 'unit' should be a pint.Unit object.")
        self._units = units
        _, self._base_units = UNITS.get_base_units(units)

    def __eq__(self, other: "Point3D") -> bool:
        """Equals operator for ``Point3D``."""
        if not isinstance(other, Point3D):
            raise TypeError(
                f"Comparison against {type(other)} is not possible. Should be of type {type(self)}"
            )

        return np.array_equal(self, other)

    def __ne__(self, other: "Point3D") -> bool:
        """Not equals operator for ``Point3D``."""
        return not self == other


class Point2D(np.ndarray):
    """
    Provides Point2D geometry primitive representation.

    Parameters
    ----------
    input : Union[np.ndarray, List[Union[float, int, None]]], optional
        The direction arguments, either as a np.ndarray, or as a list.
        By default, ``DEFAULT_POINT3D``.
    units : Unit, optional
        Units employed to define the Point3D values, by default ``UNITS.meter``
    """

    def __new__(
        cls,
        input: Optional[Union[np.ndarray, List[Union[float, int, None]]]] = DEFAULT_POINT2D,
        units: Optional[Unit] = UNITS.meter,
    ):
        """Constructor for ``Point2D``."""

        # Transform to numpy.ndarray
        obj = np.asarray([(elem * units).to_base_units().magnitude for elem in input]).view(cls)
        obj._units = units
        _, obj._base_units = UNITS.get_base_units(units)

        # Check that the size is as expected
        if obj is None or len(obj) != 2:
            raise ValueError("Point2D must have two coordinates.")

        # Check if we are dealing with the default value
        if input is DEFAULT_POINT2D:
            return obj

        # If we are not dealing with the default value... check the inputs
        if not np.issubdtype(obj.dtype, np.number) or not all(
            isinstance(value, (int, float)) for value in obj.data
        ):
            raise TypeError("The input parameters should be integer or float.")

        # If all checks went through, return the Point2D
        return obj

    @property
    def x(self) -> Union[float, int, None]:
        """Returns the X plane component value."""
        return UNITS.convert(self[0], self._base_units, self._units)

    @x.setter
    def x(self, x: Union[float, int]) -> None:
        """Set the X plane component value."""
        if not isinstance(x, (int, float)):
            raise TypeError("The parameter 'x' should be a float or an integer value.")
        self[0] = (x * self._units).to_base_units().magnitude

    @property
    def y(self) -> Union[float, int, None]:
        """Returns the Y plane component value."""
        return UNITS.convert(self[1], self._base_units, self._units)

    @y.setter
    def y(self, y: Union[float, int]) -> None:
        """Set the Y plane component value."""
        if not isinstance(y, (int, float)):
            raise TypeError("The parameter 'y' should be a float or an integer value.")
        self[1] = (y * self._units).to_base_units().magnitude

    def __eq__(self, other: "Point2D") -> bool:
        """Equals operator for ``Point2D``."""
        if not isinstance(other, Point2D):
            raise TypeError(
                f"Comparison against {type(other)} is not possible. Should be of type {type(self)}"
            )

        return np.array_equal(self, other)

    def __ne__(self, other: "Point2D") -> bool:
        """Not equals operator for ``Point2D``."""
        return not self == other
