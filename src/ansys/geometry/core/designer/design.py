"""``Design`` class module."""

from ansys.api.geometry.v0.designs_pb2 import NewDesignRequest, SaveAsDocumentRequest
from ansys.api.geometry.v0.designs_pb2_grpc import DesignsStub
from ansys.api.geometry.v0.materials_pb2 import AddMaterialToDocumentRequest
from ansys.api.geometry.v0.materials_pb2_grpc import MaterialsStub
from ansys.api.geometry.v0.models_pb2 import Material as GRPCMaterial
from ansys.api.geometry.v0.models_pb2 import MaterialProperty as GRPCMaterialProperty
from pint import Quantity

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
        self._design_stub = DesignsStub(self._grpc_client.channel)
        self._materials_stub = MaterialsStub(self._grpc_client.channel)

        new_design = self._design_stub.New(NewDesignRequest(name=name))

        self._id = new_design.id
        self._root_component = Component(new_design.name, None, self._grpc_client)
        self._root_component.id = self._id
        self._materials = []

    # TODO: allow for list of materials
    def add_material(self, material: Material) -> None:
        # TODO: Add design id to the request
        self._materials_stub.AddMaterialToDocument(
            AddMaterialToDocumentRequest(
                material=GRPCMaterial(
                    name=material._display_name,
                    materialProperties=[
                        GRPCMaterialProperty(
                            id=property.id,
                            displayName=property.display_name,
                            value=property.quantity.m,
                            units=format(property.quantity.units),
                        )
                        for property in material.properties
                    ],
                )
            )
        )
        self._materials.append(material)

    def add_component(self, name: str):
        self._root_component.add_component(name)

    def extrude_sketch(self, name: str, sketch: Sketch, distance: Quantity):
        return self._root_component.extrude_profile(name, sketch, distance)

    def save(self, file_location: str):
        self._design_stub.SaveAs(SaveAsDocumentRequest(file_location))
