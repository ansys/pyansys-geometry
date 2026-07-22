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

"""Module containing the Body Selection service implementation for v0.

The BodySelection service does not exist in the v0 proto API.
All methods raise ``NotImplementedError``.
"""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.body_selection import GRPCBodySelectionService


class GRPCBodySelectionServiceV0(GRPCBodySelectionService):
    """Body Selection service for gRPC communication with the Geometry server (v0).

    The BodySelection RPC service is not available in the v0 API.
    All methods raise :exc:`NotImplementedError`.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        pass

    def _not_implemented(self, method_name: str):
        raise NotImplementedError(
            f"Method '{self.__class__.__name__}.{method_name}' is not "
            "implemented in this protofile version."
        )

    def get_all_visible_bodies(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_all_visible_bodies")

    def get_all_bodies(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_all_bodies")

    def get_all_surface_bodies(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_all_surface_bodies")

    def get_all_solid_bodies(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_all_solid_bodies")

    def get_bodies_from_named_selection(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_bodies_from_named_selection")

    def get_bodies_with_name(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_bodies_with_name")

    def get_bodies_with_volume(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_bodies_with_volume")

    def get_bodies_with_surface_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_bodies_with_surface_area")

    def get_bodies_with_x_location(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_bodies_with_x_location")

    def get_bodies_with_y_location(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_bodies_with_y_location")

    def get_bodies_with_z_location(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_bodies_with_z_location")

    def get_bodies_with_color(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_bodies_with_color")

    def invert_body_selection(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("invert_body_selection")

    def filter_bodies_by_volume(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_by_volume")

    def filter_bodies_max_volume(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_max_volume")

    def filter_bodies_min_volume(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_min_volume")

    def filter_bodies_by_surface_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_by_surface_area")

    def filter_bodies_max_surface_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_max_surface_area")

    def filter_bodies_min_surface_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_min_surface_area")

    def filter_bodies_by_face_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_by_face_count")

    def filter_bodies_max_face_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_max_face_count")

    def filter_bodies_min_face_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_min_face_count")

    def filter_bodies_by_edge_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_by_edge_count")

    def filter_bodies_max_edge_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_max_edge_count")

    def filter_bodies_min_edge_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_min_edge_count")

    def filter_bodies_by_loop_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_by_loop_count")

    def filter_bodies_max_loop_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_max_loop_count")

    def filter_bodies_min_loop_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_min_loop_count")

    def filter_bodies_by_number_surfaces(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_by_number_surfaces")

    def filter_bodies_by_number_curves(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_by_number_curves")

    def filter_bodies_max_number_surfaces(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_max_number_surfaces")

    def filter_bodies_max_number_curves(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_max_number_curves")

    def filter_bodies_min_number_surfaces(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_min_number_surfaces")

    def filter_bodies_min_number_curves(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_min_number_curves")

    def filter_bodies_by_number_surfaces_percentile(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_by_number_surfaces_percentile")

    def filter_bodies_by_number_curves_percentile(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_by_number_curves_percentile")

    def filter_bodies_by_color(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_by_color")

    def filter_bodies_by_name(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_by_name")

    def filter_bodies_containing_surface_types(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_containing_surface_types")

    def filter_bodies_containing_curve_types(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_containing_curve_types")

    def filter_bodies_volume_percentile(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_volume_percentile")

    def filter_bodies_surface_area_percentile(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_surface_area_percentile")

    def filter_bodies_face_count_percentile(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_face_count_percentile")

    def filter_bodies_edge_count_percentile(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_edge_count_percentile")

    def filter_bodies_loop_count_percentile(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_bodies_loop_count_percentile")

    def filter_surface_bodies(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_surface_bodies")

    def filter_solid_bodies(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_solid_bodies")

    def extend_to_same_volume(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_same_volume")

    def extend_to_same_surface_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_same_surface_area")

    def extend_to_same_number_of_faces(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_same_number_of_faces")

    def extend_to_same_number_of_edges(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_same_number_of_edges")

    def extend_to_same_color(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_same_color")

    def extend_to_same_name(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_same_name")

    def extend_nearby_bodies(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_nearby_bodies")

    def order_bodies_by_volume(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("order_bodies_by_volume")

    def order_bodies_by_surface_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("order_bodies_by_surface_area")

    def order_bodies_by_face_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("order_bodies_by_face_count")

    def order_bodies_by_edge_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("order_bodies_by_edge_count")

    def order_bodies_by_loop_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("order_bodies_by_loop_count")

    def order_bodies_by_number_of_surfaces(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("order_bodies_by_number_of_surfaces")

    def order_bodies_by_number_of_curves(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("order_bodies_by_number_of_curves")

    def group_bodies_by_volume(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_bodies_by_volume")

    def group_bodies_by_surface_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_bodies_by_surface_area")

    def group_bodies_by_face_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_bodies_by_face_count")

    def group_bodies_by_edge_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_bodies_by_edge_count")

    def group_bodies_by_loop_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_bodies_by_loop_count")

    def group_bodies_by_color(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_bodies_by_color")

    def group_bodies_by_name(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_bodies_by_name")
