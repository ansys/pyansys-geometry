"""Provides various measurement-related classes."""

from threading import Lock

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
from pint import Quantity, Unit

from ansys.geometry.core.misc.checks import check_is_float_int, check_pint_unit_compatibility
from ansys.geometry.core.misc.units import UNITS, PhysicalQuantity
from ansys.geometry.core.typing import Real


class SingletonMeta(type):
    """This is a thread-safe implementation of Singleton."""

    # This class has been extracted from
    # https://refactoring.guru/design-patterns/singleton/python/example#example-1--main-py

    _instances = {}

    _lock: Lock = Lock()
    """We now have a lock object that will be used to synchronize threads during first
    access to the Singleton."""

    def __call__(cls, *args, **kwargs):
        """
        Return a single instance of the class.

        Possible changes to the value of the `__init__` argument do not affect the
        returned instance.
        """
        # Now, imagine that the program has just been launched. Since there's no
        # Singleton instance yet, multiple threads can simultaneously pass the
        # previous conditional and reach this point almost at the same time. The
        # first of them will acquire lock and will proceed further, while the
        # rest will wait here.
        with cls._lock:
            # The first thread to acquire the lock, reaches this conditional,
            # goes inside and creates the Singleton instance. Once it leaves the
            # lock block, a thread that might have been waiting for the lock
            # release may then enter this section. But since the Singleton field
            # is already initialized, the thread won't create a new object.
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class DefaultUnitsClass(metaclass=SingletonMeta):
    """PyGeometry default units singleton class."""

    def __init__(self) -> None:
        """Initialize ``DefaultUnitsClass`` class."""
        self._length: Unit = UNITS.meter
        self._angle: Unit = UNITS.radian
        self._server_length: Unit = UNITS.meter
        self._server_angle: Unit = UNITS.radian

    @property
    def LENGTH(self) -> Unit:
        """Default length unit for PyGeometry."""
        return self._length

    @LENGTH.setter
    @check_input_types
    def LENGTH(self, value: Unit) -> None:
        check_pint_unit_compatibility(value, self._length)
        self._length = value

    @property
    def ANGLE(self) -> Unit:
        """Default angle unit for PyGeometry."""
        return self._angle

    @ANGLE.setter
    @check_input_types
    def ANGLE(self, value: Unit) -> None:
        check_pint_unit_compatibility(value, self._angle)
        self._angle = value

    @property
    def SERVER_LENGTH(self) -> Unit:
        """
        Default length unit for supporting Geometry services for gRPC messages.

        Notes
        -----
        The default units on the server side are not modifiable yet.
        """
        return self._server_length

    @property
    def SERVER_AREA(self) -> Unit:
        """
        Default area unit for supporting Geometry services for gRPC messages.

        Notes
        -----
        The default units on the server side are not modifiable yet.
        """
        return self._server_length * self._server_length

    @property
    def SERVER_VOLUME(self) -> Unit:
        """
        Default volume unit for supporting Geometry services for gRPC messages.

        Notes
        -----
        The default units on the server side are not modifiable yet.
        """
        return self._server_length * self._server_length * self._server_length

    @property
    def SERVER_ANGLE(self) -> Unit:
        """
        Default angle unit for supporting Geometry services for gRPC messages.

        Notes
        -----
        The default units on the server side are not modifiable yet.
        """
        return self._server_angle


DEFAULT_UNITS = DefaultUnitsClass()
"""PyGeometry default units object."""


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
        """Initialize the ``Measurement`` class."""
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
        """Equals operator for the ``Measurement`` class."""
        return self._value == other._value and self._base_unit == other._base_unit


class Distance(Measurement):
    """Provides the ``Measurement`` subclass for holding a distance.

    Parameters
    ----------
    value : Union[Real, Quantity]
        Value of the distance.
    unit : ~pint.Unit, optional
        Units for the distance. By default, ``DEFAULT_UNITS.LENGTH``
    """

    def __init__(self, value: Union[Real, Quantity], unit: Optional[Unit] = None):
        """Initialize the ``Distance`` class."""
        # Delegates in Measurement ctor. forcing expected dimensions.
        unit = unit if unit else DEFAULT_UNITS.LENGTH
        super().__init__(value, unit, DEFAULT_UNITS.LENGTH)


class Angle(Measurement):
    """Provides the ``Measurement`` subclass for holding an angle.

    Parameters
    ----------
    value : Union[Real, Quantity]
        Value of the angle.
    unit : ~pint.Unit, optional
        Units for the distance. By default, ``DEFAULT_UNITS.ANGLE``
    """

    def __init__(self, value: Union[Real, Quantity], unit: Optional[Unit] = None):
        """Initialize the ``Angle`` class."""
        # Delegates in Measurement ctor. forcing expected dimensions.
        unit = unit if unit else DEFAULT_UNITS.ANGLE
        super().__init__(value, unit, DEFAULT_UNITS.ANGLE)
