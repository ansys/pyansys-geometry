# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
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
"""Module for managing a face."""

from enum import Enum, unique

from ansys.api.geometry.v0.edges_pb2_grpc import EdgesStub
from ansys.api.geometry.v0.faces_pb2 import EvaluateRequest, GetNormalRequest
from ansys.api.geometry.v0.faces_pb2_grpc import FacesStub
from ansys.api.geometry.v0.models_pb2 import Edge as GRPCEdge
from ansys.api.geometry.v0.models_pb2 import EntityIdentifier
from beartype.typing import TYPE_CHECKING, List
from pint import Quantity

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.designer.edge import CurveType, Edge
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body


@unique
class SurfaceType(Enum):
    """Provides values for the surface types supported by the Geometry service."""

    SURFACETYPE_UNKNOWN = 0
    SURFACETYPE_PLANE = 1
    SURFACETYPE_CYLINDER = 2
    SURFACETYPE_CONE = 3
    SURFACETYPE_TORUS = 4
    SURFACETYPE_SPHERE = 5
    SURFACETYPE_NURBS = 6
    SURFACETYPE_PROCEDURAL = 7


@unique
class FaceLoopType(Enum):
    """Provides values for the face loop types supported by the Geometry service."""

    INNER_LOOP = "INNER"
    OUTER_LOOP = "OUTER"


class FaceLoop:
    """
    Provides an internal class holding the face loops defined on the server side.

    Notes
    -----
    This class is to be used only when parsing server side results. It is not
    intended to be instantiated by a user.

    Parameters
    ----------
    type : FaceLoopType
        Type of loop.
    length : Quantity
        Length of the loop.
    min_bbox : Point3D
        Minimum point of the bounding box containing the loop.
    max_bbox : Point3D
        Maximum point of the bounding box containing the loop.
    edges : List[Edge]
        Edges contained in the loop.
    """

    def __init__(
        self,
        type: FaceLoopType,
        length: Quantity,
        min_bbox: Point3D,
        max_bbox: Point3D,
        edges: List[Edge],
    ):
        """Initialize ``FaceLoop`` class."""
        self._type = type
        self._length = length
        self._min_bbox = min_bbox
        self._max_bbox = max_bbox
        self._edges = edges

    @property
    def type(self) -> FaceLoopType:
        """Type of the loop."""
        return self._type

    @property
    def length(self) -> Quantity:
        """Length of the loop."""
        return self._length

    @property
    def min_bbox(self) -> Point3D:
        """Minimum point of the bounding box containing the loop."""
        return self._min_bbox

    @property
    def max_bbox(self) -> Point3D:
        """Maximum point of the bounding box containing the loop."""
        return self._max_bbox

    @property
    def edges(self) -> List[Edge]:
        """Edges contained in the loop."""
        return self._edges


class Face:
    """
    Represents a single face of a body within the design assembly.

    This class synchronizes to a design within a supporting Geometry service instance.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    surface_type : SurfaceType
        Type of surface that the face forms.
    body : Body
        Parent body that the face constructs.
    grpc_client : GrpcClient
        Active supporting Geometry service instance for design modeling.
    """

    def __init__(self, id: str, surface_type: SurfaceType, body: "Body", grpc_client: GrpcClient):
        """Initialize ``Face`` class."""
        self._id = id
        self._surface_type = surface_type
        self._body = body
        self._grpc_client = grpc_client
        self._faces_stub = FacesStub(grpc_client.channel)
        self._edges_stub = EdgesStub(grpc_client.channel)

    @property
    def id(self) -> str:
        """Face ID."""
        return self._id

    @property
    def _grpc_id(self) -> EntityIdentifier:
        """Entity identifier of this face on the server side."""
        return EntityIdentifier(id=self._id)

    @property
    def body(self) -> "Body":
        """Body that the face belongs to."""
        return self._body

    @property
    @protect_grpc
    def area(self) -> Quantity:
        """Calculated area of the face."""
        self._grpc_client.log.debug("Requesting face area from server.")
        area_response = self._faces_stub.GetArea(self._grpc_id)
        return Quantity(area_response.area, DEFAULT_UNITS.SERVER_AREA)

    @property
    def surface_type(self) -> SurfaceType:
        """Surface type of the face."""
        return self._surface_type

    @property
    @protect_grpc
    def edges(self) -> List[Edge]:
        """List of all edges of the face."""
        self._grpc_client.log.debug("Requesting face edges from server.")
        edges_response = self._faces_stub.GetEdges(self._grpc_id)
        return self.__grpc_edges_to_edges(edges_response.edges)

    @property
    @protect_grpc
    def loops(self) -> List[FaceLoop]:
        """List of all loops of the face."""
        self._grpc_client.log.debug("Requesting face loops from server.")
        grpc_loops = self._faces_stub.GetLoops(EntityIdentifier(id=self.id)).loops
        loops = []
        for grpc_loop in grpc_loops:
            type = FaceLoopType(grpc_loop.type)
            length = Quantity(grpc_loop.length, DEFAULT_UNITS.SERVER_LENGTH)
            min = Point3D(
                [
                    grpc_loop.bounding_box.min.x,
                    grpc_loop.bounding_box.min.y,
                    grpc_loop.bounding_box.min.z,
                ],
                DEFAULT_UNITS.SERVER_LENGTH,
            )
            max = Point3D(
                [
                    grpc_loop.bounding_box.max.x,
                    grpc_loop.bounding_box.max.y,
                    grpc_loop.bounding_box.max.z,
                ],
                DEFAULT_UNITS.SERVER_LENGTH,
            )
            grpc_edges = [
                self._edges_stub.Get(EntityIdentifier(id=edge_id)) for edge_id in grpc_loop.edges
            ]
            edges = self.__grpc_edges_to_edges(grpc_edges)
            loops.append(
                FaceLoop(type=type, length=length, min_bbox=min, max_bbox=max, edges=edges)
            )

        return loops

    @protect_grpc
    def face_normal(self, u: float = 0.5, v: float = 0.5) -> UnitVector3D:
        """
        Get the normal direction to the face evaluated at certain UV coordinates.

        Notes
        -----
        To properly use this method, you must handle UV coordinates. Thus, you must
        know how these relate to the underlying Geometry service. It is an advanced
        method for Geometry experts only.

        Parameters
        ----------
        u : float, default: 0.5
            First coordinate of the 2D representation of a surface in UV space.
            The default is ``0.5``, which is the center of the surface.
        v : float, default: 0.5
            Second coordinate of the 2D representation of a surface in UV space.
            The default is ``0.5``, which is the center of the surface.

        Returns
        -------
        UnitVector3D
            :class:`UnitVector3D` object evaluated at the given U and V coordinates.
            This :class:`UnitVector3D` object is perpendicular to the surface at the
            given UV coordinates.
        """
        self._grpc_client.log.debug(f"Requesting face normal from server with (u,v)=({u},{v}).")
        response = self._faces_stub.GetNormal(GetNormalRequest(id=self.id, u=u, v=v)).direction
        return UnitVector3D([response.x, response.y, response.z])

    @protect_grpc
    def face_point(self, u: float = 0.5, v: float = 0.5) -> Point3D:
        """
        Get a point of the face evaluated at certain UV coordinates.

        Notes
        -----
        To properly use this method, you must handle UV coordinates. Thus, you must
        know how these relate to the underlying Geometry service. It is an advanced
        method for Geometry experts only.

        Parameters
        ----------
        u : float, default: 0.5
            First coordinate of the 2D representation of a surface in UV space.
            The default is ``0.5``, which is the center of the surface.
        v : float, default: 0.5
            Second coordinate of the 2D representation of a surface in UV space.
            The default is ``0.5``, which is the center of the surface.

        Returns
        -------
        Point3D
            :class:`Point3D`
            object evaluated at the given UV coordinates.
        """
        self._grpc_client.log.debug(f"Requesting face point from server with (u,v)=({u},{v}).")
        response = self._faces_stub.Evaluate(EvaluateRequest(id=self.id, u=u, v=v)).point
        return Point3D([response.x, response.y, response.z], DEFAULT_UNITS.SERVER_LENGTH)

    def __grpc_edges_to_edges(self, edges_grpc: List[GRPCEdge]) -> List[Edge]:
        """
        Transform a list of gRPC edge messages into actual ``Edge`` objects.

        Parameters
        ----------
        edges_grpc : List[GRPCEdge]
            List of gRPC messages of type ``Edge``.

        Returns
        -------
        List[Edge]
            ``Edge`` objects to obtain from gRPC messages.
        """
        edges = []
        for edge_grpc in edges_grpc:
            edges.append(
                Edge(edge_grpc.id, CurveType(edge_grpc.curve_type), self._body, self._grpc_client)
            )
        return edges
