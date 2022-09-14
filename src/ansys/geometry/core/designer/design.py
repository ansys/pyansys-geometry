"""``Design`` class module."""

from ansys.api.geometry.v0.board_pb2 import AddMaterialToDocumentRequest, Empty
from ansys.api.geometry.v0.board_pb2 import MaterialProperty as GRPCMaterialProperty
from ansys.api.geometry.v0.board_pb2_grpc import BoardStub

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.designer.component import Component
from ansys.geometry.core.materials.material import Material
from ansys.geometry.core.sketch import Sketch


class Design:
    """
    Provides Design class for organizing 3D geometry design projects.

    Synchronizes to a server.

    Parameters
    ----------
    id : str
        An identifier defined by the source geometry service.

    """

    def __init__(self, name: str, grpc_client: GrpcClient):
        """Constructor method for ``Design``."""
        self._grpc_client = grpc_client
        self._design_stub = BoardStub(self._grpc_client.channel)

        # TODO: add name to design
        new_design = self._design_stub.New(Empty())

        self._id = new_design.moniker
        self._root_component = Component("new_design.name", None, self._grpc_client)
        self._root_component.id = self._id
        self._materials = []

    # TODO: allow for list of materials
    def add_material(self, material: Material) -> None:
        # TODO: Add design id to the request
        self._design_stub.AddMaterialToDocument(
            AddMaterialToDocumentRequest(
                name=material._display_name,
                density=0.0,  # TODO remove 0 density when proto updates
                materialProperties=[
                    GRPCMaterialProperty(
                        id=property.id,
                        displayName=property.display_name,
                        value=property.quantity.m,
                        units=None,  # units=format(mat.quantity.units)
                    )
                    for property in material.properties
                ],
            )
        )
        self._materials.append(material)

    def add_component(self, name: str):
        self._root_component.add_component(name)

    def extrude_sketch(self, component: Component, sketch: Sketch):
        return None
