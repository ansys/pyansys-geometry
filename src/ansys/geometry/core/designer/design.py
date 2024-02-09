# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Provides for managing designs."""

from enum import Enum, unique
from pathlib import Path

from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier, PartExportFormat
from ansys.api.dbu.v0.designs_pb2 import NewRequest, SaveAsRequest
from ansys.api.dbu.v0.designs_pb2_grpc import DesignsStub
from ansys.api.geometry.v0.commands_pb2 import (
    AssignMidSurfaceOffsetTypeRequest,
    AssignMidSurfaceThicknessRequest,
    CreateBeamCircularProfileRequest,
)
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from ansys.api.geometry.v0.materials_pb2 import AddToDocumentRequest
from ansys.api.geometry.v0.materials_pb2_grpc import MaterialsStub
from ansys.api.geometry.v0.models_pb2 import Material as GRPCMaterial
from ansys.api.geometry.v0.models_pb2 import MaterialProperty as GRPCMaterialProperty
from ansys.api.geometry.v0.namedselections_pb2_grpc import NamedSelectionsStub
from ansys.api.geometry.v0.parts_pb2 import ExportRequest
from ansys.api.geometry.v0.parts_pb2_grpc import PartsStub
from beartype import beartype as check_input_types
from beartype.typing import Dict, List, Optional, Union
from google.protobuf.empty_pb2 import Empty
import numpy as np
from pint import Quantity, UndefinedUnitError

from ansys.geometry.core.connection.conversions import (
    grpc_frame_to_frame,
    grpc_matrix_to_matrix,
    plane_to_grpc_plane,
    point3d_to_grpc_point,
)
from ansys.geometry.core.designer.beam import Beam, BeamCircularProfile, BeamProfile
from ansys.geometry.core.designer.body import Body, MasterBody, MidSurfaceOffsetType
from ansys.geometry.core.designer.component import Component, SharedTopologyType
from ansys.geometry.core.designer.coordinate_system import CoordinateSystem
from ansys.geometry.core.designer.designpoint import DesignPoint
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.designer.part import MasterComponent, Part
from ansys.geometry.core.designer.selection import NamedSelection
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.materials.material import Material
from ansys.geometry.core.materials.property import MaterialProperty, MaterialPropertyType
from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Y, ZERO_POINT3D
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.checks import ensure_design_is_active
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Distance
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.typing import RealSequence


@unique
class DesignFileFormat(Enum):
    """Provides supported file formats that can be downloaded for designs."""

    SCDOCX = "SCDOCX", None
    PARASOLID_TEXT = "PARASOLID_TEXT", PartExportFormat.PARTEXPORTFORMAT_PARASOLID_TEXT
    PARASOLID_BIN = "PARASOLID_BIN", PartExportFormat.PARTEXPORTFORMAT_PARASOLID_BINARY
    FMD = "FMD", PartExportFormat.PARTEXPORTFORMAT_FMD
    STEP = "STEP", PartExportFormat.PARTEXPORTFORMAT_STEP
    IGES = "IGES", PartExportFormat.PARTEXPORTFORMAT_IGES
    PMDB = "PMDB", PartExportFormat.PARTEXPORTFORMAT_PMDB
    INVALID = "INVALID", None


class Design(Component):
    """
    Provides for organizing geometry assemblies.

    This class synchronizes to a supporting Geometry service instance.

    Parameters
    ----------
    name : str
        User-defined label for the design.
    grpc_client : GrpcClient
        Active supporting Geometry service instance for design modeling.
    read_existing_design : bool, default: False
        Whether an existing design on the service should be read. This parameter is
        only valid when connecting to an existing service session. Otherwise, avoid
        using this optional parameter.
    """

    # Types of the class instance private attributes
    _materials: List[Material]
    _named_selections: Dict[str, NamedSelection]
    _beam_profiles: Dict[str, BeamProfile]

    @protect_grpc
    @check_input_types
    def __init__(self, name: str, modeler: Modeler, read_existing_design: bool = False):
        """Initialize the ``Design`` class."""
        super().__init__(name, None, modeler.client)

        # Initialize the stubs needed
        self._design_stub = DesignsStub(self._grpc_client.channel)
        self._commands_stub = CommandsStub(self._grpc_client.channel)
        self._materials_stub = MaterialsStub(self._grpc_client.channel)
        self._named_selections_stub = NamedSelectionsStub(self._grpc_client.channel)
        self._parts_stub = PartsStub(self._grpc_client.channel)

        # Initialize needed instance variables
        self._materials = []
        self._named_selections = {}
        self._beam_profiles = {}
        self._design_id = ""
        self._is_active = False
        self._modeler = modeler

        # Check whether we want to process an existing design or create a new one.
        if read_existing_design:
            self._grpc_client.log.debug("Reading Design object from service.")
            self.__read_existing_design()
        else:
            new_design = self._design_stub.New(NewRequest(name=name))
            self._design_id = new_design.id
            self._id = new_design.main_part.id
            self._activate(called_after_design_creation=True)
            self._grpc_client.log.debug("Design object instantiated successfully.")

    @property
    def design_id(self) -> str:
        """The design's object unique id."""
        return self._design_id

    @property
    def materials(self) -> List[Material]:
        """List of materials available for the design."""
        return self._materials

    @property
    def named_selections(self) -> List[NamedSelection]:
        """List of named selections available for the design."""
        return list(self._named_selections.values())

    @property
    def beam_profiles(self) -> List[BeamProfile]:
        """List of beam profile available for the design."""
        return list(self._beam_profiles.values())

    @property
    def is_active(self) -> bool:
        """Whether the design is currently active."""
        return self._is_active

    @protect_grpc
    def _activate(self, called_after_design_creation: bool = False) -> None:
        """Activate the design."""
        # Deactivate all designs first
        for design in self._modeler._designs.values():
            design._is_active = False

        # Activate the current design
        if not called_after_design_creation:
            self._design_stub.PutActive(EntityIdentifier(id=self._design_id))
        self._is_active = True
        self._grpc_client.log.debug(f"Design {self.name} is activated.")

    # TODO: allow for list of materials
    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def add_material(self, material: Material) -> None:
        """
        Add a material to the design.

        Parameters
        ----------
        material : Material
            Material to add.
        """
        # TODO: Add design id to the request
        self._materials_stub.AddToDocument(
            AddToDocumentRequest(
                material=GRPCMaterial(
                    name=material.name,
                    material_properties=[
                        GRPCMaterialProperty(
                            id=property.type.value,
                            display_name=property.name,
                            value=property.quantity.m,
                            units=format(property.quantity.units),
                        )
                        for property in material.properties.values()
                    ],
                )
            )
        )
        self._materials.append(material)

        self._grpc_client.log.debug(f"Material {material.name} is successfully added to design.")

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def save(self, file_location: Union[Path, str]) -> None:
        """
        Save a design to disk on the active Geometry server instance.

        Parameters
        ----------
        file_location : Union[~pathlib.Path, str]
            Location on disk to save the file to.
        """
        # Sanity checks on inputs
        if isinstance(file_location, Path):
            file_location = str(file_location)

        self._design_stub.SaveAs(SaveAsRequest(filepath=file_location))
        self._grpc_client.log.debug(f"Design successfully saved at location {file_location}.")

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def download(
        self,
        file_location: Union[Path, str],
        format: Optional[DesignFileFormat] = DesignFileFormat.SCDOCX,
    ) -> None:
        """
        Export and download the design from the active Geometry server instance.

        Parameters
        ----------
        file_location : Union[~pathlib.Path, str]
            Location on disk to save the file to.
        format :DesignFileFormat, default: DesignFileFormat.SCDOCX
            Format for the file to save to.
        """
        # Sanity checks on inputs
        if isinstance(file_location, Path):
            file_location = str(file_location)

        # Check if the folder for the file location exists
        if not Path(file_location).parent.exists():
            # Create the parent directory
            Path(file_location).parent.mkdir(parents=True, exist_ok=True)

        # Process response
        self._grpc_client.log.debug(f"Requesting design download in {format.value[0]} format.")
        received_bytes = bytes()
        if format is DesignFileFormat.SCDOCX:
            response = self._commands_stub.DownloadFile(Empty())
            received_bytes += response.data
        elif format in [
            DesignFileFormat.PARASOLID_TEXT,
            DesignFileFormat.PARASOLID_BIN,
            DesignFileFormat.FMD,
            DesignFileFormat.STEP,
            DesignFileFormat.IGES,
            DesignFileFormat.PMDB,
        ]:
            response = self._parts_stub.Export(ExportRequest(format=format.value[1]))
            received_bytes += response.data
        else:
            self._grpc_client.log.warning(
                f"{format.value[0]} format requested is not supported. Ignoring download request."
            )
            return

        # Write to file
        downloaded_file = open(file_location, "wb")
        downloaded_file.write(received_bytes)
        downloaded_file.close()

        self._grpc_client.log.debug(
            f"Design is successfully downloaded at location {file_location}."
        )

    @check_input_types
    @ensure_design_is_active
    def create_named_selection(
        self,
        name: str,
        bodies: Optional[List[Body]] = None,
        faces: Optional[List[Face]] = None,
        edges: Optional[List[Edge]] = None,
        beams: Optional[List[Beam]] = None,
        design_points: Optional[List[DesignPoint]] = None,
    ) -> NamedSelection:
        """
        Create a named selection on the active Geometry server instance.

        Parameters
        ----------
        name : str
            User-defined name for the named selection.
        bodies : List[Body], default: None
            All bodies to include in the named selection.
        faces : List[Face], default: None
            All faces to include in the named selection.
        edges : List[Edge], default: None
            All edges to include in the named selection.
        beams : List[Beam], default: None
            All beams to include in the named selection.
        design_points : List[DesignPoint], default: None
            All design points to include in the named selection.

        Returns
        -------
        NamedSelection
            Newly created named selection that maintains references to all target entities.
        """
        named_selection = NamedSelection(
            name,
            self._grpc_client,
            bodies=bodies,
            faces=faces,
            edges=edges,
            beams=beams,
            design_points=design_points,
        )
        self._named_selections[named_selection.name] = named_selection

        self._grpc_client.log.debug(
            f"Named selection {named_selection.name} is successfully created."
        )

        return self._named_selections[named_selection.name]

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def delete_named_selection(self, named_selection: Union[NamedSelection, str]) -> None:
        """
        Delete a named selection on the active Geometry server instance.

        Parameters
        ----------
        named_selection : Union[NamedSelection, str]
            Name of the named selection or instance.
        """
        if isinstance(named_selection, str):
            removal_name = named_selection
            removal = self._named_selections.get(named_selection, None)
            removal_id = removal.id if removal else None
        else:
            removal_name = named_selection.name
            removal_id = named_selection.id

        self._grpc_client.log.debug(f"Named selection {removal_name} deletion request received.")
        self._named_selections_stub.Delete(EntityIdentifier(id=removal_id))

        try:
            self._named_selections.pop(removal_name)
            self._grpc_client.log.debug(f"Named selection {removal_name} is successfully deleted.")
        except KeyError:
            self._grpc_client.log.warning(
                f"Attempted named selection deletion failed, with name {removal_name}."
                + " Ignoring this request."
            )
            pass

    @check_input_types
    @ensure_design_is_active
    def delete_component(self, component: Union["Component", str]) -> None:
        """
        Delete a component (itself or its children).

        Notes
        -----
        If the component is not this component (or its children), it
        is not deleted.

        Parameters
        ----------
        id : Union[Component, str]
            Name of the component or instance to delete.

        Raises
        ------
        ValueError
            The design itself cannot be deleted.
        """
        id = component if isinstance(component, str) else component.id
        if id == self.id:
            raise ValueError("The design itself cannot be deleted.")
        else:
            return super().delete_component(component)

    def set_shared_topology(self, share_type: SharedTopologyType) -> None:
        """
        Set the shared topology to apply to the component.

        Parameters
        ----------
        share_type : SharedTopologyType
            Shared topology type to assign.

        Raises
        ------
        ValueError
            Shared topology does not apply to a design.
        """
        raise ValueError("The design itself cannot have a shared topology.")

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def add_beam_circular_profile(
        self,
        name: str,
        radius: Union[Quantity, Distance],
        center: Union[np.ndarray, RealSequence, Point3D] = ZERO_POINT3D,
        direction_x: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        direction_y: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Y,
    ) -> BeamCircularProfile:
        """
        Add a new beam circular profile under the design for the creating beams.

        Parameters
        ----------
        name : str
            User-defined label for the new beam circular profile.
        radius : Real
            Radius of the beam circular profile.
        center : Union[~numpy.ndarray, RealSequence, Point3D]
            Center of the beam circular profile.
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
            raise ValueError("Direction X and direction Y must be perpendicular.")

        request = CreateBeamCircularProfileRequest(
            origin=point3d_to_grpc_point(center),
            radius=radius.value.m_as(DEFAULT_UNITS.SERVER_LENGTH),
            plane=plane_to_grpc_plane(Plane(center, dir_x, dir_y)),
            name=name,
        )

        self._grpc_client.log.debug(f"Creating a beam circular profile on {self.id}...")

        response = self._commands_stub.CreateBeamCircularProfile(request)
        profile = BeamCircularProfile(response.id, name, radius, center, dir_x, dir_y)
        self._beam_profiles[profile.name] = profile

        self._grpc_client.log.debug(
            f"Beam circular profile {profile.name} is successfully created."
        )

        return self._beam_profiles[profile.name]

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def add_midsurface_thickness(self, thickness: Quantity, bodies: List[Body]) -> None:
        """
        Add a mid-surface thickness to a list of bodies.

        Parameters
        ----------
        thickness : ~pint.Quantity
            Thickness to be assigned.
        bodies : List[Body]
            All bodies to include in the mid-surface thickness assignment.

        Notes
        -----
        Only surface bodies will be eligible for mid-surface thickness assignment.
        """
        # Store only assignable ids
        ids: List[str] = []
        ids_bodies: List[Body] = []
        for body in bodies:
            if body.is_surface:
                ids.append(body.id)
                ids_bodies.append(body)
            else:
                self._grpc_client.log.warning(
                    f"Body {body.name} cannot be assigned a mid-surface thickness since it is not a surface. Ignoring request."  # noqa : E501
                )

        # Assign mid-surface thickness
        self._commands_stub.AssignMidSurfaceThickness(
            AssignMidSurfaceThicknessRequest(
                bodies_or_faces=ids, thickness=thickness.m_as(DEFAULT_UNITS.SERVER_LENGTH)
            )
        )

        # Once the assignment has gone fine, store the values
        for body in ids_bodies:
            body._surface_thickness = thickness

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def add_midsurface_offset(self, offset_type: MidSurfaceOffsetType, bodies: List[Body]) -> None:
        """
        Add a mid-surface offset type to a list of bodies.

        Parameters
        ----------
        offset_type : MidSurfaceOffsetType
            Surface offset to be assigned.
        bodies : List[Body]
            All bodies to include in the mid-surface offset assignment.

        Notes
        -----
        Only surface bodies will be eligible for mid-surface offset assignment.
        """
        # Store only assignable ids
        ids: List[str] = []
        ids_bodies: List[Body] = []
        for body in bodies:
            if body.is_surface:
                ids.append(body.id)
                ids_bodies.append(body)
            else:
                self._grpc_client.log.warning(
                    f"Body {body.name} cannot be assigned a mid-surface offset since it is not a surface. Ignoring request."  # noqa : E501
                )

        # Assign mid-surface offset type
        self._commands_stub.AssignMidSurfaceOffsetType(
            AssignMidSurfaceOffsetTypeRequest(bodies_or_faces=ids, offset_type=offset_type.value)
        )

        # Once the assignment has gone fine, store the values
        for body in ids_bodies:
            body._surface_offset = offset_type

    @protect_grpc
    @check_input_types
    @ensure_design_is_active
    def delete_beam_profile(self, beam_profile: Union[BeamProfile, str]) -> None:
        """
        Remove a beam profile on the active geometry server instance.

        Parameters
        ----------
        beam_profile : Union[BeamProfile, str]
            A beam profile name or instance that should be deleted.
        """
        removal_name = beam_profile if isinstance(beam_profile, str) else beam_profile.name
        self._grpc_client.log.debug(f"Beam profile {removal_name} deletion request received.")
        removal_obj = self._beam_profiles.get(removal_name, None)

        if removal_obj:
            self._commands_stub.DeleteBeamProfile(EntityIdentifier(id=removal_obj.id))
            self._beam_profiles.pop(removal_name)
            self._grpc_client.log.debug(f"Beam profile {removal_name} successfully deleted.")
        else:
            self._grpc_client.log.warning(
                f"Attempted beam profile deletion failed, with name {removal_name}."
                + " Ignoring request."
            )

    def __repr__(self) -> str:
        """Represent the ``Design`` as a string."""
        alive_bodies = [1 if body.is_alive else 0 for body in self.bodies]
        alive_comps = [1 if comp.is_alive else 0 for comp in self.components]
        lines = [f"ansys.geometry.core.designer.Design {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Is active?           : {self._is_active}")
        lines.append(f"  N Bodies             : {sum(alive_bodies)}")
        lines.append(f"  N Components         : {sum(alive_comps)}")
        lines.append(f"  N Coordinate Systems : {len(self.coordinate_systems)}")
        lines.append(f"  N Named Selections   : {len(self.named_selections)}")
        lines.append(f"  N Materials          : {len(self.materials)}")
        lines.append(f"  N Beam Profiles      : {len(self.beam_profiles)}")
        lines.append(f"  N Design Points      : {len(self.design_points)}")
        return "\n".join(lines)

    def __read_existing_design(self) -> None:
        """Read an existing ``Design`` located on the server."""
        #
        # TODO: This might go out of sync with the _update_design_inplace method.
        #       Ensure that the two methods are in sync. Especially regarding cleanup.
        #
        # TODO: Not all features implemented yet. Status is as follows
        #
        # Windows:
        #
        # - [X] Components
        # - [X] Bodies
        # - [X] Materials
        # - [X] NamedSelections
        # - [ ] BeamProfiles
        # - [ ] Beams
        # - [X] CoordinateSystems
        # - [X] SharedTopology
        #
        # Linux:
        #
        # - [X] Components
        # - [X] Bodies
        # - [X] Materials
        # - [X] NamedSelections
        # - [ ] BeamProfiles
        # - [ ] Beams
        # - [X] CoordinateSystems
        # - [ ] SharedTopology
        #
        import time

        start = time.time()
        # Grab active design
        design = self._design_stub.GetActive(Empty())
        if not design:
            raise RuntimeError("No existing design available at service level.")
        else:
            self._design_id = design.id
            self._id = design.main_part.id
            self._activate(called_after_design_creation=True)
            # Here we may take the design's name instead of the main part's name.
            # Since they're the same in the backend.
            self._name = design.name

        response = self._commands_stub.GetAssembly(EntityIdentifier(id=""))

        # Store created objects
        created_parts = {p.id: Part(p.id, p.name, [], []) for p in response.parts}
        created_tps = {}
        created_components = {design.main_part.id: self}
        created_bodies = {}

        # Make dummy master for design since server doesn't have one
        self._master_component = MasterComponent(
            "1", "master_design", created_parts[design.main_part.id]
        )

        # Create MasterComponents
        for master in response.transformed_parts:
            part = created_parts.get(master.part_master.id)
            new_master = MasterComponent(
                master.id, master.name, part, grpc_matrix_to_matrix(master.placement)
            )
            created_tps[master.id] = new_master

        # Create Components
        for comp in response.components:
            parent = created_components.get(comp.parent_id)
            master = created_tps.get(comp.master_id)
            c = Component(
                comp.name,
                parent,
                self._grpc_client,
                preexisting_id=comp.id,
                master_component=master,
                read_existing_comp=True,
            )
            created_components[comp.id] = c
            parent.components.append(c)

        # Create Bodies
        for body in response.bodies:
            part = created_parts.get(body.parent_id)
            tb = MasterBody(body.id, body.name, self._grpc_client, is_surface=body.is_surface)
            part.bodies.append(tb)
            created_bodies[body.id] = tb

        # Create Materials
        for material in response.materials:
            properties = []
            density = Quantity(0)
            for property in material.material_properties:
                # TODO: Add support for more material properties...
                #      - Need to add support for more MaterialPropertyTypes
                #      - Need to add support for more Quantity units
                try:
                    mp_type = MaterialPropertyType.from_id(property.id)
                except ValueError as err:  # TODO: Errors coming from MaterialPropertyType.from_id
                    # because of unsupported MaterialPropertyType entries...
                    self._grpc_client.log.warning(
                        f"Material property {property.display_name} of type {property.id} is not supported."  # noqa : E501
                        " Storing as string."
                    )
                    self._grpc_client.log.warning(f"Root cause: {err}")
                    mp_type = property.id

                try:
                    mp_quantity = Quantity(property.value, property.units)
                except (
                    UndefinedUnitError,
                    TypeError,
                ) as err:  # TODO: Errors coming from Quantity ctor because of unsupported units...
                    self._grpc_client.log.warning(
                        f"Material property {property.display_name} with units {property.units} is not fully supported."  # noqa : E501
                        " Storing value only as float."
                    )
                    self._grpc_client.log.warning(f"Root cause: {err}")
                    mp_quantity = property.value

                mp = MaterialProperty(mp_type, property.display_name, mp_quantity)
                properties.append(mp)
                if mp.type == MaterialPropertyType.DENSITY:
                    density = mp.quantity

            m = Material(material.name, density, properties)
            self.materials.append(m)

        # Create NamedSelections
        for ns in response.named_selections:
            new_ns = NamedSelection(ns.name, self._grpc_client, preexisting_id=ns.id)
            self._named_selections[new_ns.name] = new_ns

        # Create CoordinateSystems
        num_created_coord_systems = 0
        for component_id, coordinate_systems in response.component_coord_systems.items():
            component = created_components.get(component_id)
            for cs in coordinate_systems.coordinate_systems:
                frame = grpc_frame_to_frame(cs.frame)
                new_cs = CoordinateSystem(cs.name, frame, component, self._grpc_client, cs.id)
                component.coordinate_systems.append(new_cs)
                num_created_coord_systems += 1

        end = time.time()

        # Set SharedTopology
        # TODO: Maybe just add it to Component or Part message
        #          - we're starting to iterate through all the Components too much
        # TODO: Make sure design doesn't need edge case attention
        num_created_shared_topologies = 0
        for component_id, shared_topology_type in response.component_shared_topologies.items():
            component = created_components.get(component_id)
            component._shared_topology = SharedTopologyType(shared_topology_type)
            num_created_shared_topologies += 1

        self._grpc_client.log.debug(f"Parts created: {len(created_parts)}")
        self._grpc_client.log.debug(f"MasterComponents created: {len(created_tps) + 1}")
        self._grpc_client.log.debug(f"Components created: {len(created_components)}")
        self._grpc_client.log.debug(f"Bodies created: {len(created_bodies)}")
        self._grpc_client.log.debug(f"Materials created: {len(self.materials)}")
        self._grpc_client.log.debug(f"NamedSelections created: {len(self.named_selections)}")
        self._grpc_client.log.debug(f"CoordinateSystems created: {num_created_coord_systems}")
        self._grpc_client.log.debug(f"SharedTopologyTypes set: {num_created_shared_topologies}")

        self._grpc_client.log.debug(f"\nSuccessfully read design in: {end - start} s")

    def _update_design_inplace(self) -> None:
        """
        Update the design to align with the server side.

        Notes
        -----
        This method is used to update the design inside repair tools.
        Its usage is not recommended for other purposes.
        """
        # Clear all the existing information
        #
        # TODO: This might go out of sync with the __read_existing_design method
        #       if the latter is updated and this method is not. Ensure that
        #       the two methods are in sync.
        #
        self._components = []
        self._bodies = []
        self._materials = []
        self._named_selections = {}
        self._coordinate_systems = {}

        # Get the previous design id
        previous_design_id = self._design_id

        # Read the existing design
        self.__read_existing_design()

        # If the design id has changed, update the design id in the Modeler
        if previous_design_id != self._design_id:
            self._modeler._designs[self._design_id] = self
            self._modeler._designs.pop(previous_design_id)
