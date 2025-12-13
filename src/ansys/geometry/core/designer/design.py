# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
from typing import Union

from beartype import beartype as check_input_types
import numpy as np
from pint import Quantity, UndefinedUnitError

from ansys.geometry.core._grpc._version import GeometryApiProtos
from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.designer.beam import (
    Beam,
    BeamCircularProfile,
    BeamCrossSectionInfo,
    BeamProfile,
    BeamProperties,
    SectionAnchorType,
)
from ansys.geometry.core.designer.body import Body, MasterBody, MidSurfaceOffsetType
from ansys.geometry.core.designer.component import Component, SharedTopologyType
from ansys.geometry.core.designer.coordinate_system import CoordinateSystem
from ansys.geometry.core.designer.designpoint import DesignPoint
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.designer.part import MasterComponent, Part
from ansys.geometry.core.designer.selection import NamedSelection
from ansys.geometry.core.designer.vertex import Vertex
from ansys.geometry.core.materials.material import Material
from ansys.geometry.core.materials.property import MaterialProperty, MaterialPropertyType
from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Y, ZERO_POINT3D
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.auxiliary import prepare_file_for_server_upload
from ansys.geometry.core.misc.checks import (
    ensure_design_is_active,
    min_backend_version,
)
from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.misc.options import (
    ImportOptions,
    ImportOptionsDefinitions,
    TessellationOptions,
)
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.parameters.parameter import Parameter, ParameterUpdateStatus
from ansys.geometry.core.shapes.curves.trimmed_curve import TrimmedCurve
from ansys.geometry.core.shapes.parameterization import Interval, ParamUV
from ansys.geometry.core.typing import Real, RealSequence


@unique
class DesignFileFormat(Enum):
    """Provides supported file formats that can be downloaded for designs."""

    SCDOCX = "SCDOCX"
    PARASOLID_TEXT = "PARASOLID_TEXT"
    PARASOLID_BIN = "PARASOLID_BIN"
    FMD = "FMD"
    STEP = "STEP"
    IGES = "IGES"
    PMDB = "PMDB"
    STRIDE = "STRIDE"
    DISCO = "DISCO"
    INVALID = "INVALID"

    def __str__(self):
        """Represent object in string format."""
        return self.value


class Design(Component):
    """Provides for organizing geometry assemblies.

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
    _materials: list[Material]
    _named_selections: dict[str, NamedSelection]
    _beam_profiles: dict[str, BeamProfile]

    @check_input_types
    def __init__(self, name: str, modeler: Modeler, read_existing_design: bool = False):
        """Initialize the ``Design`` class."""
        super().__init__(name, None, modeler.client)

        # Initialize needed instance variables
        self._materials = []
        self._named_selections = {}
        self._beam_profiles = {}
        self._design_id = ""
        self._is_active = False
        self._modeler = modeler
        self._design_tess = None

        # Check whether we want to process an existing design or create a new one.
        if read_existing_design:
            self._grpc_client.log.debug("Reading Design object from service.")
            self.__read_existing_design()
        else:
            response = self._grpc_client.services.designs.new(name=name)
            self._design_id = response.get("design_id")
            self._id = response.get("main_part_id")
            self._activate(called_after_design_creation=True)
            self._grpc_client.log.debug("Design object instantiated successfully.")

    @property
    def design_id(self) -> str:
        """The design's object unique id."""
        return self._design_id

    @property
    def materials(self) -> list[Material]:
        """List of materials available for the design."""
        return self._materials

    @property
    def named_selections(self) -> list[NamedSelection]:
        """List of named selections available for the design."""
        return list(self._named_selections.values())

    @property
    def beam_profiles(self) -> list[BeamProfile]:
        """List of beam profile available for the design."""
        return list(self._beam_profiles.values())

    @property
    def parameters(self) -> list[Parameter]:
        """List of parameters available for the design."""
        return self.get_all_parameters()

    @property
    def is_active(self) -> bool:
        """Whether the design is currently active."""
        return self._is_active

    @property
    def is_closed(self) -> bool:
        """Whether the design is closed (i.e. not active)."""
        return not self._is_active

    def close(self) -> None:
        """Close the design."""
        # Check if the design is already closed
        if self.is_closed:
            self._grpc_client.log.warning(f"Design {self.name} is already closed.")
            return

        # Attempt to close the design
        try:
            self._grpc_client.services.designs.close(design_id=self._design_id)
        except Exception as err:
            self._grpc_client.log.warning(f"Design {self.name} could not be closed. Error: {err}.")
            self._grpc_client.log.warning("Ignoring response and assuming the design is closed.")

        # Consider the design closed (even if the close request failed)
        self._is_active = False

    def _activate(self, called_after_design_creation: bool = False) -> None:
        """Activate the design."""
        # Activate the current design
        if not called_after_design_creation:
            self._grpc_client.services.designs.put_active(design_id=self._design_id)
        self._is_active = True
        self._grpc_client.log.debug(f"Design {self.name} is activated.")

    # TODO: allow for list of materials
    # https://github.com/ansys/pyansys-geometry/issues/1319
    @check_input_types
    @ensure_design_is_active
    def add_material(self, material: Material) -> None:
        """Add a material to the design.

        Parameters
        ----------
        material : Material
            Material to add.
        """
        self._grpc_client.services.materials.add_material(material=material)
        self._materials.append(material)
        self._grpc_client.log.debug(f"Material {material.name} is successfully added to design.")

    @min_backend_version(26, 1, 0)
    @check_input_types
    @ensure_design_is_active
    def remove_material(self, material: Material | list[Material]) -> None:
        """Remove a material from the design.

        Parameters
        ----------
        material : Material | list[Material]
            Material or list of materials to remove.
        """
        material = material if isinstance(material, list) else [material]

        self._grpc_client.services.materials.remove_material(materials=material)
        for mat in material:
            self._materials.remove(mat)
            self._grpc_client.log.debug(f"Material {mat.name} is successfully removed from design.")

    @check_input_types
    @ensure_design_is_active
    def save(self, file_location: Path | str, write_body_facets: bool = False) -> None:
        """Save a design to disk on the active Geometry server instance.

        Parameters
        ----------
        file_location : ~pathlib.Path | str
            Location on disk to save the file to.
        write_body_facets : bool, default: False
            Option to write body facets into the saved file. 26R1 and later.
        """
        # Sanity checks on inputs
        if isinstance(file_location, Path):
            file_location = str(file_location)

        self._grpc_client.services.designs.save_as(
            filepath=file_location,
            write_body_facets=write_body_facets,
            backend_version=self._grpc_client.backend_version,
            format=DesignFileFormat.SCDOCX,
        )
        self._grpc_client.log.debug(f"Design successfully saved at location {file_location}.")

    @check_input_types
    @ensure_design_is_active
    def download(
        self,
        file_location: Path | str,
        format: DesignFileFormat = DesignFileFormat.SCDOCX,
        write_body_facets: bool = False,
    ) -> None:
        """Export and download the design from the server.

        Parameters
        ----------
        file_location : ~pathlib.Path | str
            Location on disk to save the file to.
        format : DesignFileFormat, default: DesignFileFormat.SCDOCX
            Format for the file to save to.
        write_body_facets : bool, default: False
            Option to write body facets into the saved file. SCDOCX and DISCO only, 26R1 and later.
        """
        # Sanity checks on inputs
        if isinstance(file_location, str):
            file_location = Path(file_location)

        # Check if the folder for the file location exists
        if not file_location.parent.exists():
            # Create the parent directory
            file_location.parent.mkdir(parents=True, exist_ok=True)

        # Process response
        self._grpc_client.log.debug(f"Requesting design download in {format} format.")
        if self._modeler.client.backend_version < (25, 2, 0):
            received_bytes = self.__export_and_download_legacy(format=format)
        else:
            received_bytes = self.__export_and_download(
                format=format, write_body_facets=write_body_facets
            )

        # Write to file
        file_location.write_bytes(received_bytes)
        self._grpc_client.log.debug(f"Design downloaded at location {file_location}.")

    @min_backend_version(24, 1, 0)
    @check_input_types
    def _create_sketch_line(self, start: Point3D, end: Point3D) -> None:
        """Create a sketch line in the design.

        Parameters
        ----------
        start : Point3D
            Start point of the line.
        end : Point3D
            End point of the line.

        Warnings
        --------
        This method is for internal testing use only and may change without warning.
        Please use the Sketch class to create sketch lines.
        """
        # Process request
        self._grpc_client.services.model_tools.create_sketch_line(start=start, end=end)

    def __export_and_download_legacy(self, format: DesignFileFormat) -> bytes:
        """Export and download the design from the server.

        Parameters
        ----------
        format : DesignFileFormat
            Format for the file to save to.

        Returns
        -------
        bytes
            The raw data from the exported and downloaded file.

        Notes
        -----
        This is a legacy method, which is used in versions
        up to Ansys 25.1.1 products.
        """
        # Process response
        self._grpc_client.log.debug(f"Requesting design download in {format} format.")
        if format is DesignFileFormat.SCDOCX:
            response = self._grpc_client.services.designs.download_file()
            received_bytes = bytes()
            received_bytes += response.get("data")
        elif format in [
            DesignFileFormat.PARASOLID_TEXT,
            DesignFileFormat.PARASOLID_BIN,
            DesignFileFormat.FMD,
            DesignFileFormat.STEP,
            DesignFileFormat.IGES,
            DesignFileFormat.PMDB,
        ]:
            response = self._grpc_client.services.parts.export(format=format)
            received_bytes = response.get("data")
        else:
            self._grpc_client.log.warning(
                f"{format} format requested is not supported. Ignoring download request."
            )
            return

        return received_bytes

    def __export_and_download(
        self,
        format: DesignFileFormat,
        write_body_facets: bool = False,
    ) -> bytes:
        """Export and download the design from the server.

        Parameters
        ----------
        format : DesignFileFormat
            Format for the file to save to.

        Returns
        -------
        bytes
            The raw data from the exported and downloaded file.
        """
        # Process response
        self._grpc_client.log.debug(f"Requesting design download in {format} format.")

        if format in [
            DesignFileFormat.PARASOLID_TEXT,
            DesignFileFormat.PARASOLID_BIN,
            DesignFileFormat.FMD,
            DesignFileFormat.STEP,
            DesignFileFormat.IGES,
            DesignFileFormat.PMDB,
            DesignFileFormat.DISCO,
            DesignFileFormat.SCDOCX,
            DesignFileFormat.STRIDE,
        ]:
            try:
                response = self._grpc_client.services.designs.download_export(
                    format=format,
                    write_body_facets=write_body_facets,
                    backend_version=self._grpc_client.backend_version,
                )
            except Exception:
                self._grpc_client.log.warning(
                    f"Failed to download the file in {format} format."
                    " Attempting to stream download."
                )
                # Attempt to download the file via streaming
                response = self._grpc_client.services.designs.stream_download_export(
                    format=format,
                    write_body_facets=write_body_facets,
                    backend_version=self._grpc_client.backend_version,
                )
        else:
            self._grpc_client.log.warning(
                f"{format} format requested is not supported. Ignoring download request."
            )
            return None

        return response.get("data")

    def __build_export_file_location(self, location: Path | str | None, ext: str) -> Path:
        """Build the file location for export functions.

        Parameters
        ----------
        location : ~pathlib.Path | str
            Location on disk to save the file to. If None, the file will be saved
            in the current working directory.
        ext : str
            Extension to use for the file.

        Returns
        -------
        ~pathlib.Path
            The file location for the export function.
        """
        return (Path(location) if location else Path.cwd()) / f"{self.name}.{ext}"

    def export_to_scdocx(self, location: Path | str | None = None) -> Path:
        """Export the design to an scdocx file.

        Parameters
        ----------
        location : ~pathlib.Path | str, optional
            Location on disk to save the file to. If None, the file will be saved
            in the current working directory.

        Returns
        -------
        ~pathlib.Path
            The path to the saved file.
        """
        # Define the file location
        file_location = self.__build_export_file_location(location, "scdocx")

        # Export the design to an scdocx file
        self.download(file_location, DesignFileFormat.SCDOCX)

        # Return the file location
        return file_location

    def export_to_disco(self, location: Path | str | None = None) -> Path:
        """Export the design to an dsco file.

        Parameters
        ----------
        location : ~pathlib.Path | str, optional
            Location on disk to save the file to. If None, the file will be saved
            in the current working directory.

        Returns
        -------
        ~pathlib.Path
            The path to the saved file.
        """
        # Define the file location
        file_location = self.__build_export_file_location(location, "dsco")

        # Export the design to an dsco file
        self.download(file_location, DesignFileFormat.DISCO)

        # Return the file location
        return file_location

    def export_to_stride(self, location: Path | str | None = None) -> Path:
        """Export the design to an stride file.

        Parameters
        ----------
        location : ~pathlib.Path | str, optional
            Location on disk to save the file to. If None, the file will be saved
            in the current working directory.

        Returns
        -------
        ~pathlib.Path
            The path to the saved file.
        """
        # Define the file location
        file_location = self.__build_export_file_location(location, "stride")

        # Export the design to an stride file
        self.download(file_location, DesignFileFormat.STRIDE)

        # Return the file location
        return file_location

    def export_to_parasolid_text(self, location: Path | str | None = None) -> Path:
        """Export the design to a Parasolid text file.

        Parameters
        ----------
        location : ~pathlib.Path | str, optional
            Location on disk to save the file to. If None, the file will be saved
            in the current working directory.

        Returns
        -------
        ~pathlib.Path
            The path to the saved file.
        """
        # Determine the extension based on the backend type
        ext = "xmt_txt" if BackendType.is_linux_service(self._grpc_client.backend_type) else "x_t"

        # Define the file location
        file_location = self.__build_export_file_location(location, ext)

        # Export the design to a Parasolid text file
        self.download(file_location, DesignFileFormat.PARASOLID_TEXT)

        # Return the file location
        return file_location

    def export_to_parasolid_bin(self, location: Path | str | None = None) -> Path:
        """Export the design to a Parasolid binary file.

        Parameters
        ----------
        location : ~pathlib.Path | str, optional
            Location on disk to save the file to. If None, the file will be saved
            in the current working directory.

        Returns
        -------
        ~pathlib.Path
            The path to the saved file.
        """
        # Determine the extension based on the backend type
        ext = "xmt_bin" if BackendType.is_linux_service(self._grpc_client.backend_type) else "x_b"

        # Define the file location
        file_location = self.__build_export_file_location(location, ext)

        # Export the design to a Parasolid binary file
        self.download(file_location, DesignFileFormat.PARASOLID_BIN)

        # Return the file location
        return file_location

    def export_to_fmd(self, location: Path | str | None = None) -> Path:
        """Export the design to an FMD file.

        Parameters
        ----------
        location : ~pathlib.Path | str, optional
            Location on disk to save the file to. If None, the file will be saved
            in the current working directory.

        Returns
        -------
        ~pathlib.Path
            The path to the saved file.
        """
        # Define the file location
        file_location = self.__build_export_file_location(location, "fmd")

        # Export the design to an FMD file
        self.download(file_location, DesignFileFormat.FMD)

        # Return the file location
        return file_location

    def export_to_step(self, location: Path | str | None = None) -> Path:
        """Export the design to a STEP file.

        Parameters
        ----------
        location : ~pathlib.Path | str, optional
            Location on disk to save the file to. If None, the file will be saved
            in the current working directory.

        Returns
        -------
        ~pathlib.Path
            The path to the saved file.
        """
        # Define the file location
        file_location = self.__build_export_file_location(location, "stp")

        # Export the design to a STEP file
        self.download(file_location, DesignFileFormat.STEP)

        # Return the file location
        return file_location

    def export_to_iges(self, location: Path | str = None) -> Path:
        """Export the design to an IGES file.

        Parameters
        ----------
        location : ~pathlib.Path | str, optional
            Location on disk to save the file to. If None, the file will be saved
            in the current working directory.

        Returns
        -------
        ~pathlib.Path
            The path to the saved file.
        """
        # Define the file location
        file_location = self.__build_export_file_location(location, "igs")

        # Export the design to an IGES file
        self.download(file_location, DesignFileFormat.IGES)

        # Return the file location
        return file_location

    def export_to_pmdb(self, location: Path | str | None = None) -> Path:
        """Export the design to a PMDB file.

        Parameters
        ----------
        location : ~pathlib.Path | str, optional
            Location on disk to save the file to. If None, the file will be saved
            in the current working directory.

        Returns
        -------
        ~pathlib.Path
            The path to the saved file.
        """
        # Define the file location
        file_location = self.__build_export_file_location(location, "pmdb")

        # Export the design to a PMDB file
        self.download(file_location, DesignFileFormat.PMDB)

        # Return the file location
        return file_location

    @check_input_types
    @ensure_design_is_active
    def create_named_selection(
        self,
        name: str,
        bodies: list[Body] | None = None,
        faces: list[Face] | None = None,
        edges: list[Edge] | None = None,
        beams: list[Beam] | None = None,
        design_points: list[DesignPoint] | None = None,
        components: list[Component] | None = None,
        vertices: list[Vertex] | None = None,
    ) -> NamedSelection:
        """Create a named selection on the active Geometry server instance.

        Parameters
        ----------
        name : str
            User-defined name for the named selection.
        bodies : list[Body], default: None
            All bodies to include in the named selection.
        faces : list[Face], default: None
            All faces to include in the named selection.
        edges : list[Edge], default: None
            All edges to include in the named selection.
        beams : list[Beam], default: None
            All beams to include in the named selection.
        design_points : list[DesignPoint], default: None
            All design points to include in the named selection.
        components : list[Component], default: None
            All components to include in the named selection.
        vertices : list[Vertex], default: None
            All vertices to include in the named selection.

        Returns
        -------
        NamedSelection
            Newly created named selection that maintains references to all target entities.

        Raises
        ------
        ValueError
            If no entities are provided for the named selection. At least
            one of the optional parameters must be provided.
        """
        # Verify that at least one entity is provided
        if not any([bodies, faces, edges, beams, design_points, components, vertices]):
            raise ValueError(
                "At least one of the following must be provided: "
                "bodies, faces, edges, beams, design_points, components, or vertices."
            )

        named_selection = NamedSelection(
            name,
            self,
            self._grpc_client,
            bodies=bodies,
            faces=faces,
            edges=edges,
            beams=beams,
            design_points=design_points,
            components=components,
            vertices=vertices,
        )

        self._named_selections[named_selection.name] = named_selection
        self._grpc_client.log.debug(
            f"Named selection {named_selection.name} is successfully created."
        )

        return self._named_selections[named_selection.name]

    @check_input_types
    @ensure_design_is_active
    def delete_named_selection(self, named_selection: NamedSelection | str) -> None:
        """Delete a named selection on the active Geometry server instance.

        Parameters
        ----------
        named_selection : NamedSelection | str
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
        self._grpc_client.services.named_selection.delete_named_selection(id=removal_id)

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
        """Delete a component (itself or its children).

        Parameters
        ----------
        id : Union[Component, str]
            Name of the component or instance to delete.

        Raises
        ------
        ValueError
            The design itself cannot be deleted.

        Notes
        -----
        If the component is not this component (or its children), it
        is not deleted.
        """
        id = component if isinstance(component, str) else component.id
        if id == self.id:
            raise ValueError("The design itself cannot be deleted.")
        else:
            return super().delete_component(component)

    def set_shared_topology(self, share_type: SharedTopologyType) -> None:
        """Set the shared topology to apply to the component.

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

    @check_input_types
    @ensure_design_is_active
    def add_beam_circular_profile(
        self,
        name: str,
        radius: Quantity | Distance,
        center: np.ndarray | RealSequence | Point3D = ZERO_POINT3D,
        direction_x: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_X,
        direction_y: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_Y,
    ) -> BeamCircularProfile:
        """Add a new beam circular profile under the design for creating beams.

        Parameters
        ----------
        name : str
            User-defined label for the new beam circular profile.
        radius : ~pint.Quantity | Distance
            Radius of the beam circular profile.
        center : ~numpy.ndarray | RealSequence | Point3D
            Center of the beam circular profile.
        direction_x : ~numpy.ndarray | RealSequence | UnitVector3D | Vector3D
            X-plane direction.
        direction_y : ~numpy.ndarray | RealSequence | UnitVector3D | Vector3D
            Y-plane direction.
        """
        dir_x = direction_x if isinstance(direction_x, UnitVector3D) else UnitVector3D(direction_x)
        dir_y = direction_y if isinstance(direction_y, UnitVector3D) else UnitVector3D(direction_y)
        radius = radius if isinstance(radius, Distance) else Distance(radius)

        if radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

        if not dir_x.is_perpendicular_to(dir_y):
            raise ValueError("Direction X and direction Y must be perpendicular.")

        self._grpc_client.log.debug(f"Creating a beam circular profile on {self.id}...")

        response = self._grpc_client._services.beams.create_beam_circular_profile(
            center=center,
            radius=radius,
            plane=Plane(center, dir_x, dir_y),
            name=name,
        )

        profile = BeamCircularProfile(response.get("id"), name, radius, center, dir_x, dir_y)
        self._beam_profiles[profile.name] = profile

        self._grpc_client.log.debug(
            f"Beam circular profile {profile.name} is successfully created."
        )

        return self._beam_profiles[profile.name]

    @min_backend_version(25, 1, 0)
    def get_all_parameters(self) -> list[Parameter]:
        """Get parameters for the design.

        Returns
        -------
        list[Parameter]
            List of parameters for the design.

        Warnings
        --------
        This method is only available starting on Ansys release 25R1.
        """
        response = self._grpc_client._services.driving_dimensions.get_all_parameters()
        return response.get("parameters")

    @check_input_types
    @min_backend_version(25, 1, 0)
    def set_parameter(self, dimension: Parameter) -> ParameterUpdateStatus:
        """Set or update a parameter of the design.

        Parameters
        ----------
        dimension : Parameter
            Parameter to set.

        Returns
        -------
        ParameterUpdateStatus
            Status of the update operation.

        Warnings
        --------
        This method is only available starting on Ansys release 25R1.
        """
        response = self._grpc_client._services.driving_dimensions.set_parameter(
            driving_dimension=dimension
        )

        # Update the design in place. This method is computationally expensive,
        # consider finding a more efficient approach.
        self._update_design_inplace()

        return response.get("status")

    @check_input_types
    @ensure_design_is_active
    def add_midsurface_thickness(
        self, thickness: Distance | Quantity | Real, bodies: list[Body]
    ) -> None:
        """Add a mid-surface thickness to a list of bodies.

        Parameters
        ----------
        thickness : ~pint.Quantity
            Thickness to be assigned.
        bodies : list[Body]
            All bodies to include in the mid-surface thickness assignment.

        Notes
        -----
        Only surface bodies will be eligible for mid-surface thickness assignment.
        """
        thickness = thickness if isinstance(thickness, Distance) else Distance(thickness)
        # Store only assignable ids
        ids: list[str] = []
        ids_bodies: list[Body] = []
        for body in bodies:
            if body.is_surface:
                ids.append(body.id)
                ids_bodies.append(body)
            else:
                self._grpc_client.log.warning(
                    f"Body {body.name} cannot be assigned a mid-surface thickness since it is not a surface. Ignoring request."  # noqa : E501
                )

        # Assign mid-surface thickness
        self._grpc_client._services.bodies.assign_midsurface_thickness(ids=ids, thickness=thickness)

        # Once the assignment has gone fine, store the values
        for body in ids_bodies:
            body._surface_thickness = thickness.value

    @check_input_types
    @ensure_design_is_active
    def add_midsurface_offset(self, offset_type: MidSurfaceOffsetType, bodies: list[Body]) -> None:
        """Add a mid-surface offset type to a list of bodies.

        Parameters
        ----------
        offset_type : MidSurfaceOffsetType
            Surface offset to be assigned.
        bodies : list[Body]
            All bodies to include in the mid-surface offset assignment.

        Notes
        -----
        Only surface bodies will be eligible for mid-surface offset assignment.
        """
        # Store only assignable ids
        ids: list[str] = []
        ids_bodies: list[Body] = []
        for body in bodies:
            if body.is_surface:
                ids.append(body.id)
                ids_bodies.append(body)
            else:
                self._grpc_client.log.warning(
                    f"Body {body.name} cannot be assigned a mid-surface offset since it is not a surface. Ignoring request."  # noqa : E501
                )

        # Assign mid-surface offset type
        self._grpc_client._services.bodies.assign_midsurface_offset(
            ids=ids, offset_type=offset_type
        )

        # Once the assignment has gone fine, store the values
        for body in ids_bodies:
            body._surface_offset = offset_type

    @check_input_types
    @ensure_design_is_active
    def delete_beam_profile(self, beam_profile: BeamProfile | str) -> None:
        """Remove a beam profile on the active geometry server instance.

        Parameters
        ----------
        beam_profile : BeamProfile | str
            A beam profile name or instance that should be deleted.
        """
        removal_name = beam_profile if isinstance(beam_profile, str) else beam_profile.name
        self._grpc_client.log.debug(f"Beam profile {removal_name} deletion request received.")
        removal_obj = self._beam_profiles.get(removal_name, None)

        if removal_obj:
            self._grpc_client._services.beams.delete_beam_profile(id=removal_obj.id)
            self._beam_profiles.pop(removal_name)
            self._grpc_client.log.debug(f"Beam profile {removal_name} successfully deleted.")
        else:
            self._grpc_client.log.warning(
                f"Attempted beam profile deletion failed, with name {removal_name}."
                + " Ignoring request."
            )

    @check_input_types
    @ensure_design_is_active
    @min_backend_version(24, 2, 0)
    def insert_file(
        self,
        file_location: Path | str,
        import_options: ImportOptions = ImportOptions(),
        import_options_definitions: ImportOptionsDefinitions = ImportOptionsDefinitions(),
    ) -> Component:
        """Insert a file into the design.

        Parameters
        ----------
        file_location : ~pathlib.Path | str
            Location on disk where the file is located.
        import_options : ImportOptions, optional
            The options to pass into upload file. If none are provided, default options are used.
        import_options_definitions : ImportOptionsDefinitions, optional
            Additional options to pass into insert file. If none are provided, default options
            are used.

        Returns
        -------
        Component
            The newly inserted component.

        Warnings
        --------
        This method is only available starting on Ansys release 24R2.
        """
        # Upload the file to the server if using v0 protos
        if self._grpc_client.services.version == GeometryApiProtos.V0:
            filepath_server = self._modeler._upload_file(
                file_location, import_options=import_options
            )

            # Insert the file into the design
            self._grpc_client.services.designs.insert(
                filepath=filepath_server,
                import_named_selections=import_options.import_named_selections,
            )
        else:
            # Zip file and pass filepath to service to open
            fp_path = Path(file_location).resolve()

            try:
                temp_zip_path = prepare_file_for_server_upload(fp_path)

                # Pass the zip file path to the service
                self._grpc_client.services.designs.insert(
                    filepath=temp_zip_path,
                    original_file_name=fp_path.name,
                    import_options=import_options,
                    import_options_definitions=import_options_definitions,
                )

            finally:
                # Clean up the temporary zip file
                if temp_zip_path.exists():
                    temp_zip_path.unlink()

        self._grpc_client.log.debug(f"File {file_location} successfully inserted into design.")

        self._update_design_inplace()

        self._grpc_client.log.debug(f"Design {self.name} is successfully updated.")

        # Return the newly inserted component
        return self._components[-1]

    @min_backend_version(26, 1, 0)
    @check_input_types
    def get_raw_tessellation(
        self,
        tess_options: TessellationOptions | None = None,
        reset_cache: bool = False,
        include_faces: bool = True,
        include_edges: bool = False,
    ) -> dict:
        """Tessellate the entire design and return the geometry as triangles.

        Parameters
        ----------
        tess_options : TessellationOptions, optional
            Options for the tessellation. If None, default options are used.
        reset_cache : bool, default: False
            Whether to reset the cache before performing the tessellation.
        include_faces : bool, default: True
            Whether to include faces in the tessellation.
        include_edges : bool, default: False
            Whether to include edges in the tessellation.

        Returns
        -------
        dict
            A dictionary with body IDs as keys and another dictionary as values.
            The inner dictionary has face and edge IDs as keys and the corresponding face/vertice
            arrays as values.
        """
        if not self.is_alive:
            return {}  # Return an empty dictionary if the design is not alive

        self._grpc_client.log.debug(f"Requesting tessellation for design {self.id}.")

        # cache tessellation
        if not self._design_tess or reset_cache:
            response = self._grpc_client.services.designs.stream_design_tessellation(
                options=tess_options, include_faces=include_faces, include_edges=include_edges
            )

            self._design_tess = response.get("tessellation")

        return self._design_tess

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
        # This might go out of sync with the _update_design_inplace method.
        # Ensure that the two methods are in sync. Especially regarding cleanup.
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
        # https://github.com/ansys/pyansys-geometry/issues/1319
        import time

        start = time.time()
        # Grab active design
        design_response = self._grpc_client.services.designs.get_active()
        if not design_response:
            raise RuntimeError("No existing design available at service level.")
        else:
            self._design_id = design_response.get("design_id")
            self._id = design_response.get("main_part_id")
            self._name = design_response.get("name")
            self._activate(called_after_design_creation=True)

        response = self._grpc_client.services.designs.get_assembly(active_design=design_response)

        # Store created objects
        created_parts = {
            p.get("id"): Part(p.get("id"), p.get("name"), [], []) for p in response.get("parts")
        }
        created_tps = {}
        created_components = {design_response.get("main_part_id"): self}
        created_bodies = {}

        # Make dummy master for design since server doesn't have one
        self._master_component = MasterComponent(
            "1", "master_design", created_parts[design_response.get("main_part_id")]
        )

        # Create MasterComponents
        for master in response.get("transformed_parts"):
            part = created_parts.get(master.get("part_master").get("id"))
            new_master = MasterComponent(
                master.get("id"), master.get("name"), part, master.get("placement")
            )
            created_tps[master.get("id")] = new_master

        # Create Components
        for comp in response.get("components"):
            parent = created_components.get(comp.get("parent_id"))
            master = created_tps.get(comp.get("master_id"))
            c = Component(
                comp.get("name"),
                parent,
                self._grpc_client,
                preexisting_id=comp.get("id"),
                master_component=master,
                read_existing_comp=True,
            )
            created_components[comp.get("id")] = c
            parent.components.append(c)

        # Create Bodies
        for body in response.get("bodies"):
            part = created_parts.get(body.get("parent_id"))
            tb = MasterBody(
                body.get("id"),
                body.get("name"),
                self._grpc_client,
                is_surface=body.get("is_surface"),
            )
            part.bodies.append(tb)
            created_bodies[body.get("id")] = tb

        # Create Materials
        for material in response.get("materials"):
            properties = []
            density = Quantity(0)
            for property in material.get("material_properties"):
                # TODO: Add support for more material properties...
                #      - Need to add support for more MaterialPropertyTypes
                #      - Need to add support for more Quantity units
                # https://github.com/ansys/pyansys-geometry/issues/1319
                try:
                    mp_type = MaterialPropertyType.from_id(property.get("id"))
                except ValueError as err:
                    # TODO: Errors coming from MaterialPropertyType.from_id
                    # because of unsupported MaterialPropertyType entries...
                    # https://github.com/ansys/pyansys-geometry/issues/1319
                    self._grpc_client.log.warning(
                        f"Material property {property.get('display_name')} of type {property.get('id')} is not supported."  # noqa : E501
                        " Storing as string."
                    )
                    self._grpc_client.log.warning(f"Root cause: {err}")
                    mp_type = property.get("id")

                try:
                    mp_quantity = Quantity(property.get("value"), property.get("units"))
                except (
                    UndefinedUnitError,
                    TypeError,
                ) as err:  # TODO: Errors coming from Quantity ctor because of unsupported units...
                    # https://github.com/ansys/pyansys-geometry/issues/1319
                    self._grpc_client.log.warning(
                        f"Material property {property.get('display_name')} with units {property.get('units')} is not fully supported."  # noqa : E501
                        " Storing value only as float."
                    )
                    self._grpc_client.log.warning(f"Root cause: {err}")
                    mp_quantity = property.get("value")

                mp = MaterialProperty(mp_type, property.get("display_name"), mp_quantity)
                properties.append(mp)
                if mp.type == MaterialPropertyType.DENSITY:
                    density = (
                        mp.quantity if isinstance(mp.quantity, Quantity) else Quantity(mp.quantity)
                    )

            m = Material(material.get("name"), density, properties)
            self.materials.append(m)

        # Create Beams
        for beam in response.get("beams"):
            cross_section = BeamCrossSectionInfo(
                section_anchor=SectionAnchorType(beam.get("cross_section").get("section_anchor")),
                section_angle=beam.get("cross_section").get("section_angle"),
                section_frame=beam.get("cross_section").get("section_frame"),
                section_profile=[
                    [
                        TrimmedCurve(
                            geometry=curve.get("curve"),
                            start=curve.get("start"),
                            end=curve.get("end"),
                            interval=Interval(
                                curve.get("interval_start"), curve.get("interval_end")
                            ),
                            length=curve.get("length"),
                        )
                        for curve in curve_list.get("curves")
                    ]
                    for curve_list in beam.get("cross_section").get("section_profile")
                ],
            )
            properties = BeamProperties(
                area=beam.get("properties").get("area"),
                centroid=ParamUV(
                    beam.get("properties").get("centroid_x"),
                    beam.get("properties").get("centroid_y"),
                ),
                warping_constant=beam.get("properties").get("warping_constant"),
                ixx=beam.get("properties").get("ixx"),
                ixy=beam.get("properties").get("ixy"),
                iyy=beam.get("properties").get("iyy"),
                shear_center=ParamUV(
                    beam.get("properties").get("shear_center_x"),
                    beam.get("properties").get("shear_center_y"),
                ),
                torsion_constant=beam.get("properties").get("torsional_constant"),
            )

            new_beam = Beam(
                id=beam.get("id"),
                start=beam.get("start"),
                end=beam.get("end"),
                profile=None,
                # TODO: Beams need BeamProfiles imported from existing design
                # https://github.com/ansys/pyansys-geometry/issues/1825
                parent_component=self,
                name=beam.get("name"),
                is_deleted=beam.get("is_deleted"),
                is_reversed=beam.get("is_reversed"),
                is_rigid=beam.get("is_rigid"),
                material=beam.get("material"),
                cross_section=cross_section,
                properties=properties,
                beam_type=beam.get("type"),
            )

            # Find the component to which the beam belongs
            parent = created_components.get(beam.get("parent.id"), self)
            parent._beams.append(new_beam)

        # Create NamedSelections
        for ns in response.get("named_selections"):
            new_ns = NamedSelection(
                ns.get("name"),
                self,
                self._grpc_client,
                preexisting_id=ns.get("id"),
            )
            self._named_selections[new_ns.name] = new_ns

        # Create CoordinateSystems
        num_created_coord_systems = 0
        for ccs in response.get("component_coordinate_systems"):
            component_id = ccs.get("component_id")
            component = created_components.get(component_id)
            coordinate_systems = ccs.get("coordinate_systems")
            for cs in coordinate_systems:
                frame = cs.get("frame")
                new_cs = CoordinateSystem(
                    cs.get("name"), frame, component, self._grpc_client, cs.get("id")
                )
                component.coordinate_systems.append(new_cs)
                num_created_coord_systems += 1

        # Create DesignPoints
        for dp in response.get("design_points"):
            created_dp = DesignPoint(
                dp.get("id"),
                dp.get("name"),
                dp.get("point"),
                created_components.get(dp.get("parent_id"), self),
            )

            # Append the design point to the component to which it belongs
            created_dp.parent_component._design_points.append(created_dp)

        end = time.time()

        # Set SharedTopology
        # TODO: Maybe just add it to Component or Part message
        # we're starting to iterate through all the Components too much.
        # Make sure design doesn't need edge case attention
        # https://github.com/ansys/pyansys-geometry/issues/1319
        num_created_shared_topologies = 0
        for cst in response.get("component_shared_topologies"):
            component_id = cst.get("component_id")
            shared_topology_type = cst.get("shared_topology_type")
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
        """Update the design to align with the server side.

        Notes
        -----
        This method is used to update the design inside repair tools.
        Its usage is not recommended for other purposes.
        """
        # Clear all the existing information
        #
        # TODO: This might go out of sync with the __read_existing_design method
        # if the latter is updated and this method is not. Ensure that
        # the two methods are in sync.
        # https://github.com/ansys/pyansys-geometry/issues/1319
        #
        self._components = []
        self._clear_cached_bodies()
        self._materials = []
        self._named_selections = {}
        self._coordinate_systems = {}

        # Read the existing design
        self.__read_existing_design()

    def _update_from_tracker(self, tracker_response: dict):
        """Update the design with the changed entities while preserving unchanged ones.

        This method is alternative to update_design_inplace method.

        Parameters
        ----------
        tracker_response : dict
            Dictionary containing lists of created, modified, and deleted entities
            including parts, components, bodies, faces, edges, and other geometry entities.
            Processing order: parts → components → bodies → deletions (reverse dependency order).
        """
        self._grpc_client.log.debug(
            f"Starting _update_from_tracker with response: {tracker_response}"
        )

        # Track created entities for use in subsequent steps
        created_parts_dict = {}
        created_master_components_dict = {}
        created_components_dict = {}
        created_bodies_dict = {}

        # ================== HANDLE PARTS ==================

        # Handle created parts
        for part_info in tracker_response.get("created_parts", []):
            part_id = part_info["id"]
            # fall back to string if id is not an object with id attribute.
            part_name = part_info.get("name", f"Part_{part_id}")
            self._grpc_client.log.debug(
                f"Processing created part: ID={part_id}, Name='{part_name}'"
            )

            # Check if part already exists
            existing_part = self._find_existing_part(part_id)
            if existing_part:
                self._grpc_client.log.debug(
                    f"Created part '{part_name}' (ID: {part_id}) already exists."
                )
                continue

            # Create new part
            new_part = Part(part_id, part_name, [], [])
            created_parts_dict[part_id] = new_part
            # TODO: Add part to appropriate collection/registry
            self._grpc_client.log.debug(f"Created new part '{part_name}' (ID: {part_id})")

        # Handle modified parts
        # Do nothing for now, because this will almost always have the root part.

        # Handle deleted parts
        for part_info in tracker_response.get("deleted_parts", []):
            part_id = part_info["id"]
            self._grpc_client.log.debug(f"Processing deleted part: ID={part_id}")

            existing_part = self._find_existing_part(part_id)
            if existing_part:
                # Mark as not alive (if applicable)
                if hasattr(existing_part, "_is_alive"):
                    existing_part._is_alive = False
                self._grpc_client.log.debug(f"Removed part (ID: {part_id})")
                # TODO: Implement actual removal logic based on where parts are stored
            else:
                self._grpc_client.log.warning(f"Could not find part to delete: ID={part_id}")

        # ================== HANDLE COMPONENTS ==================

        # Handle created master components
        for component_info in tracker_response.get("created_components", []):
            # Check and create master components.
            if component_info.get("id") == component_info.get("master_id"):
                # This is a MasterComponent
                master_part_id = component_info.get("part_master").get("id")
                master_part = created_parts_dict.get(master_part_id) or self._find_existing_part(
                    master_part_id
                )
                if not master_part:
                    self._grpc_client.log.warning(
                        f"Could not find part for MasterComponent ID={component_info.get('id')}"
                    )
                    continue

                new_master = MasterComponent(
                    component_info["id"],
                    component_info.get("name", f"MasterComponent_{component_info['id']}"),
                    master_part,
                    component_info.get("placement"),
                )
                created_master_components_dict[component_info["id"]] = new_master
                self._grpc_client.log.debug(
                    f"Created new MasterComponent: ID={new_master.id}, Name='{new_master.name}'"
                )
                continue

        # Handle created occurrence components
        for component_info in tracker_response.get("created_components", []):
            # This is an OccurrenceComponent
            master_part_id = component_info.get("part_master").get("id")
            master_part = created_parts_dict.get(master_part_id) or self._find_existing_part(
                master_part_id
            )
            if not master_part:
                self._grpc_client.log.warning(
                    f"Could not find part for Component ID={component_info.get('id')}"
                )
                continue

            # component = Component(
            #     component_info["name"],
            #     parent_component=None,
            #     grpc_client=self._grpc_client,
            #     preexisting_id=component_info["id"],
            #     master_component=created_master_components_dict.get(component_info.get("master_id")),
            #     read_existing_comp=True,
            # )

            # created_components_dict[component_info["id"]] = component
            # self._grpc_client.log.debug(
            #     f"Created new Component: ID={component.id}, Name='{component.name}'"
            # )

            # # Find and assign parent component
            parent_id = component_info.get("parent_id")
            self._find_and_add_component_to_design(
                component_info, self.components, created_parts_dict, created_master_components_dict
            )

        # Handle modified components
        for component_info in tracker_response.get("modified_components", []):
            component_id = component_info["id"]
            component_name = component_info.get("name", f"Component_{component_id}")
            self._grpc_client.log.debug(
                f"Processing modified component: ID={component_id}, Name='{component_name}'"
            )

            # Try to find and update the component
            updated = self._find_and_update_component(component_info, self.components)
            if not updated:
                self._grpc_client.log.warning(
                    f"Could not find component to update: '{component_name}' (ID: {component_id})"
                )

        # Handle deleted components
        for component_info in tracker_response.get("deleted_components", []):
            component_id = component_info["id"]
            self._grpc_client.log.debug(f"Processing deleted component: ID={component_id}")

            # Try to find and remove the component
            removed = self._find_and_remove_component(component_info, self.components)
            if not removed:
                self._grpc_client.log.warning(
                    f"Could not find component to delete: ID={component_id}"
                )

        # ================== HANDLE BODIES ==================

        # Handle created bodies
        for body_info in tracker_response.get("created_bodies", []):
            body_id = body_info["id"]
            body_name = body_info["name"]
            is_surface = body_info.get("is_surface", False)
            self._grpc_client.log.debug(
                f"Processing created body: ID={body_id}, Name='{body_name}'"
            )

            if any(body.id == body_id for body in self.bodies):
                self._grpc_client.log.debug(
                    f"Created body '{body_name}' (ID: {body_id}) already exists at root level."
                )
                continue

            new_body = self._find_and_add_body_to_design(
                body_info, self.components, created_parts_dict, created_components_dict
            )
            if not new_body:
                new_body = MasterBody(body_id, body_name, self._grpc_client, is_surface=is_surface)
                self._master_component.part.bodies.append(new_body)
                self._clear_cached_bodies()
                self._grpc_client.log.debug(
                    f"Added new body '{body_name}' (ID: {body_id}) to root level."
                )

            if new_body:
                created_bodies_dict[body_id] = new_body

        # Handle modified bodies
        for body_info in tracker_response.get("modified_bodies", []):
            body_id = body_info["id"]
            body_name = body_info["name"]
            self._grpc_client.log.debug(
                f"Processing modified body: ID={body_id}, Name='{body_name}'"
            )
            updated = False

            for body in self.bodies:
                if body.id == body_id:
                    self._update_body(body, body_info)
                    updated = True
                    self._grpc_client.log.debug(
                        f"Modified body '{body_name}' (ID: {body_id}) updated at root level."
                    )
                    break

            if not updated:
                for component in self.components:
                    if self._find_and_update_body(body_info, component):
                        break

        # Handle deleted bodies
        for body_info in tracker_response.get("deleted_bodies", []):
            body_id = body_info["id"]
            self._grpc_client.log.debug(f"Processing deleted body: ID={body_id}")
            removed = False

            for body in self.bodies:
                if body.id == body_id:
                    body._is_alive = False
                    for bd in self._master_component.part.bodies:
                        if bd.id == body_id:
                            self._master_component.part.bodies.remove(bd)
                            break
                    self._clear_cached_bodies()
                    removed = True
                    self._grpc_client.log.info(
                        f"Deleted body (ID: {body_id}) removed from root level."
                    )
                    break

            if not removed:
                for component in self.components:
                    if self._find_and_remove_body(body_info, component):
                        break

    def update_parts(self, created_parts=None, modified_parts=None, deleted_parts=None):
        """Update parts with consolidated handling of created, modified, and deleted parts.

        Parameters
        ----------
        created_parts : list, optional
            List of created part information from tracker response.
        modified_parts : list, optional
            List of modified part information from tracker response.
        deleted_parts : list, optional
            List of deleted part information from tracker response.

        Returns
        -------
        dict
            Dictionary of created parts with part_id as key and Part object as value.
        """
        created_parts_dict = {}

        if created_parts:
            created_parts_dict = self._handle_created_parts(created_parts)
        if modified_parts:
            self._handle_modified_parts(modified_parts)
        if deleted_parts:
            self._handle_deleted_parts(deleted_parts)

        return created_parts_dict

    def _update_components(
        self,
        created_components=None,
        modified_components=None,
        deleted_components=None,
        created_parts=None,
    ):
        """Update components with consolidated handling of created, modified, and deleted components.

        Parameters
        ----------
        created_components : list, optional
            List of created component information from tracker response.
        modified_components : list, optional
            List of modified component information from tracker response.
        deleted_components : list, optional
            List of deleted component information from tracker response.
        created_parts : dict, optional
            Dictionary of created parts from previous step.

        Returns
        -------
        dict
            Dictionary of created components with component_id as key and Component object as value.
        """
        created_components_dict = {}

        if created_components:
            created_components_dict = self._handle_created_components(
                created_components, created_parts
            )
        if modified_components:
            self._handle_modified_components(modified_components)
        if deleted_components:
            self._handle_deleted_components(deleted_components)

        return created_components_dict

    def _update_bodies(
        self,
        created_bodies=None,
        modified_bodies=None,
        deleted_bodies=None,
        created_parts=None,
        created_components=None,
    ):
        """Update bodies with consolidated handling of created, modified, and deleted bodies.

        Parameters
        ----------
        created_bodies : list, optional
            List of created body information from tracker response.
        modified_bodies : list, optional
            List of modified body information from tracker response.
        deleted_bodies : list, optional
            List of deleted body information from tracker response.
        created_parts : dict, optional
            Dictionary of created parts from previous step.
        created_components : dict, optional
            Dictionary of created components from previous step.

        Returns
        -------
        dict
            Dictionary of created bodies with body_id as key and Body object as value.
        """
        created_bodies_dict = {}

        if created_bodies:
            created_bodies_dict = self._handle_created_bodies(
                created_bodies, created_parts, created_components
            )
        if modified_bodies:
            self._handle_modified_bodies(modified_bodies)
        if deleted_bodies:
            self._handle_deleted_bodies(deleted_bodies)

        return created_bodies_dict

    # ================== PART HANDLERS ==================

    def _handle_created_parts(self, created_parts):
        """Handle creation of new parts from tracker response.

        Returns
        -------
        dict
            Dictionary of created parts with part_id as key and Part object as value.
        """
        created_parts_dict = {}

        for part_info in created_parts:
            part_id = part_info["id"]
            part_name = part_info.get("name", f"Part_{part_id}")
            self._grpc_client.log.debug(
                f"Processing created part: ID={part_id}, Name='{part_name}'"
            )

            # Check if part already exists
            if self._find_existing_part(part_id):
                self._grpc_client.log.debug(
                    f"Created part '{part_name}' (ID: {part_id}) already exists."
                )
                continue

            # Create new part
            new_part = Part(part_id, part_name, [], [])
            created_parts_dict[part_id] = new_part
            # TODO: Add part to appropriate collection/registry
            self._grpc_client.log.debug(f"Created new part '{part_name}' (ID: {part_id})")

        return created_parts_dict

    def _handle_modified_parts(self, modified_parts):
        """Handle modification of existing parts from tracker response."""
        for part_info in modified_parts:
            part_id = part_info["id"]
            part_name = part_info.get("name", f"Part_{part_id}")
            self._grpc_client.log.debug(
                f"Processing modified part: ID={part_id}, Name='{part_name}'"
            )

            # Try to find and update the part
            updated = self._find_and_update_part(part_info)
            if not updated:
                self._grpc_client.log.warning(
                    f"Could not find part to update: '{part_name}' (ID: {part_id})"
                )

    def _handle_deleted_parts(self, deleted_parts):
        """Handle deletion of parts from tracker response."""
        for part_info in deleted_parts:
            part_id = part_info["id"]
            self._grpc_client.log.debug(f"Processing deleted part: ID={part_id}")

            # Try to find and remove the part
            removed = self._find_and_remove_part(part_info)
            if not removed:
                self._grpc_client.log.warning(f"Could not find part to delete: ID={part_id}")

    # ================== COMPONENT HANDLERS ==================

    def _handle_created_components(self, created_components, created_parts=None):
        """Handle creation of new components from tracker response.

        Parameters
        ----------
        created_components : list
            List of created component information from tracker response.
        created_parts : dict, optional
            Dictionary of created parts from previous step.

        Returns
        -------
        dict
            Dictionary of created components with component_id as key and Component object as value.
        """
        created_components_dict = {}

        for component_info in created_components:
            component_id = component_info["id"]
            component_name = component_info.get("name", f"Component_{component_id}")
            self._grpc_client.log.debug(
                f"Processing created component: ID={component_id}, Name='{component_name}'"
            )

            # Check if component already exists
            if any(comp.id == component_id for comp in self.components):
                self._grpc_client.log.debug(
                    f"Created component '{component_name}' (ID: {component_id}) already exists."
                )
                continue

            # Try to add the component to the appropriate parent
            new_component = self._find_and_add_component_to_design(
                component_info, self.components, created_parts
            )
            if new_component:
                created_components_dict[component_id] = new_component
            else:
                self._grpc_client.log.warning(
                    f"Could not find parent for component '{component_name}' (ID: {component_id})"
                )

        return created_components_dict

    def _handle_modified_components(self, serialized_modified_components):
        """Handle modification of existing components from tracker response."""
        for component_info in serialized_modified_components:
            component_id = component_info["id"]
            component_name = component_info.get("name", f"Component_{component_id}")
            self._grpc_client.log.debug(
                f"Processing modified component: ID={component_id}, Name='{component_name}'"
            )

            # Try to find and update the component
            updated = self._find_and_update_component(component_info, self.components)
            if not updated:
                self._grpc_client.log.warning(
                    f"Could not find component to update: '{component_name}' (ID: {component_id})"
                )

    def _handle_deleted_components(self, deleted_components):
        """Handle deletion of components from tracker response."""
        for component_info in deleted_components:
            component_id = component_info["id"]
            self._grpc_client.log.debug(f"Processing deleted component: ID={component_id}")

            # Try to find and remove the component
            removed = self._find_and_remove_component(component_info, self.components)
            if not removed:
                self._grpc_client.log.warning(
                    f"Could not find component to delete: ID={component_id}"
                )

    # ================== BODY HANDLERS ==================

    def _handle_created_bodies(self, created_bodies, created_parts=None, created_components=None):
        """Handle creation of new bodies from tracker response.

        Parameters
        ----------
        created_bodies : list
            List of created body information from tracker response.
        created_parts : dict, optional
            Dictionary of created parts from previous step.
        created_components : dict, optional
            Dictionary of created components from previous step.

        Returns
        -------
        dict
            Dictionary of created bodies with body_id as key and Body object as value.
        """
        created_bodies_dict = {}

        for body_info in created_bodies:
            body_id = body_info["id"]
            body_name = body_info["name"]
            is_surface = body_info.get("is_surface", False)
            self._grpc_client.log.debug(
                f"Processing created body: ID={body_id}, Name='{body_name}'"
            )

            if any(body.id == body_id for body in self.bodies):
                self._grpc_client.log.debug(
                    f"Created body '{body_name}' (ID: {body_id}) already exists at root level."
                )
                continue

            new_body = self._find_and_add_body_to_design(
                body_info, self.components, created_parts, created_components
            )
            if not new_body:
                new_body = MasterBody(body_id, body_name, self._grpc_client, is_surface=is_surface)
                self._master_component.part.bodies.append(new_body)
                self._clear_cached_bodies()
                self._grpc_client.log.debug(
                    f"Added new body '{body_name}' (ID: {body_id}) to root level."
                )

            if new_body:
                created_bodies_dict[body_id] = new_body

        return created_bodies_dict

    def _handle_modified_bodies(self, modified_bodies):
        """Handle modification of existing bodies from tracker response."""
        for body_info in modified_bodies:
            body_id = body_info["id"]
            body_name = body_info["name"]
            self._grpc_client.log.debug(
                f"Processing modified body: ID={body_id}, Name='{body_name}'"
            )
            updated = False

            for body in self.bodies:
                if body.id == body_id:
                    self._update_body(body, body_info)
                    updated = True
                    self._grpc_client.log.debug(
                        f"Modified body '{body_name}' (ID: {body_id}) updated at root level."
                    )
                    break

            if not updated:
                for component in self.components:
                    if self._find_and_update_body(body_info, component):
                        break

    def _handle_deleted_bodies(self, deleted_bodies):
        """Handle deletion of bodies from tracker response."""
        for body_info in deleted_bodies:
            body_id = body_info["id"]
            self._grpc_client.log.debug(f"Processing deleted body: ID={body_id}")
            removed = False

            for body in self.bodies:
                if body.id == body_id:
                    body._is_alive = False
                    for bd in self._master_component.part.bodies:
                        if bd.id == body_id:
                            self._master_component.part.bodies.remove(bd)
                            break
                    self._clear_cached_bodies()
                    removed = True
                    self._grpc_client.log.info(
                        f"Deleted body (ID: {body_id}) removed from root level."
                    )
                    break

            if not removed:
                for component in self.components:
                    if self._find_and_remove_body(body_info, component):
                        break

    # ================== HELPER METHODS ==================
    #
    # Processing order for tracker updates:
    # 1. Parts (foundational - no dependencies)
    # 2. Components (depend on parts via master_component.part)
    # 3. Bodies (depend on parts/components as containers)
    # 4. Deletions (reverse order to avoid dependency issues)

    def _find_existing_part(self, part_id):
        """Find if a part with the given ID already exists."""
        # Search through master component parts
        if hasattr(self, "_master_component") and self._master_component:
            if self._master_component.part.id == part_id:
                return self._master_component.part

        # Search through all component master parts
        for component in self._get_all_components():
            if (
                hasattr(component, "_master_component")
                and component._master_component
                and component._master_component.part.id == part_id
            ):
                return component._master_component.part

        return None

    def _get_all_components(self):
        """Get all components in the hierarchy recursively."""
        all_components = []

        def _collect_components(components):
            for comp in components:
                all_components.append(comp)
                _collect_components(comp.components)

        _collect_components(self.components)
        return all_components

    def _find_and_update_part(self, part_info):
        """Find and update an existing part."""
        part_id = part_info["id"]
        existing_part = self._find_existing_part(part_id)

        if existing_part:
            # Update part properties
            if "name" in part_info:
                existing_part._name = part_info["name"]
            self._grpc_client.log.debug(f"Updated part '{existing_part.name}' (ID: {part_id})")
            return True

        return False

    def _find_and_remove_part(self, part_info):
        """Find and remove a part from the design."""
        part_id = part_info["id"]
        existing_part = self._find_existing_part(part_id)

        if existing_part:
            # Mark as not alive (if applicable)
            if hasattr(existing_part, "_is_alive"):
                existing_part._is_alive = False
            self._grpc_client.log.debug(f"Removed part (ID: {part_id})")
            # TODO: Implement actual removal logic based on where parts are stored
            return True

        return False

    def _find_and_add_component_to_design(
        self,
        component_info: dict,
        parent_components: list["Component"],
        created_parts: dict[str, Part] | None = None,
        created_master_components: dict[str, MasterComponent] | None = None,
    ) -> "Component | None":
        """Recursively find the appropriate parent and add a new component to it.

        Parameters
        ----------
        component_info : dict
            Information about the component to create.
        parent_components : list
            List of potential parent components to search.
        created_parts : dict, optional
            Dictionary of created parts from previous step.
        created_master_components : dict, optional
            Dictionary of created master components from current step.

        Returns
        -------
        Component or None
            The newly created component if successful, None otherwise.
        """
        # Early return if there are no components to search through
        if not parent_components:
            return None

        new_component_parent_id = component_info.get("parent_id")
        master_id = component_info.get("master_id")

        # Find the master component for this component
        master_component = None
        if created_master_components and master_id:
            master_component = created_master_components.get(master_id)

        # Check if this should be added to the root design
        if new_component_parent_id == self.id:
            # Create the Component object with master_component
            new_component = Component(
                parent_component=None,
                name=component_info["name"],
                template=self,
                grpc_client=self._grpc_client,
                master_component=master_component,
                preexisting_id=component_info["id"],
                read_existing_comp=True,
            )
            self.components.append(new_component)
            self._grpc_client.log.debug(f"Added component '{component_info['id']}' to root design")
            return new_component

        # Search through existing components for the parent
        for component in parent_components:
            if component.id == new_component_parent_id:
                new_component = Component(
                    name=component_info["name"],
                    template=component,
                    grpc_client=self._grpc_client,
                    master_component=master_component,
                    preexisting_id=component_info["id"],
                    read_existing_comp=True,
                )
                component.components.append(new_component)
                self._grpc_client.log.debug(
                    f"Added component '{component_info['id']}' to component '{component.name}'"
                )
                return new_component

            # Recursively search in child components
            result = self._find_and_add_component_to_design(
                component_info, component.components, created_parts, created_master_components
            )
            if result:
                return result

        return None

    # This method is subject to change based on how component updates are defined.
    def _find_and_update_component(self, component_info, components):
        """Recursively find and update an existing component in the hierarchy."""
        component_id = component_info["id"]

        for component in components:
            if component.id == component_id:
                # Update component properties
                if "name" in component_info:
                    component._name = component_info["name"]
                self._grpc_client.log.debug(
                    f"Updated component '{component.name}' (ID: {component.id})"
                )
                return True

            if self._find_and_update_component(component_info, component.components):
                return True

        return False

    def _find_and_remove_component(self, component_info, components, parent_component=None):
        """Recursively find and remove a component from the hierarchy."""
        component_id = component_info["id"]

        for i, component in enumerate(components):
            if component.id == component_id:
                component._is_alive = False
                components.pop(i)
                self._grpc_client.log.debug(
                    f"Removed component '{component.name}' (ID: {component_id}) "
                    f"from {'root design' if parent_component is None else parent_component.name}"
                )
                return True

            if self._find_and_remove_component(component_info, component.components, component):
                return True

        return False

    def _update_body(self, existing_body, body_info):
        """Update an existing body with new information from tracker response."""
        self._grpc_client.log.debug(
            f"Updating body '{existing_body.name}' "
            f"(ID: {existing_body.id}) with new info: {body_info}"
        )
        existing_body.name = body_info["name"]
        existing_body._template._is_surface = body_info.get("is_surface", False)

    def _find_and_add_body_to_design(
        self,
        tracked_body_info: dict,
        components: list["Component"],
        created_parts: dict[str, Part] | None = None,
        created_components: dict[str, "Component"] | None = None,
    ) -> MasterBody | None:
        """Recursively find the appropriate component and add a new body to it.

        Parameters
        ----------
        body_info : dict
            Information about the body to create.
        components : list[Component]
            List of components to search.
        created_parts : dict[str, Part], optional
            Dictionary of created parts from previous step.
        created_components : dict[str, Component], optional
            Dictionary of created components from previous step.

        Returns
        -------
        MasterBody | None
            The newly created body if successful, None otherwise.
        """
        if not components:
            return None

        for component in components:
            parent_id_for_body = component._master_component.part.id
            if parent_id_for_body == tracked_body_info.get("parent_id"):
                new_body = MasterBody(
                    tracked_body_info["id"],
                    tracked_body_info["name"],
                    self._grpc_client,
                    is_surface=tracked_body_info.get("is_surface", False),
                )
                component._master_component.part.bodies.append(new_body)
                component._clear_cached_bodies()
                self._grpc_client.log.debug(
                    f"Added new body '{new_body.name}' (ID: {new_body.id}) "
                    f"to component '{component.name}' (ID: {component.id})"
                )
                return new_body

            result = self._find_and_add_body_to_design(
                tracked_body_info, component.components, created_parts, created_components
            )
            if result:
                return result

        return None

    def _find_and_update_body(self, body_info, component):
        """Recursively find and update an existing body in the component hierarchy."""
        for body in component.bodies:
            if body.id == body_info["id"]:
                self._update_body(body, body_info)
                self._grpc_client.log.debug(
                    f"Updated body '{body.name}' (ID: {body.id}) in component "
                    f"'{component.name}' (ID: {component.id})"
                )
                return True

        for subcomponent in component.components:
            if self._find_and_update_body(body_info, subcomponent):
                return True

        return False

    def _find_and_remove_body(self, body_info, component):
        """Recursively find and remove a body from the component hierarchy."""
        for body in component.bodies:
            body_info_id = body_info["id"]
            if body.id == f"{component.id}/{body_info_id}":
                body._is_alive = False
                for bd in component._master_component.part.bodies:
                    if bd.id == body_info_id:
                        component._master_component.part.bodies.remove(bd)
                        break
                component._clear_cached_bodies()
                self._grpc_client.log.debug(
                    f"Removed body (ID: {body_info['id']}) from component "
                    f"'{component.name}' (ID: {component.id})"
                )
                return True

        for subcomponent in component.components:
            if self._find_and_remove_body(body_info, subcomponent):
                return True

        return False
