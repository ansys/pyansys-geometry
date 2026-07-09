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

"""Module containing the Face Selection service implementation for v0.

The FaceSelection service does not exist in the v0 proto API.
All methods raise ``NotImplementedError``.
"""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.face_selection import GRPCFaceSelectionService


class GRPCFaceSelectionServiceV0(GRPCFaceSelectionService):
    """Face Selection service for gRPC communication with the Geometry server (v0).

    The FaceSelection RPC service is not available in the v0 API.
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

    # ── Static factory ────────────────────────────────────────────────────────

    def get_all_visible_faces(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_all_visible_faces")

    def get_all_faces(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_all_faces")

    def get_faces_from_named_selection(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_faces_from_named_selection")

    def get_faces_with_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_faces_with_area")

    def get_faces_with_x_location(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_faces_with_x_location")

    def get_faces_with_y_location(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_faces_with_y_location")

    def get_faces_with_z_location(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_faces_with_z_location")

    def get_faces_with_color(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_faces_with_color")

    # ── Instance operations ───────────────────────────────────────────────────

    def invert_face_selection(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("invert_face_selection")

    # ── Filter ────────────────────────────────────────────────────────────────

    def filter_faces_by_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_by_area")

    def filter_faces_max_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_max_area")

    def filter_faces_min_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_min_area")

    def filter_faces_by_perimeter(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_by_perimeter")

    def filter_faces_max_perimeter(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_max_perimeter")

    def filter_faces_min_perimeter(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_min_perimeter")

    def filter_faces_by_edge_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_by_edge_count")

    def filter_faces_max_edge_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_max_edge_count")

    def filter_faces_min_edge_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_min_edge_count")

    def filter_faces_by_loop_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_by_loop_count")

    def filter_faces_max_loop_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_max_loop_count")

    def filter_faces_min_loop_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_min_loop_count")

    def filter_faces_by_number_curves(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_by_number_curves")

    def filter_faces_max_number_curves(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_max_number_curves")

    def filter_faces_min_number_curves(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_min_number_curves")

    def filter_faces_containing_curve_types(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_containing_curve_types")

    def filter_faces_by_color(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_by_color")

    def filter_faces_area_percentile(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_area_percentile")

    def filter_faces_perimeter_percentile(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_perimeter_percentile")

    def filter_faces_edge_count_percentile(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_edge_count_percentile")

    def filter_faces_loop_count_percentile(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_loop_count_percentile")

    def filter_faces_by_number_curves_percentile(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_faces_by_number_curves_percentile")

    # ── Extend ────────────────────────────────────────────────────────────────

    def extend_to_same_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_same_area")

    def extend_to_same_number_of_edges(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_same_number_of_edges")

    def extend_to_same_number_of_loops(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_same_number_of_loops")

    def extend_to_same_color(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_same_color")

    def extend_to_coincident(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_coincident")

    def extend_to_coaxial_faces(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_coaxial_faces")

    # ── OrderBy ───────────────────────────────────────────────────────────────

    def order_faces_by_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("order_faces_by_area")

    def order_faces_by_perimeter(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("order_faces_by_perimeter")

    def order_faces_by_edge_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("order_faces_by_edge_count")

    def order_faces_by_loop_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("order_faces_by_loop_count")

    def order_faces_by_number_curves(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("order_faces_by_number_curves")

    # ── GroupBy ───────────────────────────────────────────────────────────────

    def group_faces_by_area(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_faces_by_area")

    def group_faces_by_perimeter(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_faces_by_perimeter")

    def group_faces_by_body(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_faces_by_body")

    def group_faces_by_edge_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_faces_by_edge_count")

    def group_faces_by_loop_count(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_faces_by_loop_count")

    def group_faces_by_color(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_faces_by_color")

    def group_faces_by_coincident(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_faces_by_coincident")
