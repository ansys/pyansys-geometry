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

"""Module containing the Face Selection service abstraction layer."""

from abc import ABC, abstractmethod

import grpc


class GRPCFaceSelectionService(ABC):  # pragma: no cover
    """Face Selection service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the GRPCFaceSelectionService class."""
        pass

    # ── Static factory ────────────────────────────────────────────────────────

    @abstractmethod
    def get_all_visible_faces(self, **kwargs) -> dict:
        """Return all visible faces in the active document."""
        pass

    @abstractmethod
    def get_all_faces(self, **kwargs) -> dict:
        """Return all faces in the active document."""
        pass

    @abstractmethod
    def get_faces_from_named_selection(self, **kwargs) -> dict:
        """Return faces belonging to a named selection."""
        pass

    @abstractmethod
    def get_faces_with_area(self, **kwargs) -> dict:
        """Return faces whose area falls within a range."""
        pass

    @abstractmethod
    def get_faces_with_x_location(self, **kwargs) -> dict:
        """Return faces whose X-location falls within a range."""
        pass

    @abstractmethod
    def get_faces_with_y_location(self, **kwargs) -> dict:
        """Return faces whose Y-location falls within a range."""
        pass

    @abstractmethod
    def get_faces_with_z_location(self, **kwargs) -> dict:
        """Return faces whose Z-location falls within a range."""
        pass

    @abstractmethod
    def get_faces_with_color(self, **kwargs) -> dict:
        """Return faces matching a given color."""
        pass

    # ── Instance operations ───────────────────────────────────────────────────

    @abstractmethod
    def invert_face_selection(self, **kwargs) -> dict:
        """Return the complement of the provided face selection."""
        pass

    # ── Filter ────────────────────────────────────────────────────────────────

    @abstractmethod
    def filter_faces_by_area(self, **kwargs) -> dict:
        """Filter faces by area range."""
        pass

    @abstractmethod
    def filter_faces_max_area(self, **kwargs) -> dict:
        """Filter faces keeping only the face with the maximum area."""
        pass

    @abstractmethod
    def filter_faces_min_area(self, **kwargs) -> dict:
        """Filter faces keeping only the face with the minimum area."""
        pass

    @abstractmethod
    def filter_faces_by_perimeter(self, **kwargs) -> dict:
        """Filter faces by perimeter range."""
        pass

    @abstractmethod
    def filter_faces_max_perimeter(self, **kwargs) -> dict:
        """Filter faces keeping only the face with the maximum perimeter."""
        pass

    @abstractmethod
    def filter_faces_min_perimeter(self, **kwargs) -> dict:
        """Filter faces keeping only the face with the minimum perimeter."""
        pass

    @abstractmethod
    def filter_faces_by_edge_count(self, **kwargs) -> dict:
        """Filter faces by edge count range."""
        pass

    @abstractmethod
    def filter_faces_max_edge_count(self, **kwargs) -> dict:
        """Filter faces keeping only the face with the maximum edge count."""
        pass

    @abstractmethod
    def filter_faces_min_edge_count(self, **kwargs) -> dict:
        """Filter faces keeping only the face with the minimum edge count."""
        pass

    @abstractmethod
    def filter_faces_by_loop_count(self, **kwargs) -> dict:
        """Filter faces by loop count range."""
        pass

    @abstractmethod
    def filter_faces_max_loop_count(self, **kwargs) -> dict:
        """Filter faces keeping only the face with the maximum loop count."""
        pass

    @abstractmethod
    def filter_faces_min_loop_count(self, **kwargs) -> dict:
        """Filter faces keeping only the face with the minimum loop count."""
        pass

    @abstractmethod
    def filter_faces_by_number_curves(self, **kwargs) -> dict:
        """Filter faces by curve-type count range."""
        pass

    @abstractmethod
    def filter_faces_max_number_curves(self, **kwargs) -> dict:
        """Filter faces keeping those with the maximum count of a curve type."""
        pass

    @abstractmethod
    def filter_faces_min_number_curves(self, **kwargs) -> dict:
        """Filter faces keeping those with the minimum count of a curve type."""
        pass

    @abstractmethod
    def filter_faces_containing_curve_types(self, **kwargs) -> dict:
        """Filter faces that contain specific curve types."""
        pass

    @abstractmethod
    def filter_faces_by_color(self, **kwargs) -> dict:
        """Filter faces by color."""
        pass

    @abstractmethod
    def filter_faces_area_percentile(self, **kwargs) -> dict:
        """Filter faces by area percentile range."""
        pass

    @abstractmethod
    def filter_faces_perimeter_percentile(self, **kwargs) -> dict:
        """Filter faces by perimeter percentile range."""
        pass

    @abstractmethod
    def filter_faces_edge_count_percentile(self, **kwargs) -> dict:
        """Filter faces by edge count percentile range."""
        pass

    @abstractmethod
    def filter_faces_loop_count_percentile(self, **kwargs) -> dict:
        """Filter faces by loop count percentile range."""
        pass

    @abstractmethod
    def filter_faces_by_number_curves_percentile(self, **kwargs) -> dict:
        """Filter faces by curve-type count percentile range."""
        pass

    # ── Extend ────────────────────────────────────────────────────────────────

    @abstractmethod
    def extend_to_same_area(self, **kwargs) -> dict:
        """Extend selection to faces with the same area."""
        pass

    @abstractmethod
    def extend_to_same_number_of_edges(self, **kwargs) -> dict:
        """Extend selection to faces with the same number of edges."""
        pass

    @abstractmethod
    def extend_to_same_number_of_loops(self, **kwargs) -> dict:
        """Extend selection to faces with the same number of loops."""
        pass

    @abstractmethod
    def extend_to_same_color(self, **kwargs) -> dict:
        """Extend selection to faces with the same color."""
        pass

    @abstractmethod
    def extend_to_coincident(self, **kwargs) -> dict:
        """Extend selection to faces that are coincident."""
        pass

    @abstractmethod
    def extend_to_coaxial_faces(self, **kwargs) -> dict:
        """Extend selection to faces that are coaxial."""
        pass

    # ── OrderBy ───────────────────────────────────────────────────────────────

    @abstractmethod
    def order_faces_by_area(self, **kwargs) -> dict:
        """Order faces by area."""
        pass

    @abstractmethod
    def order_faces_by_perimeter(self, **kwargs) -> dict:
        """Order faces by perimeter."""
        pass

    @abstractmethod
    def order_faces_by_edge_count(self, **kwargs) -> dict:
        """Order faces by edge count."""
        pass

    @abstractmethod
    def order_faces_by_loop_count(self, **kwargs) -> dict:
        """Order faces by loop count."""
        pass

    @abstractmethod
    def order_faces_by_number_curves(self, **kwargs) -> dict:
        """Order faces by number of a specific curve type."""
        pass

    # ── GroupBy ───────────────────────────────────────────────────────────────

    @abstractmethod
    def group_faces_by_area(self, **kwargs) -> dict:
        """Group faces by area."""
        pass

    @abstractmethod
    def group_faces_by_perimeter(self, **kwargs) -> dict:
        """Group faces by perimeter."""
        pass

    @abstractmethod
    def group_faces_by_body(self, **kwargs) -> dict:
        """Group faces by parent body."""
        pass

    @abstractmethod
    def group_faces_by_edge_count(self, **kwargs) -> dict:
        """Group faces by edge count."""
        pass

    @abstractmethod
    def group_faces_by_loop_count(self, **kwargs) -> dict:
        """Group faces by loop count."""
        pass

    @abstractmethod
    def group_faces_by_color(self, **kwargs) -> dict:
        """Group faces by color."""
        pass

    @abstractmethod
    def group_faces_by_coincident(self, **kwargs) -> dict:
        """Group faces by coincidence."""
        pass
