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

"""Module containing the Edge Selection service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.edge_selection import GRPCEdgeSelectionService
from .conversions import (
    build_grpc_id,
    from_length_to_grpc_quantity,
    serialize_edge_group_response,
    serialize_edge_selection_response,
)


class GRPCEdgeSelectionServiceV1(GRPCEdgeSelectionService):
    """Edge Selection service for gRPC communication with the Geometry server (v1).

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2_grpc import (
            EdgeSelectionStub,
        )

        self.stub = EdgeSelectionStub(channel)

    def _input_request(self, kwargs):
        """Build an ``EdgeSelectionInputRequest`` from ``edge_ids``."""
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            EdgeSelectionInputRequest,
            EdgeSelectionInputRequestData,
        )

        return EdgeSelectionInputRequest(
            request_data=[
                EdgeSelectionInputRequestData(
                    edge_ids=[build_grpc_id(eid) for eid in kwargs["edge_ids"]]
                )
            ]
        )

    def _extend_request(self, kwargs):
        """Build an ``EdgeSelectionExtendRequest``."""
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            EdgeSelectionExtendRequest,
            EdgeSelectionExtendRequestData,
        )

        return EdgeSelectionExtendRequest(
            request_data=[
                EdgeSelectionExtendRequestData(
                    edge_ids=[build_grpc_id(eid) for eid in kwargs["edge_ids"]],
                    scope=kwargs["scope"].value,
                )
            ]
        )

    @protect_grpc
    def get_all_visible_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            GetAllVisibleEdgesRequest,
        )

        return serialize_edge_selection_response(
            self.stub.GetAllVisibleEdges(GetAllVisibleEdgesRequest())
        )

    @protect_grpc
    def get_all_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            GetAllEdgesRequest,
        )

        return serialize_edge_selection_response(self.stub.GetAllEdges(GetAllEdgesRequest()))

    @protect_grpc
    def get_edges_from_named_selection(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            GetEdgesFromNamedSelectionRequest,
            GetEdgesFromNamedSelectionRequestData,
        )

        request = GetEdgesFromNamedSelectionRequest(
            request_data=[GetEdgesFromNamedSelectionRequestData(name=kwargs["name"])]
        )
        return serialize_edge_selection_response(self.stub.GetEdgesFromNamedSelection(request))

    @protect_grpc
    def get_edges_with_length(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            GetEdgesWithLengthRequest,
            GetEdgesWithLengthRequestData,
        )

        data = GetEdgesWithLengthRequestData(
            min=from_length_to_grpc_quantity(kwargs["min"]),
            max=from_length_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
        )
        return serialize_edge_selection_response(
            self.stub.GetEdgesWithLength(GetEdgesWithLengthRequest(request_data=[data]))
        )

    @protect_grpc
    def get_edges_with_x_location(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            GetEdgesWithLocationRequest,
            GetEdgesWithLocationRequestData,
        )

        data = GetEdgesWithLocationRequestData(
            min=from_length_to_grpc_quantity(kwargs["min"]) if kwargs["min"] is not None else None,
            max=from_length_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
            range_type=kwargs["range_type"].value,
        )
        return serialize_edge_selection_response(
            self.stub.GetEdgesWithXLocation(GetEdgesWithLocationRequest(request_data=[data]))
        )

    @protect_grpc
    def get_edges_with_y_location(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            GetEdgesWithLocationRequest,
            GetEdgesWithLocationRequestData,
        )

        data = GetEdgesWithLocationRequestData(
            min=from_length_to_grpc_quantity(kwargs["min"]) if kwargs["min"] is not None else None,
            max=from_length_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
            range_type=kwargs["range_type"].value,
        )
        return serialize_edge_selection_response(
            self.stub.GetEdgesWithYLocation(GetEdgesWithLocationRequest(request_data=[data]))
        )

    @protect_grpc
    def get_edges_with_z_location(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            GetEdgesWithLocationRequest,
            GetEdgesWithLocationRequestData,
        )

        data = GetEdgesWithLocationRequestData(
            min=from_length_to_grpc_quantity(kwargs["min"]) if kwargs["min"] is not None else None,
            max=from_length_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
            range_type=kwargs["range_type"].value,
        )
        return serialize_edge_selection_response(
            self.stub.GetEdgesWithZLocation(GetEdgesWithLocationRequest(request_data=[data]))
        )

    @protect_grpc
    def invert_edge_selection(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            InvertEdgeSelectionRequest,
            InvertEdgeSelectionRequestData,
        )

        request = InvertEdgeSelectionRequest(
            request_data=[
                InvertEdgeSelectionRequestData(
                    edge_ids=[build_grpc_id(eid) for eid in kwargs["edge_ids"]],
                    scope=kwargs["scope"].value,
                )
            ]
        )
        return serialize_edge_selection_response(self.stub.InvertEdgeSelection(request))

    @protect_grpc
    def filter_edges_by_length(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            FilterEdgesByLengthRequest,
            FilterEdgesByLengthRequestData,
        )

        data = FilterEdgesByLengthRequestData(
            edge_ids=[build_grpc_id(eid) for eid in kwargs["edge_ids"]],
            min=from_length_to_grpc_quantity(kwargs["min"]),
            max=from_length_to_grpc_quantity(kwargs["max"]) if kwargs["max"] is not None else None,
        )
        return serialize_edge_selection_response(
            self.stub.FilterEdgesByLength(FilterEdgesByLengthRequest(request_data=[data]))
        )

    @protect_grpc
    def filter_edges_max_length(self, **kwargs) -> dict:  # noqa: D102
        return serialize_edge_selection_response(
            self.stub.FilterEdgesMaxLength(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_edges_min_length(self, **kwargs) -> dict:  # noqa: D102
        return serialize_edge_selection_response(
            self.stub.FilterEdgesMinLength(self._input_request(kwargs))
        )

    @protect_grpc
    def filter_edges_by_curve_type(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            FilterEdgesByCurveTypeRequest,
            FilterEdgesByCurveTypeRequestData,
        )

        data = FilterEdgesByCurveTypeRequestData(
            edge_ids=[build_grpc_id(eid) for eid in kwargs["edge_ids"]],
            curve_type=kwargs["curve_type"].value,
        )
        return serialize_edge_selection_response(
            self.stub.FilterEdgesByCurveType(FilterEdgesByCurveTypeRequest(request_data=[data]))
        )

    @protect_grpc
    def filter_edges_length_percentile(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            FilterEdgesPercentileRequest,
            FilterEdgesPercentileRequestData,
        )

        data = FilterEdgesPercentileRequestData(
            edge_ids=[build_grpc_id(eid) for eid in kwargs["edge_ids"]],
            min_percentile=kwargs["min_percentile"],
            max_percentile=kwargs["max_percentile"],
        )
        return serialize_edge_selection_response(
            self.stub.FilterEdgesLengthPercentile(FilterEdgesPercentileRequest(request_data=[data]))
        )

    @protect_grpc
    def extend_nearby_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.selections.edgeselection_pb2 import (
            ExtendNearbyEdgesRequest,
            ExtendNearbyEdgesRequestData,
        )

        request = ExtendNearbyEdgesRequest(
            request_data=[
                ExtendNearbyEdgesRequestData(
                    edge_ids=[build_grpc_id(eid) for eid in kwargs["edge_ids"]],
                    distance=from_length_to_grpc_quantity(kwargs["distance"]),
                    scope=kwargs["scope"].value,
                )
            ]
        )
        return serialize_edge_selection_response(self.stub.ExtendNearbyEdges(request))

    @protect_grpc
    def extend_to_connected(self, **kwargs) -> dict:  # noqa: D102
        return serialize_edge_selection_response(
            self.stub.ExtendToConnected(self._extend_request(kwargs))
        )

    @protect_grpc
    def extend_to_tangent_chain(self, **kwargs) -> dict:  # noqa: D102
        return serialize_edge_selection_response(
            self.stub.ExtendToTangentChain(self._extend_request(kwargs))
        )

    @protect_grpc
    def extend_to_coaxial_edges(self, **kwargs) -> dict:  # noqa: D102
        return serialize_edge_selection_response(
            self.stub.ExtendToCoaxialEdges(self._extend_request(kwargs))
        )

    @protect_grpc
    def order_edges_by_length(self, **kwargs) -> dict:  # noqa: D102
        return serialize_edge_selection_response(
            self.stub.OrderEdgesByLength(self._input_request(kwargs))
        )

    @protect_grpc
    def group_edges_by_curve_type(self, **kwargs) -> dict:  # noqa: D102
        return serialize_edge_group_response(
            self.stub.GroupEdgesByCurveType(self._input_request(kwargs))
        )
