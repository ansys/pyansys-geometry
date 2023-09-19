"""Module for managing an edge."""

from enum import Enum, unique

from ansys.api.geometry.v0.edges_pb2_grpc import EdgesStub
from ansys.api.geometry.v0.models_pb2 import EntityIdentifier
from beartype.typing import TYPE_CHECKING, List
from pint import Quantity

from ansys.geometry.core.connection import GrpcClient, grpc_curve_to_curve
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.geometry.curves.trimmed_curve import ReversedTrimmedCurve, TrimmedCurve
from ansys.geometry.core.math import Point3D
from ansys.geometry.core.misc import DEFAULT_UNITS
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.face import Face


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
    """

    def __init__(
        self,
        id: str,
        curve_type: CurveType,
        body: "Body",
        grpc_client: GrpcClient,
        is_reversed: bool = False,
    ):
        """Initialize ``Edge`` class."""
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
        """Entity identifier of this edge on the server side."""
        return EntityIdentifier(id=self._id)

    @property
    def is_reversed(self) -> bool:
        """Edge is reversed."""
        return self._is_reversed

    @property
    def shape(self) -> TrimmedCurve:
        """
        Underlying trimmed curve of the edge.

        If the edge is reversed, its shape will be a `ReversedTrimmedCurve`, which swaps the
        start and end points of the curve and handles parameters to allow evaluation as if the
        curve is not reversed.
        """
        if self._shape is None:
            self._grpc_client.log.debug("Requesting edge properties from server.")
            response = self._edges_stub.GetCurve(self._grpc_id)
            geometry = grpc_curve_to_curve(response, self.curve_type)
            self._shape = (
                ReversedTrimmedCurve(self, geometry)
                if self.is_reversed
                else TrimmedCurve(self, geometry)
            )
        return self._shape

    @property
    @protect_grpc
    def length(self) -> Quantity:
        """Calculated length of the edge."""
        self._grpc_client.log.debug("Requesting edge length from server.")
        length_response = self._edges_stub.GetLength(self._grpc_id)
        return Quantity(length_response.length, DEFAULT_UNITS.SERVER_LENGTH)

    @property
    def curve_type(self) -> CurveType:
        """Curve type of the edge."""
        return self._curve_type

    @property
    @protect_grpc
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

    def evaluate_proportion_remove_this(self, param: Real) -> Point3D:
        """
        Evaluate the edge at a given proportion, a value in the range [0, 1].

        Parameters
        ----------
        param: Real
            The parameter at which to evaluate the edge.
        Returns
        -------
        Point3D
            The position of the evaluation.
        """
        return self.shape.evaluate(param)
