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
"""Module containing the bodies service implementation (abstraction layer)."""

from abc import ABC, abstractmethod

import grpc


class GRPCBodyService(ABC):
    """Body service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the BodyServiceBase class."""
        pass

    @abstractmethod
    def create_sphere_body(self, **kwargs) -> dict:
        """Create a sphere body."""
        raise NotImplementedError("create_sphere_body method not implemented")

    @abstractmethod
    def create_extruded_body(self, **kwargs) -> dict:
        """Create an extruded body."""
        raise NotImplementedError("create_extruded_body method not implemented")

    @abstractmethod
    def create_sweeping_profile_body(self, **kwargs) -> dict:
        """Create a sweeping profile body."""
        raise NotImplementedError("create_sweeping_profile_body method not implemented")

    @abstractmethod
    def create_sweeping_chain(self, **kwargs) -> dict:
        """Create a sweeping chain."""
        raise NotImplementedError("create_sweeping_chain method not implemented")

    @abstractmethod
    def create_extruded_body_from_face_profile(self, **kwargs) -> dict:
        """Create an extruded body from a face profile."""
        raise NotImplementedError("create_extruded_body_from_face_profile method not implemented")

    @abstractmethod
    def create_extruded_body_from_loft_profiles(self, **kwargs) -> dict:
        """Create an extruded body from loft profiles."""
        raise NotImplementedError("create_extruded_body_from_loft_profiles method not implemented")

    @abstractmethod
    def create_planar_body(self, **kwargs) -> dict:
        """Create a planar body."""
        raise NotImplementedError("create_planar_body method not implemented")

    @abstractmethod
    def create_body_from_face(self, **kwargs) -> dict:
        """Create a body from a face."""
        raise NotImplementedError("create_body_from_face method not implemented")

    @abstractmethod
    def create_surface_body(self, **kwargs) -> dict:
        """Create a surface body."""
        raise NotImplementedError("create_surface_body method not implemented")

    @abstractmethod
    def create_surface_body_from_trimmed_curves(self, **kwargs) -> dict:
        """Create a surface body from trimmed curves."""
        raise NotImplementedError("create_surface_body_from_trimmed_curves method not implemented")

    @abstractmethod
    def translate(self, **kwargs) -> dict:
        """Translate a body."""
        raise NotImplementedError("translate method not implemented")

    @abstractmethod
    def delete(self, **kwargs) -> dict:
        """Delete a body."""
        raise NotImplementedError("delete method not implemented")

    @abstractmethod
    def is_suppressed(self, **kwargs) -> dict:
        """Check if a body is suppressed."""
        raise NotImplementedError("is_suppressed method not implemented")

    @abstractmethod
    def get_color(self, **kwargs) -> dict:
        """Get the color of a body."""
        raise NotImplementedError("get_color method not implemented")

    @abstractmethod
    def get_faces(self, **kwargs) -> dict:
        """Get the faces of a body."""
        raise NotImplementedError("get_faces method not implemented")

    @abstractmethod
    def get_edges(self, **kwargs) -> dict:
        """Get the edges of a body."""
        raise NotImplementedError("get_edges method not implemented")

    @abstractmethod
    def get_volume(self, **kwargs) -> dict:
        """Get the volume of a body."""
        raise NotImplementedError("get_volume method not implemented")

    @abstractmethod
    def get_bounding_box(self, **kwargs) -> dict:
        """Get the bounding box of a body."""
        raise NotImplementedError("get_bounding_box method not implemented")

    @abstractmethod
    def set_assigned_material(self, **kwargs) -> dict:
        """Set the assigned material of a body."""
        raise NotImplementedError("set_assigned_material method not implemented")

    @abstractmethod
    def get_assigned_material(self, **kwargs) -> dict:
        """Get the assigned material of a body."""
        raise NotImplementedError("get_assigned_material method not implemented")

    @abstractmethod
    def set_name(self, **kwargs) -> dict:
        """Set the name of a body."""
        raise NotImplementedError("set_name method not implemented")

    @abstractmethod
    def set_fill_style(self, **kwargs) -> dict:
        """Set the fill style of a body."""
        raise NotImplementedError("set_fill_style method not implemented")

    @abstractmethod
    def set_color(self, **kwargs) -> dict:
        """Set the color of a body."""
        raise NotImplementedError("set_color method not implemented")

    @abstractmethod
    def rotate(self, **kwargs) -> dict:
        """Rotate a body."""
        raise NotImplementedError("rotate method not implemented")

    @abstractmethod
    def scale(self, **kwargs) -> dict:
        """Scale a body."""
        raise NotImplementedError("scale method not implemented")

    @abstractmethod
    def mirror(self, **kwargs) -> dict:
        """Mirror a body."""
        raise NotImplementedError("mirror method not implemented")

    @abstractmethod
    def map(self, **kwargs) -> dict:
        """Map a body."""
        raise NotImplementedError("map method not implemented")

    @abstractmethod
    def get_collision(self, **kwargs) -> dict:
        """Get the collision of a body."""
        raise NotImplementedError("get_collision method not implemented")

    @abstractmethod
    def copy(self, **kwargs) -> dict:
        """Copy a body."""
        raise NotImplementedError("copy method not implemented")

    @abstractmethod
    def get_tesellation(self, **kwargs) -> dict:
        """Get the tessellation of a body."""
        raise NotImplementedError("get_tesellation method not implemented")

    @abstractmethod
    def boolean(self, **kwargs) -> dict:
        """Boolean operation."""
        raise NotImplementedError("boolean method not implemented")
