"""``Face`` class module."""

from enum import Enum
from typing import TYPE_CHECKING

from ansys.api.geometry.v0.edges_pb2 import EdgeIdentifier
from ansys.api.geometry.v0.edges_pb2_grpc import EdgesStub
import numpy as np

from ansys.geometry.core.connection.client import GrpcClient

if TYPE_CHECKING:
    from ansys.geometry.core.designer.body import Body


class CurveType(Enum):
    CURVETYPE_UNKNOWN = 0
    CURVETYPE_LINE = 1
    CURVETYPE_CIRCLE = 2
    CURVETYPE_ELLIPSE = 3
    CURVETYPE_NURBS = 4
    CURVETYPE_PROCEDURAL = 5


class Edge:
    """
    Represents a single edge of a body within the design assembly.

    Synchronizes to a design within a supporting geometry service instance.

    Parameters
    ----------
    id : str
        A server defined identifier for the body.
    curve_type : CurveType
        Specifies what type of curve the edge forms.
    body : Body
        The parent body the edge constructs.
    grpc_client : GrpcClient
        An active supporting geometry service instance for design modeling.
    """

    def __init__(self, id: str, curve_type: CurveType, body: "Body", grpc_client: GrpcClient):
        """Constructor method for ``Face``."""

        self._id = id
        self._curve_type = curve_type
        self._body = body
        self._grpc_client = grpc_client
        self._length = np.nan
        self._edges_stub = EdgesStub(grpc_client.channel)

    @property
    def length(self) -> float:
        """Calculated length of the edge."""
        if self._length == np.nan:
            length_response = self._edges_stub.GetEdgeLength(EdgeIdentifier(id=self._id))
            self._length = length_response.length
        return self._length

    @property
    def curve_type(self) -> CurveType:
        """Curve type of the edge."""
        return self._curve_type
