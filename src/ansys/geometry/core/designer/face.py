"""``Face`` class module."""

from enum import Enum
from typing import TYPE_CHECKING, List

from ansys.api.geometry.v0.faces_pb2 import FaceIdentifier
from ansys.api.geometry.v0.faces_pb2_grpc import FacesStub
from ansys.api.geometry.v0.models_pb2 import Edge as GRPCEdge
from pint import Quantity

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.misc import SERVER_UNIT_AREA

if TYPE_CHECKING:
    from ansys.geometry.core.designer.body import Body


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

    @property
    def id(self) -> str:
        """ID of the face."""
        return self._id

    @property
    def area(self) -> Quantity:
        """Calculated area of the face."""
        area_response = self._faces_stub.GetFaceArea(FaceIdentifier(id=self._id))
        return Quantity(area_response.area, SERVER_UNIT_AREA)

    @property
    def surface_type(self) -> SurfaceType:
        """Surface type of the face."""
        return self._surface_type

    @property
    def edges(self) -> List[Edge]:
        """Get all ``Edge`` objects of our ``Face``."""
        edges_response = self._faces_stub.GetFaceEdges(FaceIdentifier(id=self._id))
        return self.__from_grpc_edges_to_edges(edges_response.edges)

    def __from_grpc_edges_to_edges(self, edges_grpc: List[GRPCEdge]) -> List[Edge]:
        """Transform a list of gRPC Edge messages into actual ``Edge`` objects.

        Parameters
        ----------
        edges_grpc : List[GRPCEdge]
            A list of gRPC messages of type Edge.

        Returns
        -------
        List[Edge]
            ``Edge`` objects constituting the ``Face``.
        """
        edges = []
        for edge_grpc in edges_grpc:
            edges.append(Edge(edge_grpc.id, edge_grpc.curve_type, self._body, self._grpc_client))
        return edges
