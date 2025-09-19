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
"""Module containing the patterns service implementation for v0."""

import grpc

from ansys.geometry.core._grpc._services.base.conversions import (
    from_measurement_to_server_angle,
    from_measurement_to_server_length,
)
from ansys.geometry.core._grpc._services.v0.conversions import from_unit_vector_to_grpc_direction
from ansys.geometry.core.errors import protect_grpc

from ..base.patterns import GRPCPatternsService


class GRPCPatternsServiceV0(GRPCPatternsService):  # pragma: no cover
    """Patterns service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    patterns service. It is specifically designed for the v0 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub

        self.stub = CommandsStub(channel)

    @protect_grpc
    def create_linear_pattern(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import CreateLinearPatternRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateLinearPatternRequest(
            selection=[EntityIdentifier(id=id) for id in kwargs["selection_ids"]],
            linear_direction=EntityIdentifier(id=kwargs["linear_direction_id"]),
            count_x=kwargs["count_x"],
            pitch_x=from_measurement_to_server_length(kwargs["pitch_x"]),
            two_dimensional=kwargs["two_dimensional"],
            count_y=kwargs["count_y"],
            pitch_y=(
                from_measurement_to_server_length(kwargs["pitch_y"]) if kwargs["pitch_y"] else None
            ),
        )

        # Call the gRPC service
        response = self.stub.CreateLinearPattern(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.result.success,
        }

    @protect_grpc
    def modify_linear_pattern(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import ModifyLinearPatternRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ModifyLinearPatternRequest(
            selection=[EntityIdentifier(id=id) for id in kwargs["selection_ids"]],
            count_x=kwargs["count_x"],
            pitch_x=from_measurement_to_server_length(kwargs["pitch_x"]),
            count_y=kwargs["count_y"],
            pitch_y=from_measurement_to_server_length(kwargs["pitch_y"]),
            new_seed_index=kwargs["new_seed_index"],
            old_seed_index=kwargs["old_seed_index"],
        )

        # Call the gRPC service
        response = self.stub.ModifyLinearPattern(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.result.success,
        }

    @protect_grpc
    def create_circular_pattern(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import CreateCircularPatternRequest

        # Create direction if not None
        radial_direction = (
            from_unit_vector_to_grpc_direction(kwargs["radial_direction"])
            if kwargs["radial_direction"] is not None
            else None
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateCircularPatternRequest(
            selection=[EntityIdentifier(id=id) for id in kwargs["selection_ids"]],
            circular_axis=EntityIdentifier(id=kwargs["circular_axis_id"]),
            circular_count=kwargs["circular_count"],
            circular_angle=from_measurement_to_server_angle(kwargs["circular_angle"]),
            two_dimensional=kwargs["two_dimensional"],
            linear_count=kwargs["linear_count"],
            linear_pitch=(
                from_measurement_to_server_length(kwargs["linear_pitch"])
                if kwargs["linear_pitch"]
                else None
            ),
            radial_direction=radial_direction,
        )

        # Call the gRPC service
        response = self.stub.CreateCircularPattern(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.result.success,
        }

    @protect_grpc
    def modify_circular_pattern(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import ModifyCircularPatternRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ModifyCircularPatternRequest(
            selection=[EntityIdentifier(id=id) for id in kwargs["selection_ids"]],
            circular_count=kwargs["circular_count"],
            linear_count=kwargs["linear_count"],
            step_angle=from_measurement_to_server_angle(kwargs["step_angle"]),
            step_linear=from_measurement_to_server_length(kwargs["step_linear"]),
        )

        # Call the gRPC service
        response = self.stub.ModifyCircularPattern(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.result.success,
        }

    @protect_grpc
    def create_fill_pattern(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import CreateFillPatternRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateFillPatternRequest(
            selection=[EntityIdentifier(id=id) for id in kwargs["selection_ids"]],
            linear_direction=EntityIdentifier(id=kwargs["linear_direction_id"]),
            fill_pattern_type=kwargs["fill_pattern_type"].value,
            margin=from_measurement_to_server_length(kwargs["margin"]),
            x_spacing=from_measurement_to_server_length(kwargs["x_spacing"]),
            y_spacing=from_measurement_to_server_length(kwargs["y_spacing"]),
            row_x_offset=from_measurement_to_server_length(kwargs["row_x_offset"]),
            row_y_offset=from_measurement_to_server_length(kwargs["row_y_offset"]),
            column_x_offset=from_measurement_to_server_length(kwargs["column_x_offset"]),
            column_y_offset=from_measurement_to_server_length(kwargs["column_y_offset"]),
        )

        # Call the gRPC service
        response = self.stub.CreateFillPattern(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.result.success,
        }

    @protect_grpc
    def update_fill_pattern(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import PatternRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = PatternRequest(
            selection=[EntityIdentifier(id=id) for id in kwargs["selection_ids"]],
        )

        # Call the gRPC service
        response = self.stub.UpdateFillPattern(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.result.success,
        }
