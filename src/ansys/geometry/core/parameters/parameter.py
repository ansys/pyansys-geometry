# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from ansys.api.dbu.v0.dbumodels_pb2 import DrivingDimension as GRPCDrivingDimension
from ansys.api.dbu.v0.drivingdimensions_pb2 import UpdateStatus as GRPCUpdateStatus
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

    @staticmethod
    def _from_update_status(status: GRPCUpdateStatus) -> "ParameterUpdateStatus":
        """Convert GRPCUpdateStatus to ParameterUpdateStatus.

        Notes
        -----
        This method is used to convert the status of the update from gRPC to the
        parameter update status. Not to be used directly by the user.

        Parameters
        ----------
        status : GRPCUpdateStatus
            Status of the update. Coming from gRPC.

        Returns
        -------
        ParameterUpdateStatus
            Parameter update status.
        """
        status_mapping = {
            GRPCUpdateStatus.SUCCESS: ParameterUpdateStatus.SUCCESS,
            GRPCUpdateStatus.FAILURE: ParameterUpdateStatus.FAILURE,
            GRPCUpdateStatus.CONSTRAINED_PARAMETERS: ParameterUpdateStatus.CONSTRAINED_PARAMETERS,
        }
        return status_mapping.get(status, ParameterUpdateStatus.UNKNOWN)


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
    dimension_value : float
        Value of the parameter.
    """

    def __init__(self, id: int, name: str, dimension_type: ParameterType, dimension_value: Real):
        """Initialize an instance of the ``Parameter`` class."""
        self.id = id
        self._name = name
        self._dimension_type = dimension_type
        self._dimension_value = dimension_value

    @classmethod
    def _from_proto(cls, proto: GRPCDrivingDimension) -> "Parameter":
        """Create a ``Parameter`` instance from a ``proto`` object.

        Notes
        -----
        This method is used to convert the parameter from gRPC to the parameter
        object. Not to be used directly by the user.

        Parameters
        ----------
        proto : GRPCDrivingDimension
            Parameter object coming from gRPC.

        Returns
        -------
        Parameter
            Parameter object.
        """
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
    def dimension_value(self) -> Real:
        """Get the value of the parameter."""
        return self._dimension_value

    @dimension_value.setter
    def dimension_value(self, value: Real):
        """Set the value of the parameter."""
        self._dimension_value = value

    @property
    def dimension_type(self) -> ParameterType:
        """Get the type of the parameter."""
        return self._dimension_type

    @dimension_type.setter
    def dimension_type(self, value: ParameterType):
        """Set the type of the parameter."""
        self._dimension_type = value

    def _to_proto(self):
        """Convert a ``Parameter`` instance to a ``proto`` object.

        Notes
        -----
        This method is used to convert the parameter from the parameter object to
        gRPC. Not to be used directly by the user.

        Returns
        -------
        GRPCDrivingDimension
            Parameter object in gRPC.
        """
        return GRPCDrivingDimension(
            id=self.id,
            name=self.name,
            dimension_type=self.dimension_type.value,
            dimension_value=self.dimension_value,
        )
