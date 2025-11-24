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
"""Module containing the faces service implementation for v1."""

from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest
import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.conversions import (
    from_measurement_to_server_angle,
    from_measurement_to_server_length,
    to_area,
)
from ..base.faces import GRPCFacesService
from .conversions import (
    build_grpc_id,
    from_angle_to_grpc_quantity,
    from_grpc_curve_to_curve,
    from_grpc_direction_to_unit_vector,
    from_grpc_point_to_point3d,
    from_grpc_surface_to_surface,
    from_length_to_grpc_quantity,
    from_line_to_grpc_line,
    from_point3d_to_grpc_point,
    from_unit_vector_to_grpc_direction,
    serialize_tracked_command_response,
)


class GRPCFacesServiceV1(GRPCFacesService):  # pragma: no cover
    """Faces service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    faces service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.face_pb2_grpc import FaceStub
        from ansys.api.discovery.v1.operations.edit_pb2_grpc import EditStub

        self.stub = FaceStub(channel)
        self.EditStub = EditStub(channel)

    @protect_grpc
    def get_surface(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])
        
        # Call the gRPC service
        response = self.stub.GetSurface(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "surface": from_grpc_surface_to_surface(response.surface, kwargs["surface_type"]),
        }

    @protect_grpc
    def get_box_uv(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetBoxUV(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "uv_box": {
                "u": (
                    response.start_u.value_in_geometry_units,
                    response.end_u.value_in_geometry_units,
                ),
                "v": (
                    response.start_v.value_in_geometry_units,
                    response.end_v.value_in_geometry_units,
                ),
            }
        }

    @protect_grpc
    def get_area(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetArea(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {"area": to_area(response.area.value_in_geometry_units)}

    @protect_grpc
    def get_edges(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetEdges(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "edges": [
                {
                    "id": edge.id.id,
                    "curve_type": edge.curve_type,
                    "is_reversed": edge.is_reversed,
                }
                for edge in response.edges
            ]
        }

    @protect_grpc
    def get_vertices(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetVertices(request=request).response_data[0]

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
        from ..base.conversions import to_distance

        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetLoops(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "loops": [
                {
                    "type": loop.type,
                    "length": to_distance(loop.length.value_in_geometry_units).value,
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
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetColor(request=request)

        # Return the response - formatted as a dictionary
        color = response.colors.get(kwargs["id"], "")
        return {"color": color}

    @protect_grpc
    def get_bounding_box(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetBoundingBox(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "min_corner": from_grpc_point_to_point3d(response.box.min),
            "max_corner": from_grpc_point_to_point3d(response.box.max),
            "center": from_grpc_point_to_point3d(response.box.center),
        }

    @protect_grpc
    def set_color(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.designmessages_pb2 import (
            SetColorRequest,
            SetColorRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetColorRequest(
            request_data=[
                SetColorRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    color=kwargs["color"],
                )
            ]
        )
        # Call the gRPC service
        response = self.stub.SetColor(request=request)

        # Return the response - formatted as a dictionary
        return {"success": len(response.successfully_set_ids) == 1}

    @protect_grpc
    def get_normal(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.face_pb2 import (
            GetNormalRequest,
            GetNormalRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = GetNormalRequest(
            request_data=[
                GetNormalRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    u=kwargs["u"],
                    v=kwargs["v"],
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.GetNormal(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "normal": from_grpc_direction_to_unit_vector(response.direction),
        }

    @protect_grpc
    def evaluate(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.face_pb2 import (
            EvaluateRequest,
            EvaluateRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = EvaluateRequest(
            request_data=[
                EvaluateRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    u=kwargs["u"],
                    v=kwargs["v"],
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.Evaluate(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "point": from_grpc_point_to_point3d(response.point),
        }

    @protect_grpc
    def create_iso_parametric_curve(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.face_pb2 import (
            CreateIsoParamCurvesRequest,
            CreateIsoParamCurvesRequestData,
        )

        from ansys.geometry.core.shapes.parameterization import Interval

        from ..base.conversions import to_distance

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateIsoParamCurvesRequest(
            request_data=[
                CreateIsoParamCurvesRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    u_dir_curve=kwargs["use_u_param"],
                    proportion=kwargs["parameter"],
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.CreateIsoParamCurves(request=request).response_data[0]

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
    def extrude_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            ExtrudeFacesRequest,
            ExtrudeFacesRequestData,
        )

        # Assign direction
        direction = (
            None
            if kwargs["direction"] is None
            else from_unit_vector_to_grpc_direction(kwargs["direction"])
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = ExtrudeFacesRequest(
            request_data=[
                ExtrudeFacesRequestData(
                    ids=[build_grpc_id(id) for id in kwargs["face_ids"]],
                    distance=from_length_to_grpc_quantity(kwargs["distance"]),
                    direction=direction,
                    extrude_type=kwargs["extrude_type"].value,
                    pull_symmetric=kwargs["pull_symmetric"],
                    offset_mode=kwargs["offset_mode"].value,
                    copy=kwargs["copy"],
                    force_do_as_extrude=kwargs["force_do_as_extrude"],
                )
            ]
        )

        # Call the gRPC service and serialize the response
        response = self.EditStub.ExtrudeFaces(request=request)
        tracked_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response - formatted as a dictionary
        return {
            "success": tracked_response.get("success"),
            "created_bodies": [body.get("id") for body in tracked_response.get("created_bodies")],
        }

    @protect_grpc
    def extrude_faces_up_to(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            ExtrudeFacesUpToRequest,
            ExtrudeFacesUpToRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = ExtrudeFacesUpToRequest(
            request_data=[
                ExtrudeFacesUpToRequestData(
                    faces=[build_grpc_id(id) for id in kwargs["face_ids"]],
                    up_to_selection=build_grpc_id(kwargs["up_to_selection_id"]),
                    seed_point=from_point3d_to_grpc_point(kwargs["seed_point"]),
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    extrude_type=kwargs["extrude_type"].value,
                    pull_symmetric=kwargs["pull_symmetric"],
                    offset_mode=kwargs["offset_mode"].value,
                    copy=kwargs["copy"],
                    force_do_as_extrude=kwargs["force_do_as_extrude"],
                )
            ]
        )

        # Call the gRPC service and serialize the response
        response = self.EditStub.ExtrudeFacesUpTo(request=request)
        tracked_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response - formatted as a dictionary
        return {
            "success": tracked_response.get("success"),
            "created_bodies": [body.get("id") for body in tracked_response.get("created_bodies")],
        }

    @protect_grpc
    def offset_faces_set_radius(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            OffsetFacesSetRadiusRequest,
            OffsetFacesSetRadiusRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        # TODO: multiple faces?
        request = OffsetFacesSetRadiusRequest(
            request_data=[
                OffsetFacesSetRadiusRequestData(
                    id=[build_grpc_id(id) for id in kwargs["face_ids"]],
                    radius=from_measurement_to_server_length(kwargs["radius"]),
                    offset_mode=kwargs["offset_mode"].value,
                    copy=kwargs["copy"],
                    extrude_type=kwargs["extrude_type"].value,
                )
            ]
        )

        # Call the gRPC service
        response = self.EditStub.OffsetFacesSetRadius(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_command_response.command_response.success,
        }

    @protect_grpc
    def revolve_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            RevolveFacesRequest,
            RevolveFacesRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = RevolveFacesRequest(
            request_data=[
                RevolveFacesRequestData(
                    selection_id=[build_grpc_id(id) for id in kwargs["selection_ids"]],
                    axis=from_line_to_grpc_line(kwargs["axis"]),
                    angle=from_measurement_to_server_angle(kwargs["angle"]),
                    extrude_type=kwargs["extrude_type"].value,
                )
            ]
        )

        # Call the gRPC service and serialize the response
        response = self.EditStub.RevolveFaces(request=request)
        tracked_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response - formatted as a dictionary
        return {
            "success": tracked_response.get("success"),
            "created_bodies": [body.get("id") for body in tracked_response.get("created_bodies")],
        }

    @protect_grpc
    def revolve_faces_up_to(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            RevolveFacesUpToRequest,
            RevolveFacesUpToRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = RevolveFacesUpToRequest(
            request_data=[
                RevolveFacesUpToRequestData(
                    selection_ids=[build_grpc_id(id) for id in kwargs["selection_ids"]],
                    up_to_selection_id=build_grpc_id(kwargs["up_to_selection_id"]),
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    axis=from_line_to_grpc_line(kwargs["axis"]),
                    extrude_type=kwargs["extrude_type"].value,
                )
            ]
        )

        # Call the gRPC service and serialize the response
        response = self.EditStub.RevolveFacesUpTo(request=request)
        tracked_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response - formatted as a dictionary
        return {
            "success": tracked_response.get("success"),
            "created_bodies": [body.get("id") for body in tracked_response.get("created_bodies")],
        }

    @protect_grpc
    def revolve_faces_by_helix(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            RevolveFacesByHelixRequest,
            RevolveFacesByHelixRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = RevolveFacesByHelixRequest(
            request_data=[
                RevolveFacesByHelixRequestData(
                    selection_ids=[build_grpc_id(id) for id in kwargs["selection_ids"]],
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    axis=from_line_to_grpc_line(kwargs["axis"]),
                    height=from_measurement_to_server_length(kwargs["height"]),
                    pitch=from_measurement_to_server_length(kwargs["pitch"]),
                    taper_angle=from_measurement_to_server_angle(kwargs["taper_angle"]),
                    right_handed=kwargs["right_handed"],
                    both_sides=kwargs["both_sides"],
                    extrude_type=kwargs["extrude_type"].value,
                )
            ]
        )

        # Call the gRPC service and serialize the response
        response = self.EditStub.RevolveFacesByHelix(request=request)
        tracked_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response - formatted as a dictionary
        return {
            "success": tracked_response.get("success"),
            "created_bodies": [body.get("id") for body in tracked_response.get("created_bodies")],
        }

    @protect_grpc
    def replace_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.face_pb2 import ReplaceFaceRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ReplaceFaceRequest(
            target_selection_ids=[build_grpc_id(id) for id in kwargs["target_ids"]],
            replacement_selection_ids=[build_grpc_id(id) for id in kwargs["replacement_ids"]],
        )

        # Call the gRPC service
        response = self.stub.Replace(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_command_response.command_response.success,
        }

    @protect_grpc
    def thicken_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            ThickenFacesRequest,
            ThickenFacesRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = ThickenFacesRequest(
            request_data=[
                ThickenFacesRequestData(
                    ids=[build_grpc_id(id) for id in kwargs["face_ids"]],
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    value=from_length_to_grpc_quantity(kwargs["thickness"]),
                    extrude_type=kwargs["extrude_type"].value,
                    pull_symmetric=kwargs["pull_symmetric"],
                    select_direction=kwargs["select_direction"],
                )
            ]
        )

        # Call the gRPC service
        response = self.EditStub.ThickenFaces(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_command_response.command_response.success,
        }

    @protect_grpc
    def draft_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            DraftFacesRequest,
            DraftFacesRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = DraftFacesRequest(
            request_data=[
                DraftFacesRequestData(
                    ids=[build_grpc_id(id) for id in kwargs["face_ids"]],
                    reference_ids=[build_grpc_id(id) for id in kwargs["reference_face_ids"]],
                    draft_side=kwargs["draft_side"].value,
                    draft_angle=from_angle_to_grpc_quantity(kwargs["angle"]),
                    extrude_type=kwargs["extrude_type"].value,
                )
            ]
        )

        # Call the gRPC server
        response = self.EditStub.DraftFaces(request=request)

        # Return the drafted faces
        return {
            "created_faces": [face.id for face in response.created_faces],
        }

    @protect_grpc
    def get_round_info(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["face_id"])])

        # Call the gRPC service
        response = self.stub.GetRoundInfo(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "along_u": response.along_u,
            "radius": response.radius,
        }

    @protect_grpc
    def offset_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            OffsetFacesRequest,
            OffsetFacesRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = OffsetFacesRequest(
            request_data=[
                OffsetFacesRequestData(
                    faces=[build_grpc_id(id) for id in kwargs["face_ids"]],
                    offset=from_measurement_to_server_length(kwargs["distance"]),
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    extrude_type=kwargs["extrude_type"].value,
                )
            ]
        )

        # Call the gRPC service and serialize the response
        response = self.EditStub.OffsetFaces(request=request)
        tracked_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response - formatted as a dictionary
        return {
            "results": [face.get("id") for face in tracked_response.get("created_faces")],
        }

    @protect_grpc
    def setup_offset_relationship(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            FaceOffsetRequest,
            FaceOffsetRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = FaceOffsetRequest(
            request_data=[
                FaceOffsetRequestData(
                    face1=build_grpc_id(kwargs["face1_id"]),
                    face2=build_grpc_id(kwargs["face2_id"]),
                    set_baselines=kwargs["set_baselines"],
                    process_adjacent_faces=kwargs["process_adjacent_faces"],
                )
            ]
        )

        # Call the gRPC service
        response = self.EditStub.FaceOffset(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_command_response.command_response.success,
        }
