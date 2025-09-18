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
"""Module containing the curves service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.conversions import from_measurement_to_server_angle, from_measurement_to_server_length
from ..base.curves import GRPCCurvesService
from .conversions import from_line_to_grpc_line, from_trimmed_curve_to_grpc_trimmed_curve


class GRPCCurvesServiceV0(GRPCCurvesService):  # pragma: no cover
    """Curves service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    curves service. It is specifically designed for the v0 version of the
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
    def offset_face_curves(self, **kwargs):  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import OffsetFaceCurvesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = OffsetFaceCurvesRequest(
            objects=[EntityIdentifier(id=id) for id in kwargs["curve_ids"]],
            offset=from_measurement_to_server_length(kwargs["offset"]),
        )
        
        # Call the gRPC service
        result = self.stub.OffsetFaceCurves(request)

        # Return the result - formatted as a dictionary
        return {
            "success": result.result.success,
            "created_curves": [curve.id for curve in result.created_curves]
        }

    @protect_grpc
    def revolve_edges(self, **kwargs):  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import RevolveCurvesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = RevolveCurvesRequest(
            curves=[from_trimmed_curve_to_grpc_trimmed_curve(curve) for curve in kwargs["curves"]],
            axis=from_line_to_grpc_line(kwargs["axis"]),
            angle=from_measurement_to_server_angle(kwargs["angle"]),
            symmetric=kwargs["symmetric"],
        )

        # Call the gRPC service
        _ = self.stub.RevolveCurves(request)

        # Return the result - formatted as a dictionary
        return {}
