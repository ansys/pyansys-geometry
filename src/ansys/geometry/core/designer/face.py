"""``Face`` class module."""

from enum import Enum, unique

from ansys.api.geometry.v0.edges_pb2_grpc import EdgesStub
from ansys.api.geometry.v0.faces_pb2 import (
    EvaluateRequest,
    GetNormalRequest,
)
from ansys.api.geometry.v0.faces_pb2_grpc import FacesStub
from ansys.api.geometry.v0.models_pb2 import Edge as GRPCEdge
from ansys.api.geometry.v0.models_pb2 import EntityIdentifier
from beartype.typing import TYPE_CHECKING, List
from pint import Quantity

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.designer.edge import CurveType, Edge
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.math import Point3D, UnitVector3D
from ansys.geometry.core.misc import SERVER_UNIT_AREA, SERVER_UNIT_LENGTH

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body


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
    min_bbox : Point3D
        The minimum point of the bounding box containing the loop.
    max_bbox : Point3D
        The maximum point of the bounding box containing the loop.
    edges : List[Edge]
        The edges contained in the loop.
    """

    def __init__(
        self,
        type: FaceLoopType,
        length: Quantity,
        min_bbox: Point3D,
        max_bbox: Point3D,
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
    def _grpc_id(self) -> EntityIdentifier:
        """gRPC face identifier."""
        return EntityIdentifier(id=self._id)

    @property
    def body(self) -> "Body":
        """The body to which the face belongs."""
        return self._body

    @property
    @protect_grpc
    def area(self) -> Quantity:
        """Calculated area of the face."""
        self._grpc_client.log.debug("Requesting face area from server.")
        area_response = self._faces_stub.GetArea(self._grpc_id)
        return Quantity(area_response.area, SERVER_UNIT_AREA)

    @property
    def surface_type(self) -> SurfaceType:
        """Surface type of the face."""
        return self._surface_type

    @property
    @protect_grpc
    def edges(self) -> List[Edge]:
        """Get all ``Edge`` objects of our ``Face``."""
        self._grpc_client.log.debug("Requesting face edges from server.")
        edges_response = self._faces_stub.GetEdges(self._grpc_id)
        return self.__grpc_edges_to_edges(edges_response.edges)

    @property
    @protect_grpc
    def loops(self) -> List[FaceLoop]:
        """Face loops of the ``Face``."""
        self._grpc_client.log.debug("Requesting face loops from server.")
        grpc_loops = self._faces_stub.GetLoops(EntityIdentifier(id=self.id)).loops
        loops = []
        for grpc_loop in grpc_loops:
            type = FaceLoopType(grpc_loop.type)
            length = Quantity(grpc_loop.length, SERVER_UNIT_LENGTH)
            min = Point3D(
                [
                    grpc_loop.boundingBox.min.x,
                    grpc_loop.boundingBox.min.y,
                    grpc_loop.boundingBox.min.z,
                ],
                SERVER_UNIT_LENGTH,
            )
            max = Point3D(
                [
                    grpc_loop.boundingBox.max.x,
                    grpc_loop.boundingBox.max.y,
                    grpc_loop.boundingBox.max.z,
                ],
                SERVER_UNIT_LENGTH,
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
        """Normal direction to the ``Face`` evaluated at certain UV coordinates.

        Notes
        -----
        In order to properly use this API, please consider that you must
        handle UV coordinates and thus know how these relate to the
        underlying Geometry Service. It is an advanced API for Geometry
        experts only.

        Parameters
        ----------
        u : float
            First coordinate of the 2D representation of a surface in UV space.
            By default, 0.5 (i.e. the center of the surface)
        v : float
            Second coordinate of the 2D representation of a surface in UV space.
            By default, 0.5 (i.e. the center of the surface)

        Returns
        -------
        UnitVector3D
            The :class:`UnitVector3D <ansys.geometry.core.math.vector.unitVector3D>`
            object evaluated at the given U and V coordinates.
            This :class:`UnitVector3D <ansys.geometry.core.math.vector.unitVector3D>`
            will be perpendicular to the surface at that
            given UV coordinates.
        """
        self._grpc_client.log.debug(f"Requesting face normal from server with (u,v)=({u},{v}).")
        response = self._faces_stub.GetNormal(
            GetNormalRequest(id=self.id, u=u, v=v)
        ).direction
        return UnitVector3D([response.x, response.y, response.z])

    @protect_grpc
    def face_point(self, u: float = 0.5, v: float = 0.5) -> Point3D:
        """Returns a point of the ``Face`` evaluated with UV coordinates.

        Notes
        -----
        In order to properly use this API, please consider that you must
        handle UV coordinates and thus know how these relate to the
        underlying Geometry Service. It is an advanced API for Geometry
        experts only.

        Parameters
        ----------
        u : float
            First coordinate of the 2D representation of a surface in UV space.
            By default, 0.5.
        v : float
            Second coordinate of the 2D representation of a surface in UV space.
            By default, 0.5.

        Returns
        -------
        Point
            The :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
            object evaluated at the given U and V coordinates.
        """
        self._grpc_client.log.debug(f"Requesting face point from server with (u,v)=({u},{v}).")
        response = self._faces_stub.Evaluate(EvaluateRequest(id=self.id, u=u, v=v)).point
        return Point3D([response.x, response.y, response.z], SERVER_UNIT_LENGTH)

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
