# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from ansys.api.dbu.v0.dbumodels_pb2 import DrivingDimension as ParameterProto
from ansys.api.dbu.v0.drivingdimensions_pb2 import UpdateStatus


@unique
class ParameterType(Enum):
    """Provides values for parameter types supported."""

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

    @staticmethod
    def _from_update_status(status):
        """Convert UpdateStatus to ParameterUpdateStatus."""
        status_mapping = {
            UpdateStatus.SUCCESS: ParameterUpdateStatus.SUCCESS,
            UpdateStatus.FAILURE: ParameterUpdateStatus.FAILURE,
            UpdateStatus.CONSTRAINED_PARAMETERS: ParameterUpdateStatus.CONSTRAINED_PARAMETERS,
        }
        return status_mapping.get(status, ParameterUpdateStatus.UNKNOWN)


class Parameter:
    """Represents a parameter."""

    def __init__(self, id, name, dimension_type: ParameterType, dimension_value):
        """
        Initialize an instance of the ``Parameter`` class.

        Parameters
        ----------
        id : int
            Unique ID for the parameter.
        name : str
            The name of the parameter.
        dimension_type : ParameterType
            The type of the parameter.
        dimension_value : float
            The value of the parameter.
        """
        self.id = id
        self._name = name
        self.dimension_type = dimension_type
        self._dimension_value = dimension_value

    @classmethod
    def _from_proto(cls, proto):
        """Create a ``Parameter`` instance from a proto object."""
        return cls(
            id=proto.id,
            name=proto.name,
            dimension_type=ParameterType(proto.dimension_type),
            dimension_value=proto.dimension_value,
        )

    @property
    def name(self) -> str:
        """Get the name of the parameter."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set the name of the parameter."""
        self._name = value

    @property
    def dimension_value(self) -> float:
        """Get the value of the parameter."""
        return self._dimension_value

    @dimension_value.setter
    def dimension_value(self, value):
        """Set the value of the parameter."""
        self._dimension_value = value

    def _to_proto(self):
        """Convert a ``Parameter`` instance to a proto object."""
        return ParameterProto(
            id=self.id,
            name=self.name,
            dimension_type=self.dimension_type.value,
            dimension_value=self.dimension_value,
        )
