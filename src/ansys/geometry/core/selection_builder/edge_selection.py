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

"""Provides for creating an edge selection."""

from numbers import Real
from typing import TYPE_CHECKING, Union

from ansys.geometry.core.designer.edge import CurveType
from ansys.geometry.core.misc.auxiliary import get_edges_from_ids
from ansys.geometry.core.misc.checks import min_backend_version
from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.selection_builder.selection_builder import (
    ExtendScope,
    InvertTopologyScope,
    RangeType,
)
from ansys.geometry.core.selection_builder.typed_selection import TypedSelection

if TYPE_CHECKING:
    from pint import Quantity

    from ansys.geometry.core.connection.client import GrpcClient
    from ansys.geometry.core.designer.design import Design
    from ansys.geometry.core.designer.edge import Edge


class EdgeSelection(TypedSelection):
    """A builder for creating an edge selection."""

    def __init__(self, design: "Design", grpc_client: "GrpcClient", items: list["Edge"] = None):
        """Initialize the edge selection builder.

        Parameters
        ----------
        design : Design
            The active design used to resolve edge IDs into ``Edge`` objects.
        grpc_client : GrpcClient
            The gRPC client used to communicate with the backend.
        """
        self._design = design
        self._grpc_client = grpc_client
        self._items = items or []

    def __add__(self, other: "EdgeSelection") -> "EdgeSelection":
        """Return a new selection that is the union of this selection and another."""
        return EdgeSelection(
            self._design,
            self._grpc_client,
            list(dict.fromkeys(self.items + other.items)),
        )

    def __sub__(self, other: "EdgeSelection") -> "EdgeSelection":
        """Return a new selection that is the difference of this selection and another."""
        other_set = set(other.items)
        return EdgeSelection(
            self._design,
            self._grpc_client,
            [x for x in self.items if x not in other_set],
        )

    def __and__(self, other: "EdgeSelection") -> "EdgeSelection":
        """Return a new selection that is the intersection of this selection and another."""
        other_set = set(other.items)
        return EdgeSelection(
            self._design,
            self._grpc_client,
            list(dict.fromkeys(x for x in self.items if x in other_set)),
        )

    @min_backend_version(27, 1, 0)
    def get_all_visible_edges(self) -> "EdgeSelection":
        """Return all visible edges in the active document.

        Returns
        -------
        EdgeSelection
            All visible edges.
        """
        response = self._grpc_client.services.edge_selection.get_all_visible_edges()
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def get_all_edges(self) -> "EdgeSelection":
        """Return all edges in the active document.

        Returns
        -------
        EdgeSelection
            All edges.
        """
        response = self._grpc_client.services.edge_selection.get_all_edges()
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def get_edges_from_named_selection(self, name: str) -> "EdgeSelection":
        """Return edges belonging to a named selection.

        Parameters
        ----------
        name : str
            Name of the named selection.

        Returns
        -------
        EdgeSelection
            Edges belonging to the matched named selection.
        """
        response = self._grpc_client.services.edge_selection.get_edges_from_named_selection(
            name=name,
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def get_edges_with_length(
        self,
        min: Union[Real, "Quantity"],
        max: Union[Real, "Quantity", None] = None,
    ) -> "EdgeSelection":
        """Return edges whose length falls within a range.

        Parameters
        ----------
        min : Real or Quantity
            Minimum edge length (in mm if a plain number).
        max : Real or Quantity, optional
            Maximum edge length. If ``None``, no upper bound is applied.

        Returns
        -------
        EdgeSelection
            Edges whose length is within the specified range.
        """
        min_dist = min if isinstance(min, Distance) else Distance(min)
        max_dist = (max if isinstance(max, Distance) else Distance(max)) if max is not None else None
        response = self._grpc_client.services.edge_selection.get_edges_with_length(
            min=min_dist,
            max=max_dist,
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def get_edges_with_x_location(
        self,
        range_type: RangeType,
        min: Union[Real, "Quantity", None] = None,
        max: Union[Real, "Quantity", None] = None,
    ) -> "EdgeSelection":
        """Return edges whose X-location falls within a range.

        Parameters
        ----------
        range_type : RangeType
            Whether to intersect or contain the range.
        min : Real or Quantity, optional
            Minimum X coordinate (in mm if a plain number).
        max : Real or Quantity, optional
            Maximum X coordinate.

        Returns
        -------
        EdgeSelection
            Edges within the specified X-location range.
        """
        min_dist = (min if isinstance(min, Distance) else Distance(min)) if min is not None else None
        max_dist = (max if isinstance(max, Distance) else Distance(max)) if max is not None else None
        response = self._grpc_client.services.edge_selection.get_edges_with_x_location(
            min=min_dist,
            max=max_dist,
            range_type=range_type,
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def get_edges_with_y_location(
        self,
        range_type: RangeType,
        min: Union[Real, "Quantity", None] = None,
        max: Union[Real, "Quantity", None] = None,
    ) -> "EdgeSelection":
        """Return edges whose Y-location falls within a range.

        Parameters
        ----------
        range_type : RangeType
            Whether to intersect or contain the range.
        min : Real or Quantity, optional
            Minimum Y coordinate (in mm if a plain number).
        max : Real or Quantity, optional
            Maximum Y coordinate.

        Returns
        -------
        EdgeSelection
            Edges within the specified Y-location range.
        """
        min_dist = (min if isinstance(min, Distance) else Distance(min)) if min is not None else None
        max_dist = (max if isinstance(max, Distance) else Distance(max)) if max is not None else None
        response = self._grpc_client.services.edge_selection.get_edges_with_y_location(
            min=min_dist,
            max=max_dist,
            range_type=range_type,
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def get_edges_with_z_location(
        self,
        range_type: RangeType,
        min: Union[Real, "Quantity", None] = None,
        max: Union[Real, "Quantity", None] = None,
    ) -> "EdgeSelection":
        """Return edges whose Z-location falls within a range.

        Parameters
        ----------
        range_type : RangeType
            Whether to intersect or contain the range.
        min : Real or Quantity, optional
            Minimum Z coordinate (in mm if a plain number).
        max : Real or Quantity, optional
            Maximum Z coordinate.

        Returns
        -------
        EdgeSelection
            Edges within the specified Z-location range.
        """
        min_dist = (min if isinstance(min, Distance) else Distance(min)) if min is not None else None
        max_dist = (max if isinstance(max, Distance) else Distance(max)) if max is not None else None
        response = self._grpc_client.services.edge_selection.get_edges_with_z_location(
            min=min_dist,
            max=max_dist,
            range_type=range_type,
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def invert_edge_selection(
        self,
        scope: InvertTopologyScope = InvertTopologyScope.INVERTSCOPE_ALL,
    ) -> "EdgeSelection":
        """Return the complement of this edge selection.

        Parameters
        ----------
        scope : InvertTopologyScope, default: InvertTopologyScope.INVERTSCOPE_ALL
            Whether to invert relative to all edges or only visible edges.

        Returns
        -------
        EdgeSelection
            The inverted edge selection.
        """
        response = self._grpc_client.services.edge_selection.invert_edge_selection(
            edge_ids=[e.id for e in self.items],
            scope=scope,
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def filter_edges_by_length(
        self,
        min: Union[Real, "Quantity"],
        max: Union[Real, "Quantity", None] = None,
    ) -> "EdgeSelection":
        """Filter edges by length range.

        Parameters
        ----------
        min : Real or Quantity
            Minimum edge length (in mm if a plain number).
        max : Real or Quantity, optional
            Maximum edge length. If ``None``, no upper bound is applied.

        Returns
        -------
        EdgeSelection
            Edges within the specified length range.
        """
        min_dist = min if isinstance(min, Distance) else Distance(min)
        max_dist = (max if isinstance(max, Distance) else Distance(max)) if max is not None else None
        response = self._grpc_client.services.edge_selection.filter_edges_by_length(
            edge_ids=[e.id for e in self.items],
            min=min_dist,
            max=max_dist,
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def filter_edges_max_length(self) -> "EdgeSelection":
        """Filter edges keeping only the edge(s) with the maximum length.

        Returns
        -------
        EdgeSelection
            Edge(s) with the maximum length.
        """
        response = self._grpc_client.services.edge_selection.filter_edges_max_length(
            edge_ids=[e.id for e in self.items],
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def filter_edges_min_length(self) -> "EdgeSelection":
        """Filter edges keeping only the edge(s) with the minimum length.

        Returns
        -------
        EdgeSelection
            Edge(s) with the minimum length.
        """
        response = self._grpc_client.services.edge_selection.filter_edges_min_length(
            edge_ids=[e.id for e in self.items],
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def filter_edges_by_curve_type(self, curve_type: CurveType) -> "EdgeSelection":
        """Filter edges by curve type.

        Parameters
        ----------
        curve_type : CurveType
            The curve type to retain.

        Returns
        -------
        EdgeSelection
            Edges matching the given curve type.
        """
        response = self._grpc_client.services.edge_selection.filter_edges_by_curve_type(
            edge_ids=[e.id for e in self.items],
            curve_type=curve_type,
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def filter_edges_length_percentile(
        self,
        min_percentile: float,
        max_percentile: float,
    ) -> "EdgeSelection":
        """Filter edges by length percentile range.

        Parameters
        ----------
        min_percentile : float
            Minimum percentile (0.0–100.0).
        max_percentile : float
            Maximum percentile (0.0–100.0).

        Returns
        -------
        EdgeSelection
            Edges whose lengths fall within the given percentile range.
        """
        response = self._grpc_client.services.edge_selection.filter_edges_length_percentile(
            edge_ids=[e.id for e in self.items],
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def extend_nearby_edges(
        self,
        distance: Union[Real, "Quantity"],
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "EdgeSelection":
        """Extend selection to include nearby edges within a distance.

        Parameters
        ----------
        distance : Real or Quantity
            Maximum gap distance (in mm if a plain number).
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Scope of edges to consider for extension.

        Returns
        -------
        EdgeSelection
            Extended edge selection.
        """
        dist = distance if isinstance(distance, Distance) else Distance(distance)
        response = self._grpc_client.services.edge_selection.extend_nearby_edges(
            edge_ids=[e.id for e in self.items],
            distance=dist,
            scope=scope,
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def extend_to_connected(
        self, scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL
    ) -> "EdgeSelection":
        """Extend selection to all topologically connected edges.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Scope of edges to consider for extension.

        Returns
        -------
        EdgeSelection
            Extended edge selection.
        """
        response = self._grpc_client.services.edge_selection.extend_to_connected(
            edge_ids=[e.id for e in self.items],
            scope=scope,
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def extend_to_tangent_chain(
        self, scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL
    ) -> "EdgeSelection":
        """Extend selection to all tangentially chained edges.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Scope of edges to consider for extension.

        Returns
        -------
        EdgeSelection
            Extended edge selection.
        """
        response = self._grpc_client.services.edge_selection.extend_to_tangent_chain(
            edge_ids=[e.id for e in self.items],
            scope=scope,
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def extend_to_coaxial_edges(
        self, scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL
    ) -> "EdgeSelection":
        """Extend selection to all coaxial edges.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Scope of edges to consider for extension.

        Returns
        -------
        EdgeSelection
            Extended edge selection.
        """
        response = self._grpc_client.services.edge_selection.extend_to_coaxial_edges(
            edge_ids=[e.id for e in self.items],
            scope=scope,
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def order_edges_by_length(self) -> "EdgeSelection":
        """Order edges by length (ascending).

        Returns
        -------
        EdgeSelection
            Edges ordered by ascending length.
        """
        response = self._grpc_client.services.edge_selection.order_edges_by_length(
            edge_ids=[e.id for e in self.items],
        )
        edges = get_edges_from_ids(self._design, response["response_data"][0]["edges"])
        return EdgeSelection(self._design, self._grpc_client, edges)

    @min_backend_version(27, 1, 0)
    def group_edges_by_curve_type(self) -> "list[EdgeSelection]":
        """Group edges by curve type.

        Returns
        -------
        list[EdgeSelection]
            Edges partitioned into groups of the same curve type.
        """
        response = self._grpc_client.services.edge_selection.group_edges_by_curve_type(
            edge_ids=[e.id for e in self.items],
        )
        return [
            EdgeSelection(
                self._design, self._grpc_client, get_edges_from_ids(self._design, group)
            )
            for group in response["response_data"][0]["groups"]
        ]
