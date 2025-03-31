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
        pass  # pragma: no cover

    @abstractmethod
    def create_sphere_body(self, **kwargs) -> dict:
        """Create a sphere body."""
        pass  # pragma: no cover

    @abstractmethod
    def create_extruded_body(self, **kwargs) -> dict:
        """Create an extruded body."""
        pass  # pragma: no cover

    @abstractmethod
    def create_sweeping_profile_body(self, **kwargs) -> dict:
        """Create a sweeping profile body."""
        pass  # pragma: no cover

    @abstractmethod
    def create_sweeping_chain(self, **kwargs) -> dict:
        """Create a sweeping chain."""
        pass  # pragma: no cover

    @abstractmethod
    def create_extruded_body_from_face_profile(self, **kwargs) -> dict:
        """Create an extruded body from a face profile."""
        pass  # pragma: no cover

    @abstractmethod
    def create_extruded_body_from_loft_profiles(self, **kwargs) -> dict:
        """Create an extruded body from loft profiles."""
        pass  # pragma: no cover

    @abstractmethod
    def create_planar_body(self, **kwargs) -> dict:
        """Create a planar body."""
        pass  # pragma: no cover

    @abstractmethod
    def create_body_from_face(self, **kwargs) -> dict:
        """Create a body from a face."""
        pass  # pragma: no cover

    @abstractmethod
    def create_surface_body(self, **kwargs) -> dict:
        """Create a surface body."""
        pass  # pragma: no cover

    @abstractmethod
    def create_surface_body_from_trimmed_curves(self, **kwargs) -> dict:
        """Create a surface body from trimmed curves."""
        pass  # pragma: no cover

    @abstractmethod
    def translate(self, **kwargs) -> dict:
        """Translate a body."""
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, **kwargs) -> dict:
        """Delete a body."""
        pass  # pragma: no cover

    @abstractmethod
    def is_suppressed(self, **kwargs) -> dict:
        """Check if a body is suppressed."""
        pass  # pragma: no cover

    @abstractmethod
    def get_color(self, **kwargs) -> dict:
        """Get the color of a body."""
        pass  # pragma: no cover

    @abstractmethod
    def get_faces(self, **kwargs) -> dict:
        """Get the faces of a body."""
        pass  # pragma: no cover

    @abstractmethod
    def get_edges(self, **kwargs) -> dict:
        """Get the edges of a body."""
        pass  # pragma: no cover

    @abstractmethod
    def get_volume(self, **kwargs) -> dict:
        """Get the volume of a body."""
        pass  # pragma: no cover

    @abstractmethod
    def get_bounding_box(self, **kwargs) -> dict:
        """Get the bounding box of a body."""
        pass  # pragma: no cover

    @abstractmethod
    def set_assigned_material(self, **kwargs) -> dict:
        """Set the assigned material of a body."""
        pass  # pragma: no cover

    @abstractmethod
    def get_assigned_material(self, **kwargs) -> dict:
        """Get the assigned material of a body."""
        pass  # pragma: no cover

    @abstractmethod
    def set_name(self, **kwargs) -> dict:
        """Set the name of a body."""
        pass  # pragma: no cover

    @abstractmethod
    def set_fill_style(self, **kwargs) -> dict:
        """Set the fill style of a body."""
        pass  # pragma: no cover

    @abstractmethod
    def set_suppressed(self, **kwargs) -> dict:
        """Set the suppressed state of a body."""
        pass  # pragma: no cover

    @abstractmethod
    def set_color(self, **kwargs) -> dict:
        """Set the color of a body."""
        pass  # pragma: no cover

    @abstractmethod
    def rotate(self, **kwargs) -> dict:
        """Rotate a body."""
        pass  # pragma: no cover

    @abstractmethod
    def scale(self, **kwargs) -> dict:
        """Scale a body."""
        pass  # pragma: no cover

    @abstractmethod
    def mirror(self, **kwargs) -> dict:
        """Mirror a body."""
        pass  # pragma: no cover

    @abstractmethod
    def map(self, **kwargs) -> dict:
        """Map a body."""
        pass  # pragma: no cover

    @abstractmethod
    def get_collision(self, **kwargs) -> dict:
        """Get the collision of a body."""
        pass  # pragma: no cover

    @abstractmethod
    def copy(self, **kwargs) -> dict:
        """Copy a body."""
        pass  # pragma: no cover

    @abstractmethod
    def get_tesellation(self, **kwargs) -> dict:
        """Get the tessellation of a body."""
        pass  # pragma: no cover

    @abstractmethod
    def get_tesellation_with_options(self, **kwargs) -> dict:
        """Get the tessellation of a body with options."""
        pass  # pragma: no cover

    @abstractmethod
    def boolean(self, **kwargs) -> dict:
        """Boolean operation."""
        pass  # pragma: no cover
