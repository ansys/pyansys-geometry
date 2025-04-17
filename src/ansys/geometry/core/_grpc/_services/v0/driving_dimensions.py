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
"""Module containing the Driving Dimension service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.driving_dimensions import GRPCDrivingDimensionsService
from .conversions import (
    from_driving_dimension_to_grpc_driving_dimension,
    from_grpc_driving_dimension_to_driving_dimension,
    from_grpc_update_status_to_parameter_update_status,
)


class GRPCDrivingDimensionsServiceV0(GRPCDrivingDimensionsService):
    """Driving Dimension service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    driving dimension service. It is specifically designed for the v0 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.dbu.v0.drivingdimensions_pb2_grpc import DrivingDimensionsStub

        self.stub = DrivingDimensionsStub(channel)

    @protect_grpc
    def get_all_parameters(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.drivingdimensions_pb2 import GetAllRequest

        # Call the gRPC service
        response = self.stub.GetAll(GetAllRequest())

        # Return the response - formatted as a dictionary
        return {
            "parameters": [
                from_grpc_driving_dimension_to_driving_dimension(param) 
                for param in response.driving_dimensions
            ],
        }

    @protect_grpc
    def set_parameter(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.drivingdimensions_pb2 import UpdateRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = UpdateRequest(
            driving_dimension=from_driving_dimension_to_grpc_driving_dimension(kwargs["driving_dimension"]),
        )

        # Call the gRPC service
        response = self.stub.UpdateParameter(request)

        # Return the response - formatted as a dictionary
        return {
            "status": from_grpc_update_status_to_parameter_update_status(response.status),
        }