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
"""Module containing the beams service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.beams import GRPCBeamsService
from ..base.conversions import to_distance
from .conversions import (
    from_grpc_curve_to_curve,
    from_grpc_frame_to_frame,
    from_grpc_material_to_material,
    from_grpc_point_to_point3d,
    from_point3d_to_grpc_point,
)


class GRPCBeamsServiceV0(GRPCBeamsService):
    """Beams service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    beams service. It is specifically designed for the v0 version of the
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
    def create_beam_segments(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import CreateBeamSegmentsRequest
        from ansys.api.geometry.v0.models_pb2 import Line

        # Create the gRPC Line objects
        lines = []
        for segment in kwargs["segments"]:
            lines.append(
                Line(
                    start=from_point3d_to_grpc_point(segment[0]),
                    end=from_point3d_to_grpc_point(segment[1]),
                )
            )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateBeamSegmentsRequest(
            profile=kwargs["profile_id"],
            parent=kwargs["parent_id"],
            lines=lines,
        )

        # Call the gRPC service
        resp = self.stub.CreateBeamSegments(request)

        # Return the response - formatted as a dictionary
        return {
            "beam_ids": resp.ids,
        }

    @protect_grpc
    def create_descriptive_beam_segments(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import CreateBeamSegmentsRequest
        from ansys.api.geometry.v0.models_pb2 import Line

        from ansys.geometry.core.shapes.parameterization import Interval, ParamUV

        # Create the gRPC Line objects
        lines = []
        for segment in kwargs["segments"]:
            lines.append(
                Line(
                    start=from_point3d_to_grpc_point(segment[0]),
                    end=from_point3d_to_grpc_point(segment[1]),
                )
            )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateBeamSegmentsRequest(
            profile=kwargs["profile_id"],
            parent=kwargs["parent_id"],
            lines=lines,
        )

        # Call the gRPC service
        resp = self.stub.CreateDescriptiveBeamSegments(request)

        # Return the response - formatted as a dictionary
        return {
            "created_beams": [
                {
                    "cross_section": {
                        "section_anchor": beam.cross_section.section_anchor,
                        "section_angle": beam.cross_section.section_angle,
                        "section_frame": from_grpc_frame_to_frame(beam.cross_section.section_frame),
                        "section_profile": [
                            [
                                {
                                    "geometry": from_grpc_curve_to_curve(curve.curve),
                                    "start": from_grpc_point_to_point3d(curve.start),
                                    "end": from_grpc_point_to_point3d(curve.end),
                                    "interval": Interval(curve.interval_start, curve.interval_end),
                                    "length": to_distance(curve.length).value,
                                }
                                for curve in curve_list.curves
                            ]
                            for curve_list in beam.cross_section.section_profile
                        ],
                    },
                    "properties": {
                        "area": beam.properties.area,
                        "centroid": ParamUV(beam.properties.centroid_x, beam.properties.centroid_y),
                        "warping_constant": beam.properties.warping_constant,
                        "ixx": beam.properties.ixx,
                        "ixy": beam.properties.ixy,
                        "iyy": beam.properties.iyy,
                        "shear_center": ParamUV(
                            beam.properties.shear_center_x, beam.properties.shear_center_y
                        ),
                        "torsional_constant": beam.properties.torsional_constant,
                    },
                    "id": beam.id.id,
                    "start": from_grpc_point_to_point3d(beam.shape.start),
                    "end": from_grpc_point_to_point3d(beam.shape.end),
                    "name": beam.name,
                    "is_deleted": beam.is_deleted,
                    "is_reversed": beam.is_reversed,
                    "is_rigid": beam.is_rigid,
                    "material": from_grpc_material_to_material(beam.material),
                    "shape": {
                        "geometry": from_grpc_curve_to_curve(beam.shape.curve),
                        "start": from_grpc_point_to_point3d(beam.shape.start),
                        "end": from_grpc_point_to_point3d(beam.shape.end),
                        "interval": Interval(beam.shape.interval_start, beam.shape.interval_end),
                        "length": to_distance(beam.shape.length).value,
                    },
                    "beam_type": beam.type,
                }
                for beam in resp.created_beams
            ],
        }

    @protect_grpc
    def delete_beam(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier

        # Create the request - assumes all inputs are valid and of the proper type
        request = EntityIdentifier(id=kwargs["beam_id"])

        # Call the gRPC service
        _ = self.stub.DeleteBeam(request)

        # Return the response - formatted as a dictionary
        return {}
