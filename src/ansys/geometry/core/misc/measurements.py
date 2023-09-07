# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Provides various measurement-related classes."""

from threading import Lock

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
from pint import Quantity, Unit

from ansys.geometry.core.misc.checks import check_is_float_int, check_pint_unit_compatibility
from ansys.geometry.core.misc.units import UNITS, PhysicalQuantity
from ansys.geometry.core.typing import Real


class SingletonMeta(type):
    """Provides a thread-safe implementation of a singleton design pattern."""

    # This class has been extracted from
    # https://refactoring.guru/design-patterns/singleton/python/example#example-1--main-py

    _instances = {}

    _lock: Lock = Lock()
    """We now have a lock object that will be used to synchronize threads during first
    access to the Singleton."""

    def __call__(cls, *args, **kwargs):
        """
        Return a single instance of the class.

        Possible changes to the value of the ``__init__`` argument do not affect the
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
    """Provides default units for the PyAnsys Geometry singleton design pattern."""

    def __init__(self) -> None:
        """Initialize the ``DefaultUnitsClass`` class."""
        self._length: Unit = UNITS.meter
        self._angle: Unit = UNITS.radian
        self._server_length: Unit = UNITS.meter
        self._server_angle: Unit = UNITS.radian

    @property
    def LENGTH(self) -> Unit:
        """Default length unit for PyAnsys Geometry."""
        return self._length

    @LENGTH.setter
    @check_input_types
    def LENGTH(self, value: Unit) -> None:
        check_pint_unit_compatibility(value, self._length)
        self._length = value

    @property
    def ANGLE(self) -> Unit:
        """Default angle unit for PyAnsys Geometry."""
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
"""PyAnsys Geometry default units object."""


class Measurement(PhysicalQuantity):
    """
    Provides the ``PhysicalQuantity`` subclass for holding a measurement.

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
    """
    Provides the ``Measurement`` subclass for holding a distance.

    Parameters
    ----------
    value : Union[Real, Quantity]
        Value of the distance.
    unit : ~pint.Unit, default: DEFAULT_UNITS.LENGTH
        Units for the distance.
    """

    def __init__(self, value: Union[Real, Quantity], unit: Optional[Unit] = None):
        """Initialize the ``Distance`` class."""
        # Delegates in Measurement ctor. forcing expected dimensions.
        unit = unit if unit else DEFAULT_UNITS.LENGTH
        super().__init__(value, unit, DEFAULT_UNITS.LENGTH)


class Angle(Measurement):
    """
    Provides the ``Measurement`` subclass for holding an angle.

    Parameters
    ----------
    value : Union[Real, Quantity]
        Value of the angle.
    unit : ~pint.Unit, default: DEFAULT_UNITS.ANGLE
        Units for the distance.
    """

    def __init__(self, value: Union[Real, Quantity], unit: Optional[Unit] = None):
        """Initialize the ``Angle`` class."""
        # Delegates in Measurement ctor. forcing expected dimensions.
        unit = unit if unit else DEFAULT_UNITS.ANGLE
        super().__init__(value, unit, DEFAULT_UNITS.ANGLE)
