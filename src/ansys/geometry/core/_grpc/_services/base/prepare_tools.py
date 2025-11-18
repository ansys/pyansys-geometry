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
"""Module containing the prepare tools service implementation (abstraction layer)."""

from abc import ABC, abstractmethod

import grpc


class GRPCPrepareToolsService(ABC):  # pragma: no cover
    """Prepare tools service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the GRPCPrepareToolsService class."""
        pass

    @abstractmethod
    def extract_volume_from_faces(self, **kwargs) -> dict:
        """Extract a volume from input faces."""
        pass

    @abstractmethod
    def extract_volume_from_edge_loops(self, **kwargs) -> dict:
        """Extract a volume from input edge loop."""
        pass

    @abstractmethod
    def remove_rounds(self, **kwargs) -> dict:
        """Remove rounds from geometry."""
        pass

    @abstractmethod
    def share_topology(self, **kwargs) -> dict:
        """Share topology between the given bodies."""
        pass

    @abstractmethod
    def enhanced_share_topology(self, **kwargs) -> dict:
        """Share topology between the given bodies."""
        pass

    @abstractmethod
    def find_logos(self, **kwargs) -> dict:
        """Detect logos in geometry."""
        pass

    @abstractmethod
    def find_and_remove_logos(self, **kwargs) -> dict:
        """Detect and remove logos in geometry."""
        pass

    @abstractmethod
    def remove_logo(self, **kwargs) -> dict:
        """Remove logos in geometry."""
        pass

    @abstractmethod
    def detect_helixes(self, **kwargs) -> dict:
        """Detect helixes in geometry."""
        pass

    @abstractmethod
    def create_box_enclosure(self, **kwargs) -> dict:
        """Create a box enclosure around bodies."""
        pass

    @abstractmethod
    def create_cylinder_enclosure(self, **kwargs) -> dict:
        """Create a cylinder enclosure around bodies."""
        pass

    @abstractmethod
    def create_sphere_enclosure(self, **kwargs) -> dict:
        """Create a sphere enclosure around bodies."""
