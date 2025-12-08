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
"""Module containing the bodies service implementation for v0."""

import grpc

import ansys.geometry.core as pyansys_geom
from ansys.geometry.core.errors import protect_grpc

from ..base.bodies import GRPCBodyService
from ..base.conversions import from_measurement_to_server_angle, from_measurement_to_server_length
from .conversions import (
    _nurbs_curves_compatibility,
    build_grpc_id,
    from_frame_to_grpc_frame,
    from_grpc_material_to_material,
    from_grpc_point_to_point3d,
    from_grpc_tess_to_pd,
    from_grpc_tess_to_raw_data,
    from_plane_to_grpc_plane,
    from_point3d_to_grpc_point,
    from_sketch_shapes_to_grpc_geometries,
    from_tess_options_to_grpc_tess_options,
    from_trimmed_curve_to_grpc_trimmed_curve,
    from_trimmed_surface_to_grpc_trimmed_surface,
    from_unit_vector_to_grpc_direction,
    serialize_tracker_command_response,
)


class GRPCBodyServiceV0(GRPCBodyService):
    """Body service for gRPC communication with the Geometry server.

    This class provides methods to create and manipulate bodies in the
    Geometry server using gRPC. It is specifically designed for the v0
    version of the Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
        from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub

        self.stub = BodiesStub(channel)
        self.command_stub = CommandsStub(channel)

    @protect_grpc
    def create_sphere_body(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import CreateSphereBodyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateSphereBodyRequest(
            name=kwargs["name"],
            parent=kwargs["parent"],
            center=from_point3d_to_grpc_point(kwargs["center"]),
            radius=from_measurement_to_server_length(kwargs["radius"]),
        )

        # Call the gRPC service
        resp = self.stub.CreateSphereBody(request=request)

        # Return the response - formatted as a dictionary
        return {
            "id": resp.id,
            "name": resp.name,
            "master_id": resp.master_id,
            "is_surface": resp.is_surface,
        }

    @protect_grpc
    def create_extruded_body(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import CreateExtrudedBodyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateExtrudedBodyRequest(
            name=kwargs["name"],
            parent=kwargs["parent_id"],
            plane=from_plane_to_grpc_plane(kwargs["sketch"].plane),
            distance=from_measurement_to_server_length(kwargs["distance"]) * kwargs["direction"],
            geometries=from_sketch_shapes_to_grpc_geometries(
                kwargs["sketch"].plane, kwargs["sketch"].edges, kwargs["sketch"].faces
            ),
        )

        # HACK: we should inform the user that NURBS curve sketches are not supported
        # prior to 26R1... and if passed, raise an error
        _nurbs_curves_compatibility(kwargs["backend_version"], request.geometries)

        # Call the gRPC service
        resp = self.stub.CreateExtrudedBody(request=request)

        # Return the response - formatted as a dictionary
        return {
            "id": resp.id,
            "name": resp.name,
            "master_id": resp.master_id,
            "is_surface": resp.is_surface,
        }

    @protect_grpc
    def create_sweeping_profile_body(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import CreateSweepingProfileRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateSweepingProfileRequest(
            name=kwargs["name"],
            parent=kwargs["parent_id"],
            plane=from_plane_to_grpc_plane(kwargs["sketch"].plane),
            geometries=from_sketch_shapes_to_grpc_geometries(
                kwargs["sketch"].plane, kwargs["sketch"].edges, kwargs["sketch"].faces
            ),
            path=[from_trimmed_curve_to_grpc_trimmed_curve(tc) for tc in kwargs["path"]],
        )

        # HACK: we should inform the user that NURBS curve sketches are not supported
        # prior to 26R1... and if passed, raise an error
        _nurbs_curves_compatibility(kwargs["backend_version"], request.geometries)

        # Call the gRPC service
        resp = self.stub.CreateSweepingProfile(request=request)

        # Return the response - formatted as a dictionary
        return {
            "id": resp.id,
            "name": resp.name,
            "master_id": resp.master_id,
            "is_surface": resp.is_surface,
        }

    @protect_grpc
    def create_sweeping_chain(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import CreateSweepingChainRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateSweepingChainRequest(
            name=kwargs["name"],
            parent=kwargs["parent_id"],
            path=[from_trimmed_curve_to_grpc_trimmed_curve(tc) for tc in kwargs["path"]],
            chain=[from_trimmed_curve_to_grpc_trimmed_curve(tc) for tc in kwargs["chain"]],
        )

        # Call the gRPC service
        resp = self.stub.CreateSweepingChain(request=request)

        # Return the response - formatted as a dictionary
        return {
            "id": resp.id,
            "name": resp.name,
            "master_id": resp.master_id,
            "is_surface": resp.is_surface,
        }

    @protect_grpc
    def sweep_with_guide(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import (
            SweepWithGuideRequest,
            SweepWithGuideRequestData,
        )

        # Create request object - assumes all inputs are valid and of the proper type
        request = SweepWithGuideRequest(
            request_data=[
                SweepWithGuideRequestData(
                    name=sweep_item.name,
                    parent=build_grpc_id(sweep_item.parent_id),
                    plane=from_plane_to_grpc_plane(sweep_item.sketch.plane),
                    geometries=from_sketch_shapes_to_grpc_geometries(
                        sweep_item.sketch.plane,
                        sweep_item.sketch.edges,
                        sweep_item.sketch.faces,
                    ),
                    path=from_trimmed_curve_to_grpc_trimmed_curve(sweep_item.path),
                    guide=from_trimmed_curve_to_grpc_trimmed_curve(sweep_item.guide),
                    tight_tolerance=sweep_item.tight_tolerance,
                )
                for sweep_item in kwargs["sweep_data"]
            ],
        )

        # Call the gRPC service
        resp = self.stub.SweepWithGuide(request=request)

        # Return the response - formatted as a dictionary
        return {
            "bodies": [
                {
                    "id": body.id,
                    "name": body.name,
                    "master_id": body.master_id,
                    "is_surface": body.is_surface,
                }
                for body in resp.bodies
            ]
        }

    @protect_grpc
    def create_extruded_body_from_face_profile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import CreateExtrudedBodyFromFaceProfileRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateExtrudedBodyFromFaceProfileRequest(
            name=kwargs["name"],
            parent=kwargs["parent_id"],
            face=kwargs["face_id"],
            distance=from_measurement_to_server_length(kwargs["distance"]) * kwargs["direction"],
        )

        # Call the gRPC service
        resp = self.stub.CreateExtrudedBodyFromFaceProfile(request=request)

        # Return the response - formatted as a dictionary
        return {
            "id": resp.id,
            "name": resp.name,
            "master_id": resp.master_id,
            "is_surface": resp.is_surface,
        }

    @protect_grpc
    def create_extruded_body_from_loft_profiles(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import CreateExtrudedBodyFromLoftProfilesRequest
        from ansys.api.geometry.v0.models_pb2 import TrimmedCurveList

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateExtrudedBodyFromLoftProfilesRequest(
            name=kwargs["name"],
            parent=kwargs["parent_id"],
            profiles=[
                TrimmedCurveList(
                    curves=[from_trimmed_curve_to_grpc_trimmed_curve(tc) for tc in profile]
                )
                for profile in kwargs["profiles"]
            ],
            periodic=kwargs["periodic"],
            ruled=kwargs["ruled"],
        )

        # Call the gRPC service
        resp = self.stub.CreateExtrudedBodyFromLoftProfiles(request=request)

        # Return the response - formatted as a dictionary
        return {
            "id": resp.id,
            "name": resp.name,
            "master_id": resp.master_id,
            "is_surface": resp.is_surface,
        }

    @protect_grpc
    def create_planar_body(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import CreatePlanarBodyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreatePlanarBodyRequest(
            name=kwargs["name"],
            parent=kwargs["parent_id"],
            plane=from_plane_to_grpc_plane(kwargs["sketch"].plane),
            geometries=from_sketch_shapes_to_grpc_geometries(
                kwargs["sketch"].plane, kwargs["sketch"].edges, kwargs["sketch"].faces
            ),
        )

        # HACK: we should inform the user that NURBS curve sketches are not supported
        # prior to 26R1... and if passed, raise an error
        _nurbs_curves_compatibility(kwargs["backend_version"], request.geometries)

        # Call the gRPC service
        resp = self.stub.CreatePlanarBody(request=request)

        # Return the response - formatted as a dictionary
        return {
            "id": resp.id,
            "name": resp.name,
            "master_id": resp.master_id,
            "is_surface": resp.is_surface,
        }

    @protect_grpc
    def create_body_from_face(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import CreateBodyFromFaceRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateBodyFromFaceRequest(
            name=kwargs["name"],
            parent=kwargs["parent_id"],
            face=kwargs["face_id"],
        )

        # Call the gRPC service
        resp = self.stub.CreateBodyFromFace(request=request)

        # Return the response - formatted as a dictionary
        return {
            "id": resp.id,
            "name": resp.name,
            "master_id": resp.master_id,
            "is_surface": resp.is_surface,
        }

    @protect_grpc
    def create_surface_body(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import CreateSurfaceBodyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateSurfaceBodyRequest(
            name=kwargs["name"],
            parent=kwargs["parent_id"],
            trimmed_surface=from_trimmed_surface_to_grpc_trimmed_surface(kwargs["trimmed_surface"]),
        )

        # Call the gRPC service
        resp = self.stub.CreateSurfaceBody(request=request)

        # Return the response - formatted as a dictionary
        return {
            "id": resp.id,
            "name": resp.name,
            "master_id": resp.master_id,
            "is_surface": resp.is_surface,
        }

    @protect_grpc
    def create_surface_body_from_trimmed_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import CreateSurfaceBodyFromTrimmedCurvesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateSurfaceBodyFromTrimmedCurvesRequest(
            name=kwargs["name"],
            parent=kwargs["parent_id"],
            trimmed_curves=[
                from_trimmed_curve_to_grpc_trimmed_curve(tc) for tc in kwargs["trimmed_curves"]
            ],
        )

        # Call the gRPC service
        resp = self.stub.CreateSurfaceBodyFromTrimmedCurves(request=request)

        # Return the response - formatted as a dictionary
        return {
            "id": resp.id,
            "name": resp.name,
            "master_id": resp.master_id,
            "is_surface": resp.is_surface,
        }

    @protect_grpc
    def translate(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import TranslateRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = TranslateRequest(
            ids=kwargs["ids"],
            direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
            distance=from_measurement_to_server_length(kwargs["distance"]),
        )

        # Call the gRPC service
        self.stub.Translate(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def delete(self, **kwargs) -> dict:  # noqa: D102
        # Call the gRPC service
        self.stub.Delete(request=build_grpc_id(kwargs["id"]))

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def is_suppressed(self, **kwargs) -> dict:  # noqa: D102
        # Call the gRPC service
        resp = self.stub.IsSuppressed(request=build_grpc_id(kwargs["id"]))

        # Return the response - formatted as a dictionary
        return {"result": resp.result}

    @protect_grpc
    def get_color(self, **kwargs) -> dict:  # noqa: D102
        # Call the gRPC service
        resp = self.stub.GetColor(request=build_grpc_id(kwargs["id"]))

        # Return the response - formatted as a dictionary
        return {"color": resp.color}

    @protect_grpc
    def get_faces(self, **kwargs) -> dict:  # noqa: D102
        # Call the gRPC service
        resp = self.stub.GetFaces(request=build_grpc_id(kwargs["id"]))

        # Return the response - formatted as a dictionary
        return {
            "faces": [
                {
                    "id": face.id,
                    "surface_type": face.surface_type,
                    "is_reversed": face.is_reversed,
                }
                for face in resp.faces
            ]
        }

    @protect_grpc
    def get_edges(self, **kwargs) -> dict:  # noqa: D102
        # Call the gRPC service
        resp = self.stub.GetEdges(request=build_grpc_id(kwargs["id"]))

        # Return the response - formatted as a dictionary
        return {
            "edges": [
                {
                    "id": edge.id,
                    "curve_type": edge.curve_type,
                    "is_reversed": edge.is_reversed,
                }
                for edge in resp.edges
            ]
        }

    @protect_grpc
    def get_vertices(self, **kwargs) -> dict:  # noqa: D102
        # Call the gRPC service
        resp = self.stub.GetVertices(request=build_grpc_id(kwargs["id"]))

        # Return the response - formatted as a dictionary
        return {
            "vertices": [
                {
                    "id": vertex.id.id,
                    "position": from_grpc_point_to_point3d(vertex.position),
                }
                for vertex in resp.vertices
            ]
        }

    @protect_grpc
    def get_volume(self, **kwargs) -> dict:  # noqa: D102
        from .conversions import from_grpc_volume_to_volume

        # Call the gRPC service
        resp = self.stub.GetVolume(request=build_grpc_id(kwargs["id"]))

        # Return the response - formatted as a dictionary
        return {"volume": from_grpc_volume_to_volume(resp.volume)}

    @protect_grpc
    def get_bounding_box(self, **kwargs) -> dict:  # noqa: D102
        # Call the gRPC service
        resp = self.stub.GetBoundingBox(request=build_grpc_id(kwargs["id"]))

        # Return the response - formatted as a dictionary
        return {
            "min": from_grpc_point_to_point3d(resp.box.min),
            "max": from_grpc_point_to_point3d(resp.box.max),
            "center": from_grpc_point_to_point3d(resp.box.center),
        }

    @protect_grpc
    def set_assigned_material(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import SetAssignedMaterialRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetAssignedMaterialRequest(id=kwargs["id"], material=kwargs["material"].name)

        # Call the gRPC service
        self.stub.SetAssignedMaterial(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def get_assigned_material(self, **kwargs) -> dict:  # noqa: D102
        # Call the gRPC service
        resp = self.stub.GetAssignedMaterial(request=build_grpc_id(kwargs["id"]))

        # Return the response - formatted as a dictionary
        return {"material": from_grpc_material_to_material(resp)}

    @protect_grpc
    def remove_assigned_material(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import RemoveAssignedMaterialRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = RemoveAssignedMaterialRequest(ids=[build_grpc_id(id) for id in kwargs["ids"]])

        # Call the gRPC service
        resp = self.stub.RemoveAssignedMaterial(request=request)

        # Return the response - formatted as a dictionary
        return {"successfully_removed": [id for id in resp.successfully_removed]}

    @protect_grpc
    def set_name(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import SetNameRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetNameRequest(body_id=kwargs["id"], name=kwargs["name"])

        # Call the gRPC service
        self.stub.SetName(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def set_fill_style(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import SetFillStyleRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetFillStyleRequest(body_id=kwargs["id"], fill_style=kwargs["fill_style"].value)

        # Call the gRPC service
        self.stub.SetFillStyle(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def set_suppressed(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import SetSuppressedRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetSuppressedRequest(
            bodies=[build_grpc_id(body_id) for body_id in kwargs["bodies"]],
            is_suppressed=kwargs["is_suppressed"],
        )

        # Call the gRPC service
        self.stub.SetSuppressed(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def set_color(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import SetColorRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetColorRequest(body_id=kwargs["id"], color=kwargs["color"])

        # Call the gRPC service
        self.stub.SetColor(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def rotate(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import RotateRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = RotateRequest(
            id=kwargs["id"],
            axis_origin=from_point3d_to_grpc_point(kwargs["axis_origin"]),
            axis_direction=from_unit_vector_to_grpc_direction(kwargs["axis_direction"]),
            angle=from_measurement_to_server_angle(kwargs["angle"]),
        )

        # Call the gRPC service
        self.stub.Rotate(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def scale(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import ScaleRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ScaleRequest(
            id=kwargs["id"],
            scale=kwargs["value"],
        )

        # Call the gRPC service
        self.stub.Scale(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def mirror(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import MirrorRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MirrorRequest(
            id=kwargs["id"],
            plane=from_plane_to_grpc_plane(kwargs["plane"]),
        )

        # Call the gRPC service
        self.stub.Mirror(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def map(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import MapRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MapRequest(
            id=kwargs["id"],
            frame=from_frame_to_grpc_frame(kwargs["frame"]),
        )

        # Call the gRPC service
        self.stub.Map(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def get_collision(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import GetCollisionRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = GetCollisionRequest(
            body_1_id=kwargs["id"],
            body_2_id=kwargs["other_id"],
        )

        # Call the gRPC service
        resp = self.stub.GetCollision(request=request)

        # Return the response - formatted as a dictionary
        return {"collision_type": resp.collision}

    @protect_grpc
    def copy(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import CopyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CopyRequest(
            id=kwargs["id"],
            parent=kwargs["parent_id"],
            name=kwargs["name"],
        )

        # Call the gRPC service
        resp = self.stub.Copy(request=request)

        # Return the response - formatted as a dictionary
        return {"master_id": resp.master_id, "name": resp.name}

    @protect_grpc
    def get_tesellation(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import GetTessellationRequest

        tess_map = {}
        resp = []  # For compatibility with stream response
        try:
            resp_single = self.stub.GetTessellation(request=build_grpc_id(kwargs["id"]))
            resp.append(resp_single)
        except grpc.RpcError as err:  # pragma: no cover
            if kwargs["backend_version"] < (25, 2, 0):
                raise err
            request = GetTessellationRequest(id=build_grpc_id(kwargs["id"]))
            resp = self.stub.GetTessellationStream(request=request)

        for elem in resp:
            for face_id, face_tess in elem.face_tessellation.items():
                tess_map[face_id] = (
                    from_grpc_tess_to_raw_data(face_tess)
                    if kwargs["raw_data"]
                    else from_grpc_tess_to_pd(face_tess)
                )

        return {"tessellation": tess_map}

    @protect_grpc
    def get_tesellation_with_options(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import GetTessellationRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = GetTessellationRequest(
            id=build_grpc_id(kwargs["id"]),
            options=from_tess_options_to_grpc_tess_options(kwargs["options"]),
            include_faces=kwargs["include_faces"],
            include_edges=kwargs["include_edges"],
        )

        tess_map = {}
        resp = []  # For compatibility with stream response
        try:
            resp_single = self.stub.GetTessellationWithOptions(request)
            resp.append(resp_single)
        except grpc.RpcError:  # pragma: no cover
            resp = self.stub.GetTessellationStream(request)

        for elem in resp:
            for face_id, face_tess in elem.face_tessellation.items():
                tess_map[face_id] = (
                    from_grpc_tess_to_raw_data(face_tess)
                    if kwargs["raw_data"]
                    else from_grpc_tess_to_pd(face_tess)
                )

        return {"tessellation": tess_map}

    @protect_grpc
    def boolean(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import BooleanRequest

        # Call the gRPC service and build the requests accordingly
        response_success = 0
        serialized_tracker_response = {}
        try:
            request = BooleanRequest(
                body1=kwargs["target"],
                tool_bodies=[other for other in kwargs["other"]],
                method=kwargs["method"],
            )
            if pyansys_geom.USE_TRACKER_TO_UPDATE_DESIGN:
                request.keep_other = kwargs["keep_other"]
            resp = self.stub.Boolean(request=request)
            response_success = resp.empty_result
            if pyansys_geom.USE_TRACKER_TO_UPDATE_DESIGN:
                serialized_tracker_response = serialize_tracker_command_response(
                    response=resp.response
                )
        except grpc.RpcError as err:  # pragma: no cover
            # TODO: to be deleted - old versions did not have "tool_bodies" in the request
            # This is a temporary fix to support old versions of the server - should be deleted
            # once the server is no longer supported.
            # https://github.com/ansys/pyansys-geometry/issues/1319
            if len(kwargs["other"]) > 1:
                all_resp = []
                for body2 in kwargs["other"]:
                    tmp_resp = self.stub.Boolean(
                        request=BooleanRequest(
                            body1=kwargs["target"].id,
                            body2=body2.id,
                            method=kwargs["method"],
                        )
                    ).empty_result
                    all_resp.append(tmp_resp)

                if all_resp.count(1) > 0:
                    response_success = 1
            elif len(kwargs["other"]) == 1:
                resp = self.stub.Boolean(
                    request=BooleanRequest(
                        body1=kwargs["target"].id,
                        body2=kwargs["other"][0].id,
                        method=kwargs["method"],
                    )
                )
                response_success = resp.empty_result
            else:
                raise err

        if response_success == 1:
            raise ValueError(
                f"Boolean operation of type '{kwargs['method']}' failed: {kwargs['err_msg']}.\n"
                f"Involving bodies:{kwargs['target']}, {kwargs['other']}"
            )

        # Return the response - formatted as a dictionary
        return {"complete_command_response": serialized_tracker_response}

    @protect_grpc
    def combine(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import (
            CombineIntersectBodiesRequest,
            CombineMergeBodiesRequest,
        )

        target_body = kwargs["target"]
        other_bodies = kwargs["other"]
        type_bool_op = kwargs["type_bool_op"]
        keep_other = kwargs["keep_other"]
        transfer_named_selections = kwargs["transfer_named_selections"]

        if type_bool_op == "intersect":
            body_ids = [build_grpc_id(body) for body in other_bodies]
            target_ids = [build_grpc_id(target_body)]
            request = CombineIntersectBodiesRequest(
                target_selection=target_ids,
                tool_selection=body_ids,
                subtract_from_target=False,
                keep_cutter=keep_other,
                transfer_named_selections=transfer_named_selections,
            )
            response = self.command_stub.CombineIntersectBodies(request)
        elif type_bool_op == "subtract":
            body_ids = [build_grpc_id(body) for body in other_bodies]
            target_ids = [build_grpc_id(target_body)]
            request = CombineIntersectBodiesRequest(
                target_selection=target_ids,
                tool_selection=body_ids,
                subtract_from_target=True,
                keep_cutter=keep_other,
                transfer_named_selections=transfer_named_selections,
            )
            response = self.command_stub.CombineIntersectBodies(request)
        elif type_bool_op == "unite":
            bodies = [target_body]
            bodies.extend(other_bodies)
            body_ids = [build_grpc_id(body) for body in bodies]
            request = CombineMergeBodiesRequest(target_selection=body_ids)
            response = self.command_stub.CombineMergeBodies(request)
        else:
            raise ValueError("Unknown operation requested")
        if not response.success:
            raise ValueError(
                (
                    f"Operation of type '{type_bool_op}' failed: "
                    f"{kwargs.get('err_msg', 'No error message provided.')}. "
                    f"Involving bodies: {target_body}, {other_bodies}"
                )
            )

        # Return the response - formatted as a dictionary
        return {"complete_command_response": serialize_tracker_command_response(response=response)}

    @protect_grpc
    def split_body(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import SplitBodyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = SplitBodyRequest(
            selection=[build_grpc_id(id) for id in kwargs["body_ids"]],
            split_by_plane=from_plane_to_grpc_plane(kwargs["plane"]) if kwargs["plane"] else None,
            split_by_slicer=[build_grpc_id(id) for id in kwargs["slicer_ids"]],
            split_by_faces=[build_grpc_id(id) for id in kwargs["face_ids"]],
            extend_surfaces=kwargs["extend_surfaces"],
        )

        # Call the gRPC service
        resp = self.command_stub.SplitBody(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": resp.success,
        }

    @protect_grpc
    def create_body_from_loft_profiles_with_guides(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import (
            CreateBodyFromLoftWithGuidesRequest,
            CreateBodyFromLoftWithGuidesRequestData,
        )
        from ansys.api.geometry.v0.models_pb2 import TrimmedCurveList

        # Create request object - assumes all inputs are valid and of the proper type
        request = CreateBodyFromLoftWithGuidesRequest(
            request_data=[
                CreateBodyFromLoftWithGuidesRequestData(
                    name=kwargs["name"],
                    parent=build_grpc_id(kwargs["parent_id"]),
                    profiles=[
                        TrimmedCurveList(
                            curves=[from_trimmed_curve_to_grpc_trimmed_curve(tc) for tc in profile]
                        )
                        for profile in kwargs["profiles"]
                    ],
                    guides=TrimmedCurveList(
                        curves=[
                            from_trimmed_curve_to_grpc_trimmed_curve(tc) for tc in kwargs["guides"]
                        ]
                    ),
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.CreateBodyFromLoftWithGuides(request)

        # Return the response - formatted as a dictionary
        new_body = response.created_bodies[0]
        return {
            "id": new_body.id,
            "name": new_body.name,
            "master_id": new_body.master_id,
            "is_surface": new_body.is_surface,
        }

    @protect_grpc
    def combine_merge(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import CombineMergeBodiesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CombineMergeBodiesRequest(
            target_selection=[build_grpc_id(id) for id in kwargs["body_ids"]],
        )

        # Call the gRPC service
        _ = self.command_stub.CombineMergeBodies(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def assign_midsurface_thickness(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import AssignMidSurfaceThicknessRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = AssignMidSurfaceThicknessRequest(
            bodies_or_faces=kwargs["ids"],
            thickness=from_measurement_to_server_length(kwargs["thickness"]),
        )

        # Call the gRPC service
        self.command_stub.AssignMidSurfaceThickness(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def assign_midsurface_offset(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import AssignMidSurfaceOffsetTypeRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = AssignMidSurfaceOffsetTypeRequest(
            bodies_or_faces=kwargs["ids"],
            offset_type=kwargs["offset_type"].value,
        )

        # Call the gRPC service
        self.command_stub.AssignMidSurfaceOffsetType(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def shell(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import ShellRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ShellRequest(
            selection=build_grpc_id(kwargs["id"]),
            offset=from_measurement_to_server_length(kwargs["offset"]),
        )

        # Call the gRPC service
        response = self.command_stub.Shell(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
        }

    @protect_grpc
    def remove_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import RemoveFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = RemoveFacesRequest(
            selection=[build_grpc_id(id) for id in kwargs["face_ids"]],
            offset=from_measurement_to_server_length(kwargs["offset"]),
        )

        # Call the gRPC service
        response = self.command_stub.RemoveFaces(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
        }

    @protect_grpc
    def imprint_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import ImprintCurvesRequest

        # Convert sketch and trimmed curves to gRPC format
        sketch = kwargs["sketch"]
        curves = None
        if sketch:
            curves = from_sketch_shapes_to_grpc_geometries(sketch.plane, sketch.edges, sketch.faces)

        trimmed_curves = None
        if kwargs["tc"]:
            trimmed_curves = [from_trimmed_curve_to_grpc_trimmed_curve(tc) for tc in kwargs["tc"]]

        # Create the request - assumes all inputs are valid and of the proper type
        request = ImprintCurvesRequest(
            body=kwargs["id"],
            curves=curves,
            faces=kwargs["face_ids"],
            plane=from_plane_to_grpc_plane(sketch.plane) if sketch else None,
            trimmed_curves=trimmed_curves,
        )

        # Call the gRPC service
        response = self.command_stub.ImprintCurves(request=request)

        # Return the response - formatted as a dictionary
        return {
            "edges": [
                {
                    "id": edge.id,
                    "curve_type": edge.curve_type,
                    "is_reversed": edge.is_reversed,
                }
                for edge in response.edges
            ],
            "faces": [
                {
                    "id": face.id,
                    "surface_type": face.surface_type,
                    "is_reversed": face.is_reversed,
                }
                for face in response.faces
            ],
        }

    @protect_grpc
    def project_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import ProjectCurvesRequest

        # Convert sketch and trimmed curves to gRPC format
        sketch = kwargs["sketch"]
        curves = from_sketch_shapes_to_grpc_geometries(
            sketch.plane, sketch.edges, sketch.faces, kwargs["only_one_curve"]
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = ProjectCurvesRequest(
            body=kwargs["id"],
            curves=curves,
            direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
            closest_face=kwargs["closest_face"],
            plane=from_plane_to_grpc_plane(sketch.plane),
        )

        # Call the gRPC service
        response = self.command_stub.ProjectCurves(request=request)

        # Return the response - formatted as a dictionary
        return {
            "faces": [
                {
                    "id": face.id,
                    "surface_type": face.surface_type,
                    "is_reversed": face.is_reversed,
                }
                for face in response.faces
            ],
        }

    @protect_grpc
    def imprint_projected_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import ProjectCurvesRequest

        # Convert sketch and trimmed curves to gRPC format
        sketch = kwargs["sketch"]
        curves = from_sketch_shapes_to_grpc_geometries(
            sketch.plane, sketch.edges, sketch.faces, kwargs["only_one_curve"]
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = ProjectCurvesRequest(
            body=kwargs["id"],
            curves=curves,
            direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
            closest_face=kwargs["closest_face"],
            plane=from_plane_to_grpc_plane(sketch.plane),
        )

        # Call the gRPC service
        response = self.command_stub.ImprintProjectedCurves(request=request)

        # Return the response - formatted as a dictionary
        return {
            "faces": [
                {
                    "id": face.id,
                    "surface_type": face.surface_type,
                    "is_reversed": face.is_reversed,
                }
                for face in response.faces
            ],
        }

    @protect_grpc
    def get_full_tessellation(self, **kwargs):  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import (
            GetFullTessellationRequest,
            GetFullTessellationRequestData,
            GetTessellationRequest,
        )

        from .conversions import (
            from_grpc_edge_tess_to_pd,
            from_grpc_edge_tess_to_raw_data,
        )

        # Create options
        options = kwargs["options"] if kwargs["options"] else None

        # Create the request - assumes all inputs are valid and of the proper type
        request = GetFullTessellationRequest(
            request_data=[
                GetFullTessellationRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    options=from_tess_options_to_grpc_tess_options(options) if options else None,
                    include_faces=kwargs["include_faces"],
                    include_edges=kwargs["include_edges"],
                )
            ]
        )

        # Call the gRPC service
        resp = []  # For compatibility with stream response
        try:
            resp_single = self.stub.GetFullTessellation(request).response_data[0]
            resp.append(resp_single)
        except grpc.RpcError:  # pragma: no cover
            request = GetTessellationRequest(
                id=build_grpc_id(kwargs["id"]),
                options=from_tess_options_to_grpc_tess_options(options) if options else None,
                include_faces=kwargs["include_faces"],
                include_edges=kwargs["include_edges"],
            )
            resp = self.stub.GetTessellationStream(request)

        # Return the response - formatted as a dictionary
        tess_map = {}
        for elem in resp:
            for face_id, face_tess in elem.face_tessellation.items():
                tess_map[face_id] = (
                    from_grpc_tess_to_raw_data(face_tess)
                    if kwargs["raw_data"]
                    else from_grpc_tess_to_pd(face_tess)
                )
            for edge_id, edge_tess in elem.edge_tessellation.items():
                tess_map[edge_id] = (
                    from_grpc_edge_tess_to_raw_data(edge_tess)
                    if kwargs["raw_data"]
                    else from_grpc_edge_tess_to_pd(edge_tess)
                )

        return {"tessellation": tess_map}
