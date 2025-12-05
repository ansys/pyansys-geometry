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
"""Module containing the bodies service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.misc.measurements import Distance

from ..base.bodies import GRPCBodyService
from ..base.conversions import from_measurement_to_server_length
from .conversions import (
    build_grpc_id,
    from_frame_to_grpc_frame,
    from_grpc_point_to_point3d,
    from_grpc_tess_to_pd,
    from_grpc_tess_to_raw_data,
    from_length_to_grpc_quantity,
    from_plane_to_grpc_plane,
    from_point3d_to_grpc_point,
    from_sketch_shapes_to_grpc_geometries,
    from_tess_options_to_grpc_tess_options,
    from_trimmed_curve_to_grpc_trimmed_curve,
    from_unit_vector_to_grpc_direction,
)


class GRPCBodyServiceV1(GRPCBodyService):  # pragma: no cover
    """Body service for gRPC communication with the Geometry server.

    This class provides methods to create and manipulate bodies in the
    Geometry server using gRPC. It is specifically designed for the v1
    version of the Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):
        """Initialize the BodyService with the gRPC stub."""
        from ansys.api.discovery.v1.design.geometry.body_pb2_grpc import BodyStub
        from ansys.api.discovery.v1.design.geometry.face_pb2_grpc import FaceStub
        from ansys.api.discovery.v1.operations.edit_pb2_grpc import EditStub

        self.stub = BodyStub(channel)
        self.edit_stub = EditStub(channel)
        self.face_stub = FaceStub(channel)

    @protect_grpc
    def create_sphere_body(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            CreateSphereBodyRequest,
            CreateSphereBodyRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateSphereBodyRequest(
            request_data=[
                CreateSphereBodyRequestData(
                    name=kwargs["name"],
                    parent_id=build_grpc_id(kwargs["parent"]),
                    center=from_point3d_to_grpc_point(kwargs["center"]),
                    radius=from_length_to_grpc_quantity(kwargs["radius"]),
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreateSphereBody(request=request)

        # Return the response - formatted as a dictionary
        # Note: response.bodies is a repeated field, we return the first one
        body = resp.bodies[0]
        return {
            "id": body.id.id,
            "name": body.name,
            "master_id": body.master_id.id,
            "is_surface": body.is_surface,
        }

    @protect_grpc
    def create_extruded_body(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            CreateExtrudedBodyRequest,
            CreateExtrudedBodyRequestData,
        )

        # Apply direction (can be 1 or -1) to distance
        # distance_value = kwargs["distance"].value * kwargs["direction"]
        # distance=from_measurement_to_server_length(kwargs["distance"]) * kwargs["direction"],
        distance = Distance(kwargs["distance"].value * kwargs["direction"], kwargs["distance"].unit)

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateExtrudedBodyRequest(
            request_data=[
                CreateExtrudedBodyRequestData(
                    name=kwargs["name"],
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    plane=from_plane_to_grpc_plane(kwargs["sketch"].plane),
                    geometries=from_sketch_shapes_to_grpc_geometries(
                        kwargs["sketch"].plane, kwargs["sketch"].edges, kwargs["sketch"].faces
                    ),
                    distance=from_length_to_grpc_quantity(distance),
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreateExtrudedBody(request=request)

        # Return the response - formatted as a dictionary
        body = resp.bodies[0]
        return {
            "id": body.id.id,
            "name": body.name,
            "master_id": body.master_id.id,
            "is_surface": body.is_surface,
        }

    @protect_grpc
    def create_sweeping_profile_body(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            CreateSweepingProfileRequest,
            CreateSweepingProfileRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateSweepingProfileRequest(
            request_data=[
                CreateSweepingProfileRequestData(
                    name=kwargs["name"],
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    plane=from_plane_to_grpc_plane(kwargs["sketch"].plane),
                    geometries=from_sketch_shapes_to_grpc_geometries(
                        kwargs["sketch"].plane, kwargs["sketch"].edges, kwargs["sketch"].faces
                    ),
                    path=[from_trimmed_curve_to_grpc_trimmed_curve(tc) for tc in kwargs["path"]],
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreateSweepingProfile(request=request)

        # Return the response - formatted as a dictionary
        body = resp.bodies[0]
        return {
            "id": body.id.id,
            "name": body.name,
            "master_id": body.master_id.id,
            "is_surface": body.is_surface,
        }

    @protect_grpc
    def create_sweeping_chain(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            CreateSweepingChainRequest,
            CreateSweepingChainRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateSweepingChainRequest(
            request_data=[
                CreateSweepingChainRequestData(
                    name=kwargs["name"],
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    chain=[from_trimmed_curve_to_grpc_trimmed_curve(tc) for tc in kwargs["chain"]],
                    path=[from_trimmed_curve_to_grpc_trimmed_curve(tc) for tc in kwargs["path"]],
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreateSweepingChain(request=request)

        # Return the response - formatted as a dictionary
        body = resp.bodies[0]
        return {
            "id": body.id.id,
            "name": body.name,
            "master_id": body.master_id.id,
            "is_surface": body.is_surface,
        }

    @protect_grpc
    def sweep_with_guide(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            SweepWithGuideRequest,
            SweepWithGuideRequestData,
        )

        # Create request object - assumes all inputs are valid and of the proper type
        request = SweepWithGuideRequest(
            request_data=[
                SweepWithGuideRequestData(
                    name=sweep_item.name,
                    parent_id=build_grpc_id(sweep_item.parent_id),
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
        resp = self.edit_stub.SweepWithGuide(request=request)

        # Return the response - formatted as a dictionary
        return {
            "bodies": [
                {
                    "id": body.id.id,
                    "name": body.name,
                    "master_id": body.master_id.id,
                    "is_surface": body.is_surface,
                }
                for body in resp.bodies
            ]
        }

    @protect_grpc
    def create_extruded_body_from_face_profile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            CreateExtrudedBodyFromFaceProfileRequest,
            CreateExtrudedBodyFromFaceProfileRequestData,
        )

        # Apply direction (can be 1 or -1) to distance
        # distance_value = kwargs["distance"].value * kwargs["direction"]
        distance = Distance(kwargs["distance"].value * kwargs["direction"], kwargs["distance"].unit)
        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateExtrudedBodyFromFaceProfileRequest(
            request_data=[
                CreateExtrudedBodyFromFaceProfileRequestData(
                    name=kwargs["name"],
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    face_id=build_grpc_id(kwargs["face_id"]),
                    distance=from_length_to_grpc_quantity(distance),
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreateExtrudedBodyFromFaceProfile(request=request)

        # Return the response - formatted as a dictionary
        body = resp.bodies[0]
        return {
            "id": body.id.id,
            "name": body.name,
            "master_id": body.master_id.id,
            "is_surface": body.is_surface,
        }

    @protect_grpc
    def create_extruded_body_from_loft_profiles(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.designmessages_pb2 import TrimmedCurveList
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            CreateExtrudedBodyFromLoftProfilesRequest,
            CreateExtrudedBodyFromLoftProfilesRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateExtrudedBodyFromLoftProfilesRequest(
            request_data=[
                CreateExtrudedBodyFromLoftProfilesRequestData(
                    name=kwargs["name"],
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    profiles=[
                        TrimmedCurveList(
                            curves=[from_trimmed_curve_to_grpc_trimmed_curve(tc) for tc in profile]
                        )
                        for profile in kwargs["profiles"]
                    ],
                    periodic=kwargs["periodic"],
                    ruled=kwargs["ruled"],
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreateExtrudedBodyFromLoftProfiles(request=request)

        # Return the response - formatted as a dictionary
        body = resp.bodies[0]
        return {
            "id": body.id.id,
            "name": body.name,
            "master_id": body.master_id.id,
            "is_surface": body.is_surface,
        }

    @protect_grpc
    def create_planar_body(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            CreatePlanarBodyRequest,
            CreatePlanarBodyRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreatePlanarBodyRequest(
            request_data=[
                CreatePlanarBodyRequestData(
                    name=kwargs["name"],
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    plane=from_plane_to_grpc_plane(kwargs["sketch"].plane),
                    geometries=from_sketch_shapes_to_grpc_geometries(
                        kwargs["sketch"].plane, kwargs["sketch"].edges, kwargs["sketch"].faces
                    ),
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreatePlanarBody(request=request)

        # Return the response - formatted as a dictionary
        body = resp.bodies[0]
        return {
            "id": body.id.id,
            "name": body.name,
            "master_id": body.master_id.id,
            "is_surface": body.is_surface,
        }

    @protect_grpc
    def create_body_from_face(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            CreateBodyFromFaceRequest,
            CreateBodyFromFaceRequestData,
        )

        # Create the request with inline request_data
        request = CreateBodyFromFaceRequest(
            request_data=[
                CreateBodyFromFaceRequestData(
                    name=kwargs["name"],
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    face_id=build_grpc_id(kwargs["face_id"]),
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreateFromFace(request=request)

        # Return the response - formatted as a dictionary
        body = resp.bodies[0]
        return {
            "id": body.id.id,
            "name": body.name,
            "master_id": body.master_id.id,
            "is_surface": body.is_surface,
        }

    @protect_grpc
    def create_surface_body(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            CreateSurfaceBodyRequest,
            CreateSurfaceBodyRequestData,
        )

        from ansys.geometry.core._grpc._services.v1.conversions import (
            from_trimmed_surface_to_grpc_trimmed_surface,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateSurfaceBodyRequest(
            request_data=[
                CreateSurfaceBodyRequestData(
                    name=kwargs["name"],
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    trimmed_surface=from_trimmed_surface_to_grpc_trimmed_surface(
                        kwargs["trimmed_surface"]
                    ),
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreateSurfaceBody(request=request)

        # Return the response - formatted as a dictionary
        body = resp.bodies[0]
        return {
            "id": body.id.id,
            "name": body.name,
            "master_id": body.master_id.id,
            "is_surface": body.is_surface,
        }

    @protect_grpc
    def create_surface_body_from_trimmed_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            CreateSurfaceBodyFromTrimmedCurvesRequest,
            CreateSurfaceBodyFromTrimmedCurvesRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateSurfaceBodyFromTrimmedCurvesRequest(
            request_data=[
                CreateSurfaceBodyFromTrimmedCurvesRequestData(
                    name=kwargs["name"],
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    trimmed_curves=[
                        from_trimmed_curve_to_grpc_trimmed_curve(tc)
                        for tc in kwargs["trimmed_curves"]
                    ],
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreateSurfaceBodyFromTrimmedCurves(request=request)

        # Return the response - formatted as a dictionary
        body = resp.bodies[0]
        return {
            "id": body.id.id,
            "name": body.name,
            "master_id": body.master_id.id,
            "is_surface": body.is_surface,
        }

    @protect_grpc
    def translate(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            MoveTranslateRequest,
            MoveTranslateRequestData,
        )

        # Create the request with selection_ids, direction, and distance
        request = MoveTranslateRequest(
            request_data=[
                MoveTranslateRequestData(
                    selection_ids=[build_grpc_id(body_id) for body_id in kwargs["ids"]],
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    distance=from_length_to_grpc_quantity(kwargs["distance"]),
                )
            ]
        )

        # Call the gRPC service
        self.edit_stub.MoveTranslate(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def delete(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        # Create the request with MultipleEntitiesRequest
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        self.stub.Delete(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def is_suppressed(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        # Create the request with MultipleEntitiesRequest
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        resp = self.stub.GetIsSuppressed(request=request)

        # Return the response - formatted as a dictionary (get first value from map)
        result = next(iter(resp.result.values())) if resp.result else False
        return {"result": result}

    @protect_grpc
    def get_color(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import (
            MultipleEntitiesRequest,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        resp = self.stub.GetColor(request=request)

        # Return the response - formatted as a dictionary (get first color from map)
        color = next(iter(resp.colors.values())) if resp.colors else None
        return {"color": color}

    @protect_grpc
    def set_color(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.designmessages_pb2 import (
            SetColorRequest,
            SetColorRequestData,
        )

        # Create the request with repeated request_data
        request = SetColorRequest(
            request_data=[
                SetColorRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    color=kwargs["color"],
                )
            ]
        )

        # Call the gRPC service
        self.stub.SetColor(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def get_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        # Create the request with MultipleEntitiesRequest
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        resp = self.stub.GetFaces(request=request)

        # Get the first response data from the array
        response_data = resp.response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "faces": [
                {
                    "id": face.id.id,
                    "surface_type": face.surface_type,
                    "is_reversed": face.is_reversed,
                }
                for face in response_data.faces
            ]
        }

    @protect_grpc
    def get_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        # Create the request with MultipleEntitiesRequest
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        resp = self.stub.GetEdges(request=request)

        # Get the first response data from the array
        response_data = resp.response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "edges": [
                {
                    "id": edge.id.id,
                    "curve_type": edge.curve_type,
                    "is_reversed": edge.is_reversed,
                }
                for edge in response_data.edges
            ]
        }

    @protect_grpc
    def get_vertices(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        # Create the request with MultipleEntitiesRequest
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        resp = self.stub.GetVertices(request=request)

        # Get the first response data from the array
        response_data = resp.response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "vertices": [
                {
                    "id": vertex.id.id,
                    "position": from_grpc_point_to_point3d(vertex.position),
                }
                for vertex in response_data.vertices
            ]
        }

    @protect_grpc
    def get_volume(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        from .conversions import from_grpc_volume_to_volume

        # Create the request with MultipleEntitiesRequest
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        resp = self.stub.GetVolume(request=request)

        # Get the first response data from the array
        response_data = resp.response_data[0]

        # Return the response - formatted as a dictionary
        return {"volume": from_grpc_volume_to_volume(response_data.volume)}

    @protect_grpc
    def get_bounding_box(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import (
            MultipleEntitiesRequest,
        )

        # Create the request with MultipleEntitiesRequest
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        resp = self.stub.GetBoundingBox(request=request)

        # Get the first bounding box from the response array
        resp = resp.response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "min": from_grpc_point_to_point3d(resp.box.min),
            "max": from_grpc_point_to_point3d(resp.box.max),
            "center": from_grpc_point_to_point3d(resp.box.center),
        }

    @protect_grpc
    def set_assigned_material(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            SetAssignedCADMaterialRequest,
            SetAssignedCADMaterialRequestData,
        )

        from ansys.geometry.core._grpc._services.v1.conversions import (
            from_material_to_grpc_material,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetAssignedCADMaterialRequest(
            request_data=[
                SetAssignedCADMaterialRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    material=from_material_to_grpc_material(kwargs["material"]),
                )
            ]
        )

        # Call the gRPC service
        self.stub.SetAssignedCADMaterial(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def get_assigned_material(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest
        from ansys.api.discovery.v1.design.designmessages_pb2 import MaterialEntity

        from ansys.geometry.core._grpc._services.v1.conversions import (
            from_grpc_material_to_material,
        )

        # Create the request with MultipleEntitiesRequest
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        resp = self.stub.GetAssignedCADMaterial(request=request)

        # Return the response - formatted as a dictionary
        # Get the first response data from the array
        response_data = resp.response_data[0] if resp.response_data else None
        grpc_material = (
            response_data.material
            if response_data and response_data.HasField("material")
            else MaterialEntity()
        )
        return {"material": from_grpc_material_to_material(grpc_material)}

    @protect_grpc
    def remove_assigned_material(self, **kwargs):  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            RemoveAssignedCADMaterialRequest,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = RemoveAssignedCADMaterialRequest(ids=[build_grpc_id(id) for id in kwargs["ids"]])

        # Call the gRPC service
        resp = self.stub.RemoveAssignedCADMaterial(request=request)

        # Return the response - formatted as a dictionary
        return {"successfully_removed": [id.id for id in resp.successfully_removed_ids]}

    @protect_grpc
    def set_name(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.designmessages_pb2 import (
            SetDesignEntityNameRequest,
            SetDesignEntityNameRequestData,
        )

        # Create the request with repeated request_data
        request = SetDesignEntityNameRequest(
            request_data=[
                SetDesignEntityNameRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    name=kwargs["name"],
                )
            ]
        )

        # Call the gRPC service
        self.stub.SetName(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def set_fill_style(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            SetFillStyleRequest,
            SetFillStyleRequestData,
        )

        # Create the request with request_data
        request = SetFillStyleRequest(
            request_data=[
                SetFillStyleRequestData(
                    id=build_grpc_id(kwargs["id"]), fill_style=kwargs["fill_style"].value
                )
            ]
        )

        # Call the gRPC service
        self.stub.SetFillStyle(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def set_suppressed(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import SetSuppressedRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetSuppressedRequest(
            body_ids=[build_grpc_id(body_id) for body_id in kwargs["bodies"]],
            is_suppressed=kwargs["is_suppressed"],
        )

        # Call the gRPC service
        self.stub.SetSuppressed(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def rotate(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            MoveRotateRequest,
            MoveRotateRequestData,
        )

        from ansys.geometry.core.shapes.curves.line import Line

        from .conversions import from_angle_to_grpc_quantity, from_line_to_grpc_line

        # Create a Line from axis_origin and axis_direction
        axis = Line(kwargs["axis_origin"], kwargs["axis_direction"])

        # Create the request with selection_ids, axis, and angle
        request = MoveRotateRequest(
            request_data=[
                MoveRotateRequestData(
                    selection_ids=[build_grpc_id(kwargs["id"])],
                    axis=from_line_to_grpc_line(axis),
                    angle=from_angle_to_grpc_quantity(kwargs["angle"]),
                )
            ]
        )

        # Call the gRPC service
        self.edit_stub.MoveRotate(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def scale(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import ScaleRequest, ScaleRequestData

        # Create the request with inline request_data
        request = ScaleRequest(
            request_data=[
                ScaleRequestData(
                    object_ids=[build_grpc_id(kwargs["id"])],
                    scale=kwargs["value"],
                )
            ]
        )

        # Call the gRPC service
        self.edit_stub.Scale(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def mirror(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import MirrorRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MirrorRequest(
            selection_ids=[build_grpc_id(kwargs["id"])],
            plane=from_plane_to_grpc_plane(kwargs["plane"]),
        )

        # Call the gRPC service
        self.edit_stub.Mirror(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def map(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import MapRequest, MapRequestData

        # Create the request - assumes all inputs are valid and of the proper type
        request = MapRequest(
            request_data=[
                MapRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    frame=from_frame_to_grpc_frame(kwargs["frame"]),
                )
            ]
        )

        # Call the gRPC service
        self.edit_stub.MapBody(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def get_collision(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            GetCollisionRequest,
            GetCollisionRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = GetCollisionRequest(
            request_data=[
                GetCollisionRequestData(
                    body_1_id=build_grpc_id(kwargs["id"]),
                    body_2_id=build_grpc_id(kwargs["other_id"]),
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.GetCollision(request=request)

        # Return the response - formatted as a dictionary
        return {"collision_type": resp.response_data[0].collision}

    @protect_grpc
    def copy(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            CreateDuplicateBodyRequest,
            DuplicateBodyRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateDuplicateBodyRequest(
            request_data=[
                DuplicateBodyRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    parent=build_grpc_id(kwargs["parent_id"]),
                    name=kwargs["name"],
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreateDuplicate(request=request)

        # Return the response - formatted as a dictionary
        response_data = resp.response_data[0]
        body = response_data.body
        return {"id": body.id.id, "master_id": body.master_id.id, "name": body.name}

    @protect_grpc
    def get_tesellation(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            GetTessellationRequest,
            GetTessellationRequestData,
        )

        tess_map = {}
        resp = []  # For compatibility with stream response
        try:
            request = GetTessellationRequest(
                request_data=[GetTessellationRequestData(id=build_grpc_id(kwargs["id"]))]
            )
            resp = [self.stub.GetTessellation(request=request)]
        except grpc.RpcError:
            request = GetTessellationRequest(
                request_data=[GetTessellationRequestData(id=build_grpc_id(kwargs["id"]))]
            )
            resp = self.stub.GetTessellation(request=request)

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
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            GetTessellationRequest,
            GetTessellationRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = GetTessellationRequest(
            request_data=[
                GetTessellationRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    options=from_tess_options_to_grpc_tess_options(kwargs["options"]),
                    include_faces=kwargs["include_faces"],
                    include_edges=kwargs["include_edges"],
                )
            ]
        )

        tess_map = {}
        resp = []  # For compatibility with stream response
        try:
            resp = [self.stub.GetTessellation(request=request)]
        except grpc.RpcError:
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
    def boolean(self, **kwargs) -> dict:  # noqa: D102
        # v1 uses the combine method instead of a separate boolean method
        # Map the v0 parameters to v1 combine parameters
        return self.combine(
            target=kwargs["target"],
            other=kwargs["other"],
            type_bool_op=kwargs["method"],
            keep_other=kwargs["keep_other"],
            transfer_named_selections=False,
        )

    @protect_grpc
    def combine(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            CombineIntersectBodiesRequest,
            CombineIntersectBodiesRequestData,
            CombineMergeBodiesRequest,
            CombineMergeBodiesRequestData,
        )

        target_body = kwargs["target"]
        other_bodies = kwargs["other"]
        type_bool_op = kwargs["type_bool_op"]
        keep_other = kwargs["keep_other"]
        transfer_named_selections = kwargs.get("transfer_named_selections", False)

        if type_bool_op == "intersect":
            request_data = CombineIntersectBodiesRequestData(
                target_selection_ids=[build_grpc_id(target_body)],
                tool_selection_ids=[build_grpc_id(body) for body in other_bodies],
                keep_cutter=keep_other,
                subtract_from_target=False,
                transfer_named_selections=transfer_named_selections,
            )
            request = CombineIntersectBodiesRequest(request_data=[request_data])
            response = self.edit_stub.CombineIntersectBodies(request=request)
        elif type_bool_op == "subtract":
            request_data = CombineIntersectBodiesRequestData(
                target_selection_ids=[build_grpc_id(target_body)],
                tool_selection_ids=[build_grpc_id(body) for body in other_bodies],
                keep_cutter=keep_other,
                subtract_from_target=True,
                transfer_named_selections=transfer_named_selections,
            )
            request = CombineIntersectBodiesRequest(request_data=[request_data])
            response = self.edit_stub.CombineIntersectBodies(request=request)
        elif type_bool_op == "unite":
            # Create request data with all body IDs
            all_body_ids = [build_grpc_id(target_body)]
            all_body_ids.extend([build_grpc_id(body) for body in other_bodies])

            request_data = CombineMergeBodiesRequestData(target_selection_ids=all_body_ids)
            request = CombineMergeBodiesRequest(request_data=[request_data])
            response = self.edit_stub.CombineMergeBodies(request=request)
        else:
            raise ValueError(f"Invalid boolean operation type: {type_bool_op}")

        if not response.success:
            raise ValueError(f"Boolean operation failed: {response}")

        # Return the response - formatted as a dictionary
        return {"complete_command_response": response}

    @protect_grpc
    def split_body(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import SplitBodyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = SplitBodyRequest(
            selection=[build_grpc_id(id) for id in kwargs["body_ids"]],
            split_by_plane=from_plane_to_grpc_plane(kwargs["plane"]) if kwargs["plane"] else None,
            split_by_slicer=[build_grpc_id(id) for id in kwargs["slicer_ids"]],
            split_by_faces=[build_grpc_id(id) for id in kwargs["face_ids"]],
            extend_surfaces=kwargs["extend_surfaces"],
        )

        # Call the gRPC service
        resp = self.edit_stub.SplitBodies(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": resp.success,
        }

    @protect_grpc
    def create_body_from_loft_profiles_with_guides(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.designmessages_pb2 import TrimmedCurveList
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            CreateBodyFromLoftWithGuidesRequest,
            CreateBodyFromLoftWithGuidesRequestData,
        )

        # Create request object - assumes all inputs are valid and of the proper type
        request = CreateBodyFromLoftWithGuidesRequest(
            request_data=[
                CreateBodyFromLoftWithGuidesRequestData(
                    name=kwargs["name"],
                    parent_id=build_grpc_id(kwargs["parent_id"]),
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
        response = self.stub.CreateFromLoftWithGuides(request)

        # Return the response - formatted as a dictionary
        new_body = response.created_bodies[0]
        return {
            "id": new_body.id.id,
            "name": new_body.name,
            "master_id": new_body.master_id.id,
            "is_surface": new_body.is_surface,
        }

    @protect_grpc
    def combine_merge(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            CombineMergeBodiesRequest,
            CombineMergeBodiesRequestData,
        )

        # Create the request with inline request_data
        request = CombineMergeBodiesRequest(
            request_data=[
                CombineMergeBodiesRequestData(
                    target_selection_ids=[build_grpc_id(body_id) for body_id in kwargs["body_ids"]]
                )
            ]
        )

        # Call the gRPC service
        _ = self.edit_stub.CombineMergeBodies(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def assign_midsurface_thickness(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            SetMidSurfaceThicknessRequest,
            SetMidSurfaceThicknessRequestData,
        )

        request = SetMidSurfaceThicknessRequest(
            request_data=[
                SetMidSurfaceThicknessRequestData(
                    ids=[build_grpc_id(id) for id in kwargs["ids"]],
                    thickness=from_measurement_to_server_length(kwargs["thickness"]),
                )
            ]
        )

        _ = self.stub.SetMidSurfaceThickness(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def assign_midsurface_offset(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            SetMidSurfaceOffsetTypeRequest,
            SetMidSurfaceOffsetTypeRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetMidSurfaceOffsetTypeRequest(
            request_data=[
                SetMidSurfaceOffsetTypeRequestData(
                    ids=[build_grpc_id(id) for id in kwargs["ids"]],
                    offset_type=kwargs["offset_type"].value,
                )
            ]
        )

        # Call the gRPC service
        _ = self.stub.SetMidSurfaceOffsetType(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def shell(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import ShellRequest, ShellRequestData

        # Create the request with request_data
        request = ShellRequest(
            request_data=[
                ShellRequestData(
                    selection_id=build_grpc_id(kwargs["id"]),
                    offset=from_length_to_grpc_quantity((kwargs["offset"])),
                )
            ]
        )

        # Call the gRPC service
        response = self.edit_stub.Shell(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_command_response.command_response.success,
            "tracked_command_response": response.tracked_command_response,
        }

    @protect_grpc
    def remove_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.face_pb2 import (
            RemoveFacesRequest,
            RemoveFacesRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        offset_quantity = from_length_to_grpc_quantity(kwargs["offset"])
        request_data = RemoveFacesRequestData(
            selection_ids=[build_grpc_id(id) for id in kwargs["face_ids"]],
            offset=offset_quantity,
        )
        request = RemoveFacesRequest(
            request_data=[request_data],
            offset=offset_quantity,
        )

        # Call the gRPC service
        response = self.face_stub.Remove(request=request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_command_response.command_response.success,
            "tracked_command_response": response.tracked_command_response,
        }

    @protect_grpc
    def imprint_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            ImprintCurvesRequest,
            ImprintCurvesRequestData,
        )

        # Convert trimmed curves to gRPC format
        trimmed_curves = []
        if kwargs.get("tc"):
            trimmed_curves = [from_trimmed_curve_to_grpc_trimmed_curve(tc) for tc in kwargs["tc"]]

        # Create the request using request_data pattern
        request = ImprintCurvesRequest(
            request_data=[
                ImprintCurvesRequestData(
                    body_ids=build_grpc_id(kwargs["id"]),
                    face_ids=[build_grpc_id(id) for id in kwargs["face_ids"]],
                    trimmed_curves=trimmed_curves,
                )
            ]
        )

        # Call the gRPC service
        _ = self.edit_stub.ImprintCurves(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def project_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            ProjectCurvesRequest,
            ProjectCurvesRequestData,
        )

        # Convert sketch to geometries
        sketch = kwargs["sketch"]
        curves = from_sketch_shapes_to_grpc_geometries(sketch.plane, sketch.edges, sketch.faces)

        # Create the request using ProjectCurvesRequestData
        request = ProjectCurvesRequest(
            request_data=[
                ProjectCurvesRequestData(
                    body_id=build_grpc_id(kwargs["id"]),
                    curves=curves,
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    closest_face=kwargs["closest_face"],
                    plane=from_plane_to_grpc_plane(sketch.plane),
                )
            ]
        )

        # Call the gRPC service
        resp = self.edit_stub.ProjectCurves(request=request)

        # Return the response - formatted as a dictionary
        return {
            "faces": [
                {
                    "id": face.id.id,
                    "surface_type": face.surface_type,
                    "is_reversed": face.is_reversed,
                }
                for face in resp.response_data[0].faces
            ]
        }

    @protect_grpc
    def imprint_projected_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            ImprintProjectedCurvesRequest,
            ImprintProjectedCurvesRequestData,
        )

        # Convert sketch to geometries
        sketch = kwargs["sketch"]
        curves = from_sketch_shapes_to_grpc_geometries(sketch.plane, sketch.edges, sketch.faces)

        # Create the request using ImprintProjectedCurvesRequestData
        request = ImprintProjectedCurvesRequest(
            request_data=[
                ImprintProjectedCurvesRequestData(
                    body_id=build_grpc_id(kwargs["id"]),
                    curves=curves,
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    closest_face=kwargs["closest_face"],
                    plane=from_plane_to_grpc_plane(sketch.plane),
                )
            ]
        )

        # Call the gRPC service
        resp = self.edit_stub.ImprintProjectedCurves(request=request)

        # Return the response - formatted as a dictionary
        return {
            "faces": [
                {
                    "id": face.id.id,
                    "surface_type": face.surface_type,
                    "is_reversed": face.is_reversed,
                }
                for face in resp.response_data[0].faces
            ]
        }

    @protect_grpc
    def get_full_tessellation(self, **kwargs):  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.body_pb2 import (
            GetTessellationRequest,
            GetTessellationRequestData,
        )

        # Create options
        options = kwargs["options"] if kwargs["options"] else None

        # Create the request - assumes all inputs are valid and of the proper type
        request = GetTessellationRequest(
            request_data=[
                GetTessellationRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    options=from_tess_options_to_grpc_tess_options(options) if options else None,
                    include_faces=kwargs["include_faces"],
                    include_edges=kwargs["include_edges"],
                )
            ]
        )

        # Call the gRPC service - using streaming
        resp = self.stub.GetTessellationStream(request=request)

        # Return the response - formatted as a dictionary
        return {"tessellation": from_grpc_tess_to_pd(resp)}
