"""``Body`` class module."""

from typing import TYPE_CHECKING

from ansys.api.geometry.v0.bodies_pb2 import SetAssignedMaterialRequest
from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub

from ansys.geometry.core.connection.client import GrpcClient
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

    def assign_material(self, material: Material) -> None:
        self._bodies_stub.SetAssignedMaterial(
            SetAssignedMaterialRequest(id=self._id, material=material._display_name)
        )
