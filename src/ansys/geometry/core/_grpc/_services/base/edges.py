# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
"""Module containing the edges service implementation (abstraction layer)."""

from abc import ABC, abstractmethod

import grpc


class GRPCEdgesService(ABC):  # pragma: no cover
    """Edges service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the GRPCEdgesService class."""
        pass

    @abstractmethod
    def get_edge(self, **kwargs) -> dict:
        """Get edge."""
        pass

    @abstractmethod
    def get_curve(self, **kwargs) -> dict:
        """Get curve information for the edge."""
        pass

    @abstractmethod
    def get_start_and_end_points(self, **kwargs) -> dict:
        """Get start and end points for the edge."""
        pass

    @abstractmethod
    def get_length(self, **kwargs) -> dict:
        """Get the length of the edge."""
        pass

    @abstractmethod
    def get_interval(self, **kwargs) -> dict:
        """Get the interval of the edge."""
        pass

    @abstractmethod
    def get_faces(self, **kwargs) -> dict:
        """Get the faces that are connected to the edge."""
        pass

    @abstractmethod
    def get_vertices(self, **kwargs) -> dict:
        """Get the vertices that are connected to the edge."""
        pass

    @abstractmethod
    def get_bounding_box(self, **kwargs) -> dict:
        """Get the bounding box of the edge."""
        pass

    @abstractmethod
    def extrude_edges(self, **kwargs) -> dict:
        """Extrude edges."""
        pass

    @abstractmethod
    def extrude_edges_up_to(self, **kwargs) -> dict:
        """Extrude edges up to a face."""
        pass

    @abstractmethod
    def move_imprint_edges(self, **kwargs) -> dict:
        """Move imprint edges."""
        pass

    @abstractmethod
    def offset_edges(self, **kwargs) -> dict:
        """Offset edges."""
        pass
