# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
"""Module for managing an edge."""

from enum import Enum, unique
from typing import TYPE_CHECKING

from ansys.geometry.core.misc.auxiliary import get_design_from_body
from pint import Quantity

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.errors import GeometryRuntimeError
from ansys.geometry.core.math.bbox import BoundingBox
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.misc.checks import ensure_design_is_active, min_backend_version
from ansys.geometry.core.shapes.curves.trimmed_curve import ReversedTrimmedCurve, TrimmedCurve
from ansys.geometry.core.shapes.parameterization import Interval

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.face import Face
    from ansys.geometry.core.designer.selection import NamedSelection
    from ansys.geometry.core.designer.vertex import Vertex


@unique
class CurveType(Enum):
    """Provides values for the curve types supported."""

    CURVETYPE_UNKNOWN = 0
    CURVETYPE_LINE = 1
    CURVETYPE_CIRCLE = 2
    CURVETYPE_ELLIPSE = 3
    CURVETYPE_NURBS = 4
    CURVETYPE_PROCEDURAL = 5


class Edge:
    """Represents a single edge of a body within the design assembly.

    This class synchronizes to a design within a supporting Geometry service instance.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    curve_type : CurveType
        Type of curve that the edge forms.
    body : Body
        Parent body that the edge constructs.
    grpc_client : GrpcClient
        Active supporting Geometry service instance for design modeling.
    is_reversed : bool
        Direction of the edge.
    """

    def __init__(
        self,
        id: str,
        curve_type: CurveType,
        body: "Body",
        grpc_client: GrpcClient,
        is_reversed: bool = False,
    ):
        """Initialize the ``Edge`` class."""
        self._id = id
        self._curve_type = curve_type
        self._body = body
        self._grpc_client = grpc_client
        self._is_reversed = is_reversed
        self._shape = None

    @property
    def id(self) -> str:
        """ID of the edge."""
        return self._id

    @property
    def body(self) -> "Body":
        """Body of the edge."""
        return self._body

    @property
    def is_reversed(self) -> bool:
        """Flag indicating if the edge is reversed."""
        return self._is_reversed

    @property
    @ensure_design_is_active
    @min_backend_version(24, 2, 0)
    def shape(self) -> TrimmedCurve:
        """Underlying trimmed curve of the edge.

        If the edge is reversed, its shape is the ``ReversedTrimmedCurve`` type, which swaps the
        start and end points of the curve and handles parameters to allow evaluation as if the
        curve is not reversed.

        Warnings
        --------
        This method is only available starting on Ansys release 24R2.
        """
        if self._shape is None:
            self._grpc_client.log.debug("Requesting edge properties from server.")
            geometry = self._grpc_client.services.edges.get_curve(id=self._id).get("curve")

            response = self._grpc_client.services.edges.get_start_and_end_points(id=self._id)
            start = response.get("start")
            end = response.get("end")

            length = self._grpc_client.services.edges.get_length(id=self._id).get("length")

            response = self._grpc_client.services.edges.get_interval(id=self._id)
            interval = Interval(response.get("start"), response.get("end"))

            self._shape = (
                ReversedTrimmedCurve(geometry, start, end, interval, length.value)
                if self.is_reversed
                else TrimmedCurve(geometry, start, end, interval, length.value)
            )
        return self._shape

    @property
    @ensure_design_is_active
    def length(self) -> Quantity:
        """Calculated length of the edge."""
        try:
            return self.shape.length
        except GeometryRuntimeError:  # pragma: no cover
            # Only for versions earlier than 24.2.0 (before the introduction of the shape property)
            self._grpc_client.log.debug("Requesting edge length from server.")
            return self._grpc_client.services.edges.get_length(id=self._id).get("length").value

    @property
    def curve_type(self) -> CurveType:
        """Curve type of the edge."""
        return self._curve_type

    @property
    @ensure_design_is_active
    def faces(self) -> list["Face"]:
        """Faces that contain the edge."""
        from ansys.geometry.core.designer.face import Face, SurfaceType

        self._grpc_client.log.debug("Requesting edge faces from server.")
        response = self._grpc_client.services.edges.get_faces(id=self._id)
        return [
            Face(
                face_resp.get("id"),
                SurfaceType(face_resp.get("surface_type")),
                self._body,
                self._grpc_client,
                face_resp.get("is_reversed"),
            )
            for face_resp in response.get("faces")
        ]

    @property
    @ensure_design_is_active
    @min_backend_version(26, 1, 0)
    def vertices(self) -> list["Vertex"]:
        """Vertices that define the edge."""
        from ansys.geometry.core.designer.vertex import Vertex

        self._grpc_client.log.debug("Requesting edge vertices from server.")
        response = self._grpc_client.services.edges.get_vertices(id=self._id)

        return [
            Vertex(
                vertex_resp.get("id"),
                vertex_resp.get("position"),
                self.body,
            )
            for vertex_resp in response.get("vertices")
        ]

    @property
    @ensure_design_is_active
    def start(self) -> Point3D:
        """Start point of the edge."""
        try:
            return self.shape.start
        except GeometryRuntimeError:  # pragma: no cover
            # Only for versions earlier than 24.2.0 (before the introduction of the shape property)
            self._grpc_client.log.debug("Requesting edge start point from server.")
            return self._grpc_client.services.edges.get_start_and_end_points(id=self._id).get(
                "start"
            )

    @property
    @ensure_design_is_active
    def end(self) -> Point3D:
        """End point of the edge."""
        try:
            return self.shape.end
        except GeometryRuntimeError:  # pragma: no cover
            # Only for versions earlier than 24.2.0 (before the introduction of the shape property)
            self._grpc_client.log.debug("Requesting edge end point from server.")
            return self._grpc_client.services.edges.get_start_and_end_points(id=self._id).get("end")

    @property
    @ensure_design_is_active
    @min_backend_version(25, 2, 0)
    def bounding_box(self) -> BoundingBox:
        """Bounding box of the edge.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        self._grpc_client.log.debug("Requesting bounding box from server.")

        response = self._grpc_client.services.edges.get_bounding_box(id=self._id)
        return BoundingBox(
            response.get("min_corner"), response.get("max_corner"), response.get("center")
        )

    @ensure_design_is_active
    def get_named_selections(self) -> list["NamedSelection"]:
        """Get named selections associated with the edge.
        
        Returns
        -------
        list[NamedSelection]
            List of named selections that include the edge.
        """
        named_selections = get_design_from_body(self.body).named_selections
        
        included_ns = []
        for ns in named_selections:
            if self in ns.edges:
                included_ns.append(ns)

        return included_ns
