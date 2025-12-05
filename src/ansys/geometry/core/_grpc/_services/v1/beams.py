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
"""Module containing the beams service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.beams import GRPCBeamsService
from ..base.conversions import to_distance
from .conversions import (
    build_grpc_id,
    from_grpc_curve_to_curve,
    from_grpc_frame_to_frame,
    from_grpc_material_to_material,
    from_grpc_point_to_point3d,
    from_plane_to_grpc_plane,
    from_point3d_to_grpc_point,
)


class GRPCBeamsServiceV1(GRPCBeamsService):
    """Beams service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    beams service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.engineeringdata.beamprofiledata_pb2_grpc import (
            BeamProfileDataStub,
        )

        self.beam_commands_stub = BeamProfileDataStub

    @protect_grpc
    def create_beam_segments(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import Line
        from ansys.api.discovery.v1.engineeringdata.beamprofiledata_pb2 import (
            CreateBeamProfileSegmentsRequest,
            CreateBeamProfileSegmentsRequestData,
        )

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
        request = CreateBeamProfileSegmentsRequest(
            request_data=[
                CreateBeamProfileSegmentsRequestData(
                    profile_id=build_grpc_id(kwargs["profile_id"]),
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    lines=lines,
                )
            ]
        )

        # Call the gRPC service
        response = self.beam_commands_stub.CreateSegments(request)

        # Return the response - formatted as a dictionary
        return {
            "beam_ids": [
                [beam.id for beam in response_data.beams_ids]
                for response_data in response.response_data
            ]
        }

    @protect_grpc
    def create_descriptive_beam_segments(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import Line
        from ansys.api.discovery.v1.engineeringdata.beamprofiledata_pb2 import (
            CreateBeamProfileSegmentsRequest,
            CreateBeamProfileSegmentsRequestData,
        )

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
        request = CreateBeamProfileSegmentsRequest(
            request_data=[
                CreateBeamProfileSegmentsRequestData(
                    profile_id=kwargs["profile_id"],
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    lines=lines,
                )
            ]
        )

        # Call the gRPC service
        response = self.beam_commands_stub.CreateDescriptiveSegments(request)

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
                for response_data in response.response_data
                for beam in response_data.beams
            ],
        }

    @protect_grpc
    def delete_beam(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["beam_id"])])

        # Call the gRPC service
        _ = self.beam_commands_stub.Delete(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def delete_beam_profile(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def create_beam_circular_profile(self, **kwargs) -> dict:  # noqa: D10
        from ansys.api.discovery.v1.engineeringdata.beamprofiledata_pb2 import (
            CreateBeamProfileCircularRequest,
            CreateBeamProfileCircularRequestData,
        )

        from .conversions import from_length_to_grpc_quantity

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateBeamProfileCircularRequest(
            request_data=[
                CreateBeamProfileCircularRequestData(
                    origin=from_point3d_to_grpc_point(kwargs["center"]),
                    radius=from_length_to_grpc_quantity(kwargs["radius"]),
                    plane=from_plane_to_grpc_plane(kwargs["plane"]),
                    name=kwargs["name"],
                )
            ]
        )

        # Call the gRPC service
        response = self.beam_commands_stub.CreateCircular(request)

        # Return the response - formatted as a dictionary
        # Note: response.ids is a repeated field, we return the first one
        created_beam_entity = response.ids[0]
        return {"id": created_beam_entity.id}
