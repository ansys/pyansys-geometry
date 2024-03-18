# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
from ansys.api.geometry.v0.edges_pb2_grpc import EdgesStub
from beartype.typing import TYPE_CHECKING, List, Union
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.conversions import grpc_curve_to_curve
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.logger import LOG
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.misc.checks import ensure_design_is_active
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS
from ansys.geometry.core.shapes.curves.trimmed_curve import ReversedTrimmedCurve, TrimmedCurve
from ansys.geometry.core.shapes.parameterization import Interval

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.face import Face
    from ansys.geometry.core.shapes.curves.circle import Circle
    from ansys.geometry.core.shapes.curves.ellipse import Ellipse


@unique
class CurveType(Enum):
    """Provides values for the curve types supported by the Geometry service."""

    CURVETYPE_UNKNOWN = 0
    CURVETYPE_LINE = 1
    CURVETYPE_CIRCLE = 2
    CURVETYPE_ELLIPSE = 3
    CURVETYPE_NURBS = 4
    CURVETYPE_PROCEDURAL = 5


class Edge:
    """
    Represents a single edge of a body within the design assembly.

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
        self._edges_stub = EdgesStub(grpc_client.channel)
        self._is_reversed = is_reversed
        self._shape = None

    @property
    def id(self) -> str:
        """ID of the edge."""
        return self._id

    @property
    def _grpc_id(self) -> EntityIdentifier:
        """Entity ID of this edge on the server side."""
        return EntityIdentifier(id=self._id)

    @property
    def is_reversed(self) -> bool:
        """Flag indicating if the edge is reversed."""
        return self._is_reversed

    @property
    def shape(self) -> TrimmedCurve:
        """
        Underlying trimmed curve of the edge.

        If the edge is reversed, its shape is the ``ReversedTrimmedCurve`` type, which swaps the
        start and end points of the curve and handles parameters to allow evaluation as if the
        curve is not reversed.
        """
        if self._shape is None:
            self._grpc_client.log.debug("Requesting edge properties from server.")
            response = self._edges_stub.GetCurve(self._grpc_id)
            geometry = grpc_curve_to_curve(response)

            response = self._edges_stub.GetStartAndEndPoints(self._grpc_id)
            start = Point3D([response.start.x, response.start.y, response.start.z])
            end = Point3D([response.end.x, response.end.y, response.end.z])

            response = self._edges_stub.GetLength(self._grpc_id)
            length = Quantity(response.length, DEFAULT_UNITS.SERVER_LENGTH)

            response = self._edges_stub.GetInterval(self._grpc_id)
            interval = Interval(response.start, response.end)

            self._shape = (
                ReversedTrimmedCurve(geometry, start, end, interval, length)
                if self.is_reversed
                else TrimmedCurve(geometry, start, end, interval, length)
            )
        return self._shape

    @property
    @protect_grpc
    @ensure_design_is_active
    def length(self) -> Quantity:
        """Calculated length of the edge."""
        return self.shape.length

    @property
    def curve_type(self) -> CurveType:
        """Curve type of the edge."""
        return self._curve_type

    @property
    @protect_grpc
    @ensure_design_is_active
    def faces(self) -> List["Face"]:
        """Faces that contain the edge."""
        from ansys.geometry.core.designer.face import Face, SurfaceType

        self._grpc_client.log.debug("Requesting edge faces from server.")
        grpc_faces = self._edges_stub.GetFaces(self._grpc_id).faces
        return [
            Face(
                grpc_face.id,
                SurfaceType(grpc_face.surface_type),
                self._body,
                self._grpc_client,
                grpc_face.is_reversed,
            )
            for grpc_face in grpc_faces
        ]

    @property
    @protect_grpc
    def start_point(self) -> Point3D:
        """Edge start point."""
        self._grpc_client.log.debug("Requesting edge points from server.")
        point = self._edges_stub.GetStartAndEndPoints(self._grpc_id).start
        return Point3D([point.x, point.y, point.z])

    @property
    @protect_grpc
    def end_point(self) -> Point3D:
        """Edge end point."""
        self._grpc_client.log.debug("Requesting edge points from server.")
        point = self._edges_stub.GetStartAndEndPoints(self._grpc_id).end
        return Point3D([point.x, point.y, point.z])

    def to_polydata(self) -> Union[pv.PolyData, None]:
        """
        Return the edge as polydata.

        This is useful to represent the edge in a PyVista plotter.

        Returns
        -------
        Union[pv.PolyData, None]
            Edge as polydata
        """
        if (
            self._curve_type == CurveType.CURVETYPE_UNKNOWN
            or self._curve_type == CurveType.CURVETYPE_LINE
        ):
            return pv.Line(pointa=self.start_point, pointb=self.end_point)
        elif self._curve_type == CurveType.CURVETYPE_CIRCLE:
            self.shape.geometry: Circle
            point_a = self.shape.geometry.evaluate(0)
            circle = pv.CircularArc(
                center=list(self.shape.geometry.origin),
                pointa=list(point_a.position),
                pointb=list(point_a.position),
                negative=True,
            )
            return circle

        elif self._curve_type == CurveType.CURVETYPE_ELLIPSE:
            self.shape.geometry: Ellipse
            ellipse = pv.Ellipse(
                semi_major_axis=self.shape.geometry.major_radius.magnitude,
                semi_minor_axis=self.shape.geometry.minor_radius.magnitude,
            )
            ellipse = ellipse.translate(list(self.shape.geometry.origin))
            return ellipse
        else:
            LOG.warning("Non linear edges not supported.")
            return None
