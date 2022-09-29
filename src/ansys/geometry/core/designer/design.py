"""``Design`` class module."""

from pathlib import Path
from typing import List, Optional, Union

from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from ansys.api.geometry.v0.designs_pb2 import NewDesignRequest, SaveAsDocumentRequest
from ansys.api.geometry.v0.designs_pb2_grpc import DesignsStub
from ansys.api.geometry.v0.materials_pb2 import AddMaterialToDocumentRequest
from ansys.api.geometry.v0.materials_pb2_grpc import MaterialsStub
from ansys.api.geometry.v0.models_pb2 import Empty
from ansys.api.geometry.v0.models_pb2 import Material as GRPCMaterial
from ansys.api.geometry.v0.models_pb2 import MaterialProperty as GRPCMaterialProperty
from ansys.api.geometry.v0.namedselections_pb2 import NamedSelectionIdentifier
from ansys.api.geometry.v0.namedselections_pb2_grpc import NamedSelectionsStub

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.designer.component import Component, SharedTopologyType
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
        self._commands_stub = CommandsStub(self._grpc_client.channel)
        self._materials_stub = MaterialsStub(self._grpc_client.channel)
        self._named_selections_stub = NamedSelectionsStub(self._grpc_client.channel)

        new_design = self._design_stub.New(NewDesignRequest(name=name))
        self._id = new_design.id

        self._materials = []
        self._named_selections = {}

    @property
    def materials(self) -> List[Material]:
        """List of available ``Material`` objects for our ``Design``."""
        return self._materials

    @property
    def named_selections(self) -> List[NamedSelection]:
        """List of available ``NamedSelection`` objects for our ``Design``."""
        return list(self._named_selections.values())

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
                    name=material.name,
                    materialProperties=[
                        GRPCMaterialProperty(
                            id=property.type.value,
                            displayName=property.name,
                            value=property.quantity.m,
                            units=format(property.quantity.units),
                        )
                        for property in material.properties.values()
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

    def download(self, file_location: Path, as_stream: Optional[bool] = False) -> None:
        """Downloads a design from the active geometry server instance.

        Parameters
        ----------
        file_location : Path
            Full path of the location on disk where the file should be saved.
        as_stream : bool, optional
            Boolean indicating whether we should use the gRPC stream functionality
            or the single message approach. By default, ``False``
        """
        # Sanity checks on inputs
        check_type(file_location, Path)

        # Process response (as stream or single file)
        received_bytes = bytes()
        if as_stream:
            response_iterator = self._commands_stub.DownloadFileStream(Empty())
            for response in response_iterator:
                received_bytes += response.chunk
        else:
            response = self._commands_stub.DownloadFile(Empty())
            received_bytes += response.data

        # Write to file
        downloaded_file = open(file_location, "wb")
        downloaded_file.write(received_bytes)
        downloaded_file.close()

    def create_named_selection(
        self,
        name: str,
        bodies: Optional[List[Body]] = [],
        faces: Optional[List[Face]] = [],
        edges: Optional[List[Edge]] = [],
    ) -> NamedSelection:
        """Creates a named selection on the active geometry server instance.

        Parameters
        ----------
        name : str
            A user-defined name for the named selection.
        bodies : List[Body], optional
            All bodies that should be included in the named selection.
            By default, ``[]``.
        faces : List[Face], optional
            All faces that should be included in the named selection.
            By default, ``[]``.
        edges : List[Edge], optional
            All edges that should be included in the named selection.
            By default, ``[]``.

        Returns
        -------
        NamedSelection
            A newly created named selection maintaining references to all target entities.
        """
        named_selection = NamedSelection(
            name, self._grpc_client, bodies=bodies, faces=faces, edges=edges
        )
        self._named_selections[named_selection.name] = named_selection
        return self._named_selections[named_selection.name]

    def delete_named_selection(self, named_selection: Union[NamedSelection, str]) -> None:
        """Removes a named selection on the active geometry server instance.

        Parameters
        ----------
        named_selection : Union[NamedSelection, str]
            A named selection name or instance that should be deleted.
        """
        check_type(named_selection, (NamedSelection, str))

        removal_name = (
            named_selection.name if not isinstance(named_selection, str) else named_selection
        )
        self._named_selections_stub.Delete(NamedSelectionIdentifier(name=removal_name))

        try:
            self._named_selections.pop(removal_name)
        except KeyError:
            # TODO: throw warning informing that the requested NamedSelection does not exist
            pass

    def delete_component(self, component: Union["Component", str]) -> None:
        """Deletes an existing component (itself or its children).

        Notes
        -----
        If the component is not this component (or its children), it
        will not be deleted.

        Parameters
        ----------
        id : Union[Component, str]
            The name of the component or instance that should be deleted.

        Raises
        ------
        ValueError
            ``Design`` itself cannot be deleted.
        """
        check_type(component, (Component, str))
        id = component.id if not isinstance(component, str) else component
        if id == self.id:
            raise ValueError("The Design object itself cannot be deleted.")
        else:
            return super().delete_component(component)

    def set_shared_topology(self, share_type: SharedTopologyType) -> None:
        """Defines the shared topology to be applied to the component.

        Parameters
        ----------
        share_type : SharedTopologyType
            The shared topology type to be assigned to the component.

        Raises
        ------
        ValueError
            Shared topology does not apply on ``Design``.
        """
        raise ValueError("The Design object itself cannot have a shared topology.")

    def tessellate(self, merge_design=False, merge_components=False):
        """Tessellate the design.

        Parameters
        ----------
        merge_design : bool, optional
            Merge the entire design into a single dataset. This effectively
            destroys the hierarchy of the design.
        merge_component : bool, default: False
            Merge each component into a single dataset. This effectively
            combines all the individual bodies into a single dataset without
            any hierarchy for each component.
        merge_bodies : bool, default: False
            Merge each body into a single dataset. This effectively combines
            all the faces of each individual body into a single dataset
            without separating faces.

        Returns
        -------
        pyvista.PolyData, pyvista.MultiBlock
            Merged :class:`pyvista.PolyData` if ``merge_component=True`` or
            composite dataset.

        Examples
        --------
        Create a three bodies in two different components return the
        tessellation of the entire design.

        >>> from ansys.geometry.core.sketch import Sketch
        >>> from ansys.geometry.core import Modeler
        >>> from ansys.geometry.core.math import Point, Plane
        >>> from ansys.geometry.core.misc import UNITS
        >>> from ansys.geometry.core.plotting.plotter import Plotter
        >>> modeler = Modeler()
        >>> sketch_1 = Sketch()
        >>> sketch_1.draw_box(Point([10, 10, 0]), width=10, height=5)
        >>> sketch_1.draw_circle(Point([0, 0, 0]), radius=25 * UNITS.m)
        >>> design = modeler.create_design("MyDesign-0")
        >>> comp = design.add_component("MyComponent-0")
        >>> comp.extrude_sketch("MyBody-0", sketch=sketch_1, distance=10 * UNITS.m)
        >>> sketch_2 = Sketch(Plane([0, 0, 10]))
        >>> sketch_2.draw_box(Point([10, 10, 10]), width=10, height=5)
        >>> sketch_2.draw_circle(Point([0, 0, 10]), radius=25 * UNITS.m)
        >>> comp.extrude_sketch("MyBody-1", sketch=sketch_2, distance=10 * UNITS.m)
        >>> sketch_3 = Sketch()
        >>> sketch_3.draw_circle(Point([29, 29, 0]), radius=15 * UNITS.m)
        >>> sketch_3.draw_circle(Point([29, 29, 0]), radius=16 * UNITS.m)
        >>> comp = design.add_component("MyComponent-1")
        >>> comp.extrude_sketch("MyBody-2", sketch=sketch_3, distance=10 * UNITS.m)
        >>> dataset = design.tessellate()
        MultiBlock (0x7fcfd40d6920)
          N Blocks:     2
          X Bounds:     -25.000, 45.000
          Y Bounds:     -24.991, 44.999
          Z Bounds:     0.000, 20.000

        """
        import pyvista as pv

        datasets = pv.MultiBlock(
            [component.tessellate(merge_components) for component in self.components]
        )
        if merge_design:
            return datasets.combine()
        return datasets

    def plot(
        self,
        merge_design: bool = False,
        merge_components: bool = False,
        merge_bodies: bool = False,
        **kwargs: Optional[dict]
    ) -> None:
        """Plot the entire design.

        Parameters
        ----------
        merge_design : bool, optional
            Merge the entire design into a single dataset. This effectively
            destroys the hierarchy of the design.
        merge_component : bool, default: False
            Merge each component into a single dataset. This effectively
            combines all the individual bodies into a single dataset without
            any hierarchy for each component.
        merge_bodies : bool, default: False
            Merge each body into a single dataset. This effectively combines
            all the faces of each individual body into a single dataset
            without separating faces.
        **kwargs : dict, optional
            Optional keyword arguments. See :func:`pyvista.Plotter.add_mesh`
            for allowable keyword arguments.

        Examples
        --------
        Create a three bodies in two different components return the
        tessellation of the entire design.

        >>> from ansys.geometry.core.sketch import Sketch
        >>> from ansys.geometry.core import Modeler
        >>> from ansys.geometry.core.math import Point, Plane
        >>> from ansys.geometry.core.misc import UNITS
        >>> from ansys.geometry.core.plotting.plotter import Plotter
        >>> modeler = Modeler()
        >>> sketch_1 = Sketch()
        >>> sketch_1.draw_box(Point([10, 10, 0]), width=10, height=5)
        >>> sketch_1.draw_circle(Point([0, 0, 0]), radius=25 * UNITS.m)
        >>> design = modeler.create_design("MyDesign-0")
        >>> comp = design.add_component("MyComponent-0")
        >>> comp.extrude_sketch("MyBody-0", sketch=sketch_1, distance=10 * UNITS.m)
        >>> sketch_2 = Sketch(Plane([0, 0, 10]))
        >>> sketch_2.draw_box(Point([10, 10, 10]), width=10, height=5)
        >>> sketch_2.draw_circle(Point([0, 0, 10]), radius=25 * UNITS.m)
        >>> comp.extrude_sketch("MyBody-1", sketch=sketch_2, distance=10 * UNITS.m)
        >>> sketch_3 = Sketch()
        >>> sketch_3.draw_circle(Point([29, 29, 0]), radius=15 * UNITS.m)
        >>> sketch_3.draw_circle(Point([29, 29, 0]), radius=16 * UNITS.m)
        >>> comp = design.add_component("MyComponent-1")
        >>> comp.extrude_sketch("MyBody-2", sketch=sketch_3, distance=10 * UNITS.m)
        >>> dataset = design.plot()

        """
        from ansys.geometry.core.plotting.plotter import Plotter

        pl = Plotter()
        pl.add_design(self, **kwargs)
        pl.show()
