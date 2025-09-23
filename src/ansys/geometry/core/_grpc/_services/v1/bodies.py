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

from ..base.bodies import GRPCBodyService


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
        from ansys.api.geometry.v1.bodies_pb2_grpc import BodiesStub

        self.stub = BodiesStub(channel)

    @protect_grpc
    def create_sphere_body(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

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
    def sweep_with_guide(self, **kwargs) -> dict:  # noqa: D102
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
        raise NotImplementedError

    @protect_grpc
    def delete(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

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
    def get_vertices(self, **kwargs) -> dict:  # noqa: D102
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
    def remove_assigned_material(self, **kwargs):  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def set_name(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def set_fill_style(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def set_suppressed(self, **kwargs) -> dict:  # noqa: D102
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
    def get_tesellation_with_options(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def boolean(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def combine(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError
