"""``Point3D`` and ``Point2D`` class module."""

from typing import Optional, Union

import numpy as np
from pint import Unit

from ansys.geometry.core.misc import (
    UNIT_LENGTH,
    UNITS,
    check_is_float_int,
    check_ndarray_is_float_int,
    check_type_equivalence,
)
from ansys.geometry.core.misc.units import PhysicalQuantity
from ansys.geometry.core.typing import Real, RealSequence

DEFAULT_POINT3D = [np.Inf, np.Inf, np.Inf]
"""Default value for ``Point3D``"""

DEFAULT_POINT2D = [np.Inf, np.Inf]
"""Default value for ``Point2D``"""


class Point(np.ndarray, PhysicalQuantity):
    """
    Provides Point geometry primitive representation.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence]
        The direction arguments, either as a :class:`numpy.ndarray`, or as a RealSequence.
    unit : ~pint.Unit, optional
        Units employed to define the Point3D values, by default ``UNIT_LENGTH``
    """

    def __new__(
        cls,
        input: Union[np.ndarray, RealSequence],
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor for ``Point``."""
        # Build an empty np.ndarray object
        return np.zeros(len(input)).view(cls)

    def __init__(self, input: Union[np.ndarray, RealSequence], unit: Optional[Unit] = UNIT_LENGTH):
        # Call the PhysicalQuantity ctor
        super().__init__(unit, expected_dimensions=UNIT_LENGTH)

        # Check the inputs
        check_ndarray_is_float_int(input, "input") if isinstance(
            input, np.ndarray
        ) else check_ndarray_is_float_int(np.asarray(input), "input")

        # Store values
        self.flat = [(elem * self.unit).to_base_units().magnitude for elem in input]

    def __eq__(self, other: "Point") -> bool:
        """Equals operator for ``Point``."""
        check_type_equivalence(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Point") -> bool:
        """Not equals operator for ``Point``."""
        return not self == other


class Point3D(Point):
    """
    Provides Point3D geometry primitive representation.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence], optional
        The direction arguments, either as a :class:`numpy.ndarray`, or as a RealSequence.
        By default, ``DEFAULT_POINT3D``.
    unit : ~pint.Unit, optional
        Units employed to define the Point3D values, by default ``UNIT_LENGTH``
    """

    def __new__(
        cls,
        input: Optional[Union[np.ndarray, RealSequence]] = DEFAULT_POINT3D,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        return super().__new__(Point3D, input, unit)

    def __init__(
        self,
        input: Optional[Union[np.ndarray, RealSequence]] = DEFAULT_POINT3D,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor for ``Point3D``."""
        # Call the Point ctor.
        super().__init__(input, unit)

        # Check that the size is as expected
        if len(self) != 3:
            raise ValueError("Point3D must have three coordinates.")

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


class Point2D(Point):
    """
    Provides Point2D geometry primitive representation.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence], optional
        The direction arguments, either as a :class:`numpy.ndarray`, or as a RealSequence.
        By default, ``DEFAULT_POINT3D``.
    unit : ~pint.Unit, optional
        Units employed to define the Point3D values, by default ``UNIT_LENGTH``
    """

    def __new__(
        cls,
        input: Optional[Union[np.ndarray, RealSequence]] = DEFAULT_POINT2D,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        return super().__new__(Point2D, input, unit)

    def __init__(
        self,
        input: Optional[Union[np.ndarray, RealSequence]] = DEFAULT_POINT2D,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor for ``Point2D``."""
        # Call the Point ctor.
        super().__init__(input, unit)

        # Check that the size is as expected
        if len(self) != 2:
            raise ValueError("Point2D must have two coordinates.")

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
