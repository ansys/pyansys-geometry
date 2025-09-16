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
"""Module containing the faces service implementation (abstraction layer)."""

from abc import ABC, abstractmethod

import grpc


class GRPCFacesService(ABC):  # pragma: no cover
    """Faces service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the GRPCFacesService class."""
        pass

    @abstractmethod
    def get_surface(self, **kwargs) -> dict:
        """Get the surface of a face."""
        pass

    @abstractmethod
    def get_box_uv(self, **kwargs) -> dict:
        """Get the UV box of a face."""
        pass

    @abstractmethod
    def get_area(self, **kwargs) -> dict:
        """Get the area of a face."""
        pass

    @abstractmethod
    def get_edges(self, **kwargs) -> dict:
        """Get the edges of a face."""
        pass

    @abstractmethod
    def get_vertices(self, **kwargs) -> dict:
        """Get the vertices of a face."""
        pass

    @abstractmethod
    def get_loops(self, **kwargs) -> dict:
        """Get the loops of a face."""
        pass

    @abstractmethod
    def get_color(self, **kwargs) -> dict:
        """Get the color of a face."""
        pass

    @abstractmethod
    def get_bounding_box(self, **kwargs) -> dict:
        """Get the bounding box of a face."""
        pass

    @abstractmethod
    def set_color(self, **kwargs) -> dict:
        """Set the color of a face."""
        pass

    @abstractmethod
    def get_normal(self, **kwargs) -> dict:
        """Get the normal of a face."""
        pass

    @abstractmethod
    def evaluate(self, **kwargs) -> dict:
        """Evaluate a face at a given parameter."""
        pass

    @abstractmethod
    def create_iso_parametric_curve(self, **kwargs) -> dict:
        """Create an iso-parametric curve on a face."""
        pass

    @abstractmethod
    def extrude_faces(self, **kwargs) -> dict:
        """Extrude a selection of faces."""
        pass

    @abstractmethod
    def extrude_faces_up_to(self, **kwargs) -> dict:
        """Extrude a selection of faces up to another object."""
        pass

    @abstractmethod
    def offset_faces_set_radius(self, **kwargs) -> dict:
        """Offset a selection of faces by a given radius."""
        pass

    @abstractmethod
    def revolve_faces(self, **kwargs) -> dict:
        """Revolve a selection of faces around an axis."""
        pass

    @abstractmethod
    def revolve_faces_up_to(self, **kwargs) -> dict:
        """Revolve a selection of faces around an axis up to another object."""
        pass

    @abstractmethod
    def revolve_faces_by_helix(self, **kwargs) -> dict:
        """Revolve a selection of faces around an axis by a helix."""
        pass

    @abstractmethod
    def replace_faces(self, **kwargs) -> dict:
        """Replace a selection of faces with new faces."""
        pass

    @abstractmethod
    def thicken_faces(self, **kwargs) -> dict:
        """Thicken a selection of faces."""
        pass

    @abstractmethod
    def draft_faces(self, **kwargs) -> dict:
        """Draft a selection of faces."""
        pass

    @abstractmethod
    def get_round_info(self, **kwargs) -> dict:
        """Get round information for a selection of faces."""
        pass