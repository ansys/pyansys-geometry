# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Provides various option classes."""

from dataclasses import asdict, dataclass
from enum import Enum, unique
from pathlib import Path

from pint import Quantity

from ansys.geometry.core.misc.checks import check_input_types
from ansys.geometry.core.misc.measurements import Angle, Distance
from ansys.geometry.core.shapes.surfaces.surface_evaluation import SurfaceEvaluation
from ansys.geometry.core.typing import Real


@dataclass
class ImportOptions:
    """Import options when opening a file.

    Parameters
    ----------
    cleanup_bodies : bool = False
        Simplify geometry and clean up topology.
    import_coordinate_systems : bool = False
        Import coordinate systems.
    import_curves : bool = False
        Import curves.
    import_hidden_components_and_geometry : bool = False
        Import hidden components and geometry.
    import_names : bool = False
        Import names of bodies and curves.
    import_planes : bool = False
        Import planes.
    import_points : bool = False
        Import points.
    import_named_selections : bool = True
        Import the named selections associated with the root component being inserted.
    import_as_lightweight : bool = False
        Import bodies as lightweight.
    import_using_spaceclaim_colors : bool = False
        Import geometry using SpaceClaim colors.

    Notes
    -----
    import_as_lightweight and import_using_spaceclaim_colors are only available
    starting in version 2027 R1.
    """

    cleanup_bodies: bool = False
    import_coordinate_systems: bool = False
    import_curves: bool = False
    import_hidden_components_and_geometry: bool = False
    import_names: bool = False
    import_planes: bool = False
    import_points: bool = False
    import_named_selections: bool = True
    import_as_lightweight: bool = False
    import_using_spaceclaim_colors: bool = False

    def to_dict(self):
        """Provide the dictionary representation of the ImportOptions class."""
        return {k: bool(v) for k, v in asdict(self).items()}


@dataclass
class ImportOptionsDefinitions:
    """Import options definitions when opening a file.

    Parameters
    ----------
    import_named_selections_keys : string = None
        Import the named selections keys associated with the root component being inserted.
    """

    import_named_selections_keys: str = None

    def to_dict(self):
        """Provide the dictionary representation of the ImportOptionsDefinitions class."""
        return {k: str(v) for k, v in asdict(self).items()}


class TessellationOptions:
    """Provides options for getting tessellation.

    Parameters
    ----------
    surface_deviation : Distance | Quantity | Real
        The maximum deviation from the true surface position.
        If a Real is provided, it is assumed to be in the default length unit.
    angle_deviation : Angle | Quantity | Real
        The maximum deviation from the true surface normal.
        If a Real is provided, it is assumed to be in radians.
    max_aspect_ratio : Real, default=0.0
        The maximum aspect ratio of facets.
    max_edge_length : Distance | Quantity | Real, default=0.0
        The maximum facet edge length.
    watertight : bool, default=False
        Whether triangles on opposite sides of an edge should match.
    """

    @check_input_types
    def __init__(
        self,
        surface_deviation: Distance | Quantity | Real,
        angle_deviation: Angle | Quantity | Real,
        max_aspect_ratio: Real = 0.0,
        max_edge_length: Distance | Quantity | Real = 0.0,
        watertight: bool = False,
    ):
        """Initialize ``TessellationOptions`` class."""
        # Convert inputs to Distance and Angle objects
        self._surface_deviation = (
            surface_deviation
            if isinstance(surface_deviation, Distance)
            else Distance(surface_deviation)
        )
        self._angle_deviation = (
            angle_deviation if isinstance(angle_deviation, Angle) else Angle(angle_deviation)
        )
        self._max_aspect_ratio = max_aspect_ratio
        self._max_edge_length = (
            max_edge_length if isinstance(max_edge_length, Distance) else Distance(max_edge_length)
        )
        self._watertight = watertight

    @property
    def surface_deviation(self) -> Distance:
        """Surface Deviation.

        The maximum deviation from the true surface position.
        """
        return self._surface_deviation

    @property
    def angle_deviation(self) -> Angle:
        """Angle deviation.

        The maximum deviation from the true surface normal.
        """
        return self._angle_deviation

    @property
    def max_aspect_ratio(self) -> Real:
        """Maximum aspect ratio.

        The maximum aspect ratio of facets.
        """
        return self._max_aspect_ratio

    @property
    def max_edge_length(self) -> Distance:
        """Maximum edge length.

        The maximum facet edge length.
        """
        return self._max_edge_length

    @property
    def watertight(self) -> bool:
        """Watertight.

        Whether triangles on opposite sides of an edge should match.
        """
        return self._watertight


class FMDExportOptions:
    """Provides options for FMD export.

    Parameters
    ----------
    deviation : Distance | Quantity | Real
        The maximum deviation from the true surface position.
        If a Real is provided, it is assumed to be in the default length unit.
        Must be between 0.00003 m and 0.002 m.
    angle : Angle | Quantity | Real
        The maximum deviation from the true surface normal.
        If a Real is provided, it is assumed to be in radians.
        Must be between 0.05 degrees (≈ 8.727e-4 rad) and 30 degrees (≈ 0.5236 rad).
    aspect_ratio : int, default=-3
        The maximum aspect ratio of facets.
    max_edge_length : Distance | Quantity | Real, default=0.0
        The maximum facet edge length.
    """

    @check_input_types
    def __init__(
        self,
        deviation: Distance | Quantity | Real,
        angle: Angle | Quantity | Real,
        aspect_ratio: int = -3,
        max_edge_length: Distance | Quantity | Real = 0.0,
    ):
        """Initialize ``FMDExportOptions`` class."""
        # Convert inputs to Distance and Angle objects
        self._deviation = deviation if isinstance(deviation, Distance) else Distance(deviation)
        _dev_m = self._deviation.value.m_as("m")
        if not (0.00003 <= _dev_m <= 0.002):
            raise ValueError(f"deviation must be between 0.00003 m and 0.002 m, got {_dev_m} m.")

        self._angle = angle if isinstance(angle, Angle) else Angle(angle)
        _ang_deg = self._angle.value.m_as("degree")
        if not (0.05 <= _ang_deg <= 30.0):
            raise ValueError(
                f"angle must be between 0.05 degrees and 30 degrees, got {_ang_deg:.6f} degrees."
            )

        self._aspect_ratio = aspect_ratio
        self._max_edge_length = (
            max_edge_length if isinstance(max_edge_length, Distance) else Distance(max_edge_length)
        )

    @property
    def deviation(self) -> Distance:
        """Deviation.

        The maximum deviation from the true surface position.
        """
        return self._deviation

    @property
    def angle(self) -> Angle:
        """Angle.

        The maximum deviation from the true surface normal.
        """
        return self._angle

    @property
    def aspect_ratio(self) -> int:
        """Aspect ratio.

        The maximum aspect ratio of facets.
        """
        return self._aspect_ratio

    @property
    def max_edge_length(self) -> Distance:
        """Maximum edge length.

        The maximum facet edge length.
        """
        return self._max_edge_length


@unique
class AnalysisType(Enum):
    """Provides values for the analysis type used during PMDB export."""

    THREE_D = 0
    TWO_D = 1


@unique
class PMDBMixedPartExportType(Enum):
    """Provides values for the mixed-part export type used during PMDB export."""

    NONE = 0
    SOLID = 1
    SHEET = 2
    WIRE = 3
    POINT = 4
    SOLID_SHEET = 5
    SOLID_WIRE = 6
    SOLID_POINT = 7
    SHEET_WIRE = 8
    SHEET_POINT = 9
    WIRE_POINT = 10
    SHEET_WIRE_POINT = 11
    SOLID_WIRE_POINT = 12
    SOLID_SHEET_POINT = 13
    SOLID_SHEET_WIRE = 14
    ALL = 15


@unique
class PMDBAttachWeightClass(Enum):
    """Provides values for the attach weight class used during PMDB export."""

    HEAVYWEIGHT = 0
    MIDDLEWEIGHT = 1
    LIGHTWEIGHT = 2
    FEATHERWEIGHT = 3


@unique
class PMDBImportParameterType(Enum):
    """Provides values for the parameter processing type used during PMDB export."""

    NONE = 0
    INDEPENDENT = 1
    ALL = 2


@unique
class PMDBPlugInFacetQuality(Enum):
    """Provides values for the plug-in facet quality used during PMDB export."""

    NONE = 0
    VERY_COARSE = 1
    COARSE = 2
    NORMAL = 3
    FINE = 4
    VERY_FINE = 5
    SOURCE = 6
    USER_DEFINED = 7


@unique
class PMDBTargetApplication(Enum):
    """Provides values for the target application used during PMDB export."""

    PARTMGR = 0
    DESIGNMODELER = 1
    FLUENTMESHING = 2
    AIM = 3
    SPACECLAIM = 4


@dataclass
class PMDBExportOptions:
    """Provides options for PMDB export.

    Parameters
    ----------
    parameter_prefixes : str, default: ""
        Prefixes used to filter parameters for export.
    cad_attribute_prefixes : str, default: ""
        Prefixes used to filter CAD attributes for export.
    named_selection_prefixes : str, default: ""
        Prefixes used to filter named selections for export.
    analysis_type : AnalysisType, default: AnalysisType.THREE_D
        The analysis type (2D or 3D).
    mixed_part_export_type : PMDBMixedPartExportType, default: PMDBMixedPartExportType.NONE
        The type of mixed parts to export.
    attach_flattened_assembly : bool, default: False
        Whether to attach the assembly in a flattened structure.
    use_cad_mass_properties : bool, default: False
        Whether to use CAD mass properties.
    plane_prefixes : str, default: ""
        Prefixes used to filter planes for export.
    coordinate_system_prefixes : str, default: ""
        Prefixes used to filter coordinate systems for export.
    advanced_geom_processing : bool, default: False
        Whether to enable advanced geometry processing.
    angular_deviation : float, default: 0.0
        Angular deviation for faceting (in degrees).
    attach_weight_class : PMDBAttachWeightClass, default: PMDBAttachWeightClass.HEAVYWEIGHT
        The weight class for the attachment.
    cad_associativity : bool, default: False
        Whether to enable CAD associativity.
    cad_attribute_transfer : bool, default: False
        Whether to transfer CAD attributes.
    do_smart_update : bool, default: False
        Whether to perform a smart update.
    geometry_deviation : float, default: 0.0
        Geometry deviation for faceting (in meters).
    process_coordinate_sys : bool, default: False
        Whether to process coordinate systems.
    process_planes : bool, default: False
        Whether to process planes.
    import_using_instances : bool, default: False
        Whether to import using instances.
    process_work_points : bool, default: False
        Whether to process work points.
    is_selective_update : bool, default: False
        Whether to perform a selective update.
    material_properties : bool, default: False
        Whether to include material properties.
    granta_material_properties : bool, default: False
        Whether to include Granta material properties.
    max_facet_size : float, default: 0.0
        Maximum facet size (in meters). Zero means no limit.
    named_selection : bool, default: False
        Whether to export named selections.
    parameter_processing_type : PMDBImportParameterType, default: PMDBImportParameterType.NONE
        The type of parameters to process.
    plug_in_facet_quality : PMDBPlugInFacetQuality, default: PMDBPlugInFacetQuality.NONE
        The facet quality setting for plug-in readers.
    process_enclosure_and_symmetry : bool, default: False
        Whether to process enclosure and symmetry.
    reader_save_part : bool, default: False
        Whether the reader should save the part.
    target_application : PMDBTargetApplication, default: PMDBTargetApplication.PARTMGR
        The target application for the exported PMDB.
    temp_directory : str, default: ""
        Temporary directory path used during export.
    process_physics_definition : bool, default: False
        Whether to process physics definitions.
    process_solid_bodies : bool, default: False
        Whether to process solid bodies.
    process_surface_bodies : bool, default: False
        Whether to process surface bodies.
    process_line_bodies : bool, default: False
        Whether to process line bodies.
    """

    parameter_prefixes: str = ""
    cad_attribute_prefixes: str = ""
    named_selection_prefixes: str = ""
    analysis_type: AnalysisType = AnalysisType.THREE_D
    mixed_part_export_type: PMDBMixedPartExportType = PMDBMixedPartExportType.ALL
    attach_flattened_assembly: bool = True
    use_cad_mass_properties: bool = True
    plane_prefixes: str = ""
    coordinate_system_prefixes: str = ""
    advanced_geom_processing: bool = False
    angular_deviation: float = 0.0
    attach_weight_class: PMDBAttachWeightClass = PMDBAttachWeightClass.HEAVYWEIGHT
    cad_associativity: bool = False
    cad_attribute_transfer: bool = True
    do_smart_update: bool = False
    geometry_deviation: float = 0.0
    process_coordinate_sys: bool = True
    process_planes: bool = True
    import_using_instances: bool = True
    process_work_points: bool = True
    is_selective_update: bool = False
    material_properties: bool = True
    granta_material_properties: bool = False
    max_facet_size: float = 0.0
    named_selection: bool = True
    parameter_processing_type: PMDBImportParameterType = PMDBImportParameterType.ALL
    plug_in_facet_quality: PMDBPlugInFacetQuality = PMDBPlugInFacetQuality.SOURCE
    process_enclosure_and_symmetry: bool = True
    reader_save_part: bool = False
    target_application: PMDBTargetApplication = PMDBTargetApplication.PARTMGR
    temp_directory: str | Path | None = None
    process_physics_definition: bool = True
    process_solid_bodies: bool = True
    process_surface_bodies: bool = True
    process_line_bodies: bool = True


class VolumeExtractOptions:
    """Provides options for volume extraction.

    Parameters
    ----------
    create_shared_topology : bool | None, default: None
        Create shared topology between capping surfaces and the seed body.
    imprint_capping_edges : bool | None, default: None
        Imprint capping edges onto the seed body.
    merge_created_volume : bool | None, default: None
        Merge the created volume into the existing model.
    seed_point : SurfaceEvaluation | None, default: None
        Seed point on the surface from which to extract the volume.
    tolerance : Distance | Quantity | Real | None, default: None
        Tolerance for volume extraction.
        If a Real is provided, it is assumed to be in the default length unit.
    create_capping_surfaces : bool | None, default: None
        Create capping surfaces to close open regions.
    detect_leaks : bool | None, default: None
        Detect leaks in the model before extraction.
    """

    @check_input_types
    def __init__(
        self,
        create_shared_topology: bool | None = None,
        imprint_capping_edges: bool | None = None,
        merge_created_volume: bool | None = None,
        seed_point: SurfaceEvaluation | None = None,
        tolerance: Distance | Quantity | Real | None = None,
        create_capping_surfaces: bool | None = None,
        detect_leaks: bool | None = None,
    ):
        """Initialize ``VolumeExtractOptions`` class."""
        self._create_shared_topology = create_shared_topology
        self._imprint_capping_edges = imprint_capping_edges
        self._merge_created_volume = merge_created_volume
        self._seed_point = seed_point
        self._tolerance = (
            tolerance
            if tolerance is None or isinstance(tolerance, Distance)
            else Distance(tolerance)
        )
        self._create_capping_surfaces = create_capping_surfaces
        self._detect_leaks = detect_leaks

    @property
    def create_shared_topology(self) -> bool | None:
        """Create shared topology.

        Create shared topology between capping surfaces and the seed body.
        """
        return self._create_shared_topology

    @property
    def imprint_capping_edges(self) -> bool | None:
        """Imprint capping edges.

        Imprint capping edges onto the seed body.
        """
        return self._imprint_capping_edges

    @property
    def merge_created_volume(self) -> bool | None:
        """Merge created volume.

        Merge the created volume into the existing model.
        """
        return self._merge_created_volume

    @property
    def seed_point(self) -> SurfaceEvaluation | None:
        """Seed point.

        Seed point on the surface from which to extract the volume.
        """
        return self._seed_point

    @property
    def tolerance(self) -> Distance | None:
        """Tolerance.

        Tolerance for volume extraction.
        """
        return self._tolerance

    @property
    def create_capping_surfaces(self) -> bool | None:
        """Create capping surfaces.

        Create capping surfaces to close open regions.
        """
        return self._create_capping_surfaces

    @property
    def detect_leaks(self) -> bool | None:
        """Detect leaks.

        Detect leaks in the model before extraction.
        """
        return self._detect_leaks