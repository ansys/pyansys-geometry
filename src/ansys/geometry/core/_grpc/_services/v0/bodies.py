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

from ansys.geometry.core.errors import protect_grpc

from ..base.bodies import GRPCBodyService
from ..base.conversions import from_measurement_to_server_length
from ..base.misc import verify_input_keys
from .conversions import from_point3d_to_grpc_point, from_unit_vector_to_grpc_direction


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
    def __init__(self, channel: grpc.Channel):
        """Initialize the BodyService with the gRPC stub."""
        from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub

        self.stub = BodiesStub(channel)

    @protect_grpc
    def create_sphere_body(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import CreateSphereBodyRequest

        # Ensure all inputs are passed
        verify_input_keys(kwargs, ["name", "parent", "center", "radius"])

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
        }

    @protect_grpc
    def create_extruded_body(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def create_sweeping_profile_body(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def create_sweeping_chain(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def create_extruded_body_from_face_profile(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def create_extruded_body_from_loft_profiles(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def create_planar_body(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def create_body_from_face(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def create_surface_body(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def create_surface_body_from_trimmed_curves(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def translate(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.bodies_pb2 import TranslateRequest

        # Ensure all inputs are passed
        verify_input_keys(kwargs, ["ids", "direction", "distance"])

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
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier

        # Ensure all inputs are passed
        verify_input_keys(kwargs, ["id"])

        # Create the request - assumes all inputs are valid and of the proper type
        request = EntityIdentifier(id=kwargs["id"])

        # Call the gRPC service
        self.stub.Delete(request=request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def is_suppressed(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def get_color(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def get_faces(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def get_edges(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def get_volume(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def get_bounding_box(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def set_assigned_material(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def get_assigned_material(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def set_name(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def set_fill_style(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def set_color(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def rotate(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def scale(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def mirror(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def map(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def get_collision(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def copy(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def get_tesellation(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def boolean(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError
