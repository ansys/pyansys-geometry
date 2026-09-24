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

"""Module containing the Edge Selection service implementation for v0.

The EdgeSelection service does not exist in the v0 proto API.
All methods raise ``NotImplementedError``.
"""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.edge_selection import GRPCEdgeSelectionService


class GRPCEdgeSelectionServiceV0(GRPCEdgeSelectionService):
    """Edge Selection service for gRPC communication with the Geometry server (v0).

    The EdgeSelection RPC service is not available in the v0 API.
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

    def get_all_visible_edges(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_all_visible_edges")

    def get_all_edges(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_all_edges")

    def get_edges_from_named_selection(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_edges_from_named_selection")

    def get_edges_with_length(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_edges_with_length")

    def get_edges_with_x_location(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_edges_with_x_location")

    def get_edges_with_y_location(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_edges_with_y_location")

    def get_edges_with_z_location(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("get_edges_with_z_location")

    def invert_edge_selection(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("invert_edge_selection")

    def filter_edges_by_length(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_edges_by_length")

    def filter_edges_max_length(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_edges_max_length")

    def filter_edges_min_length(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_edges_min_length")

    def filter_edges_by_curve_type(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_edges_by_curve_type")

    def filter_edges_length_percentile(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("filter_edges_length_percentile")

    def extend_nearby_edges(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_nearby_edges")

    def extend_to_connected(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_connected")

    def extend_to_tangent_chain(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_tangent_chain")

    def extend_to_coaxial_edges(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("extend_to_coaxial_edges")

    def order_edges_by_length(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("order_edges_by_length")

    def group_edges_by_curve_type(self, **kwargs) -> dict:  # noqa: D102
        self._not_implemented("group_edges_by_curve_type")
