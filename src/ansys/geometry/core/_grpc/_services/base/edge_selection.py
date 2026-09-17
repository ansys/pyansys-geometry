# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Module containing the Edge Selection service abstraction layer."""

from abc import ABC, abstractmethod

import grpc


class GRPCEdgeSelectionService(ABC):  # pragma: no cover
    """Edge Selection service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the GRPCEdgeSelectionService class."""
        pass

    @abstractmethod
    def get_all_visible_edges(self, **kwargs) -> dict:
        """Return all visible edges in the active document."""
        pass

    @abstractmethod
    def get_all_edges(self, **kwargs) -> dict:
        """Return all edges in the active document."""
        pass

    @abstractmethod
    def get_edges_from_named_selection(self, **kwargs) -> dict:
        """Return edges belonging to a named selection."""
        pass

    @abstractmethod
    def get_edges_with_length(self, **kwargs) -> dict:
        """Return edges whose length falls within a range."""
        pass

    @abstractmethod
    def get_edges_with_x_location(self, **kwargs) -> dict:
        """Return edges whose X-location falls within a range."""
        pass

    @abstractmethod
    def get_edges_with_y_location(self, **kwargs) -> dict:
        """Return edges whose Y-location falls within a range."""
        pass

    @abstractmethod
    def get_edges_with_z_location(self, **kwargs) -> dict:
        """Return edges whose Z-location falls within a range."""
        pass

    @abstractmethod
    def invert_edge_selection(self, **kwargs) -> dict:
        """Return the complement of the provided edge selection."""
        pass

    @abstractmethod
    def filter_edges_by_length(self, **kwargs) -> dict:
        """Filter edges by length range."""
        pass

    @abstractmethod
    def filter_edges_max_length(self, **kwargs) -> dict:
        """Filter edges keeping only the edge with maximum length."""
        pass

    @abstractmethod
    def filter_edges_min_length(self, **kwargs) -> dict:
        """Filter edges keeping only the edge with minimum length."""
        pass

    @abstractmethod
    def filter_edges_by_curve_type(self, **kwargs) -> dict:
        """Filter edges by curve type."""
        pass

    @abstractmethod
    def filter_edges_length_percentile(self, **kwargs) -> dict:
        """Filter edges by length percentile range."""
        pass

    @abstractmethod
    def extend_nearby_edges(self, **kwargs) -> dict:
        """Extend selection to include nearby edges within a distance."""
        pass

    @abstractmethod
    def extend_to_connected(self, **kwargs) -> dict:
        """Extend selection to all topologically connected edges."""
        pass

    @abstractmethod
    def extend_to_tangent_chain(self, **kwargs) -> dict:
        """Extend selection to all tangentially chained edges."""
        pass

    @abstractmethod
    def extend_to_coaxial_edges(self, **kwargs) -> dict:
        """Extend selection to all coaxial edges."""
        pass

    @abstractmethod
    def order_edges_by_length(self, **kwargs) -> dict:
        """Order edges by length."""
        pass

    @abstractmethod
    def group_edges_by_curve_type(self, **kwargs) -> dict:
        """Group edges by curve type."""
        pass
