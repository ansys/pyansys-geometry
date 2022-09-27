"""``Face`` class module."""

from enum import Enum, unique
from typing import TYPE_CHECKING, List

from ansys.api.geometry.v0.edges_pb2 import EdgeIdentifier
from ansys.api.geometry.v0.edges_pb2_grpc import EdgesStub
from ansys.api.geometry.v0.faces_pb2 import (
    FaceIdentifier,
    GetFaceLoopsRequest,
    GetFaceNormalRequest,
)
from ansys.api.geometry.v0.faces_pb2_grpc import FacesStub
from ansys.api.geometry.v0.models_pb2 import Edge as GRPCEdge
from pint import Quantity

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.designer.edge import CurveType, Edge
from ansys.geometry.core.math import Point, UnitVector
from ansys.geometry.core.misc import SERVER_UNIT_AREA
from ansys.geometry.core.misc.measurements import SERVER_UNIT_LENGTH

if TYPE_CHECKING:
    from ansys.geometry.core.designer.body import Body  # pragma: no cover


@unique
class SurfaceType(Enum):
    """Enum holding the possible values for surface types by the geometry service."""

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
    """Enum holding the possible values for face loop types."""

    INNER_LOOP = "INNER"
    OUTER_LOOP = "OUTER"


class FaceLoop:
    """Internal class to hold ``Face`` loops defined by the server side.

    Notes
    -----
    This class is to be used only when parsing server side results. It is not
    intended to be instantiated by a user.

    Parameters
    ----------
    type : FaceLoopType
        The type of loop defined.
    length : Quantity
        The length of the loop.
    min_bbox : Point
        The minimum point of the bounding box containing the loop.
    max_bbox : Point
        The maximum point of the bounding box containing the loop.
    edges : List[Edge]
        The edges contained in the loop.
    """

    def __init__(
        self,
        type: FaceLoopType,
        length: Quantity,
        min_bbox: Point,
        max_bbox: Point,
        edges: List[Edge],
    ):

        self._type = type
        self._length = length
        self._min_bbox = min_bbox
        self._max_bbox = max_bbox
        self._edges = edges

    @property
    def type(self) -> FaceLoopType:
        """Type of face loop."""
        return self._type

    @property
    def length(self) -> Quantity:
        """Length of the loop."""
        return self._length

    @property
    def min_bbox(self) -> Point:
        """Minimum point of the bounding box containing the loop."""
        return self._min_bbox

    @property
    def max_bbox(self) -> Point:
        """Maximum point of the bounding box containing the loop."""
        return self._max_bbox

    @property
    def edges(self) -> List[Edge]:
        """Edges contained the loop."""
        return self._edges


class Face:
    """
    Represents a single face of a body within the design assembly.

    Synchronizes to a design within a supporting geometry service instance.

    Parameters
    ----------
    id : str
        A server defined identifier for the body.
    surface_type : SurfaceType
        Specifies what type of surface the face forms.
    body : Body
        The parent body the face constructs.
    grpc_client : GrpcClient
        An active supporting geometry service instance for design modeling.
    """

    def __init__(self, id: str, surface_type: SurfaceType, body: "Body", grpc_client: GrpcClient):
        """Constructor method for ``Face``."""

        self._id = id
        self._surface_type = surface_type
        self._body = body
        self._grpc_client = grpc_client
        self._faces_stub = FacesStub(grpc_client.channel)
        self._edges_stub = EdgesStub(grpc_client.channel)

    @property
    def id(self) -> str:
        """ID of the face."""
        return self._id

    @property
    def area(self) -> Quantity:
        """Calculated area of the face."""
        area_response = self._faces_stub.GetFaceArea(FaceIdentifier(id=self.id))
        return Quantity(area_response.area, SERVER_UNIT_AREA)

    @property
    def surface_type(self) -> SurfaceType:
        """Surface type of the face."""
        return self._surface_type

    @property
    def edges(self) -> List[Edge]:
        """Get all ``Edge`` objects of our ``Face``."""
        edges_response = self._faces_stub.GetFaceEdges(FaceIdentifier(id=self.id))
        return self.__grpc_edges_to_edges(edges_response.edges)

    @property
    def normal(self) -> UnitVector:
        """Normal direction to the ``Face``."""
        response = self._faces_stub.GetFaceNormal(
            GetFaceNormalRequest(id=self.id, u=0.5, v=0.5)
        ).direction
        return UnitVector([response.x, response.y, response.z])

    @property
    def loops(self) -> List[FaceLoop]:
        """Face loops of the ``Face``."""
        grpc_loops = self._faces_stub.GetFaceLoops(GetFaceLoopsRequest(face=self.id)).loops
        loops = []
        for grpc_loop in grpc_loops:
            type = FaceLoopType(grpc_loop.type)
            length = Quantity(grpc_loop.length, SERVER_UNIT_LENGTH)
            min = Point(
                [
                    grpc_loop.boundingBox.min.x,
                    grpc_loop.boundingBox.min.y,
                    grpc_loop.boundingBox.min.z,
                ],
                SERVER_UNIT_LENGTH,
            )
            max = Point(
                [
                    grpc_loop.boundingBox.max.x,
                    grpc_loop.boundingBox.max.y,
                    grpc_loop.boundingBox.max.z,
                ],
                SERVER_UNIT_LENGTH,
            )
            grpc_edges = [
                self._edges_stub.GetEdge(EdgeIdentifier(id=edge_id)) for edge_id in grpc_loop.edges
            ]
            edges = self.__grpc_edges_to_edges(grpc_edges)
            loops.append(
                FaceLoop(type=type, length=length, min_bbox=min, max_bbox=max, edges=edges)
            )

        return loops

    def __grpc_edges_to_edges(self, edges_grpc: List[GRPCEdge]) -> List[Edge]:
        """Transform a list of gRPC Edge messages into actual ``Edge`` objects.

        Parameters
        ----------
        edges_grpc : List[GRPCEdge]
            A list of gRPC messages of type Edge.

        Returns
        -------
        List[Edge]
            ``Edge`` objects obtained from gRPC messages.
        """
        edges = []
        for edge_grpc in edges_grpc:
            edges.append(
                Edge(edge_grpc.id, CurveType(edge_grpc.curve_type), self._body, self._grpc_client)
            )
        return edges
