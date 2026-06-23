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

"""Provides for creating a body selection."""

from numbers import Real
from typing import TYPE_CHECKING

from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.designer.edge import CurveType
from ansys.geometry.core.designer.face import SurfaceType
from ansys.geometry.core.misc.auxiliary import convert_color_to_hex, get_bodies_from_ids
from ansys.geometry.core.misc.checks import min_backend_version
from ansys.geometry.core.misc.measurements import Area, Distance, Volume
from ansys.geometry.core.selection_builder.selection_builder import (
    ExtendScope,
    InvertScope,
    RangeType,
    StringFilterType,
)
from ansys.geometry.core.selection_builder.typed_selection import TypedSelection

if TYPE_CHECKING:
    from pint import Quantity

    from ansys.geometry.core.connection.client import GrpcClient
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.design import Design


class BodySelection(TypedSelection):
    """A builder for creating a body selection."""

    def __init__(self, design: "Design", grpc_client: "GrpcClient", items: list["Body"] = None):
        """Initialize the body selection builder.

        Parameters
        ----------
        design : Design
            The active design used to resolve body IDs into ``Body`` objects.
        grpc_client : GrpcClient
            The gRPC client used to communicate with the backend.
        """
        self._design = design
        self._grpc_client = grpc_client
        self._items = items or []

    # ── Static factory (get) ─────────────────────────────────────────────────

    @min_backend_version(27, 1, 0)
    def get_all_visible_bodies(self) -> "BodySelection":
        """Return all visible bodies in the active document.

        Returns
        -------
        BodySelection
            All visible bodies.
        """
        response = self._grpc_client.services.body_selection.get_all_visible_bodies()
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def get_all_bodies(self) -> "BodySelection":
        """Return all bodies in the active document.

        Returns
        -------
        BodySelection
            All bodies.
        """
        response = self._grpc_client.services.body_selection.get_all_bodies()
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def get_all_surface_bodies(self) -> "BodySelection":
        """Return all surface bodies in the active document.

        Returns
        -------
        BodySelection
            All surface bodies.
        """
        response = self._grpc_client.services.body_selection.get_all_surface_bodies()
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def get_all_solid_bodies(self) -> "BodySelection":
        """Return all solid bodies in the active document.

        Returns
        -------
        BodySelection
            All solid bodies.
        """
        response = self._grpc_client.services.body_selection.get_all_solid_bodies()
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def get_bodies_from_named_selection(
        self,
        name: str,
        filter_type: "StringFilterType" = StringFilterType.STRINGFILTERTYPE_TEXT,
        ignore_case: bool = False,
    ) -> "BodySelection":
        """Return bodies belonging to a named selection.

        Parameters
        ----------
        name : str
            Name (or pattern) of the named selection to match.
        filter_type : StringFilterType, default: StringFilterType.STRINGFILTERTYPE_TEXT
            String filter type.
        ignore_case : bool, default: False
            Whether the name match is case-insensitive.

        Returns
        -------
        BodySelection
            Bodies belonging to the matched named selection.
        """
        response = self._grpc_client.services.body_selection.get_bodies_from_named_selection(
            name=name,
            filter_type=filter_type,
            ignore_case=ignore_case,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def get_bodies_with_name(
        self,
        name: str,
        filter_type: StringFilterType = StringFilterType.STRINGFILTERTYPE_TEXT,
        ignore_case: bool = False,
    ) -> "BodySelection":
        """Return bodies whose name matches a filter.

        Parameters
        ----------
        name : str
            Name pattern to match against body names.
        filter_type : StringFilterType, default: StringFilterType.STRINGFILTERTYPE_TEXT
            String filter type.
        ignore_case : bool, default: False
            Whether the name match is case-insensitive.

        Returns
        -------
        BodySelection
            Bodies whose name matches the filter.
        """
        response = self._grpc_client.services.body_selection.get_bodies_with_name(
            name=name,
            filter_type=filter_type,
            ignore_case=ignore_case,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def get_bodies_with_volume(
        self,
        min: Volume | "Quantity" | Real,
        max: Volume | "Quantity" | Real | None = None,
    ) -> "BodySelection":
        """Return bodies whose volume falls within a range.

        Parameters
        ----------
        min : Volume | Quantity | Real
            Minimum volume (inclusive).
        max : Volume | Quantity | Real, optional
            Maximum volume (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        BodySelection
            Bodies whose volume is within the specified range.
        """
        min = min if isinstance(min, Volume) else Volume(min)
        max = (max if isinstance(max, Volume) else Volume(max)) if max is not None else None
        response = self._grpc_client.services.body_selection.get_bodies_with_volume(
            min=min,
            max=max,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def get_bodies_with_surface_area(
        self,
        min: Area | "Quantity" | Real,
        max: Area | "Quantity" | Real | None = None,
    ) -> "BodySelection":
        """Return bodies whose surface area falls within a range.

        Parameters
        ----------
        min : Area | Quantity | Real
            Minimum surface area (inclusive).
        max : Area | Quantity | Real, optional
            Maximum surface area (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        BodySelection
            Bodies whose surface area is within the specified range.
        """
        min = min if isinstance(min, Area) else Area(min)
        max = (max if isinstance(max, Area) else Area(max)) if max is not None else None
        response = self._grpc_client.services.body_selection.get_bodies_with_surface_area(
            min=min,
            max=max,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def get_bodies_with_x_location(
        self,
        range_type: RangeType = RangeType.RANGETYPE_INTERSECT,
        min: Distance | "Quantity" | Real | None = None,
        max: Distance | "Quantity" | Real | None = None,
    ) -> "BodySelection":
        """Return bodies whose X-location centroid falls within a range.

        Parameters
        ----------
        range_type : RangeType, default: RangeType.RANGETYPE_INTERSECT
            Range type specifier.
        min : Distance | Quantity | Real, optional
            Minimum X-location. If not provided, no lower bound is applied.
        max : Distance | Quantity | Real, optional
            Maximum X-location. If not provided, no upper bound is applied.

        Returns
        -------
        BodySelection
            Bodies whose X-location is within the specified range.
        """
        min = (min if isinstance(min, Distance) else Distance(min)) if min is not None else None
        max = (max if isinstance(max, Distance) else Distance(max)) if max is not None else None
        response = self._grpc_client.services.body_selection.get_bodies_with_x_location(
            range_type=range_type,
            min=min,
            max=max,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def get_bodies_with_y_location(
        self,
        range_type: RangeType = RangeType.RANGETYPE_INTERSECT,
        min: Distance | "Quantity" | Real | None = None,
        max: Distance | "Quantity" | Real | None = None,
    ) -> "BodySelection":
        """Return bodies whose Y-location centroid falls within a range.

        Parameters
        ----------
        range_type : RangeType, default: RangeType.RANGETYPE_INTERSECT
            Range type specifier.
        min : Distance | Quantity | Real, optional
            Minimum Y-location. If not provided, no lower bound is applied.
        max : Distance | Quantity | Real, optional
            Maximum Y-location. If not provided, no upper bound is applied.

        Returns
        -------
        BodySelection
            Bodies whose Y-location is within the specified range.
        """
        min = (min if isinstance(min, Distance) else Distance(min)) if min is not None else None
        max = (max if isinstance(max, Distance) else Distance(max)) if max is not None else None
        response = self._grpc_client.services.body_selection.get_bodies_with_y_location(
            range_type=range_type,
            min=min,
            max=max,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def get_bodies_with_z_location(
        self,
        range_type: RangeType = RangeType.RANGETYPE_INTERSECT,
        min: Distance | "Quantity" | Real | None = None,
        max: Distance | "Quantity" | Real | None = None,
    ) -> "BodySelection":
        """Return bodies whose Z-location centroid falls within a range.

        Parameters
        ----------
        range_type : RangeType, default: RangeType.RANGETYPE_INTERSECT
            Range type specifier.
        min : Distance | Quantity | Real, optional
            Minimum Z-location. If not provided, no lower bound is applied.
        max : Distance | Quantity | Real, optional
            Maximum Z-location. If not provided, no upper bound is applied.

        Returns
        -------
        BodySelection
            Bodies whose Z-location is within the specified range.
        """
        min = (min if isinstance(min, Distance) else Distance(min)) if min is not None else None
        max = (max if isinstance(max, Distance) else Distance(max)) if max is not None else None
        response = self._grpc_client.services.body_selection.get_bodies_with_z_location(
            range_type=range_type,
            min=min,
            max=max,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def get_bodies_with_color(
        self, color: str | tuple[float, float, float] | tuple[float, float, float, float]
    ) -> "BodySelection":
        """Return bodies that match a specific color.

        Parameters
        ----------
        color : str | tuple[float, float, float] | tuple[float, float, float, float]
            Color to set the body to. This can be a string representing a color name
            or a tuple of RGB values in the range [0, 1] (RGBA) or [0, 255] (pure RGB).

        Returns
        -------
        BodySelection
            Bodies with the specified color.
        """
        response = self._grpc_client.services.body_selection.get_bodies_with_color(
            color=convert_color_to_hex(color)
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    # ── Instance operations ───────────────────────────────────────────────────

    @min_backend_version(27, 1, 0)
    def invert_body_selection(
        self,
        scope: InvertScope = InvertScope.INVERTSCOPE_VISIBLE,
    ) -> "BodySelection":
        """Return all bodies not in the given selection.

        Parameters
        ----------
        scope : InvertScope, default: InvertScope.INVERTSCOPE_VISIBLE
            Whether to invert within visible bodies or all bodies.

        Returns
        -------
        BodySelection
            Bodies that are the inverse of the input selection.
        """
        response = self._grpc_client.services.body_selection.invert_body_selection(
            body_ids=[b.id for b in self.items],
            scope=scope,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    # ── Filter ────────────────────────────────────────────────────────────────

    @min_backend_version(27, 1, 0)
    def filter_bodies_by_volume(
        self,
        min: Volume | "Quantity" | Real,
        max: Volume | "Quantity" | Real | None = None,
    ) -> "BodySelection":
        """Filter bodies whose volume falls within a range.

        Parameters
        ----------
        min : Volume | Quantity | Real
            Minimum volume (inclusive).
        max : Volume | Quantity | Real, optional
            Maximum volume (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        BodySelection
            Bodies whose volume is within the specified range.
        """
        min = min if isinstance(min, Volume) else Volume(min)
        max = (max if isinstance(max, Volume) else Volume(max)) if max is not None else None
        response = self._grpc_client.services.body_selection.filter_bodies_by_volume(
            body_ids=[b.id for b in self.items],
            min=min,
            max=max,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_max_volume(self) -> "BodySelection":
        """Return the body with the maximum volume from the selection.

        Returns
        -------
        BodySelection
            Body with the maximum volume.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_max_volume(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_min_volume(self) -> "BodySelection":
        """Return the body with the minimum volume from the selection.

        Returns
        -------
        BodySelection
            Body with the minimum volume.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_min_volume(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_by_surface_area(
        self,
        min: Area | "Quantity" | Real,
        max: Area | "Quantity" | Real | None = None,
    ) -> "BodySelection":
        """Filter bodies whose surface area falls within a range.

        Parameters
        ----------
        min : Area | Quantity | Real
            Minimum surface area (inclusive).
        max : Area | Quantity | Real, optional
            Maximum surface area (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        BodySelection
            Bodies whose surface area is within the specified range.
        """
        min = min if isinstance(min, Area) else Area(min)
        max = (max if isinstance(max, Area) else Area(max)) if max is not None else None
        response = self._grpc_client.services.body_selection.filter_bodies_by_surface_area(
            body_ids=[b.id for b in self.items],
            min=min,
            max=max,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_max_surface_area(self) -> "BodySelection":
        """Return the body with the maximum surface area from the selection.

        Returns
        -------
        BodySelection
            Body with the maximum surface area.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_max_surface_area(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_min_surface_area(self) -> "BodySelection":
        """Return the body with the minimum surface area from the selection.

        Returns
        -------
        BodySelection
            Body with the minimum surface area.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_min_surface_area(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_by_face_count(
        self,
        min: int,
        max: int = None,
    ) -> "BodySelection":
        """Filter bodies whose face count falls within a range.

        Parameters
        ----------
        min : int
            Minimum face count (inclusive).
        max : int, optional
            Maximum face count (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        BodySelection
            Bodies whose face count is within the specified range.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_by_face_count(
            body_ids=[b.id for b in self.items],
            min=min,
            max=max,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_max_face_count(self) -> "BodySelection":
        """Return the body with the maximum face count from the selection.

        Returns
        -------
        BodySelection
            Body with the maximum face count.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_max_face_count(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_min_face_count(self) -> "BodySelection":
        """Return the body with the minimum face count from the selection.

        Returns
        -------
        BodySelection
            Body with the minimum face count.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_min_face_count(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_by_edge_count(
        self,
        min: int,
        max: int = None,
    ) -> "BodySelection":
        """Filter bodies whose edge count falls within a range.

        Parameters
        ----------
        min : int
            Minimum edge count (inclusive).
        max : int, optional
            Maximum edge count (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        BodySelection
            Bodies whose edge count is within the specified range.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_by_edge_count(
            body_ids=[b.id for b in self.items],
            min=min,
            max=max,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_max_edge_count(self) -> "BodySelection":
        """Return the body with the maximum edge count from the selection.

        Returns
        -------
        BodySelection
            Body with the maximum edge count.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_max_edge_count(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_min_edge_count(self) -> "BodySelection":
        """Return the body with the minimum edge count from the selection.

        Returns
        -------
        BodySelection
            Body with the minimum edge count.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_min_edge_count(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_by_loop_count(
        self,
        min: int,
        max: int = None,
    ) -> "BodySelection":
        """Filter bodies whose loop count falls within a range.

        Parameters
        ----------
        min : int
            Minimum loop count (inclusive).
        max : int, optional
            Maximum loop count (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        BodySelection
            Bodies whose loop count is within the specified range.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_by_loop_count(
            body_ids=[b.id for b in self.items],
            min=min,
            max=max,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_max_loop_count(self) -> "BodySelection":
        """Return the body with the maximum loop count from the selection.

        Returns
        -------
        BodySelection
            Body with the maximum loop count.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_max_loop_count(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_min_loop_count(self) -> "BodySelection":
        """Return the body with the minimum loop count from the selection.

        Returns
        -------
        BodySelection
            Body with the minimum loop count.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_min_loop_count(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_by_number_surfaces(
        self,
        surface_type: SurfaceType,
        min: int,
        max: int = None,
    ) -> "BodySelection":
        """Filter bodies by the count of a specific surface type they contain.

        Parameters
        ----------
        surface_type : SurfaceType
            The surface type to count per body.
        min : int
            Minimum count (inclusive).
        max : int, optional
            Maximum count (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        BodySelection
            Bodies with a matching count of the specified surface type.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_by_number_surfaces(
            body_ids=[b.id for b in self.items],
            surface_type=surface_type.value,
            min=min,
            max=max,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_by_number_curves(
        self,
        curve_type: CurveType,
        min: int,
        max: int = None,
    ) -> "BodySelection":
        """Filter bodies by the count of a specific curve type they contain.

        Parameters
        ----------
        curve_type : CurveType
            The curve type to count per body.
        min : int
            Minimum count (inclusive).
        max : int, optional
            Maximum count (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        BodySelection
            Bodies with a matching count of the specified curve type.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_by_number_curves(
            body_ids=[b.id for b in self.items],
            curve_type=curve_type.value,
            min=min,
            max=max,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_max_number_surfaces(
        self,
        surface_type: SurfaceType,
    ) -> "BodySelection":
        """Return the body with the most surfaces of a given type.

        Parameters
        ----------
        surface_type : SurfaceType
            The surface type to count per body.

        Returns
        -------
        BodySelection
            Body with the maximum count of the specified surface type.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_max_number_surfaces(
            body_ids=[b.id for b in self.items],
            surface_type=surface_type.value,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_max_number_curves(
        self,
        curve_type: CurveType,
    ) -> "BodySelection":
        """Return the body with the most curves of a given type.

        Parameters
        ----------
        curve_type : CurveType
            The curve type to count per body.

        Returns
        -------
        BodySelection
            Body with the maximum count of the specified curve type.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_max_number_curves(
            body_ids=[b.id for b in self.items],
            curve_type=curve_type.value,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_min_number_surfaces(
        self,
        surface_type: SurfaceType,
    ) -> "BodySelection":
        """Return the body with the fewest surfaces of a given type.

        Parameters
        ----------
        surface_type : SurfaceType
            The surface type to count per body.

        Returns
        -------
        BodySelection
            Body with the minimum count of the specified surface type.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_min_number_surfaces(
            body_ids=[b.id for b in self.items],
            surface_type=surface_type.value,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_min_number_curves(
        self,
        curve_type: CurveType,
    ) -> "BodySelection":
        """Return the body with the fewest curves of a given type.

        Parameters
        ----------
        curve_type : CurveType
            The curve type to count per body.

        Returns
        -------
        BodySelection
            Body with the minimum count of the specified curve type.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_min_number_curves(
            body_ids=[b.id for b in self.items],
            curve_type=curve_type.value,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_by_number_surfaces_percentile(
        self,
        surface_type: SurfaceType,
        min_percentile: float,
        max_percentile: float,
    ) -> "BodySelection":
        """Filter bodies by the percentile of a surface type count relative to the selection.

        Parameters
        ----------
        surface_type : SurfaceType
            The surface type to count per body.
        min_percentile : float
            Minimum percentile threshold (0–100).
        max_percentile : float
            Maximum percentile threshold (0–100).

        Returns
        -------
        BodySelection
            Bodies within the percentile range for the surface type count.
        """
        svc = self._grpc_client.services.body_selection
        response = svc.filter_bodies_by_number_surfaces_percentile(
            body_ids=[b.id for b in self.items],
            surface_type=surface_type.value,
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_by_number_curves_percentile(
        self,
        curve_type: CurveType,
        min_percentile: float,
        max_percentile: float,
    ) -> "BodySelection":
        """Filter bodies by the percentile of a curve type count relative to the selection.

        Parameters
        ----------
        curve_type : CurveType
            The curve type to count per body.
        min_percentile : float
            Minimum percentile threshold (0–100).
        max_percentile : float
            Maximum percentile threshold (0–100).

        Returns
        -------
        BodySelection
            Bodies within the percentile range for the curve type count.
        """
        svc = self._grpc_client.services.body_selection
        response = svc.filter_bodies_by_number_curves_percentile(
            body_ids=[b.id for b in self.items],
            curve_type=curve_type.value,
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_by_color(
        self, color: str | tuple[float, float, float] | tuple[float, float, float, float]
    ) -> "BodySelection":
        """Filter bodies that match a specific color.

        Parameters
        ----------
        color : str | tuple[float, float, float] | tuple[float, float, float, float]
            Color to match. This can be a string representing a color name
            or a tuple of RGB values in the range [0, 1] (RGBA) or [0, 255] (pure RGB).

        Returns
        -------
        BodySelection
            Bodies with the specified color.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_by_color(
            body_ids=[b.id for b in self.items],
            color=convert_color_to_hex(color),
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_by_name(
        self,
        name: str,
        filter_type: StringFilterType = StringFilterType.STRINGFILTERTYPE_TEXT,
        ignore_case: bool = False,
    ) -> "BodySelection":
        """Filter bodies whose name matches a filter.

        Parameters
        ----------
        name : str
            Name pattern to match.
        filter_type : StringFilterType, default: StringFilterType.STRINGFILTERTYPE_TEXT
            String filter type.
        ignore_case : bool, default: False
            Whether the name match is case-insensitive.

        Returns
        -------
        BodySelection
            Bodies whose name matches the filter.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_by_name(
            body_ids=[b.id for b in self.items],
            name=name,
            filter_type=filter_type.value,
            ignore_case=ignore_case,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_containing_surface_types(
        self,
        surface_type: SurfaceType,
        exclusive: bool = False,
    ) -> "BodySelection":
        """Filter bodies that contain specific surface types.

        Parameters
        ----------
        surface_type : SurfaceType
            Surface type that the body must contain.
        exclusive : bool, default: False
            If ``True``, the body must contain *only* the specified surface type.

        Returns
        -------
        BodySelection
            Bodies containing the specified surface type.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_containing_surface_types(
            body_ids=[b.id for b in self.items],
            surface_types=surface_type,
            exclusive=exclusive,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_containing_curve_types(
        self,
        curve_type: CurveType,
        exclusive: bool = False,
    ) -> "BodySelection":
        """Filter bodies that contain specific curve types.

        Parameters
        ----------
        curve_type : CurveType
            Curve type that the body must contain.
        exclusive : bool, default: False
            If ``True``, the body must contain *only* the specified curve type.

        Returns
        -------
        BodySelection
            Bodies containing the specified curve type.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_containing_curve_types(
            body_ids=[b.id for b in self.items],
            curve_types=curve_type,
            exclusive=exclusive,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_volume_percentile(
        self,
        min_percentile: float,
        max_percentile: float,
    ) -> "BodySelection":
        """Filter bodies by volume percentile relative to the selection.

        Parameters
        ----------
        min_percentile : float
            Minimum percentile threshold (0–100).
        max_percentile : float
            Maximum percentile threshold (0–100).

        Returns
        -------
        BodySelection
            Bodies within the specified volume percentile range.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_volume_percentile(
            body_ids=[b.id for b in self.items],
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_surface_area_percentile(
        self,
        min_percentile: float,
        max_percentile: float,
    ) -> "BodySelection":
        """Filter bodies by surface area percentile relative to the selection.

        Parameters
        ----------
        min_percentile : float
            Minimum percentile threshold (0–100).
        max_percentile : float
            Maximum percentile threshold (0–100).

        Returns
        -------
        BodySelection
            Bodies within the specified surface area percentile range.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_surface_area_percentile(
            body_ids=[b.id for b in self.items],
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_face_count_percentile(
        self,
        min_percentile: float,
        max_percentile: float,
    ) -> "BodySelection":
        """Filter bodies by face count percentile relative to the selection.

        Parameters
        ----------
        min_percentile : float
            Minimum percentile threshold (0–100).
        max_percentile : float
            Maximum percentile threshold (0–100).

        Returns
        -------
        BodySelection
            Bodies within the specified face count percentile range.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_face_count_percentile(
            body_ids=[b.id for b in self.items],
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_edge_count_percentile(
        self,
        min_percentile: float,
        max_percentile: float,
    ) -> "BodySelection":
        """Filter bodies by edge count percentile relative to the selection.

        Parameters
        ----------
        min_percentile : float
            Minimum percentile threshold (0–100).
        max_percentile : float
            Maximum percentile threshold (0–100).

        Returns
        -------
        BodySelection
            Bodies within the specified edge count percentile range.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_edge_count_percentile(
            body_ids=[b.id for b in self.items],
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_bodies_loop_count_percentile(
        self,
        min_percentile: float,
        max_percentile: float,
    ) -> "BodySelection":
        """Filter bodies by loop count percentile relative to the selection.

        Parameters
        ----------
        min_percentile : float
            Minimum percentile threshold (0–100).
        max_percentile : float
            Maximum percentile threshold (0–100).

        Returns
        -------
        BodySelection
            Bodies within the specified loop count percentile range.
        """
        response = self._grpc_client.services.body_selection.filter_bodies_loop_count_percentile(
            body_ids=[b.id for b in self.items],
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_surface_bodies(self) -> "BodySelection":
        """Keep only surface bodies from the selection.

        Returns
        -------
        BodySelection
            Only the surface bodies from the input selection.
        """
        response = self._grpc_client.services.body_selection.filter_surface_bodies(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def filter_solid_bodies(self) -> "BodySelection":
        """Keep only solid bodies from the selection.

        Returns
        -------
        BodySelection
            Only the solid bodies from the input selection.
        """
        response = self._grpc_client.services.body_selection.filter_solid_bodies(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    # ── Extend ────────────────────────────────────────────────────────────────

    @min_backend_version(27, 1, 0)
    def extend_to_same_volume(
        self,
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "BodySelection":
        """Extend the selection with bodies that have the same volume.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Whether to search all bodies or only visible ones.

        Returns
        -------
        BodySelection
            Input bodies plus additional bodies with matching volumes.
        """
        response = self._grpc_client.services.body_selection.extend_to_same_volume(
            body_ids=[b.id for b in self.items],
            scope=scope.value,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def extend_to_same_surface_area(
        self,
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "BodySelection":
        """Extend the selection with bodies that have the same surface area.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Whether to search all bodies or only visible ones.

        Returns
        -------
        BodySelection
            Input bodies plus additional bodies with matching surface areas.
        """
        response = self._grpc_client.services.body_selection.extend_to_same_surface_area(
            body_ids=[b.id for b in self.items],
            scope=scope.value,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def extend_to_same_number_of_faces(
        self,
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "BodySelection":
        """Extend the selection with bodies that have the same number of faces.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Whether to search all bodies or only visible ones.

        Returns
        -------
        BodySelection
            Input bodies plus additional bodies with the same face count.
        """
        response = self._grpc_client.services.body_selection.extend_to_same_number_of_faces(
            body_ids=[b.id for b in self.items],
            scope=scope.value,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def extend_to_same_number_of_edges(
        self,
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "BodySelection":
        """Extend the selection with bodies that have the same number of edges.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Whether to search all bodies or only visible ones.

        Returns
        -------
        BodySelection
            Input bodies plus additional bodies with the same edge count.
        """
        response = self._grpc_client.services.body_selection.extend_to_same_number_of_edges(
            body_ids=[b.id for b in self.items],
            scope=scope.value,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def extend_to_same_color(
        self,
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "BodySelection":
        """Extend the selection with bodies that share the same color.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Whether to search all bodies or only visible ones.

        Returns
        -------
        BodySelection
            Input bodies plus additional bodies with matching colors.
        """
        response = self._grpc_client.services.body_selection.extend_to_same_color(
            body_ids=[b.id for b in self.items],
            scope=scope.value,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def extend_to_same_name(
        self,
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "BodySelection":
        """Extend the selection with bodies that share the same name.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Whether to search all bodies or only visible ones.

        Returns
        -------
        BodySelection
            Input bodies plus additional bodies with matching names.
        """
        response = self._grpc_client.services.body_selection.extend_to_same_name(
            body_ids=[b.id for b in self.items],
            scope=scope.value,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def extend_nearby_bodies(
        self,
        distance: Distance | "Quantity" | Real,
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "BodySelection":
        """Extend the selection with bodies within a given distance.

        Parameters
        ----------
        distance : Distance | Quantity | Real
            Maximum proximity distance.
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Whether to search all bodies or only visible ones.

        Returns
        -------
        BodySelection
            Input bodies plus additional bodies within the specified distance.

        Warnings
        --------
        This is not currently supported for CoreService backends.
        """
        if BackendType.is_core_service(self._grpc_client.backend_type):
            raise NotImplementedError(
                "The 'extend_nearby_bodies' method is not supported for CoreService backends."
            )
        distance = distance if isinstance(distance, Distance) else Distance(distance)
        response = self._grpc_client.services.body_selection.extend_nearby_bodies(
            body_ids=[b.id for b in self.items],
            distance=distance,
            scope=scope.value,
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    # ── OrderBy ───────────────────────────────────────────────────────────────

    @min_backend_version(27, 1, 0)
    def order_bodies_by_volume(self) -> "BodySelection":
        """Return bodies sorted by volume in ascending order.

        Returns
        -------
        BodySelection
            Bodies ordered from smallest to largest volume.
        """
        response = self._grpc_client.services.body_selection.order_bodies_by_volume(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def order_bodies_by_surface_area(self) -> "BodySelection":
        """Return bodies sorted by surface area in ascending order.

        Returns
        -------
        BodySelection
            Bodies ordered from smallest to largest surface area.
        """
        response = self._grpc_client.services.body_selection.order_bodies_by_surface_area(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def order_bodies_by_face_count(self) -> "BodySelection":
        """Return bodies sorted by face count in ascending order.

        Returns
        -------
        BodySelection
            Bodies ordered from fewest to most faces.
        """
        response = self._grpc_client.services.body_selection.order_bodies_by_face_count(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def order_bodies_by_edge_count(self) -> "BodySelection":
        """Return bodies sorted by edge count in ascending order.

        Returns
        -------
        BodySelection
            Bodies ordered from fewest to most edges.
        """
        response = self._grpc_client.services.body_selection.order_bodies_by_edge_count(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def order_bodies_by_loop_count(self) -> "BodySelection":
        """Return bodies sorted by loop count in ascending order.

        Returns
        -------
        BodySelection
            Bodies ordered from fewest to most loops.
        """
        response = self._grpc_client.services.body_selection.order_bodies_by_loop_count(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def order_bodies_by_number_of_surfaces(self) -> "BodySelection":
        """Return bodies sorted by total surface count in ascending order.

        Returns
        -------
        BodySelection
            Bodies ordered from fewest to most surfaces.
        """
        response = self._grpc_client.services.body_selection.order_bodies_by_number_of_surfaces(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    @min_backend_version(27, 1, 0)
    def order_bodies_by_number_of_curves(self) -> "BodySelection":
        """Return bodies sorted by total curve count in ascending order.

        Returns
        -------
        BodySelection
            Bodies ordered from fewest to most curves.
        """
        response = self._grpc_client.services.body_selection.order_bodies_by_number_of_curves(
            body_ids=[b.id for b in self.items],
        )
        bodies = get_bodies_from_ids(self._design, response["response_data"][0]["bodies"])
        return BodySelection(self._design, self._grpc_client, bodies)

    # ── GroupBy ───────────────────────────────────────────────────────────────

    @min_backend_version(27, 1, 0)
    def group_bodies_by_volume(self) -> "list[BodySelection]":
        """Group bodies by volume.

        Returns
        -------
        list[BodySelection]
            Bodies partitioned into groups of equal volume.
        """
        response = self._grpc_client.services.body_selection.group_bodies_by_volume(
            body_ids=[b.id for b in self.items],
        )
        return [
            BodySelection(self._design, self._grpc_client, get_bodies_from_ids(self._design, group))
            for group in response["response_data"][0]["groups"]
        ]

    @min_backend_version(27, 1, 0)
    def group_bodies_by_surface_area(self) -> "list[BodySelection]":
        """Group bodies by surface area.

        Returns
        -------
        list[BodySelection]
            Bodies partitioned into groups of equal surface area.
        """
        response = self._grpc_client.services.body_selection.group_bodies_by_surface_area(
            body_ids=[b.id for b in self.items],
        )
        return [
            BodySelection(self._design, self._grpc_client, get_bodies_from_ids(self._design, group))
            for group in response["response_data"][0]["groups"]
        ]

    @min_backend_version(27, 1, 0)
    def group_bodies_by_face_count(self) -> "list[BodySelection]":
        """Group bodies by face count.

        Returns
        -------
        list[BodySelection]
            Bodies partitioned into groups with the same face count.
        """
        response = self._grpc_client.services.body_selection.group_bodies_by_face_count(
            body_ids=[b.id for b in self.items],
        )
        return [
            BodySelection(self._design, self._grpc_client, get_bodies_from_ids(self._design, group))
            for group in response["response_data"][0]["groups"]
        ]

    @min_backend_version(27, 1, 0)
    def group_bodies_by_edge_count(self) -> "list[BodySelection]":
        """Group bodies by edge count.

        Returns
        -------
        list[BodySelection]
            Bodies partitioned into groups with the same edge count.
        """
        response = self._grpc_client.services.body_selection.group_bodies_by_edge_count(
            body_ids=[b.id for b in self.items],
        )
        return [
            BodySelection(self._design, self._grpc_client, get_bodies_from_ids(self._design, group))
            for group in response["response_data"][0]["groups"]
        ]

    @min_backend_version(27, 1, 0)
    def group_bodies_by_loop_count(self) -> "list[BodySelection]":
        """Group bodies by loop count.

        Returns
        -------
        list[BodySelection]
            Bodies partitioned into groups with the same loop count.
        """
        response = self._grpc_client.services.body_selection.group_bodies_by_loop_count(
            body_ids=[b.id for b in self.items],
        )
        return [
            BodySelection(self._design, self._grpc_client, get_bodies_from_ids(self._design, group))
            for group in response["response_data"][0]["groups"]
        ]

    @min_backend_version(27, 1, 0)
    def group_bodies_by_color(self) -> "list[BodySelection]":
        """Group bodies by color.

        Returns
        -------
        list[BodySelection]
            Bodies partitioned into groups sharing the same color.
        """
        response = self._grpc_client.services.body_selection.group_bodies_by_color(
            body_ids=[b.id for b in self.items],
        )
        return [
            BodySelection(self._design, self._grpc_client, get_bodies_from_ids(self._design, group))
            for group in response["response_data"][0]["groups"]
        ]

    @min_backend_version(27, 1, 0)
    def group_bodies_by_name(self) -> "list[BodySelection]":
        """Group bodies by name.

        Returns
        -------
        list[BodySelection]
            Bodies partitioned into groups sharing the same name.
        """
        response = self._grpc_client.services.body_selection.group_bodies_by_name(
            body_ids=[b.id for b in self.items],
        )
        return [
            BodySelection(self._design, self._grpc_client, get_bodies_from_ids(self._design, group))
            for group in response["response_data"][0]["groups"]
        ]
