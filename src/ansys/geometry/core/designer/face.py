"""``Face`` class module."""

from enum import Enum
from typing import TYPE_CHECKING

from ansys.api.geometry.v0.faces_pb2 import FaceIdentifier
from ansys.api.geometry.v0.faces_pb2_grpc import FacesStub
from pint import Quantity

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.misc import SERVER_UNIT_AREA

if TYPE_CHECKING:
    from ansys.geometry.core.designer.body import Body


class SurfaceType(Enum):
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
