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
"""Module containing the patterns service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.patterns import GRPCPatternsService
from .conversions import (
    build_grpc_id,
    from_angle_to_grpc_quantity,
    from_length_to_grpc_quantity,
)


class GRPCPatternsServiceV1(GRPCPatternsService):  # pragma: no cover
    """Patterns service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    patterns service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.relationships.pattern_pb2_grpc import PatternStub

        self.stub = PatternStub(channel)

    @protect_grpc
    def create_linear_pattern(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.relationships.pattern_pb2 import (
            LinearPatternCreationRequest,
            LinearPatternCreationRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = LinearPatternCreationRequest(
            request_data=[
                LinearPatternCreationRequestData(
                    selection_ids=[build_grpc_id(id) for id in kwargs["selection_ids"]],
                    linear_direction_id=build_grpc_id(kwargs["linear_direction_id"]),
                    count_x=kwargs["count_x"],
                    pitch_x=from_length_to_grpc_quantity(kwargs["pitch_x"]),
                    two_dimensional=kwargs["two_dimensional"],
                    count_y=kwargs["count_y"],
                    pitch_y=from_length_to_grpc_quantity(kwargs["pitch_y"]),
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.CreateLinear(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_creation_response.creation_response.success,
        }

    @protect_grpc
    def modify_linear_pattern(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.relationships.pattern_pb2 import (
            SetLinearPatternDataRequest,
            SetLinearPatternDataRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetLinearPatternDataRequest(
            request_data=[
                SetLinearPatternDataRequestData(
                    selection_ids=[build_grpc_id(id) for id in kwargs["selection_ids"]],
                    count_x=kwargs["count_x"],
                    pitch_x=from_length_to_grpc_quantity(kwargs["pitch_x"]),
                    count_y=kwargs["count_y"],
                    pitch_y=from_length_to_grpc_quantity(kwargs["pitch_y"]),
                    new_seed_index=kwargs["new_seed_index"],
                    old_seed_index=kwargs["old_seed_index"],
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.SetLinearData(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_set_response.set_response.success,
        }

    @protect_grpc
    def create_circular_pattern(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.relationships.pattern_pb2 import (
            CircularPatternCreationRequest,
            CircularPatternCreationRequestData,
        )

        from ansys.geometry.core.shapes.curves.line import Line

        from .conversions import from_line_to_grpc_line, from_unit_vector_to_grpc_direction

        # Create direction if not None
        radial_direction = (
            from_unit_vector_to_grpc_direction(kwargs["radial_direction"])
            if kwargs["radial_direction"] is not None
            else None
        )

        # Create line if axis is a line object
        circular_axis, axis = None, None
        if isinstance(kwargs["circular_axis"], Line):
            axis = from_line_to_grpc_line(kwargs["circular_axis"])
        else:
            circular_axis = build_grpc_id(kwargs["circular_axis"])

        # Create the request - assumes all inputs are valid and of the proper type
        request = CircularPatternCreationRequest(
            request_data=[
                CircularPatternCreationRequestData(
                    selection_ids=[build_grpc_id(id) for id in kwargs["selection_ids"]],
                    circular_count=kwargs["circular_count"],
                    edge_axis_id=circular_axis,
                    circular_angle=from_angle_to_grpc_quantity(kwargs["circular_angle"]),
                    two_dimensional=kwargs["two_dimensional"],
                    linear_count=kwargs["linear_count"],
                    linear_pitch=from_length_to_grpc_quantity(kwargs["linear_pitch"]),
                    radial_direction=radial_direction,
                    line_axis=axis,
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.CreateCircular(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_creation_response.creation_response.success,
        }

    @protect_grpc
    def modify_circular_pattern(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.relationships.pattern_pb2 import (
            SetCircularPatternDataRequest,
            SetCircularPatternDataRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetCircularPatternDataRequest(
            request_data=[
                SetCircularPatternDataRequestData(
                    selection_ids=[build_grpc_id(id) for id in kwargs["selection_ids"]],
                    circular_count=kwargs["circular_count"],
                    linear_count=kwargs["linear_count"],
                    step_angle=from_angle_to_grpc_quantity(kwargs["step_angle"]),
                    step_linear=from_length_to_grpc_quantity(kwargs["step_linear"]),
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.SetCircularData(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_set_response.set_response.success,
        }

    @protect_grpc
    def create_fill_pattern(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.relationships.pattern_pb2 import (
            FillPatternCreationRequest,
            FillPatternCreationRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = FillPatternCreationRequest(
            request_data=[
                FillPatternCreationRequestData(
                    selection_ids=[build_grpc_id(id) for id in kwargs["selection_ids"]],
                    linear_direction_id=build_grpc_id(kwargs["linear_direction_id"]),
                    fill_pattern_type=kwargs["fill_pattern_type"].value,
                    margin=from_length_to_grpc_quantity(kwargs["margin"]),
                    x_spacing=from_length_to_grpc_quantity(kwargs["x_spacing"]),
                    y_spacing=from_length_to_grpc_quantity(kwargs["y_spacing"]),
                    row_x_offset=from_length_to_grpc_quantity(kwargs["row_x_offset"]),
                    row_y_offset=from_length_to_grpc_quantity(kwargs["row_y_offset"]),
                    column_x_offset=from_length_to_grpc_quantity(kwargs["column_x_offset"]),
                    column_y_offset=from_length_to_grpc_quantity(kwargs["column_y_offset"]),
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.CreateFill(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_creation_response.creation_response.success,
        }

    @protect_grpc
    def update_fill_pattern(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.relationships.pattern_pb2 import UpdateFillRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = UpdateFillRequest(
            ids=[build_grpc_id(id) for id in kwargs["selection_ids"]],
        )

        # Call the gRPC service
        response = self.stub.UpdateFill(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_command_response.command_response.success,
        }
