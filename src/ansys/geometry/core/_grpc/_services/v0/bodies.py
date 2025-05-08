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
import pint

from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS

from ..base.bodies import GRPCBodyService
from ..base.conversions import from_measurement_to_server_angle, from_measurement_to_server_length
from .conversions import (
    build_grpc_id,
    from_frame_to_grpc_frame,
    from_grpc_material_to_material,
    from_grpc_point_to_point3d,
    from_grpc_tess_to_pd,
    from_plane_to_grpc_plane,
    from_point3d_to_grpc_point,
    from_sketch_shapes_to_grpc_geometries,
    from_tess_options_to_grpc_tess_options,
    from_trimmed_curve_to_grpc_trimmed_curve,
    from_trimmed_surface_to_grpc_trimmed_surface,
    from_unit_vector_to_grpc_direction,
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

        self.stub = BodiesStub(channel)

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
    def get_volume(self, **kwargs) -> dict:  # noqa: D102
        # Call the gRPC service
        resp = self.stub.GetVolume(request=build_grpc_id(kwargs["id"]))

        # Return the response - formatted as a dictionary
        return {"volume": pint.Quantity(resp.volume, DEFAULT_UNITS.SERVER_VOLUME)}

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
                tess_map[face_id] = from_grpc_tess_to_pd(face_tess)

        return {"tessellation": tess_map}

    @protect_grpc
    def get_tesellation_with_options(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import GetTessellationRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = GetTessellationRequest(
            id=build_grpc_id(kwargs["id"]),
            options=from_tess_options_to_grpc_tess_options(kwargs["options"]),
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
                tess_map[face_id] = from_grpc_tess_to_pd(face_tess)

        return {"tessellation": tess_map}

    @protect_grpc
    def boolean(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import BooleanRequest

        # Call the gRPC service and build the requests accordingly
        resp = 0
        try:
            resp = self.stub.Boolean(
                request=BooleanRequest(
                    body1=kwargs["target"].id,
                    tool_bodies=[other.id for other in kwargs["other"]],
                    method=kwargs["method"],
                )
            ).empty_result
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
                    resp = 1
            elif len(kwargs["other"]) == 1:
                resp = self.stub.Boolean(
                    request=BooleanRequest(
                        body1=kwargs["target"].id,
                        body2=kwargs["other"][0].id,
                        method=kwargs["method"],
                    )
                ).empty_result
            else:
                raise err

        if resp == 1:
            raise ValueError(
                f"Boolean operation of type '{kwargs['method']}' failed: {kwargs['err_msg']}.\n"
                f"Involving bodies:{kwargs['target']}, {kwargs['other']}"
            )

        # Return the response - formatted as a dictionary
        return {}
