"""``Point`` class module."""

from typing import Optional, Union

import numpy as np
from pint import Quantity, Unit

from ansys.geometry.core.misc import (
    UNIT_LENGTH,
    check_ndarray_is_float_int,
    check_type_equivalence,
    only_for_3d,
)
from ansys.geometry.core.misc.units import PhysicalQuantity
from ansys.geometry.core.typing import RealSequence

DEFAULT_POINT_VALUES = [np.Inf, np.Inf, np.Inf]
"""Default values for a ``Point``."""


class Point(np.ndarray, PhysicalQuantity):
    """
    Provides Point geometry primitive representation.

    2D and 3D points are supported with the same class upon initialization.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence], optional
        The direction arguments, either as a :class:`numpy.ndarray`, or as a RealSequence.
        By default, ``[np.Inf, np.Inf, np.Inf]``.
    unit : ~pint.Unit, optional
        Units employed to define the Point values, by default ``UNIT_LENGTH``.
    """

    def __new__(
        cls,
        input: Optional[Union[np.ndarray, RealSequence]] = DEFAULT_POINT_VALUES,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Constructor for ``Point``."""
        # Build an empty np.ndarray object
        return np.zeros(len(input)).view(cls)

    def __init__(
        self,
        input: Union[np.ndarray, RealSequence] = DEFAULT_POINT_VALUES,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        # Call the PhysicalQuantity ctor
        super().__init__(unit, expected_dimensions=UNIT_LENGTH)

        # Check the inputs
        check_ndarray_is_float_int(input, "input") if isinstance(
            input, np.ndarray
        ) else check_ndarray_is_float_int(np.asarray(input), "input")

        # Check dimensions
        if len(input) == 2:
            self._is_3d = False
        elif len(input) == 3:
            self._is_3d = True
        else:
            raise ValueError(
                "Point class can only receive 2 or 3 arguments, creating a 2D or 3D point, respectively."  # noqa: E501
            )

        # Store values
        self.flat = [(elem * self.unit).to_base_units().magnitude for elem in input]

    def __eq__(self, other: "Point") -> bool:
        """Equals operator for ``Point``."""
        check_type_equivalence(other, self)
        return self.is_3d == other.is_3d and np.array_equal(self, other)

    def __ne__(self, other: "Point") -> bool:
        """Not equals operator for ``Point``."""
        return not self == other

    def __set_value(self, input: Quantity, idx: int) -> None:
        """General setter method for ``Point`` class."""
        self[idx] = self._base_units_magnitude(input)

    @property
    def is_3d(self) -> bool:
        """Returns ``True`` if our ``Point`` is defined in 3D space."""
        return self._is_3d

    @property
    def is_2d(self) -> bool:
        """Returns ``True`` if our ``Point`` is defined in 2D space."""
        return not self.is_3d

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
    @only_for_3d
    def z(self) -> Quantity:
        """Returns the Z plane component value.

        Notes
        -----
        Only valid for ``Point`` objects defined in 3D space.
        """
        return self._get_quantity(self[2])

    @z.setter
    @only_for_3d
    def z(self, z: Quantity) -> None:
        """Set the Z plane component value.

        Notes
        -----
        Only valid for ``Point`` objects defined in 3D space.
        """
        self.__set_value(z, 2)
