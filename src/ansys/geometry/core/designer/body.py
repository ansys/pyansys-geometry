"""``Body`` class module."""

from typing import TYPE_CHECKING, List

from ansys.api.geometry.v0.bodies_pb2 import BodyIdentifier, SetAssignedMaterialRequest
from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
import numpy as np

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.materials import Material

if TYPE_CHECKING:
    from ansys.geometry.core.designer.component import Component


class Body:
    """
    Represents solids and surfaces organized within the design assembly.

    Synchronizes to a design within a supporting geometry service instance.

    Parameters
    ----------
    id : str
        A server defined identifier for the body.
    name : str
        A user-defined label for the body.
    parent_component : Component
        The parent component to nest the new component under within the design assembly.
    grpc_client : GrpcClient
        An active supporting geometry service instance for design modeling.
    """

    def __init__(self, id: str, name: str, parent_component: "Component", grpc_client: GrpcClient):
        """Constructor method for ``Body``."""

        self._id = id
        self._name = name
        self._parent_component = parent_component
        self._grpc_client = grpc_client
        self._bodies_stub = BodiesStub(self._grpc_client.channel)
        self._volume = np.nan
        self._edges = []

    @property
    def volume(self) -> float:
        """Calculated volume of the face."""
        if self._volume == np.nan:
            volume_response = self._bodies_stub.GetVolume(BodyIdentifier(id=self._id))
            self._volume = volume_response.volume
        return self._area

    def assign_material(self, material: Material) -> None:
        """Sets the provided material against the design in the active geometry service instance.

        Parameters
        ----------
        material : Material
            Source material data.
        """
        self._bodies_stub.SetAssignedMaterial(
            SetAssignedMaterialRequest(id=self._id, material=material._display_name)
        )

    @property
    def faces(self) -> List[Face]:
        """Lazy-loads all of the faces within the body.

        Returns
        ----------
        List[Face]
        """
        if self._edges.count == 0:
            grpc_faces = self._bodies_stub.GetFaces(BodyIdentifier(id=self._id))

            self._edges = [
                Face(grpc_face.id, grpc_face.surface_type, self, self._grpc_client)
                for grpc_face in grpc_faces
            ]

        return self._edges
