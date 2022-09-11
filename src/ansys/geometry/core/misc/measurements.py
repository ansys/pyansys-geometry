"""Module holding various measurement-related classes."""

from typing import Optional, Union

from pint import Quantity, Unit

from ansys.geometry.core.misc.checks import check_is_float_int
from ansys.geometry.core.misc.units import UNITS, PhysicalQuantity
from ansys.geometry.core.typing import Real

UNIT_LENGTH = UNITS.meter
"""Default length unit for PyGeometry."""

UNIT_ANGLE = UNITS.radian
"""Default angle unit for PyGeometry."""

UNIT_AREA = UNIT_LENGTH * UNIT_LENGTH
"""Default area unit for PyGeometry."""

UNIT_VOLUME = UNIT_AREA * UNIT_LENGTH
"""Default volume unit for PyGeometry."""


class Measurement(PhysicalQuantity):
    """``PhysicalQuantity`` subclass for holding a measurement.

    Parameters
    ----------
    value : Union[Real, Quantity]
        The value of the measurement to be considered.
    unit : ~pint.Unit
        The units to be considered for the given measurement.
    dimensions : ~pint.Unit
        The units to be considered for extracting the dimensions of the measurement.
        If ~pint.Unit.meter is given, the dimension extracted will be ``[length]``.
    """

    def __init__(self, value: Union[Real, Quantity], unit: Unit, dimensions: Unit):
        """Constructor for ``Measurement``."""
        # Check the input
        if isinstance(value, Quantity):
            # TODO: inform that if Quantity is given, we will ignore provided unit value
            unit = value.units
        else:
            check_is_float_int(value, "value")
            value = Quantity(value, unit)

        # Call the PhysicalQuantity ctor.
        super().__init__(unit, expected_dimensions=dimensions)

        # Store the value
        self._value = self._base_units_magnitude(value)

    @property
    def value(self) -> Quantity:
        """Get the value of the measurement."""
        return self._get_quantity(self._value)

    @value.setter
    def value(self, value: Quantity) -> None:
        """Set the measurement value."""
        self._value = self._base_units_magnitude(value)


class Distance(Measurement):
    """``Measurement`` subclass for holding a distance.

    Parameters
    ----------
    value : Union[Real, Quantity]
        The value of the distance to be considered.
    unit : ~pint.Unit
        The units to be considered for the given measurement.
    """

    def __init__(self, value: Union[Real, Quantity], unit: Optional[Unit] = UNIT_LENGTH):
        """Constructor for ``Distance``."""
        # Delegates in Measurement ctor. forcing expected dimensions.
        super().__init__(value, unit, UNIT_LENGTH)


class Angle(Measurement):
    """``Measurement`` subclass for holding an angle.

    Parameters
    ----------
    value : Union[Real, Quantity]
        The value of the angle to be considered.
    unit : ~pint.Unit
        The units to be considered for the given measurement.
    """

    def __init__(self, value: Union[Real, Quantity], unit: Optional[Unit] = UNIT_ANGLE):
        """Constructor for ``Angle``."""
        # Delegates in Measurement ctor. forcing expected dimensions.
        super().__init__(value, unit, UNIT_ANGLE)


class Area(Measurement):
    """``Measurement`` subclass for holding an area.

    Parameters
    ----------
    value : Union[Real, Quantity]
        The value of the area to be considered.
    unit : ~pint.Unit
        The units to be considered for the given measurement.
    """

    def __init__(self, value: Union[Real, Quantity], unit: Optional[Unit] = UNIT_AREA):
        """Constructor for ``Area``."""
        # Delegates in Measurement ctor. forcing expected dimensions.
        super().__init__(value, unit, UNIT_AREA)


class Volume(Measurement):
    """``Measurement`` subclass for holding a volume.

    Parameters
    ----------
    value : Union[Real, Quantity]
        The value of the volume to be considered.
    unit : ~pint.Unit
        The units to be considered for the given measurement.
    """

    def __init__(self, value: Union[Real, Quantity], unit: Optional[Unit] = UNIT_VOLUME):
        """Constructor for ``Volume``."""
        # Delegates in Measurement ctor. forcing expected dimensions.
        super().__init__(value, unit, UNIT_VOLUME)
