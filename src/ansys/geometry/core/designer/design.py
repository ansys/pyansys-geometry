"""``Design`` class module."""

from typing import List, Union

from ansys.api.geometry.v0.designs_pb2 import NewDesignRequest, SaveAsDocumentRequest
from ansys.api.geometry.v0.designs_pb2_grpc import DesignsStub
from ansys.api.geometry.v0.materials_pb2 import AddMaterialToDocumentRequest
from ansys.api.geometry.v0.materials_pb2_grpc import MaterialsStub
from ansys.api.geometry.v0.models_pb2 import Material as GRPCMaterial
from ansys.api.geometry.v0.models_pb2 import MaterialProperty as GRPCMaterialProperty
from ansys.api.geometry.v0.namedselections_pb2 import NamedSelectionIdentifier
from ansys.api.geometry.v0.namedselections_pb2_grpc import NamedSelectionsStub

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.designer.component import Component
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.designer.selection import NamedSelection
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
        self._named_selections = []

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

    def create_named_selection(
        self, name: str, bodies: List[Body], faces: List[Face], edges: List[Edge]
    ) -> NamedSelection:
        """Creates a named selection on the active geometry server instance.

        Parameters
        ----------
        name : str
            A user-defined name for the named selection.
        bodies : List[Body]
            All bodies that should be included in the named selection.
        faces : List[Face]
            All faces that should be included in the named selection.
        edges : List[Edge]
            All edges that should be included in the named selection.

        Returns
        -------
        NamedSelection
            A newly created named selection maintaining references to all target entities.
        """
        check_type(name, str)

        self._named_selections.append(NamedSelection(name, self._grpc_client, bodies, faces, edges))
        return self._named_selections[-1]

    def delete_named_selection(self, named_selection: Union[NamedSelection, str]) -> None:
        """Removes a named selection on the active geometry server instance.

        Parameters
        ----------
        named_selection : Union[NamedSelection, str]
            A named selection id or instance that should be deleted.
        """
        check_type(named_selection, Union[NamedSelection, str])

        removal_id = named_selection.id if not isinstance(named_selection, str) else named_selection

        named_selections_stub = NamedSelectionsStub(self._grpc_client.channel)
        named_selections_stub.Delete(NamedSelectionIdentifier(id=removal_id))

        try:
            self._named_selections.remove(removal_id)
        except ValueError:
            pass  # if the value is not in the list, not an issue to handle as asking to remove
