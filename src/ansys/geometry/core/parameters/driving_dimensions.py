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
"""Provides get and set methods for driving dimensions."""

from enum import Enum, unique

from ansys.api.dbu.v0.dbumodels_pb2 import DrivingDimension as DrivingDimensionProto
from ansys.api.dbu.v0.drivingdimensions_pb2 import GetAllRequest, UpdateRequest
from ansys.api.dbu.v0.drivingdimensions_pb2_grpc import DrivingDimensionsStub
from beartype import beartype as check_input_types

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.misc.checks import min_backend_version


@unique
class DrivingDimensionType(Enum):
    """Provides values for driving dimension types supported."""

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


class DrivingDimension:
    """Represents a driving dimension."""

    def __init__(self, id, name, dimension_type: DrivingDimensionType, dimension_value):
        """Initialize Driving Dimension class."""
        self.id = id
        self._name = name
        self.dimension_type = dimension_type
        self._dimension_value = dimension_value

    @classmethod
    def _from_proto(cls, proto):
        """Create a DrivingDimension instance from a proto object."""
        return cls(
            id=proto.id,
            name=proto.name,
            dimension_type=DrivingDimensionType(proto.dimension_type),
            dimension_value=proto.dimension_value,
        )

    @property
    def name(self):
        """Set the name of the driving dimension."""
        return self._name

    @name.setter
    def name(self, value):
        """Set the name of the driving dimension."""
        self._name = value

    @property
    def dimension_value(self):
        """Get the value of the driving dimension."""
        return self._dimension_value

    @dimension_value.setter
    def dimension_value(self, value):
        """Set the value of the driving dimension."""
        self._dimension_value = value

    def _to_proto(self):
        """Convert a DrivingDimension instance to a proto object."""
        return DrivingDimensionProto(
            id=self.id,
            name=self.name,
            dimension_type=self.dimension_type.value,
            dimension_value=self.dimension_value,
        )


class DrivingDimensions:
    """Represents Driving Dimensions."""

    def __init__(self, grpc_client: GrpcClient):
        """Initialize Driving Dimensions class."""
        self._grpc_client = grpc_client
        self._driving_dimensions_stub = DrivingDimensionsStub(self._grpc_client.channel)
        self.id = None

    @protect_grpc
    @min_backend_version(25, 1, 0)
    def get_all_driving_dimensions(self):
        """Get driving dimensions for a body.

        Parameters
        ----------
        body : Body
            Body to get driving dimensions.

        Returns
        -------
        List[DrivingDimension]
            List of driving dimensions for the body.
        """
        response = self._driving_dimensions_stub.GetAll(GetAllRequest())
        print(response)
        return [
            DrivingDimension._from_proto(dimension) for dimension in response.driving_dimensions
        ]

    @protect_grpc
    @check_input_types
    @min_backend_version(25, 1, 0)
    def set_driving_dimensions(self, driving_dimension: DrivingDimension) -> bool:
        """Set driving dimensions for a body.

        Parameters
        ----------
        body : Body
            Body to set driving dimensions.
        dimensions : List[DrivingDimension]
            List of driving dimensions to set.

        Returns
        -------
        bool
            True if driving dimensions were set successfully.
        """
        request = UpdateRequest(driving_dimension=driving_dimension._to_proto())
        response = self._driving_dimensions_stub.Update(request)
        return response.success
