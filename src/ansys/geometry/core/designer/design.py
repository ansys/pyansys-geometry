"""``Design`` class module."""

from ansys.api.geometry.v0.designs_pb2 import NewDesignRequest, SaveAsDocumentRequest
from ansys.api.geometry.v0.designs_pb2_grpc import DesignsStub
from ansys.api.geometry.v0.materials_pb2 import AddMaterialToDocumentRequest
from ansys.api.geometry.v0.materials_pb2_grpc import MaterialsStub
from ansys.api.geometry.v0.models_pb2 import Material as GRPCMaterial
from ansys.api.geometry.v0.models_pb2 import MaterialProperty as GRPCMaterialProperty

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.designer.component import Component
from ansys.geometry.core.materials import Material
from ansys.geometry.core.misc import check_type


class Design(Component):
    """
    Provides a ``Design`` for organizing geometry assemblies.

    Synchronizes to a supporting geometry service instance.

    Parameters
    ----------
    name : str
        A user-defined label for the design.
    grpc_client : GrpcClient
        An active supporting geometry service instance for design modeling.
    """

    def __init__(self, name: str, grpc_client: GrpcClient):
        """Constructor method for ``Design``."""
        super().__init__(name, None, grpc_client)

        self._design_stub = DesignsStub(self._grpc_client.channel)
        self._materials_stub = MaterialsStub(self._grpc_client.channel)

        new_design = self._design_stub.New(NewDesignRequest(name=name))
        self._id = new_design.id

        self._materials = []

    @property
    def name(self) -> str:
        """Name of the ``Design``."""
        return self._name

    # TODO: allow for list of materials
    def add_material(self, material: Material) -> None:
        """Adds a ``Material`` to the ``Design``

        Parameters
        ----------
        material : Material
            ``Material`` to be added.
        """
        # Sanity check
        check_type(material, Material)

        # TODO: Add design id to the request
        self._materials_stub.AddMaterialToDocument(
            AddMaterialToDocumentRequest(
                material=GRPCMaterial(
                    name=material._display_name,
                    materialProperties=[
                        GRPCMaterialProperty(
                            id=property.type.value,
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

    def save(self, file_location: str) -> None:
        """Saves a design to disk on the active geometry server instance.

        Parameters
        ----------
        file_location : str
            Full path of the location on disk where the file should be saved.
        """
        # Sanity checks on inputs
        check_type(file_location, str)

        self._design_stub.SaveAs(SaveAsDocumentRequest(filepath=file_location))
