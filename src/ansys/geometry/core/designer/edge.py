"""Module for managing an edge."""

from enum import Enum, unique

from ansys.api.geometry.v0.edges_pb2 import EvaluateRequest
from ansys.api.geometry.v0.edges_pb2_grpc import EdgesStub
from ansys.api.geometry.v0.models_pb2 import EntityIdentifier
from beartype.typing import TYPE_CHECKING, List
from pint import Quantity

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.geometry.curves.circle import Circle
from ansys.geometry.core.geometry.curves.curve import Curve
from ansys.geometry.core.geometry.curves.ellipse import Ellipse
from ansys.geometry.core.geometry.curves.line import Line
from ansys.geometry.core.geometry.curves.trimmed_curve import TrimmedCurve
from ansys.geometry.core.math import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
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
        self._shape = TrimmedCurve(self)
        # request the underlying curve from the server
        self._grpc_client.log.debug("Requesting edge properties from server.")
        curve_response = self._edges_stub.GetCurve(self._grpc_id)
        origin = Point3D(
            [curve_response.origin.x, curve_response.origin.y, curve_response.origin.z]
        )
        # check if the curve is a circle or ellipse
        if (
            self.curve_type == CurveType.CURVETYPE_CIRCLE
            or self.curve_type == CurveType.CURVETYPE_ELLIPSE
        ):
            axis_response = curve_response.axis
            reference_response = curve_response.reference
            axis = UnitVector3D([axis_response.x, axis_response.y, axis_response.z])
            reference = UnitVector3D(
                [reference_response.x, reference_response.y, reference_response.z]
            )
            if self.curve_type == CurveType.CURVETYPE_CIRCLE:
                # circle
                self._curve = Circle(origin, curve_response.radius, reference, axis)
            else:
                # ellipse
                self._curve = Ellipse(
                    origin,
                    curve_response.major_radius,
                    curve_response.minor_radius,
                    reference,
                    axis,
                )
        elif self.curve_type == CurveType.CURVETYPE_LINE:
            # line
            self._curve = Line(
                origin,
                UnitVector3D(
                    [
                        curve_response.direction.x,
                        curve_response.direction.y,
                        curve_response.direction.z,
                    ]
                ),
            )
        else:
            self._curve = None

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
    def curve(self) -> Curve:
        """Internal curve object."""
        return self._curve

    @property
    def shape(self) -> TrimmedCurve:
        """Internal Trimmed Curve object."""
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

    @protect_grpc
    def evaluate_proportion(self, param: Real) -> Point3D:
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
        response = self._edges_stub.EvaluateProportion(
            EvaluateRequest(id=self.id, param=param)
        ).point
        return Point3D([response.x, response.y, response.z], DEFAULT_UNITS.SERVER_LENGTH)
