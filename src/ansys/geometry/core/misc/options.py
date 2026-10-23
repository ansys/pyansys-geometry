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
from typing import TYPE_CHECKING

from pint import Quantity

from ansys.geometry.core.misc.checks import check_input_types
from ansys.geometry.core.misc.measurements import Angle, Distance
from ansys.geometry.core.shapes.surfaces.surface_evaluation import SurfaceEvaluation
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.math.vector import UnitVector3D


def _typechecked_dataclass(cls):
    """Create a dataclass whose generated ``__init__`` supports runtime type checking."""
    cls = dataclass(cls)
    cls.__init__ = check_input_types(cls.__init__)
    return cls


def _to_measurement(value, measurement_type: Distance | Angle):
    """Convert a ``Real`` or ``Quantity`` to the given measurement type, preserving ``None``."""
    if value is None or isinstance(value, measurement_type):
        return value
    return measurement_type(value)


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


@_typechecked_dataclass
class TessellationOptions:
    """Provides options for getting tessellation.

    Parameters
    ----------
    surface_deviation : Distance | Quantity | Real
        The maximum deviation from the true surface position.
        If a Real is provided, it is assumed to be in the default length unit.
    angle_deviation : Angle | Quantity | Real
        The maximum deviation from the true surface normal.
        If a Real is provided, it is assumed to be in the default angle unit.
    curve_deviation : Distance | Quantity | Real, default=0.0
        The maximum deviation from the true curve position.
        If a Real is provided, it is assumed to be in the default length unit.
    max_aspect_ratio : Real, default=0.0
        The maximum aspect ratio of facets.
    max_edge_length : Distance | Quantity | Real, default=0.0
        The maximum facet edge length.
    watertight : bool, default=False
        Whether triangles on opposite sides of an edge should match.
    """

    surface_deviation: Distance | Quantity | Real
    angle_deviation: Angle | Quantity | Real
    curve_deviation: Distance | Quantity | Real = 0.0
    max_aspect_ratio: Real = 0.0
    max_edge_length: Distance | Quantity | Real = 0.0
    watertight: bool = False

    def __post_init__(self):
        """Normalize measurement fields to ``Distance`` and ``Angle`` objects."""
        self.surface_deviation = _to_measurement(self.surface_deviation, Distance)
        self.angle_deviation = _to_measurement(self.angle_deviation, Angle)
        self.curve_deviation = _to_measurement(self.curve_deviation, Distance)
        self.max_edge_length = _to_measurement(self.max_edge_length, Distance)


@_typechecked_dataclass
class RayfireOptions:
    """Additional options for ray fire operations.

    Parameters
    ----------
    radius : Distance | Quantity | Real
        The radius of the ray.
        If a Real is provided, it is assumed to be in the default length unit.
    direction : UnitVector3D
        The direction for the ray to be fired in.
    max_distance : Distance | Quantity | Real
        The maximum distance the ray should travel.
        If a Real is provided, it is assumed to be in the default length unit.
    min_distance : Distance | Quantity | Real
        The minimum distance the ray should travel.
        If a Real is provided, it is assumed to be in the default length unit.
    tight_tolerance : bool, default=False
        Whether to use a tight tolerance for the ray fire operation.
    pick_back_faces : bool, default=False
        Whether to pick back faces during the ray fire operation.
    max_hits : int, default=0
        The maximum number of hits the ray should register.
    request_params : bool, default=False
        Whether to request additional parameters for the ray fire operation.
    request_secondary : bool, default=False
        Whether to request secondary hits for the ray fire operation.
    """

    radius: Distance | Quantity | Real
    direction: "UnitVector3D"
    max_distance: Distance | Quantity | Real
    min_distance: Distance | Quantity | Real
    tight_tolerance: bool = False
    pick_back_faces: bool = False
    max_hits: int = 0
    request_params: bool = False
    request_secondary: bool = False

    def __post_init__(self):
        """Normalize measurement fields to ``Distance`` objects."""
        self.radius = _to_measurement(self.radius, Distance)
        self.max_distance = _to_measurement(self.max_distance, Distance)
        self.min_distance = _to_measurement(self.min_distance, Distance)


@_typechecked_dataclass
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
        If a Real is provided, it is assumed to be in the default angle unit.
        Must be between 0.05 degrees (≈ 8.727e-4 rad) and 30 degrees (≈ 0.5236 rad).
    aspect_ratio : int, default=-3
        The maximum aspect ratio of facets.
    max_edge_length : Distance | Quantity | Real, default=0.0
        The maximum facet edge length.
    """

    deviation: Distance | Quantity | Real
    angle: Angle | Quantity | Real
    aspect_ratio: int = -3
    max_edge_length: Distance | Quantity | Real = 0.0

    def __post_init__(self):
        """Normalize measurement fields and validate their ranges."""
        self.deviation = _to_measurement(self.deviation, Distance)
        _dev_m = self.deviation.value.m_as("m")
        if not (0.00003 <= _dev_m <= 0.002):
            raise ValueError(f"deviation must be between 0.00003 m and 0.002 m, got {_dev_m} m.")

        self.angle = _to_measurement(self.angle, Angle)
        _ang_deg = self.angle.value.m_as("degree")
        if not (0.05 <= _ang_deg <= 30.0):
            raise ValueError(
                f"angle must be between 0.05 degrees and 30 degrees, got {_ang_deg:.6f} degrees."
            )

        self.max_edge_length = _to_measurement(self.max_edge_length, Distance)


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
    angular_deviation : Angle | Quantity | Real, default: 0.0
        Angular deviation for faceting.
        If a Real is provided, it is assumed to be in the default angle unit.
    attach_weight_class : PMDBAttachWeightClass, default: PMDBAttachWeightClass.HEAVYWEIGHT
        The weight class for the attachment.
    cad_associativity : bool, default: False
        Whether to enable CAD associativity.
    cad_attribute_transfer : bool, default: False
        Whether to transfer CAD attributes.
    do_smart_update : bool, default: False
        Whether to perform a smart update.
    geometry_deviation : Distance | Quantity | Real, default: 0.0
        Geometry deviation for faceting.
        If a Real is provided, it is assumed to be in the default length unit.
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
    max_facet_size : Distance | Quantity | Real, default: 0.0
        Maximum facet size. Zero means no limit.
        If a Real is provided, it is assumed to be in the default length unit.
    named_selection : bool, default: False
        Whether to export named selections.
    parameter_processing_type : PMDBImportParameterType, default: PMDBImportParameterType.NONE
        The type of parameters to process.
    plug_in_facet_quality : PMDBPlugInFacetQuality, default: PMDBPlugInFacetQuality.SOURCE
        The facet quality setting for plug-in readers.
        Automatically set to ``USER_DEFINED`` when ``angular_deviation``,
        ``geometry_deviation``, or ``max_facet_size`` is nonzero, including after
        field assignment. Custom controls override any supplied preset.
        Resetting all controls to zero does not restore the previous preset;
        a preset must then be assigned explicitly.
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
    angular_deviation: Angle | Quantity | Real = 0.0
    attach_weight_class: PMDBAttachWeightClass = PMDBAttachWeightClass.HEAVYWEIGHT
    cad_associativity: bool = False
    cad_attribute_transfer: bool = True
    do_smart_update: bool = False
    geometry_deviation: Distance | Quantity | Real = 0.0
    process_coordinate_sys: bool = True
    process_planes: bool = True
    import_using_instances: bool = True
    process_work_points: bool = True
    is_selective_update: bool = False
    material_properties: bool = True
    granta_material_properties: bool = False
    max_facet_size: Distance | Quantity | Real = 0.0
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

    def __setattr__(self, name: str, value: object) -> None:
        """Normalize custom controls and select user-defined facet quality."""
        if name == "angular_deviation":
            value = _to_measurement(value, Angle)
        elif name in ("geometry_deviation", "max_facet_size"):
            value = _to_measurement(value, Distance)

        object.__setattr__(self, name, value)
        controls = ("angular_deviation", "geometry_deviation", "max_facet_size")
        if name in (*controls, "plug_in_facet_quality") and any(
            self.__dict__[control].value.magnitude != 0
            for control in controls
            if control in self.__dict__
        ):
            object.__setattr__(self, "plug_in_facet_quality", PMDBPlugInFacetQuality.USER_DEFINED)


@_typechecked_dataclass
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

    create_shared_topology: bool | None = None
    imprint_capping_edges: bool | None = None
    merge_created_volume: bool | None = None
    seed_point: SurfaceEvaluation | None = None
    tolerance: Distance | Quantity | Real | None = None
    create_capping_surfaces: bool | None = None
    detect_leaks: bool | None = None

    def __post_init__(self):
        """Normalize the tolerance to a ``Distance`` object."""
        self.tolerance = _to_measurement(self.tolerance, Distance)
