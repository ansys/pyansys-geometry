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
"""Module containing the model tools service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.conversions import (
    from_measurement_to_server_angle,
    from_measurement_to_server_length,
)
from ..base.model_tools import GRPCModelToolsService
from .conversions import (
    from_line_to_grpc_line,
    from_unit_vector_to_grpc_direction,
)


class GRPCModelToolsServiceV0(GRPCModelToolsService):
    """Model tools service for gRPC communication with the Geometry server.
    
    This class provides methods to interact with the Geometry server's
    model tools service. It is specifically designed for the v0 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub

        self._stub = CommandsStub(channel)

    @protect_grpc
    def chamfer(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import ChamferRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ChamferRequest(
            ids=[EntityIdentifier(id=id) for id in kwargs["selection_ids"]],
            distance=from_measurement_to_server_length(kwargs["distance"]),
        )

        # Call the gRPC service
        response = self._stub.Chamfer(request)

        # Return the response as a dictionary
        return {
            "success": response.success,
        }

    @protect_grpc
    def fillet(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import FilletRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FilletRequest(
            ids=[EntityIdentifier(id=id) for id in kwargs["selection_ids"]],
            radius=from_measurement_to_server_length(kwargs["radius"]),
        )

        # Call the gRPC service
        response = self._stub.Fillet(request)

        # Return the response as a dictionary
        return {
            "success": response.success,
        }

    @protect_grpc
    def full_fillet(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import FullFilletRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FullFilletRequest(
            faces=[EntityIdentifier(id=id) for id in kwargs["selection_ids"]],
        )

        # Call the gRPC service
        response = self._stub.FullFillet(request)

        # Return the response as a dictionary
        return {
            "success": response.success,
        }
    
    @protect_grpc
    def move_rotate(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import MoveRotateRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MoveRotateRequest(
            selection=[EntityIdentifier(id=kwargs["selection_id"])],
            axis=from_line_to_grpc_line(kwargs["axis"]),
            angle=from_measurement_to_server_angle(kwargs["angle"]),
        )

        # Call the gRPC service
        response = self._stub.MoveRotate(request)

        # Return the response as a dictionary
        return {
            "success": response.success,
            "modified_bodies": response.modified_bodies,
            "modified_faces": response.modified_faces,
            "modified_edges": response.modified_edges,
        }
    
    @protect_grpc
    def move_translate(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import MoveTranslateRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MoveTranslateRequest(
            selection=[EntityIdentifier(id=kwargs["selection_id"])],
            direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
            distance=from_measurement_to_server_length(kwargs["distance"]),
        )

        # Call the gRPC service
        response = self._stub.MoveTranslate(request)

        # Return the response as a dictionary
        return {
            "success": response.success,
        }