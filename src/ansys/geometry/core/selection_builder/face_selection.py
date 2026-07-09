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

"""Provides for creating a face selection."""

from numbers import Real
from typing import TYPE_CHECKING, Union

from ansys.geometry.core.designer.edge import CurveType
from ansys.geometry.core.misc.auxiliary import convert_color_to_hex, get_faces_from_ids
from ansys.geometry.core.misc.checks import min_backend_version
from ansys.geometry.core.misc.measurements import Area, Distance
from ansys.geometry.core.selection_builder.selection_builder import (
    ExtendScope,
    InvertScope,
    RangeType,
)
from ansys.geometry.core.selection_builder.typed_selection import TypedSelection

if TYPE_CHECKING:
    from pint import Quantity

    from ansys.geometry.core.connection.client import GrpcClient
    from ansys.geometry.core.designer.design import Design
    from ansys.geometry.core.designer.face import Face


class FaceSelection(TypedSelection):
    """A builder for creating a face selection."""

    def __init__(self, design: "Design", grpc_client: "GrpcClient", items: list["Face"] = None):
        """Initialize the face selection builder.

        Parameters
        ----------
        design : Design
            The active design used to resolve face IDs into ``Face`` objects.
        grpc_client : GrpcClient
            The gRPC client used to communicate with the backend.
        """
        self._design = design
        self._grpc_client = grpc_client
        self._items = items or []

    # ── Set-like operators ───────────────────────────────────────────────────

    def __add__(self, other: "FaceSelection") -> "FaceSelection":
        """Return a new selection that is the union of this selection and another."""
        return FaceSelection(
            self._design,
            self._grpc_client,
            list(dict.fromkeys(self.items + other.items)),
        )

    def __sub__(self, other: "FaceSelection") -> "FaceSelection":
        """Return a new selection that is the difference of this selection and another."""
        other_set = set(other.items)
        return FaceSelection(
            self._design,
            self._grpc_client,
            [x for x in self.items if x not in other_set],
        )

    def __and__(self, other: "FaceSelection") -> "FaceSelection":
        """Return a new selection that is the intersection of this selection and another."""
        other_set = set(other.items)
        return FaceSelection(
            self._design,
            self._grpc_client,
            list(dict.fromkeys(x for x in self.items if x in other_set)),
        )

    # ── Static factory (get) ─────────────────────────────────────────────────

    @min_backend_version(27, 1, 0)
    def get_all_visible_faces(self) -> "FaceSelection":
        """Return all visible faces in the active document.

        Returns
        -------
        FaceSelection
            All visible faces.
        """
        response = self._grpc_client.services.face_selection.get_all_visible_faces()
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def get_all_faces(self) -> "FaceSelection":
        """Return all faces in the active document.

        Returns
        -------
        FaceSelection
            All faces.
        """
        response = self._grpc_client.services.face_selection.get_all_faces()
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def get_faces_from_named_selection(self, name: str) -> "FaceSelection":
        """Return faces belonging to a named selection.

        Parameters
        ----------
        name : str
            Name of the named selection to match.

        Returns
        -------
        FaceSelection
            Faces belonging to the matched named selection.
        """
        response = self._grpc_client.services.face_selection.get_faces_from_named_selection(
            name=name,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def get_faces_with_area(
        self,
        min: Union[Area, "Quantity", Real],
        max: Union[Area, "Quantity", Real, None] = None,
    ) -> "FaceSelection":
        """Return faces whose area falls within a range.

        Parameters
        ----------
        min : Area | Quantity | Real
            Minimum area (inclusive).
        max : Area | Quantity | Real, optional
            Maximum area (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        FaceSelection
            Faces whose area is within the specified range.
        """
        min = min if isinstance(min, Area) else Area(min)
        max = (max if isinstance(max, Area) else Area(max)) if max is not None else None
        response = self._grpc_client.services.face_selection.get_faces_with_area(
            min=min,
            max=max,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def get_faces_with_x_location(
        self,
        range_type: RangeType = RangeType.RANGETYPE_INTERSECT,
        min: Union[Distance, "Quantity", Real, None] = None,
        max: Union[Distance, "Quantity", Real, None] = None,
    ) -> "FaceSelection":
        """Return faces whose X-location centroid falls within a range.

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
        FaceSelection
            Faces whose X-location is within the specified range.
        """
        min = (min if isinstance(min, Distance) else Distance(min)) if min is not None else None
        max = (max if isinstance(max, Distance) else Distance(max)) if max is not None else None
        response = self._grpc_client.services.face_selection.get_faces_with_x_location(
            range_type=range_type,
            min=min,
            max=max,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def get_faces_with_y_location(
        self,
        range_type: RangeType = RangeType.RANGETYPE_INTERSECT,
        min: Union[Distance, "Quantity", Real, None] = None,
        max: Union[Distance, "Quantity", Real, None] = None,
    ) -> "FaceSelection":
        """Return faces whose Y-location centroid falls within a range.

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
        FaceSelection
            Faces whose Y-location is within the specified range.
        """
        min = (min if isinstance(min, Distance) else Distance(min)) if min is not None else None
        max = (max if isinstance(max, Distance) else Distance(max)) if max is not None else None
        response = self._grpc_client.services.face_selection.get_faces_with_y_location(
            range_type=range_type,
            min=min,
            max=max,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def get_faces_with_z_location(
        self,
        range_type: RangeType = RangeType.RANGETYPE_INTERSECT,
        min: Union[Distance, "Quantity", Real, None] = None,
        max: Union[Distance, "Quantity", Real, None] = None,
    ) -> "FaceSelection":
        """Return faces whose Z-location centroid falls within a range.

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
        FaceSelection
            Faces whose Z-location is within the specified range.
        """
        min = (min if isinstance(min, Distance) else Distance(min)) if min is not None else None
        max = (max if isinstance(max, Distance) else Distance(max)) if max is not None else None
        response = self._grpc_client.services.face_selection.get_faces_with_z_location(
            range_type=range_type,
            min=min,
            max=max,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def get_faces_with_color(
        self, color: Union[str, tuple[float, float, float], tuple[float, float, float, float]]
    ) -> "FaceSelection":
        """Return faces that match a specific color.

        Parameters
        ----------
        color : str | tuple[float, float, float] | tuple[float, float, float, float]
            Color to match. This can be a string representing a color name
            or a tuple of RGB values in the range [0, 1] (RGBA) or [0, 255] (pure RGB).

        Returns
        -------
        FaceSelection
            Faces with the specified color.
        """
        response = self._grpc_client.services.face_selection.get_faces_with_color(
            color=convert_color_to_hex(color)
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    # ── Instance operations ───────────────────────────────────────────────────

    @min_backend_version(27, 1, 0)
    def invert_face_selection(
        self,
        scope: InvertScope = InvertScope.INVERTSCOPE_VISIBLE,
    ) -> "FaceSelection":
        """Return all faces not in the given selection.

        Parameters
        ----------
        scope : InvertScope, default: InvertScope.INVERTSCOPE_VISIBLE
            Whether to invert within visible faces or all faces.

        Returns
        -------
        FaceSelection
            Faces that are the inverse of the input selection.
        """
        response = self._grpc_client.services.face_selection.invert_face_selection(
            face_ids=[f.id for f in self.items],
            scope=scope,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    # ── Filter ────────────────────────────────────────────────────────────────

    @min_backend_version(27, 1, 0)
    def filter_faces_by_area(
        self,
        min: Union[Area, "Quantity", Real],
        max: Union[Area, "Quantity", Real, None] = None,
    ) -> "FaceSelection":
        """Filter faces whose area falls within a range.

        Parameters
        ----------
        min : Area | Quantity | Real
            Minimum area (inclusive).
        max : Area | Quantity | Real, optional
            Maximum area (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        FaceSelection
            Faces whose area is within the specified range.
        """
        min = min if isinstance(min, Area) else Area(min)
        max = (max if isinstance(max, Area) else Area(max)) if max is not None else None
        response = self._grpc_client.services.face_selection.filter_faces_by_area(
            face_ids=[f.id for f in self.items],
            min=min,
            max=max,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_max_area(self) -> "FaceSelection":
        """Return the face with the maximum area from the selection.

        Returns
        -------
        FaceSelection
            Face with the maximum area.
        """
        response = self._grpc_client.services.face_selection.filter_faces_max_area(
            face_ids=[f.id for f in self.items],
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_min_area(self) -> "FaceSelection":
        """Return the face with the minimum area from the selection.

        Returns
        -------
        FaceSelection
            Face with the minimum area.
        """
        response = self._grpc_client.services.face_selection.filter_faces_min_area(
            face_ids=[f.id for f in self.items],
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_by_perimeter(
        self,
        min: Union[Distance, "Quantity", Real],
        max: Union[Distance, "Quantity", Real, None] = None,
    ) -> "FaceSelection":
        """Filter faces whose perimeter falls within a range.

        Parameters
        ----------
        min : Distance | Quantity | Real
            Minimum perimeter (inclusive).
        max : Distance | Quantity | Real, optional
            Maximum perimeter (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        FaceSelection
            Faces whose perimeter is within the specified range.
        """
        min = min if isinstance(min, Distance) else Distance(min)
        max = (max if isinstance(max, Distance) else Distance(max)) if max is not None else None
        response = self._grpc_client.services.face_selection.filter_faces_by_perimeter(
            face_ids=[f.id for f in self.items],
            min=min,
            max=max,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_max_perimeter(self) -> "FaceSelection":
        """Return the face with the maximum perimeter from the selection.

        Returns
        -------
        FaceSelection
            Face with the maximum perimeter.
        """
        response = self._grpc_client.services.face_selection.filter_faces_max_perimeter(
            face_ids=[f.id for f in self.items],
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_min_perimeter(self) -> "FaceSelection":
        """Return the face with the minimum perimeter from the selection.

        Returns
        -------
        FaceSelection
            Face with the minimum perimeter.
        """
        response = self._grpc_client.services.face_selection.filter_faces_min_perimeter(
            face_ids=[f.id for f in self.items],
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_by_edge_count(
        self,
        min: int,
        max: int = None,
    ) -> "FaceSelection":
        """Filter faces whose edge count falls within a range.

        Parameters
        ----------
        min : int
            Minimum edge count (inclusive).
        max : int, optional
            Maximum edge count (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        FaceSelection
            Faces whose edge count is within the specified range.
        """
        response = self._grpc_client.services.face_selection.filter_faces_by_edge_count(
            face_ids=[f.id for f in self.items],
            min=min,
            max=max,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_max_edge_count(self) -> "FaceSelection":
        """Return the face with the maximum edge count from the selection.

        Returns
        -------
        FaceSelection
            Face with the maximum edge count.
        """
        response = self._grpc_client.services.face_selection.filter_faces_max_edge_count(
            face_ids=[f.id for f in self.items],
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_min_edge_count(self) -> "FaceSelection":
        """Return the face with the minimum edge count from the selection.

        Returns
        -------
        FaceSelection
            Face with the minimum edge count.
        """
        response = self._grpc_client.services.face_selection.filter_faces_min_edge_count(
            face_ids=[f.id for f in self.items],
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_by_loop_count(
        self,
        min: int,
        max: int = None,
    ) -> "FaceSelection":
        """Filter faces whose loop count falls within a range.

        Parameters
        ----------
        min : int
            Minimum loop count (inclusive).
        max : int, optional
            Maximum loop count (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        FaceSelection
            Faces whose loop count is within the specified range.
        """
        response = self._grpc_client.services.face_selection.filter_faces_by_loop_count(
            face_ids=[f.id for f in self.items],
            min=min,
            max=max,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_max_loop_count(self) -> "FaceSelection":
        """Return the face with the maximum loop count from the selection.

        Returns
        -------
        FaceSelection
            Face with the maximum loop count.
        """
        response = self._grpc_client.services.face_selection.filter_faces_max_loop_count(
            face_ids=[f.id for f in self.items],
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_min_loop_count(self) -> "FaceSelection":
        """Return the face with the minimum loop count from the selection.

        Returns
        -------
        FaceSelection
            Face with the minimum loop count.
        """
        response = self._grpc_client.services.face_selection.filter_faces_min_loop_count(
            face_ids=[f.id for f in self.items],
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_by_number_curves(
        self,
        curve_type: CurveType,
        min: int,
        max: int = None,
    ) -> "FaceSelection":
        """Filter faces by the count of a specific curve type they contain.

        Parameters
        ----------
        curve_type : CurveType
            The curve type to count per face.
        min : int
            Minimum count (inclusive).
        max : int, optional
            Maximum count (inclusive). If not provided, no upper bound is applied.

        Returns
        -------
        FaceSelection
            Faces with a matching count of the specified curve type.
        """
        response = self._grpc_client.services.face_selection.filter_faces_by_number_curves(
            face_ids=[f.id for f in self.items],
            curve_type=curve_type.value,
            min=min,
            max=max,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_max_number_curves(self, curve_type: CurveType) -> "FaceSelection":
        """Return the face with the most curves of a given type.

        Parameters
        ----------
        curve_type : CurveType
            The curve type to count per face.

        Returns
        -------
        FaceSelection
            Face with the maximum count of the specified curve type.
        """
        response = self._grpc_client.services.face_selection.filter_faces_max_number_curves(
            face_ids=[f.id for f in self.items],
            curve_type=curve_type.value,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_min_number_curves(self, curve_type: CurveType) -> "FaceSelection":
        """Return the face with the fewest curves of a given type.

        Parameters
        ----------
        curve_type : CurveType
            The curve type to count per face.

        Returns
        -------
        FaceSelection
            Face with the minimum count of the specified curve type.
        """
        response = self._grpc_client.services.face_selection.filter_faces_min_number_curves(
            face_ids=[f.id for f in self.items],
            curve_type=curve_type.value,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_containing_curve_types(
        self,
        curve_type: CurveType,
        exclusive: bool = False,
    ) -> "FaceSelection":
        """Filter faces that contain specific curve types.

        Parameters
        ----------
        curve_type : CurveType
            Curve type that the face must contain.
        exclusive : bool, default: False
            If ``True``, the face must contain *only* the specified curve type.

        Returns
        -------
        FaceSelection
            Faces containing the specified curve type.
        """
        response = self._grpc_client.services.face_selection.filter_faces_containing_curve_types(
            face_ids=[f.id for f in self.items],
            curve_types=curve_type,
            exclusive=exclusive,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_by_color(
        self, color: Union[str, tuple[float, float, float], tuple[float, float, float, float]]
    ) -> "FaceSelection":
        """Filter faces that match a specific color.

        Parameters
        ----------
        color : str | tuple[float, float, float] | tuple[float, float, float, float]
            Color to match. This can be a string representing a color name
            or a tuple of RGB values in the range [0, 1] (RGBA) or [0, 255] (pure RGB).

        Returns
        -------
        FaceSelection
            Faces with the specified color.
        """
        response = self._grpc_client.services.face_selection.filter_faces_by_color(
            face_ids=[f.id for f in self.items],
            color=convert_color_to_hex(color),
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_area_percentile(
        self,
        min_percentile: float,
        max_percentile: float,
    ) -> "FaceSelection":
        """Filter faces by area percentile relative to the selection.

        Parameters
        ----------
        min_percentile : float
            Minimum percentile threshold (0–100).
        max_percentile : float
            Maximum percentile threshold (0–100).

        Returns
        -------
        FaceSelection
            Faces within the specified area percentile range.
        """
        response = self._grpc_client.services.face_selection.filter_faces_area_percentile(
            face_ids=[f.id for f in self.items],
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_perimeter_percentile(
        self,
        min_percentile: float,
        max_percentile: float,
    ) -> "FaceSelection":
        """Filter faces by perimeter percentile relative to the selection.

        Parameters
        ----------
        min_percentile : float
            Minimum percentile threshold (0–100).
        max_percentile : float
            Maximum percentile threshold (0–100).

        Returns
        -------
        FaceSelection
            Faces within the specified perimeter percentile range.
        """
        response = self._grpc_client.services.face_selection.filter_faces_perimeter_percentile(
            face_ids=[f.id for f in self.items],
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_edge_count_percentile(
        self,
        min_percentile: float,
        max_percentile: float,
    ) -> "FaceSelection":
        """Filter faces by edge count percentile relative to the selection.

        Parameters
        ----------
        min_percentile : float
            Minimum percentile threshold (0–100).
        max_percentile : float
            Maximum percentile threshold (0–100).

        Returns
        -------
        FaceSelection
            Faces within the specified edge count percentile range.
        """
        response = self._grpc_client.services.face_selection.filter_faces_edge_count_percentile(
            face_ids=[f.id for f in self.items],
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_loop_count_percentile(
        self,
        min_percentile: float,
        max_percentile: float,
    ) -> "FaceSelection":
        """Filter faces by loop count percentile relative to the selection.

        Parameters
        ----------
        min_percentile : float
            Minimum percentile threshold (0–100).
        max_percentile : float
            Maximum percentile threshold (0–100).

        Returns
        -------
        FaceSelection
            Faces within the specified loop count percentile range.
        """
        response = self._grpc_client.services.face_selection.filter_faces_loop_count_percentile(
            face_ids=[f.id for f in self.items],
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def filter_faces_by_number_curves_percentile(
        self,
        curve_type: CurveType,
        min_percentile: float,
        max_percentile: float,
    ) -> "FaceSelection":
        """Filter faces by the percentile of a curve type count relative to the selection.

        Parameters
        ----------
        curve_type : CurveType
            The curve type to count per face.
        min_percentile : float
            Minimum percentile threshold (0–100).
        max_percentile : float
            Maximum percentile threshold (0–100).

        Returns
        -------
        FaceSelection
            Faces within the percentile range for the curve type count.
        """
        svc = self._grpc_client.services.face_selection
        response = svc.filter_faces_by_number_curves_percentile(
            face_ids=[f.id for f in self.items],
            curve_type=curve_type.value,
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    # ── Extend ────────────────────────────────────────────────────────────────

    @min_backend_version(27, 1, 0)
    def extend_to_same_area(
        self,
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "FaceSelection":
        """Extend the selection with faces that have the same area.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Whether to search all faces or only visible ones.

        Returns
        -------
        FaceSelection
            Input faces plus additional faces with matching areas.
        """
        response = self._grpc_client.services.face_selection.extend_to_same_area(
            face_ids=[f.id for f in self.items],
            scope=scope.value,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def extend_to_same_number_of_edges(
        self,
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "FaceSelection":
        """Extend the selection with faces that have the same number of edges.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Whether to search all faces or only visible ones.

        Returns
        -------
        FaceSelection
            Input faces plus additional faces with the same edge count.
        """
        response = self._grpc_client.services.face_selection.extend_to_same_number_of_edges(
            face_ids=[f.id for f in self.items],
            scope=scope.value,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def extend_to_same_number_of_loops(
        self,
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "FaceSelection":
        """Extend the selection with faces that have the same number of loops.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Whether to search all faces or only visible ones.

        Returns
        -------
        FaceSelection
            Input faces plus additional faces with the same loop count.
        """
        response = self._grpc_client.services.face_selection.extend_to_same_number_of_loops(
            face_ids=[f.id for f in self.items],
            scope=scope.value,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def extend_to_same_color(
        self,
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "FaceSelection":
        """Extend the selection with faces that share the same color.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Whether to search all faces or only visible ones.

        Returns
        -------
        FaceSelection
            Input faces plus additional faces with matching colors.
        """
        response = self._grpc_client.services.face_selection.extend_to_same_color(
            face_ids=[f.id for f in self.items],
            scope=scope.value,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def extend_to_coincident(
        self,
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "FaceSelection":
        """Extend the selection with faces that are coincident to the selection.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Whether to search all faces or only visible ones.

        Returns
        -------
        FaceSelection
            Input faces plus additional coincident faces.
        """
        response = self._grpc_client.services.face_selection.extend_to_coincident(
            face_ids=[f.id for f in self.items],
            scope=scope.value,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def extend_to_coaxial_faces(
        self,
        scope: ExtendScope = ExtendScope.EXTENDSCOPE_ALL,
    ) -> "FaceSelection":
        """Extend the selection with faces that are coaxial to the selection.

        Parameters
        ----------
        scope : ExtendScope, default: ExtendScope.EXTENDSCOPE_ALL
            Whether to search all faces or only visible ones.

        Returns
        -------
        FaceSelection
            Input faces plus additional coaxial faces.
        """
        response = self._grpc_client.services.face_selection.extend_to_coaxial_faces(
            face_ids=[f.id for f in self.items],
            scope=scope.value,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    # ── OrderBy ───────────────────────────────────────────────────────────────

    @min_backend_version(27, 1, 0)
    def order_faces_by_area(self) -> "FaceSelection":
        """Return faces sorted by area in ascending order.

        Returns
        -------
        FaceSelection
            Faces ordered from smallest to largest area.
        """
        response = self._grpc_client.services.face_selection.order_faces_by_area(
            face_ids=[f.id for f in self.items],
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def order_faces_by_perimeter(self) -> "FaceSelection":
        """Return faces sorted by perimeter in ascending order.

        Returns
        -------
        FaceSelection
            Faces ordered from smallest to largest perimeter.
        """
        response = self._grpc_client.services.face_selection.order_faces_by_perimeter(
            face_ids=[f.id for f in self.items],
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def order_faces_by_edge_count(self) -> "FaceSelection":
        """Return faces sorted by edge count in ascending order.

        Returns
        -------
        FaceSelection
            Faces ordered from fewest to most edges.
        """
        response = self._grpc_client.services.face_selection.order_faces_by_edge_count(
            face_ids=[f.id for f in self.items],
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def order_faces_by_loop_count(self) -> "FaceSelection":
        """Return faces sorted by loop count in ascending order.

        Returns
        -------
        FaceSelection
            Faces ordered from fewest to most loops.
        """
        response = self._grpc_client.services.face_selection.order_faces_by_loop_count(
            face_ids=[f.id for f in self.items],
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    @min_backend_version(27, 1, 0)
    def order_faces_by_number_curves(self, curve_type: CurveType) -> "FaceSelection":
        """Return faces sorted by the count of a given curve type in ascending order.

        Parameters
        ----------
        curve_type : CurveType
            The curve type to count per face.

        Returns
        -------
        FaceSelection
            Faces ordered from fewest to most curves of the given type.
        """
        response = self._grpc_client.services.face_selection.order_faces_by_number_curves(
            face_ids=[f.id for f in self.items],
            curve_type=curve_type.value,
        )
        faces = get_faces_from_ids(self._design, response["response_data"][0]["faces"])
        return FaceSelection(self._design, self._grpc_client, faces)

    # ── GroupBy ───────────────────────────────────────────────────────────────

    @min_backend_version(27, 1, 0)
    def group_faces_by_area(self) -> "list[FaceSelection]":
        """Group faces by area.

        Returns
        -------
        list[FaceSelection]
            Faces partitioned into groups with the same area.
        """
        response = self._grpc_client.services.face_selection.group_faces_by_area(
            face_ids=[f.id for f in self.items],
        )
        return [
            FaceSelection(
                self._design, self._grpc_client, get_faces_from_ids(self._design, group)
            )
            for group in response["response_data"][0]["groups"]
        ]

    @min_backend_version(27, 1, 0)
    def group_faces_by_perimeter(self) -> "list[FaceSelection]":
        """Group faces by perimeter.

        Returns
        -------
        list[FaceSelection]
            Faces partitioned into groups with the same perimeter.
        """
        response = self._grpc_client.services.face_selection.group_faces_by_perimeter(
            face_ids=[f.id for f in self.items],
        )
        return [
            FaceSelection(
                self._design, self._grpc_client, get_faces_from_ids(self._design, group)
            )
            for group in response["response_data"][0]["groups"]
        ]

    @min_backend_version(27, 1, 0)
    def group_faces_by_body(self) -> "list[FaceSelection]":
        """Group faces by their parent body.

        Returns
        -------
        list[FaceSelection]
            Faces partitioned into groups by parent body.
        """
        response = self._grpc_client.services.face_selection.group_faces_by_body(
            face_ids=[f.id for f in self.items],
        )
        return [
            FaceSelection(
                self._design, self._grpc_client, get_faces_from_ids(self._design, group)
            )
            for group in response["response_data"][0]["groups"]
        ]

    @min_backend_version(27, 1, 0)
    def group_faces_by_edge_count(self) -> "list[FaceSelection]":
        """Group faces by edge count.

        Returns
        -------
        list[FaceSelection]
            Faces partitioned into groups with the same edge count.
        """
        response = self._grpc_client.services.face_selection.group_faces_by_edge_count(
            face_ids=[f.id for f in self.items],
        )
        return [
            FaceSelection(
                self._design, self._grpc_client, get_faces_from_ids(self._design, group)
            )
            for group in response["response_data"][0]["groups"]
        ]

    @min_backend_version(27, 1, 0)
    def group_faces_by_loop_count(self) -> "list[FaceSelection]":
        """Group faces by loop count.

        Returns
        -------
        list[FaceSelection]
            Faces partitioned into groups with the same loop count.
        """
        response = self._grpc_client.services.face_selection.group_faces_by_loop_count(
            face_ids=[f.id for f in self.items],
        )
        return [
            FaceSelection(
                self._design, self._grpc_client, get_faces_from_ids(self._design, group)
            )
            for group in response["response_data"][0]["groups"]
        ]

    @min_backend_version(27, 1, 0)
    def group_faces_by_color(self) -> "list[FaceSelection]":
        """Group faces by color.

        Returns
        -------
        list[FaceSelection]
            Faces partitioned into groups sharing the same color.
        """
        response = self._grpc_client.services.face_selection.group_faces_by_color(
            face_ids=[f.id for f in self.items],
        )
        return [
            FaceSelection(
                self._design, self._grpc_client, get_faces_from_ids(self._design, group)
            )
            for group in response["response_data"][0]["groups"]
        ]

    @min_backend_version(27, 1, 0)
    def group_faces_by_coincident(self) -> "list[FaceSelection]":
        """Group faces by coincidence.

        Returns
        -------
        list[FaceSelection]
            Faces partitioned into groups of coincident faces.
        """
        response = self._grpc_client.services.face_selection.group_faces_by_coincident(
            face_ids=[f.id for f in self.items],
        )
        return [
            FaceSelection(
                self._design, self._grpc_client, get_faces_from_ids(self._design, group)
            )
            for group in response["response_data"][0]["groups"]
        ]
