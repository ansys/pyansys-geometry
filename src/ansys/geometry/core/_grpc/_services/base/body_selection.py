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

"""Module containing the Body Selection service abstraction layer."""

from abc import ABC, abstractmethod

import grpc


class GRPCBodySelectionService(ABC):  # pragma: no cover
    """Body Selection service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the GRPCBodySelectionService class."""
        pass

    @abstractmethod
    def get_all_visible_bodies(self, **kwargs) -> dict:
        """Return all visible bodies in the active document."""
        pass

    @abstractmethod
    def get_all_bodies(self, **kwargs) -> dict:
        """Return all bodies in the active document."""
        pass

    @abstractmethod
    def get_all_surface_bodies(self, **kwargs) -> dict:
        """Return all surface bodies in the active document."""
        pass

    @abstractmethod
    def get_all_solid_bodies(self, **kwargs) -> dict:
        """Return all solid bodies in the active document."""
        pass

    @abstractmethod
    def get_bodies_from_named_selection(self, **kwargs) -> dict:
        """Return bodies belonging to a named selection."""
        pass

    @abstractmethod
    def get_bodies_with_name(self, **kwargs) -> dict:
        """Return bodies whose name matches a filter."""
        pass

    @abstractmethod
    def get_bodies_with_volume(self, **kwargs) -> dict:
        """Return bodies whose volume falls within a range."""
        pass

    @abstractmethod
    def get_bodies_with_surface_area(self, **kwargs) -> dict:
        """Return bodies whose surface area falls within a range."""
        pass

    @abstractmethod
    def get_bodies_with_x_location(self, **kwargs) -> dict:
        """Return bodies whose X-location falls within a range."""
        pass

    @abstractmethod
    def get_bodies_with_y_location(self, **kwargs) -> dict:
        """Return bodies whose Y-location falls within a range."""
        pass

    @abstractmethod
    def get_bodies_with_z_location(self, **kwargs) -> dict:
        """Return bodies whose Z-location falls within a range."""
        pass

    @abstractmethod
    def get_bodies_with_color(self, **kwargs) -> dict:
        """Return bodies matching a given color."""
        pass

    @abstractmethod
    def invert_body_selection(self, **kwargs) -> dict:
        """Return the complement of the provided body selection."""
        pass

    @abstractmethod
    def filter_bodies_by_volume(self, **kwargs) -> dict:
        """Filter bodies by volume range."""
        pass

    @abstractmethod
    def filter_bodies_max_volume(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with maximum volume."""
        pass

    @abstractmethod
    def filter_bodies_min_volume(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with minimum volume."""
        pass

    @abstractmethod
    def filter_bodies_by_surface_area(self, **kwargs) -> dict:
        """Filter bodies by surface area range."""
        pass

    @abstractmethod
    def filter_bodies_max_surface_area(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with maximum surface area."""
        pass

    @abstractmethod
    def filter_bodies_min_surface_area(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with minimum surface area."""
        pass

    @abstractmethod
    def filter_bodies_by_face_count(self, **kwargs) -> dict:
        """Filter bodies by face count range."""
        pass

    @abstractmethod
    def filter_bodies_max_face_count(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with the maximum face count."""
        pass

    @abstractmethod
    def filter_bodies_min_face_count(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with the minimum face count."""
        pass

    @abstractmethod
    def filter_bodies_by_edge_count(self, **kwargs) -> dict:
        """Filter bodies by edge count range."""
        pass

    @abstractmethod
    def filter_bodies_max_edge_count(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with the maximum edge count."""
        pass

    @abstractmethod
    def filter_bodies_min_edge_count(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with the minimum edge count."""
        pass

    @abstractmethod
    def filter_bodies_by_loop_count(self, **kwargs) -> dict:
        """Filter bodies by loop count range."""
        pass

    @abstractmethod
    def filter_bodies_max_loop_count(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with the maximum loop count."""
        pass

    @abstractmethod
    def filter_bodies_min_loop_count(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with the minimum loop count."""
        pass

    @abstractmethod
    def filter_bodies_by_number_surfaces(self, **kwargs) -> dict:
        """Filter bodies by surface-type count range."""
        pass

    @abstractmethod
    def filter_bodies_by_number_curves(self, **kwargs) -> dict:
        """Filter bodies by curve-type count range."""
        pass

    @abstractmethod
    def filter_bodies_max_number_surfaces(self, **kwargs) -> dict:
        """Filter bodies keeping those with the maximum count of a surface type."""
        pass

    @abstractmethod
    def filter_bodies_max_number_curves(self, **kwargs) -> dict:
        """Filter bodies keeping those with the maximum count of a curve type."""
        pass

    @abstractmethod
    def filter_bodies_min_number_surfaces(self, **kwargs) -> dict:
        """Filter bodies keeping those with the minimum count of a surface type."""
        pass

    @abstractmethod
    def filter_bodies_min_number_curves(self, **kwargs) -> dict:
        """Filter bodies keeping those with the minimum count of a curve type."""
        pass

    @abstractmethod
    def filter_bodies_by_number_surfaces_percentile(self, **kwargs) -> dict:
        """Filter bodies by surface-type count percentile range."""
        pass

    @abstractmethod
    def filter_bodies_by_number_curves_percentile(self, **kwargs) -> dict:
        """Filter bodies by curve-type count percentile range."""
        pass

    @abstractmethod
    def filter_bodies_by_color(self, **kwargs) -> dict:
        """Filter bodies by color."""
        pass

    @abstractmethod
    def filter_bodies_by_name(self, **kwargs) -> dict:
        """Filter bodies by name pattern."""
        pass

    @abstractmethod
    def filter_bodies_containing_surface_types(self, **kwargs) -> dict:
        """Filter bodies that contain specific surface types."""
        pass

    @abstractmethod
    def filter_bodies_containing_curve_types(self, **kwargs) -> dict:
        """Filter bodies that contain specific curve types."""
        pass

    @abstractmethod
    def filter_bodies_volume_percentile(self, **kwargs) -> dict:
        """Filter bodies by volume percentile range."""
        pass

    @abstractmethod
    def filter_bodies_surface_area_percentile(self, **kwargs) -> dict:
        """Filter bodies by surface area percentile range."""
        pass

    @abstractmethod
    def filter_bodies_face_count_percentile(self, **kwargs) -> dict:
        """Filter bodies by face count percentile range."""
        pass

    @abstractmethod
    def filter_bodies_edge_count_percentile(self, **kwargs) -> dict:
        """Filter bodies by edge count percentile range."""
        pass

    @abstractmethod
    def filter_bodies_loop_count_percentile(self, **kwargs) -> dict:
        """Filter bodies by loop count percentile range."""
        pass

    @abstractmethod
    def filter_surface_bodies(self, **kwargs) -> dict:
        """Filter down to only surface bodies."""
        pass

    @abstractmethod
    def filter_solid_bodies(self, **kwargs) -> dict:
        """Filter down to only solid bodies."""
        pass

    @abstractmethod
    def extend_to_same_volume(self, **kwargs) -> dict:
        """Extend selection to bodies with the same volume."""
        pass

    @abstractmethod
    def extend_to_same_surface_area(self, **kwargs) -> dict:
        """Extend selection to bodies with the same surface area."""
        pass

    @abstractmethod
    def extend_to_same_number_of_faces(self, **kwargs) -> dict:
        """Extend selection to bodies with the same number of faces."""
        pass

    @abstractmethod
    def extend_to_same_number_of_edges(self, **kwargs) -> dict:
        """Extend selection to bodies with the same number of edges."""
        pass

    @abstractmethod
    def extend_to_same_color(self, **kwargs) -> dict:
        """Extend selection to bodies with the same color."""
        pass

    @abstractmethod
    def extend_to_same_name(self, **kwargs) -> dict:
        """Extend selection to bodies with the same name."""
        pass

    @abstractmethod
    def extend_nearby_bodies(self, **kwargs) -> dict:
        """Extend selection to bodies within a specified distance."""
        pass

    @abstractmethod
    def order_bodies_by_volume(self, **kwargs) -> dict:
        """Return bodies ordered by volume."""
        pass

    @abstractmethod
    def order_bodies_by_surface_area(self, **kwargs) -> dict:
        """Return bodies ordered by surface area."""
        pass

    @abstractmethod
    def order_bodies_by_face_count(self, **kwargs) -> dict:
        """Return bodies ordered by face count."""
        pass

    @abstractmethod
    def order_bodies_by_edge_count(self, **kwargs) -> dict:
        """Return bodies ordered by edge count."""
        pass

    @abstractmethod
    def order_bodies_by_loop_count(self, **kwargs) -> dict:
        """Return bodies ordered by loop count."""
        pass

    @abstractmethod
    def order_bodies_by_number_of_surfaces(self, **kwargs) -> dict:
        """Return bodies ordered by number of surfaces."""
        pass

    @abstractmethod
    def order_bodies_by_number_of_curves(self, **kwargs) -> dict:
        """Return bodies ordered by number of curves."""
        pass

    @abstractmethod
    def group_bodies_by_volume(self, **kwargs) -> dict:
        """Return bodies grouped by volume."""
        pass

    @abstractmethod
    def group_bodies_by_surface_area(self, **kwargs) -> dict:
        """Return bodies grouped by surface area."""
        pass

    @abstractmethod
    def group_bodies_by_face_count(self, **kwargs) -> dict:
        """Return bodies grouped by face count."""
        pass

    @abstractmethod
    def group_bodies_by_edge_count(self, **kwargs) -> dict:
        """Return bodies grouped by edge count."""
        pass

    @abstractmethod
    def group_bodies_by_loop_count(self, **kwargs) -> dict:
        """Return bodies grouped by loop count."""
        pass

    @abstractmethod
    def group_bodies_by_color(self, **kwargs) -> dict:
        """Return bodies grouped by color."""
        pass

    @abstractmethod
    def group_bodies_by_name(self, **kwargs) -> dict:
        """Return bodies grouped by name."""
        pass

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

"""Module containing the Body Selection service abstraction layer."""

from abc import ABC, abstractmethod

import grpc


class GRPCBodySelectionService(ABC):  # pragma: no cover
    """Body Selection service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the GRPCBodySelectionService class."""
        pass

    # ── Static factory ────────────────────────────────────────────────────────

    @abstractmethod
    def get_all_visible_bodies(self, **kwargs) -> dict:
        """Return all visible bodies in the active document."""
        pass

    @abstractmethod
    def get_all_bodies(self, **kwargs) -> dict:
        """Return all bodies in the active document."""
        pass

    @abstractmethod
    def get_all_surface_bodies(self, **kwargs) -> dict:
        """Return all surface bodies in the active document."""
        pass

    @abstractmethod
    def get_all_solid_bodies(self, **kwargs) -> dict:
        """Return all solid bodies in the active document."""
        pass

    @abstractmethod
    def get_bodies_from_named_selection(self, **kwargs) -> dict:
        """Return bodies belonging to a named selection."""
        pass

    @abstractmethod
    def get_bodies_with_name(self, **kwargs) -> dict:
        """Return bodies whose name matches a filter."""
        pass

    @abstractmethod
    def get_bodies_with_volume(self, **kwargs) -> dict:
        """Return bodies whose volume falls within a range."""
        pass

    @abstractmethod
    def get_bodies_with_surface_area(self, **kwargs) -> dict:
        """Return bodies whose surface area falls within a range."""
        pass

    @abstractmethod
    def get_bodies_with_x_location(self, **kwargs) -> dict:
        """Return bodies whose X-location falls within a range."""
        pass

    @abstractmethod
    def get_bodies_with_y_location(self, **kwargs) -> dict:
        """Return bodies whose Y-location falls within a range."""
        pass

    @abstractmethod
    def get_bodies_with_z_location(self, **kwargs) -> dict:
        """Return bodies whose Z-location falls within a range."""
        pass

    @abstractmethod
    def get_bodies_with_color(self, **kwargs) -> dict:
        """Return bodies matching a given color."""
        pass

    # ── Instance operations ───────────────────────────────────────────────────

    @abstractmethod
    def invert_body_selection(self, **kwargs) -> dict:
        """Return the complement of the provided body selection."""
        pass

    # ── Filter ────────────────────────────────────────────────────────────────

    @abstractmethod
    def filter_bodies_by_volume(self, **kwargs) -> dict:
        """Filter bodies by volume range."""
        pass

    @abstractmethod
    def filter_bodies_max_volume(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with maximum volume."""
        pass

    @abstractmethod
    def filter_bodies_min_volume(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with minimum volume."""
        pass

    @abstractmethod
    def filter_bodies_by_surface_area(self, **kwargs) -> dict:
        """Filter bodies by surface area range."""
        pass

    @abstractmethod
    def filter_bodies_max_surface_area(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with maximum surface area."""
        pass

    @abstractmethod
    def filter_bodies_min_surface_area(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with minimum surface area."""
        pass

    @abstractmethod
    def filter_bodies_by_face_count(self, **kwargs) -> dict:
        """Filter bodies by face count range."""
        pass

    @abstractmethod
    def filter_bodies_max_face_count(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with the maximum face count."""
        pass

    @abstractmethod
    def filter_bodies_min_face_count(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with the minimum face count."""
        pass

    @abstractmethod
    def filter_bodies_by_edge_count(self, **kwargs) -> dict:
        """Filter bodies by edge count range."""
        pass

    @abstractmethod
    def filter_bodies_max_edge_count(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with the maximum edge count."""
        pass

    @abstractmethod
    def filter_bodies_min_edge_count(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with the minimum edge count."""
        pass

    @abstractmethod
    def filter_bodies_by_loop_count(self, **kwargs) -> dict:
        """Filter bodies by loop count range."""
        pass

    @abstractmethod
    def filter_bodies_max_loop_count(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with the maximum loop count."""
        pass

    @abstractmethod
    def filter_bodies_min_loop_count(self, **kwargs) -> dict:
        """Filter bodies keeping only the body with the minimum loop count."""
        pass

    @abstractmethod
    def filter_bodies_by_number_surfaces(self, **kwargs) -> dict:
        """Filter bodies by surface-type count range."""
        pass

    @abstractmethod
    def filter_bodies_by_number_curves(self, **kwargs) -> dict:
        """Filter bodies by curve-type count range."""
        pass

    @abstractmethod
    def filter_bodies_max_number_surfaces(self, **kwargs) -> dict:
        """Filter bodies keeping those with the maximum count of a surface type."""
        pass

    @abstractmethod
    def filter_bodies_max_number_curves(self, **kwargs) -> dict:
        """Filter bodies keeping those with the maximum count of a curve type."""
        pass

    @abstractmethod
    def filter_bodies_min_number_surfaces(self, **kwargs) -> dict:
        """Filter bodies keeping those with the minimum count of a surface type."""
        pass

    @abstractmethod
    def filter_bodies_min_number_curves(self, **kwargs) -> dict:
        """Filter bodies keeping those with the minimum count of a curve type."""
        pass

    @abstractmethod
    def filter_bodies_by_number_surfaces_percentile(self, **kwargs) -> dict:
        """Filter bodies by surface-type count percentile range."""
        pass

    @abstractmethod
    def filter_bodies_by_number_curves_percentile(self, **kwargs) -> dict:
        """Filter bodies by curve-type count percentile range."""
        pass

    @abstractmethod
    def filter_bodies_by_color(self, **kwargs) -> dict:
        """Filter bodies by color."""
        pass

    @abstractmethod
    def filter_bodies_by_name(self, **kwargs) -> dict:
        """Filter bodies by name pattern."""
        pass

    @abstractmethod
    def filter_bodies_containing_surface_types(self, **kwargs) -> dict:
        """Filter bodies that contain specific surface types."""
        pass

    @abstractmethod
    def filter_bodies_containing_curve_types(self, **kwargs) -> dict:
        """Filter bodies that contain specific curve types."""
        pass

    @abstractmethod
    def filter_bodies_volume_percentile(self, **kwargs) -> dict:
        """Filter bodies by volume percentile range."""
        pass

    @abstractmethod
    def filter_bodies_surface_area_percentile(self, **kwargs) -> dict:
        """Filter bodies by surface area percentile range."""
        pass

    @abstractmethod
    def filter_bodies_face_count_percentile(self, **kwargs) -> dict:
        """Filter bodies by face count percentile range."""
        pass

    @abstractmethod
    def filter_bodies_edge_count_percentile(self, **kwargs) -> dict:
        """Filter bodies by edge count percentile range."""
        pass

    @abstractmethod
    def filter_bodies_loop_count_percentile(self, **kwargs) -> dict:
        """Filter bodies by loop count percentile range."""
        pass

    @abstractmethod
    def filter_surface_bodies(self, **kwargs) -> dict:
        """Filter down to only surface bodies."""
        pass

    @abstractmethod
    def filter_solid_bodies(self, **kwargs) -> dict:
        """Filter down to only solid bodies."""
        pass

    # ── Extend ────────────────────────────────────────────────────────────────

    @abstractmethod
    def extend_to_same_volume(self, **kwargs) -> dict:
        """Extend selection to bodies with the same volume."""
        pass

    @abstractmethod
    def extend_to_same_surface_area(self, **kwargs) -> dict:
        """Extend selection to bodies with the same surface area."""
        pass

    @abstractmethod
    def extend_to_same_number_of_faces(self, **kwargs) -> dict:
        """Extend selection to bodies with the same number of faces."""
        pass

    @abstractmethod
    def extend_to_same_number_of_edges(self, **kwargs) -> dict:
        """Extend selection to bodies with the same number of edges."""
        pass

    @abstractmethod
    def extend_to_same_color(self, **kwargs) -> dict:
        """Extend selection to bodies with the same color."""
        pass

    @abstractmethod
    def extend_to_same_name(self, **kwargs) -> dict:
        """Extend selection to bodies with the same name."""
        pass

    @abstractmethod
    def extend_nearby_bodies(self, **kwargs) -> dict:
        """Extend selection to bodies within a specified distance."""
        pass

    # ── OrderBy ───────────────────────────────────────────────────────────────

    @abstractmethod
    def order_bodies_by_volume(self, **kwargs) -> dict:
        """Return bodies ordered by volume."""
        pass

    @abstractmethod
    def order_bodies_by_surface_area(self, **kwargs) -> dict:
        """Return bodies ordered by surface area."""
        pass

    @abstractmethod
    def order_bodies_by_face_count(self, **kwargs) -> dict:
        """Return bodies ordered by face count."""
        pass

    @abstractmethod
    def order_bodies_by_edge_count(self, **kwargs) -> dict:
        """Return bodies ordered by edge count."""
        pass

    @abstractmethod
    def order_bodies_by_loop_count(self, **kwargs) -> dict:
        """Return bodies ordered by loop count."""
        pass

    @abstractmethod
    def order_bodies_by_number_of_surfaces(self, **kwargs) -> dict:
        """Return bodies ordered by number of surfaces."""
        pass

    @abstractmethod
    def order_bodies_by_number_of_curves(self, **kwargs) -> dict:
        """Return bodies ordered by number of curves."""
        pass

    # ── GroupBy ───────────────────────────────────────────────────────────────

    @abstractmethod
    def group_bodies_by_volume(self, **kwargs) -> dict:
        """Return bodies grouped by volume."""
        pass

    @abstractmethod
    def group_bodies_by_surface_area(self, **kwargs) -> dict:
        """Return bodies grouped by surface area."""
        pass

    @abstractmethod
    def group_bodies_by_face_count(self, **kwargs) -> dict:
        """Return bodies grouped by face count."""
        pass

    @abstractmethod
    def group_bodies_by_edge_count(self, **kwargs) -> dict:
        """Return bodies grouped by edge count."""
        pass

    @abstractmethod
    def group_bodies_by_loop_count(self, **kwargs) -> dict:
        """Return bodies grouped by loop count."""
        pass

    @abstractmethod
    def group_bodies_by_color(self, **kwargs) -> dict:
        """Return bodies grouped by color."""
        pass

    @abstractmethod
    def group_bodies_by_name(self, **kwargs) -> dict:
        """Return bodies grouped by name."""
        pass
