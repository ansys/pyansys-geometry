# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
"""Provides get and set methods for parameters."""

from enum import Enum, unique

from pint import Quantity

from ansys.geometry.core.misc import DEFAULT_UNITS
from ansys.geometry.core.typing import Real


@unique
class ParameterType(Enum):
    """Provides values for the parameter types supported."""

    DIMENSIONTYPE_UNKNOWN = 0
    DIMENSIONTYPE_LINEAR = 1
    DIMENSIONTYPE_DIAMETRIC = 2
    DIMENSIONTYPE_RADIAL = 3
    DIMENSIONTYPE_ARC = 4
    DIMENSIONTYPE_AREA = 5
    DIMENSIONTYPE_VOLUME = 6
    DIMENSIONTYPE_MASS = 7
    DIMENSIONTYPE_ANGULAR = 8
    DIMENSIONTYPE_COUNT = 9
    DIMENSIONTYPE_UNITLESS = 10


@unique
class ParameterUpdateStatus(Enum):
    """Provides values for the status messages associated with parameter updates."""

    SUCCESS = 0
    FAILURE = 1
    CONSTRAINED_PARAMETERS = 2
    UNKNOWN = 3


class Parameter:
    """Represents a parameter.

    Parameters
    ----------
    id : int
        Unique ID for the parameter.
    name : str
        Name of the parameter.
    dimension_type : ParameterType
        Type of the parameter.
    dimension_value : Quantity | Real
        Value of the parameter. If a Quantity, it will be converted to default units
        based on the dimension_type.
    """

    def __init__(
        self, id: int, name: str, dimension_type: ParameterType, dimension_value: Quantity | Real
    ):
        """Initialize an instance of the ``Parameter`` class."""
        self.id = id
        self._name = name
        self._dimension_type = dimension_type
        self._dimension_value = self._convert_to_default_units(dimension_value, dimension_type)

    def _convert_to_default_units(self, value: Quantity | Real, dim_type: ParameterType) -> Real:
        """Convert a value to default units based on dimension type.
        
        Parameters
        ----------
        value : Quantity | Real
            The value to convert.
        dim_type : ParameterType
            The dimension type to determine the appropriate unit.
            
        Returns
        -------
        Real
            The value in default units (or the original value if not a Quantity).
        """
        if not isinstance(value, Quantity):
            return value
        
        unit_map = {
            ParameterType.DIMENSIONTYPE_LINEAR: DEFAULT_UNITS.LENGTH,
            ParameterType.DIMENSIONTYPE_DIAMETRIC: DEFAULT_UNITS.LENGTH,
            ParameterType.DIMENSIONTYPE_RADIAL: DEFAULT_UNITS.LENGTH,
            ParameterType.DIMENSIONTYPE_ARC: DEFAULT_UNITS.LENGTH,
            ParameterType.DIMENSIONTYPE_AREA: DEFAULT_UNITS.AREA,
            ParameterType.DIMENSIONTYPE_VOLUME: DEFAULT_UNITS.VOLUME,
            ParameterType.DIMENSIONTYPE_ANGULAR: DEFAULT_UNITS.ANGLE,
        }
        
        default_unit = unit_map.get(dim_type)
        if default_unit is None:
            return value.magnitude
        
        return value.m_as(default_unit)

    @property
    def name(self) -> str:
        """Get the name of the parameter."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set the name of the parameter."""
        self._name = value

    @property
    def dimension_value(self) -> Real:
        """Get the value of the parameter."""
        return self._dimension_value

    @dimension_value.setter
    def dimension_value(self, value: Quantity | Real):
        """Set the value of the parameter.
        
        Parameters
        ----------
        value : Quantity | Real
            The new value. If a Quantity, it will be converted to default units
            based on the dimension_type.
        """
        self._dimension_value = self._convert_to_default_units(value, self._dimension_type)

    @property
    def dimension_type(self) -> ParameterType:
        """Get the type of the parameter."""
        return self._dimension_type

    @dimension_type.setter
    def dimension_type(self, value: ParameterType):
        """Set the type of the parameter."""
        self._dimension_type = value
