"""Provides various measurement-related classes."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
from pint import Quantity, Unit

from ansys.geometry.core.misc.checks import check_is_float_int
from ansys.geometry.core.misc.units import UNITS, PhysicalQuantity
from ansys.geometry.core.typing import Real

UNIT_LENGTH = UNITS.meter
"""Default length unit for PyGeometry."""

UNIT_ANGLE = UNITS.radian
"""Default angle unit for PyGeometry."""

SERVER_UNIT_LENGTH = UNITS.meter
"""Default length unit for supporting Geometry services for gRPC messages."""

SERVER_UNIT_AREA = SERVER_UNIT_LENGTH * SERVER_UNIT_LENGTH
"""Default area unit for supporting Geometry services for gRPC messages."""

SERVER_UNIT_VOLUME = SERVER_UNIT_AREA * SERVER_UNIT_LENGTH
"""Default volume unit for supporting Geometry services for gRPC messages."""


class Measurement(PhysicalQuantity):
    """Provides the ``PhysicalQuantity`` subclass for holding a measurement.

    Parameters
    ----------
    value : Union[Real, Quantity]
        Value of the measurement.
    unit : ~pint.Unit
        Units for the measurement.
    dimensions : ~pint.Unit
        Units for extracting the dimensions of the measurement.
        If ``~pint.Unit.meter`` is given, the dimension extracted is ``[length]``.
    """

    def __init__(self, value: Union[Real, Quantity], unit: Unit, dimensions: Unit):
        """Constructor for the ``Measurement`` class."""
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
        """Value of the measurement."""
        return self._get_quantity(self._value)

    @value.setter
    def value(self, value: Quantity) -> None:
        """Set the measurement value."""
        self._value = self._base_units_magnitude(value)

    @check_input_types
    def __eq__(self, other: "Measurement") -> bool:
        return self._value == other._value and self._base_unit == other._base_unit


class Distance(Measurement):
    """Provides the ``Measurement`` subclass for holding a distance.

    Parameters
    ----------
    value : Union[Real, Quantity]
        Value of the distance.
    unit : ~pint.Unit
        Units for the distance.
    """

    def __init__(self, value: Union[Real, Quantity], unit: Optional[Unit] = UNIT_LENGTH):
        """Constructor for the ``Distance`` class."""
        # Delegates in Measurement ctor. forcing expected dimensions.
        super().__init__(value, unit, UNIT_LENGTH)


class Angle(Measurement):
    """Provides the ``Measurement`` subclass for holding an angle.

    Parameters
    ----------
    value : Union[Real, Quantity]
        Value of the angle.
    unit : ~pint.Unit
        Units for the angle.
    """

    def __init__(self, value: Union[Real, Quantity], unit: Optional[Unit] = UNIT_ANGLE):
        """Constructor for the ``Angle`` class."""
        # Delegates in Measurement ctor. forcing expected dimensions.
        super().__init__(value, unit, UNIT_ANGLE)
