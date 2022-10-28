"""``Design`` class module."""

from enum import Enum
from pathlib import Path

from ansys.api.geometry.v0.commands_pb2 import CreateBeamCircularProfileRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from ansys.api.geometry.v0.designs_pb2 import (
    ExportDesignRequest,
    NewDesignRequest,
    SaveAsDocumentRequest,
)
from ansys.api.geometry.v0.designs_pb2_grpc import DesignsStub
from ansys.api.geometry.v0.materials_pb2 import AddMaterialToDocumentRequest
from ansys.api.geometry.v0.materials_pb2_grpc import MaterialsStub
from ansys.api.geometry.v0.models_pb2 import Empty
from ansys.api.geometry.v0.models_pb2 import Material as GRPCMaterial
from ansys.api.geometry.v0.models_pb2 import MaterialProperty as GRPCMaterialProperty
from ansys.api.geometry.v0.models_pb2 import PartExportFormat
from ansys.api.geometry.v0.namedselections_pb2 import NamedSelectionIdentifier
from ansys.api.geometry.v0.namedselections_pb2_grpc import NamedSelectionsStub
from beartype import beartype as check_input_types
from beartype.typing import List, Optional, Union
import numpy as np
from pint import Quantity

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.connection.conversions import plane_to_grpc_plane, point3d_to_grpc_point
from ansys.geometry.core.designer.beam import BeamCircularProfile, BeamProfile
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.designer.component import Component, SharedTopologyType
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.designer.selection import NamedSelection
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.materials import Material
from ansys.geometry.core.math import (
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    ZERO_POINT3D,
    Plane,
    Point3D,
    UnitVector3D,
    Vector3D,
)
from ansys.geometry.core.misc import SERVER_UNIT_LENGTH, Distance
from ansys.geometry.core.typing import RealSequence


class DesignFileFormat(Enum):
    """Available file formats supported by the Design class for download."""

    SCDOCX = "SCDOCX", None
    PARASOLID_TEXT = "PARASOLID_TEXT", PartExportFormat.PARTEXPORTFORMAT_PARASOLID_TEXT
    PARASOLID_BIN = "PARASOLID_BIN", PartExportFormat.PARTEXPORTFORMAT_PARASOLID_BINARY
    INVALID = "INVALID", None


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

    # Types of the class instance private attributes
    _materials: List[Material]
    _named_selections: List[NamedSelection]
    _beam_profiles: List[BeamProfile]

    @protect_grpc
    @check_input_types
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
        self._beam_profiles = {}

        self._grpc_client.log.debug("Design object instantiated successfully.")

    @property
    def materials(self) -> List[Material]:
        """List of available ``Material`` objects for our ``Design``."""
        return self._materials

    @property
    def named_selections(self) -> List[NamedSelection]:
        """List of available ``NamedSelection`` objects for our ``Design``."""
        return list(self._named_selections.values())

    @property
    def beam_profiles(self) -> List[BeamProfile]:
        """List of available ``BeamProfile`` objects for our ``Design``."""
        return list(self._beam_profiles.values())

    # TODO: allow for list of materials
    @protect_grpc
    @check_input_types
    def add_material(self, material: Material) -> None:
        """Adds a ``Material`` to the ``Design``

        Parameters
        ----------
        material : Material
            ``Material`` to be added.
        """
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

        self._grpc_client.log.debug(f"Material {material.name} successfully added to design.")

    @protect_grpc
    @check_input_types
    def save(self, file_location: Union[Path, str]) -> None:
        """Saves a design to disk on the active geometry server instance.

        Parameters
        ----------
        file_location : Union[Path, str]
            Location on disk where the file should be saved.
        """
        # Sanity checks on inputs
        if isinstance(file_location, Path):
            file_location = str(file_location)

        self._design_stub.SaveAs(SaveAsDocumentRequest(filepath=file_location))
        self._grpc_client.log.debug(f"Design successfully saved at location {file_location}.")

    @protect_grpc
    @check_input_types
    def download(
        self,
        file_location: Union[Path, str],
        format: Optional[DesignFileFormat] = DesignFileFormat.SCDOCX,
        as_stream: Optional[bool] = False,
    ) -> None:
        """Downloads a design from the active geometry server instance.

        Parameters
        ----------
        file_location : Union[Path, str]
            Location on disk where the file should be saved.
        format : Optional[DesignFileFormat]
            Format in which to export the design. By default, as an ``SCDOCX`` file.
        as_stream : bool, default: False
            Boolean indicating whether to use the gRPC stream functionality (if possible).
            or the single message approach.
        """
        # Sanity checks on inputs
        if isinstance(file_location, Path):
            file_location = str(file_location)

        # Process response (as stream or single file)
        stream_msg = f"Downloading design in {format.value[0]} format using stream mechanism."
        single_msg = (
            f"Downloading design in {format.value[0]} format using single-message mechanism."
        )
        received_bytes = bytes()
        if format is DesignFileFormat.SCDOCX:
            if as_stream:
                self._grpc_client.log.debug(stream_msg)
                response_iterator = self._commands_stub.DownloadFileStream(Empty())
                for response in response_iterator:
                    received_bytes += response.chunk
            else:
                self._grpc_client.log.debug(single_msg)
                response = self._commands_stub.DownloadFile(Empty())
                received_bytes += response.data
        elif (format is DesignFileFormat.PARASOLID_TEXT) or (
            format is DesignFileFormat.PARASOLID_BIN
        ):
            if as_stream:
                self._grpc_client.log.warning(
                    "Streaming mechanism not supported for Parasolid format."
                )
            self._grpc_client.log.debug(single_msg)
            response = self._design_stub.ExportDesign(ExportDesignRequest(format=format.value[1]))
            received_bytes += response.data
        else:
            self._grpc_client.log.warning(
                f"{format.value[0]} format requested not supported. Ignoring download request."
            )
            return

        # Write to file
        downloaded_file = open(file_location, "wb")
        downloaded_file.write(received_bytes)
        downloaded_file.close()

        self._grpc_client.log.debug(f"Design successfully downloaded at location {file_location}.")

    @check_input_types
    def create_named_selection(
        self,
        name: str,
        bodies: Optional[List[Body]] = None,
        faces: Optional[List[Face]] = None,
        edges: Optional[List[Edge]] = None,
    ) -> NamedSelection:
        """Creates a named selection on the active geometry server instance.

        Parameters
        ----------
        name : str
            A user-defined name for the named selection.
        bodies : List[Body], default: None
            All bodies that should be included in the named selection.
        faces : List[Face], default: None
            All faces that should be included in the named selection.
        edges : List[Edge], default: None
            All edges that should be included in the named selection.

        Returns
        -------
        NamedSelection
            A newly created named selection maintaining references to all target entities.
        """
        named_selection = NamedSelection(
            name, self._grpc_client, bodies=bodies, faces=faces, edges=edges
        )
        self._named_selections[named_selection.name] = named_selection

        self._grpc_client.log.debug(f"Named selection {named_selection.name} successfully created.")

        return self._named_selections[named_selection.name]

    @protect_grpc
    @check_input_types
    def delete_named_selection(self, named_selection: Union[NamedSelection, str]) -> None:
        """Removes a named selection on the active geometry server instance.

        Parameters
        ----------
        named_selection : Union[NamedSelection, str]
            A named selection name or instance that should be deleted.
        """
        removal_name = (
            named_selection.name if not isinstance(named_selection, str) else named_selection
        )
        self._named_selections_stub.Delete(NamedSelectionIdentifier(name=removal_name))

        try:
            self._named_selections.pop(removal_name)
            self._grpc_client.log.debug(f"Named selection {removal_name} successfully deleted.")
        except KeyError:
            self._grpc_client.log.warning(
                f"Attempted named selection deletion failed, with name {removal_name}."
                + " Ignoring request."
            )
            pass

    @check_input_types
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

    @protect_grpc
    @check_input_types
    def add_beam_circular_profile(
        self,
        name: str,
        radius: Union[Quantity, Distance],
        center: Union[np.ndarray, RealSequence, Point3D] = ZERO_POINT3D,
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Y,
    ) -> BeamCircularProfile:
        """
        Creates a new ``BeamCircularProfile`` under the design for future
        creation of ``Beam`` entities.

        Parameters
        ----------
        name : str
            User-defined label identifying the ``BeamCircularProfile``
        radius : Real
            Radius of the ``BeamCircularProfile``.
        center : Union[~numpy.ndarray, RealSequence, Point3D]
            Center of the ``BeamCircularProfile``.
        direction_x : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
            X-plane direction.
        direction_y : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
            Y-plane direction.
        """
        dir_x = direction_x if isinstance(direction_x, UnitVector3D) else UnitVector3D(direction_x)
        dir_y = direction_y if isinstance(direction_y, UnitVector3D) else UnitVector3D(direction_y)
        radius = radius if isinstance(radius, Distance) else Distance(radius)

        if radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

        if not dir_x.is_perpendicular_to(dir_y):
            raise ValueError("Direction x and direction y must be perpendicular.")

        request = CreateBeamCircularProfileRequest(
            origin=point3d_to_grpc_point(center),
            radius=radius.value.m_as(SERVER_UNIT_LENGTH),
            plane=plane_to_grpc_plane(Plane(center, dir_x, dir_y)),
            name=name,
        )

        self._grpc_client.log.debug(f"Creating beam circular profile on {self.id}...")

        response = self._commands_stub.CreateBeamCircularProfile(request)
        profile = BeamCircularProfile(response.id, name, radius, center, dir_x, dir_y)
        self._beam_profiles[profile.name] = profile

        self._grpc_client.log.debug(f"Beam circular profile {profile.name} successfully created.")

        return self._beam_profiles[profile.name]

    def __repr__(self):
        """String representation of the design."""
        alive_bodies = [1 if body.is_alive else 0 for body in self.bodies]
        alive_comps = [1 if comp.is_alive else 0 for comp in self.components]
        lines = [f"ansys.geometry.core.designer.Design {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  N Bodies             : {sum(alive_bodies)}")
        lines.append(f"  N Components         : {sum(alive_comps)}")
        lines.append(f"  N Coordinate Systems : {len(self.coordinate_systems)}")
        lines.append(f"  N Named Selections   : {len(self.named_selections)}")
        lines.append(f"  N Materials          : {len(self.materials)}")
        lines.append(f"  N Beam Profiles      : {len(self.beam_profiles)}")
        return "\n".join(lines)
