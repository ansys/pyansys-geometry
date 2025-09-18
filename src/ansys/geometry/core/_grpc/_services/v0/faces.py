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
"""Module containing the faces service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.conversions import (
    from_measurement_to_server_angle,
    from_measurement_to_server_length,
    to_area,
    to_distance,
)
from ..base.faces import GRPCFacesService
from .conversions import (
    build_grpc_id,
    from_grpc_curve_to_curve,
    from_grpc_point_to_point3d,
    from_grpc_surface_to_surface,
    from_line_to_grpc_line,
    from_point3d_to_grpc_point,
    from_unit_vector_to_grpc_direction,
)


class GRPCFacesServiceV0(GRPCFacesService):  # pragma: no cover
    """Faces service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    faces service. It is specifically designed for the v0 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
        from ansys.api.geometry.v0.faces_pb2_grpc import FacesStub

        self.stub = FacesStub(channel)
        self.commands_stub = CommandsStub(channel)

    @protect_grpc
    def get_surface(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetSurface(request=request)

        # Return the response - formatted as a dictionary
        return {
            "surface": from_grpc_surface_to_surface(response, kwargs["surface_type"]),
        }

    @protect_grpc
    def get_box_uv(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetBoxUV(request=request)

        # Return the response - formatted as a dictionary
        return {
            "uv_box": {
                "u": (response.start_u, response.end_u),
                "v": (response.start_v, response.end_v),
            }
        }

    @protect_grpc
    def get_area(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetArea(request=request)

        # Return the response - formatted as a dictionary
        return {"area": to_area(response.area)}

    @protect_grpc
    def get_edges(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetEdges(request=request)

        # Return the response - formatted as a dictionary
        return {
            "edges": [
                {
                    "id": edge.id,
                    "curve_type": edge.curve_type,
                    "is_reversed": edge.is_reversed,
                }
                for edge in response.edges
            ]
        }

    @protect_grpc
    def get_vertices(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        from ansys.api.geometry.v0.faces_pb2 import GetVerticesRequest

        request = GetVerticesRequest(face_id=build_grpc_id(kwargs["id"]))

        # Call the gRPC service
        response = self.stub.GetVertices(request=request)

        # Return the response - formatted as a dictionary
        return {
            "vertices": [
                {
                    "id": vertex.id.id,
                    "position": from_grpc_point_to_point3d(vertex.position),
                }
                for vertex in response.vertices
            ]
        }

    @protect_grpc
    def get_loops(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetLoops(request=request)

        # Return the response - formatted as a dictionary
        return {
            "loops": [
                {
                    "type": loop.type,
                    "length": to_distance(loop.length).value,
                    "min_corner": from_grpc_point_to_point3d(loop.bounding_box.min),
                    "max_corner": from_grpc_point_to_point3d(loop.bounding_box.max),
                    "edges": [edge for edge in loop.edges],
                }
                for loop in response.loops
            ]
        }

    @protect_grpc
    def get_color(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetColor(request=request)

        # Return the response - formatted as a dictionary
        return {"color": response.color}

    @protect_grpc
    def get_bounding_box(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetBoundingBox(request=request)

        # Return the response - formatted as a dictionary
        return {
            "min_corner": from_grpc_point_to_point3d(response.min),
            "max_corner": from_grpc_point_to_point3d(response.max),
            "center": from_grpc_point_to_point3d(response.center),
        }

    @protect_grpc
    def set_color(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.faces_pb2 import SetColorRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetColorRequest(
            face_id=kwargs["id"],
            color=kwargs["color"],
        )
        # Call the gRPC service
        response = self.stub.SetColor(request=request)

        # Return the response - formatted as a dictionary
        return {"success": response.success}

    @protect_grpc
    def get_normal(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.faces_pb2 import GetNormalRequest

        from ansys.geometry.core.math.vector import UnitVector3D

        # Create the request - assumes all inputs are valid and of the proper type
        request = GetNormalRequest(
            id=kwargs["id"],
            u=kwargs["u"],
            v=kwargs["v"],
        )

        # Call the gRPC service
        response = self.stub.GetNormal(request=request)

        # Return the response - formatted as a dictionary
        return {
            "normal": UnitVector3D(
                [response.direction.x, response.direction.y, response.direction.z]
            ),
        }

    @protect_grpc
    def evaluate(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.faces_pb2 import EvaluateRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = EvaluateRequest(
            id=kwargs["id"],
            u=kwargs["u"],
            v=kwargs["v"],
        )

        # Call the gRPC service
        response = self.stub.Evaluate(request=request)

        # Return the response - formatted as a dictionary
        return {
            "point": from_grpc_point_to_point3d(response.point),
        }

    @protect_grpc
    def create_iso_parametric_curve(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.faces_pb2 import CreateIsoParamCurvesRequest

        from ansys.geometry.core.shapes.parameterization import Interval

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateIsoParamCurvesRequest(
            id=kwargs["id"],
            u_dir_curve=kwargs["use_u_param"],
            proportion=kwargs["parameter"],
        )

        # Call the gRPC service
        response = self.stub.CreateIsoParamCurves(request=request)

        # Return the response - formatted as a dictionary
        return {
            "curves": [
                {
                    "geometry": from_grpc_curve_to_curve(curve.curve),
                    "start": from_grpc_point_to_point3d(curve.start),
                    "end": from_grpc_point_to_point3d(curve.end),
                    "interval": Interval(curve.interval_start, curve.interval_end),
                    "length": to_distance(curve.length).value,
                }
                for curve in response.curves
            ]
        }

    @protect_grpc
    def extrude_faces(self, **kwargs):  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import ExtrudeFacesRequest

        # Assign direction
        direction = (
            None
            if kwargs["direction"] is None
            else from_unit_vector_to_grpc_direction(kwargs["direction"])
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = ExtrudeFacesRequest(
            faces=[EntityIdentifier(id=face_id) for face_id in kwargs["face_ids"]],
            distance=from_measurement_to_server_length(kwargs["distance"]),
            direction=direction,
            extrude_type=kwargs["extrude_type"].value,
            pull_symmetric=kwargs["pull_symmetric"],
            offset_mode=kwargs["offset_mode"].value,
            copy=kwargs["copy"],
            force_do_as_extrude=kwargs["force_do_as_extrude"],
        )

        # Call the gRPC service
        response = self.commands_stub.ExtrudeFaces(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "created_bodies": [body.id for body in response.created_bodies],
        }

    @protect_grpc
    def extrude_faces_up_to(self, **kwargs):  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import ExtrudeFacesUpToRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ExtrudeFacesUpToRequest(
            faces=[EntityIdentifier(id=face_id) for face_id in kwargs["face_ids"]],
            up_to_selection=EntityIdentifier(id=kwargs["up_to_selection_id"]),
            seed_point=from_point3d_to_grpc_point(kwargs["seed_point"]),
            direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
            extrude_type=kwargs["extrude_type"].value,
            pull_symmetric=kwargs["pull_symmetric"],
            offset_mode=kwargs["offset_mode"].value,
            copy=kwargs["copy"],
            force_do_as_extrude=kwargs["force_do_as_extrude"],
        )

        # Call the gRPC service
        response = self.commands_stub.ExtrudeFacesUpTo(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "created_bodies": [body.id for body in response.created_bodies],
        }

    @protect_grpc
    def offset_faces_set_radius(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import OffsetFacesSetRadiusRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = OffsetFacesSetRadiusRequest(
            faces=[EntityIdentifier(id=face_id) for face_id in kwargs["face_ids"]],
            radius=from_measurement_to_server_length(kwargs["radius"]),
            offset_mode=kwargs["offset_mode"].value,
            copy=kwargs["copy"],
            extrude_type=kwargs["extrude_type"].value,
        )

        # Call the gRPC service
        response = self.commands_stub.OffsetFacesSetRadius(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
        }

    @protect_grpc
    def revolve_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import RevolveFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = RevolveFacesRequest(
            selection=[EntityIdentifier(id=object_id) for object_id in kwargs["selection_ids"]],
            axis=from_line_to_grpc_line(kwargs["axis"]),
            angle=from_measurement_to_server_angle(kwargs["angle"]),
            extrude_type=kwargs["extrude_type"].value,
        )

        # Call the gRPC service
        response = self.commands_stub.RevolveFaces(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "created_bodies": [body.id for body in response.created_bodies],
        }

    @protect_grpc
    def revolve_faces_up_to(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import RevolveFacesUpToRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = RevolveFacesUpToRequest(
            selection=[EntityIdentifier(id=object_id) for object_id in kwargs["selection_ids"]],
            up_to_selection=EntityIdentifier(id=kwargs["up_to_selection_id"]),
            axis=from_line_to_grpc_line(kwargs["axis"]),
            direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
            extrude_type=kwargs["extrude_type"].value,
        )

        # Call the gRPC service
        response = self.commands_stub.RevolveFacesUpTo(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "created_bodies": [body.id for body in response.created_bodies],
        }

    @protect_grpc
    def revolve_faces_by_helix(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import RevolveFacesByHelixRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = RevolveFacesByHelixRequest(
            selection=[EntityIdentifier(id=object_id) for object_id in kwargs["selection_ids"]],
            axis=from_line_to_grpc_line(kwargs["axis"]),
            direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
            height=from_measurement_to_server_length(kwargs["height"]),
            pitch=from_measurement_to_server_length(kwargs["pitch"]),
            taper_angle=from_measurement_to_server_angle(kwargs["taper_angle"]),
            right_handed=kwargs["right_handed"],
            both_sides=kwargs["both_sides"],
            extrude_type=kwargs["extrude_type"].value,
        )

        # Call the gRPC service
        response = self.commands_stub.RevolveFacesByHelix(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "created_bodies": [body.id for body in response.created_bodies],
        }

    @protect_grpc
    def replace_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import ReplaceFaceRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ReplaceFaceRequest(
            target_selection=[EntityIdentifier(id=object_id) for object_id in kwargs["target_ids"]],
            replacement_selection=[
                EntityIdentifier(id=object_id) for object_id in kwargs["replacement_ids"]
            ],
        )

        # Call the gRPC service
        response = self.commands_stub.ReplaceFace(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
        }

    @protect_grpc
    def thicken_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import ThickenFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ThickenFacesRequest(
            faces=[EntityIdentifier(id=face_id) for face_id in kwargs["face_ids"]],
            direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
            value=from_measurement_to_server_length(kwargs["thickness"]),
            extrude_type=kwargs["extrude_type"].value,
            pull_symmetric=kwargs["pull_symmetric"],
            select_direction=kwargs["select_direction"],
        )

        # Call the gRPC service
        response = self.commands_stub.ThickenFaces(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
        }

    @protect_grpc
    def draft_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import DraftFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = DraftFacesRequest(
            faces=[EntityIdentifier(id=face_id) for face_id in kwargs["face_ids"]],
            reference_faces=[
                EntityIdentifier(id=face_id) for face_id in kwargs["reference_face_ids"]
            ],
            draft_side=kwargs["draft_side"].value,
            draft_angle=from_measurement_to_server_angle(kwargs["angle"]),
            extrude_type=kwargs["extrude_type"].value,
        )

        # Call the gRPC server
        response = self.commands_stub.DraftFaces(request=request)

        # Return the drafted faces
        return {
            "created_faces": [face.id for face in response.created_faces],
        }

    @protect_grpc
    def get_round_info(self, **kwargs):  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
        from ansys.api.geometry.v0.commands_pb2 import RoundInfoRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = RoundInfoRequest(
            face=EntityIdentifier(id=kwargs["face_id"]),
        )

        # Call the gRPC service
        response = self.commands_stub.GetRoundInfo(request=request)

        # Return the response - formatted as a dictionary
        return {
            "along_u": response.along_u,
            "radius": response.radius,
        }
