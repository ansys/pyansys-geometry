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
"""Provides for creating and managing a beam."""

from enum import Enum
from typing import TYPE_CHECKING

from beartype import beartype as check_input_types

from ansys.geometry.core.materials.material import Material
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc.checks import check_type
from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.shapes.curves.trimmed_curve import TrimmedCurve
from ansys.geometry.core.shapes.parameterization import ParamUV

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.component import Component


class BeamType(Enum):
    """Provides values for the beam types supported."""

    BEAM = 0
    SPRING = 1
    LINK_TRUSS = 2
    CABLE = 3
    PIPE = 4
    THERMALFLUID = 5
    UNKNOWN = 6


class SectionAnchorType(Enum):
    """Provides values for the section anchor types supported."""

    CENTROID = 0
    SHEAR_CENTER = 1
    ANCHOR_LOCATION = 2


class BeamProfile:
    """Represents a single beam profile organized within the design assembly.

    This profile synchronizes to a design within a supporting Geometry service instance.

    Parameters
    ----------
    id : str
        Server-defined ID for the beam profile.
    name : str
        User-defined label for the beam profile.

    Notes
    -----
    ``BeamProfile`` objects are expected to be created from the ``Design`` object.
    This means that you are not expected to instantiate your own ``BeamProfile``
    object. You should call the specific ``Design`` API for the ``BeamProfile`` desired.
    """

    def __init__(self, id: str, name: str):
        """Initialize ``BeamProfile`` class."""
        self._id = id
        self._name = name

    @property
    def id(self) -> str:
        """ID of the beam profile."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the beam profile."""
        return self._name


class BeamCircularProfile(BeamProfile):
    """Represents a single circular beam profile.

    This profile synchronizes to a design within a supporting Geometry service instance.

    Parameters
    ----------
    id : str
        Server-defined ID for the beam profile.
    name : str
        User-defined label for the beam profile.
    radius : Distance
        Radius of the circle.
    center: Point3D
        3D point representing the center of the circle.
    direction_x: UnitVector3D
        X-axis direction.
    direction_y: UnitVector3D
        Y-axis direction.

    Notes
    -----
    ``BeamProfile`` objects are expected to be created from the ``Design`` object.
    This means that you are not expected to instantiate your own ``BeamProfile``
    object. You should call the specific ``Design`` API for the ``BeamProfile`` desired.
    """

    def __init__(
        self,
        id: str,
        name: str,
        radius: Distance,
        center: Point3D,
        direction_x: UnitVector3D,
        direction_y: UnitVector3D,
    ):
        """Initialize ``BeamCircularProfile`` class."""
        super().__init__(id, name)

        # Store specific BeamCircularProfile variables
        self._radius = radius
        self._center = center
        self._dir_x = direction_x
        self._dir_y = direction_y

    @property
    def radius(self) -> Distance:
        """Radius of the circular beam profile."""
        return self._radius

    @property
    def center(self) -> Point3D:
        """Center of the circular beam profile."""
        return self._center

    @property
    def direction_x(self) -> UnitVector3D:
        """X-axis direction of the circular beam profile."""
        return self._dir_x

    @property
    def direction_y(self) -> UnitVector3D:
        """Y-axis direction of the circular beam profile."""
        return self._dir_y

    def __repr__(self) -> str:
        """Represent the ``BeamCircularProfile`` as a string."""
        lines = [f"ansys.geometry.core.designer.BeamCircularProfile {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Radius               : {str(self.radius.value)}")
        lines.append(
            f"  Center               : [{','.join([str(x) for x in self.center])}] in meters"
        )
        lines.append(f"  Direction x          : [{','.join([str(x) for x in self.direction_x])}]")
        lines.append(f"  Direction y          : [{','.join([str(x) for x in self.direction_y])}]")
        return "\n".join(lines)


class BeamCrossSectionInfo:
    """Represents the cross-section information for a beam.

    Parameters
    ----------
    section_anchor : SectionAnchorType
        Specifies how the beam section is anchored to the beam path.
    section_angle : float
        The rotation angle of the cross section clockwise from the default perpendicular of the
        beam path.
    section_frame : Frame
        The section frame at the start of the beam.
    section_profile : BeamProfile
        The section profile in the XY plane.
    """

    @check_input_types
    def __init__(
        self,
        section_anchor: SectionAnchorType,
        section_angle: float,
        section_frame: Frame,
        section_profile: list[list[TrimmedCurve]] | None,
    ):
        """Initialize ``BeamCrossSectionInfo`` class."""
        self._section_anchor = section_anchor
        self._section_angle = section_angle
        self._section_frame = section_frame
        self._section_profile = section_profile

    @property
    def section_anchor(self) -> SectionAnchorType:
        """Specifies how the beam section is anchored to the beam path."""
        return self._section_anchor

    @property
    def section_angle(self) -> float:
        """Rotation angle of the cross section clockwise from the perpendicular of the beam path."""
        return self._section_angle

    @property
    def section_frame(self) -> Frame:
        """The section frame at the start of the beam."""
        return self._section_frame

    @property
    def section_profile(self) -> list[list[TrimmedCurve]] | None:
        """The section profile in the XY plane."""
        return self._section_profile

    def __repr__(self) -> str:
        """Represent the ``BeamCrossSectionInfo`` as a string."""
        lines = [f"ansys.geometry.core.designer.BeamCrossSectionInfo {hex(id(self))}"]
        lines.append(f"  Section Anchor       : {self.section_anchor.name}")
        lines.append(f"  Section Angle        : {self.section_angle}")
        lines.append(f"  Section Frame        : {self.section_frame}")
        lines.extend(
            ["\n", "  Section Profile info", "  -------------------", str(self.section_profile)]
        )
        return "\n".join(lines)


class BeamProperties:
    """Represents the properties of a beam.

    Parameters
    ----------
    area : float
        The cross-sectional area of the beam.
    centroid : ParamUV
        The centroid of the beam section.
    warping_constant : float
        The warping constant of the beam.
    ixx : float
        The moment of inertia about the x-axis.
    ixy : float
        The product of inertia.
    iyy : float
        The moment of inertia about the y-axis.
    shear_center : ParamUV
        The shear center of the beam.
    torsion_constant : float
        The torsion constant of the beam.
    """

    def __init__(
        self,
        area: float,
        centroid: ParamUV,
        warping_constant: float,
        ixx: float,
        ixy: float,
        iyy: float,
        shear_center: ParamUV,
        torsion_constant: float,
    ):
        """Initialize ``BeamProperties`` class."""
        check_type(area, float)
        check_type(centroid, ParamUV)
        check_type(warping_constant, float)
        check_type(ixx, float)
        check_type(ixy, float)
        check_type(iyy, float)
        check_type(shear_center, ParamUV)
        check_type(torsion_constant, float)

        self._area = area
        self._centroid = centroid
        self._warping_constant = warping_constant
        self._ixx = ixx
        self._ixy = ixy
        self._iyy = iyy
        self._shear_center = shear_center
        self._torsion_constant = torsion_constant

    @property
    def area(self) -> float:
        """The cross-sectional area of the beam."""
        return self._area

    @property
    def centroid(self) -> ParamUV:
        """The centroid of the beam section."""
        return self._centroid

    @property
    def warping_constant(self) -> float:
        """The warping constant of the beam."""
        return self._warping_constant

    @property
    def ixx(self) -> float:
        """The moment of inertia about the x-axis."""
        return self._ixx

    @property
    def ixy(self) -> float:
        """The product of inertia."""
        return self._ixy

    @property
    def iyy(self) -> float:
        """The moment of inertia about the y-axis."""
        return self._iyy

    @property
    def shear_center(self) -> ParamUV:
        """The shear center of the beam."""
        return self._shear_center

    @property
    def torsion_constant(self) -> float:
        """The torsion constant of the beam."""
        return self._torsion_constant


class Beam:
    """Represents a simplified solid body with an assigned 2D cross-section.

    This body synchronizes to a design within a supporting Geometry service instance.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    name : str
        User-defined label for the body.
    start : Point3D
        Start of the beam line segment.
    end : Point3D
        End of the beam line segment.
    profile : BeamProfile
        Beam profile to use to create the beam.
    parent_component : Component
        Parent component to nest the new beam under within the design assembly.
    """

    def __init__(
        self,
        id: str,
        start: Point3D,
        end: Point3D,
        profile: BeamProfile | None,
        # TODO: Beams need BeamProfiles imported from existing design
        # https://github.com/ansys/pyansys-geometry/issues/1825
        parent_component: "Component",
        name: str = None,
        is_deleted: bool = False,
        is_reversed: bool = False,
        is_rigid: bool = False,
        material: Material = None,
        cross_section: BeamCrossSectionInfo = None,
        properties: BeamProperties = None,
        shape: TrimmedCurve = None,
        beam_type: BeamType = None,
    ):
        """Initialize ``Beam`` class."""
        from ansys.geometry.core.designer.component import Component

        check_type(id, str)
        check_type(start, Point3D)
        check_type(end, Point3D)
        check_type(profile, (type(None), BeamProfile))
        check_type(parent_component, Component)

        self._id = id
        self._start = start
        self._end = end
        self._profile = profile
        self._parent_component = parent_component
        self._is_alive = True
        self._name = name
        self._is_deleted = is_deleted
        self._is_reversed = is_reversed
        self._is_rigid = is_rigid
        self._material = material
        self._cross_section = cross_section
        self._properties = properties
        self._shape = shape
        self._type = beam_type

    @property
    def id(self) -> str:
        """Service-defined ID of the beam."""
        return self._id

    @property
    def start(self) -> Point3D:
        """Start of the beam line segment."""
        return self._start

    @property
    def end(self) -> Point3D:
        """End of the beam line segment."""
        return self._end

    @property
    def profile(self) -> BeamProfile:
        """Beam profile of the beam line segment."""
        return self._profile

    @property
    def parent_component(self) -> "Component":
        """Component node that the beam is under."""
        return self._parent_component

    @property
    def is_alive(self) -> bool:
        """Flag indicating whether the beam is still alive on the server."""
        return self._is_alive

    def __repr__(self) -> str:
        """Represent the beam as a string."""
        lines = [f"ansys.geometry.core.designer.Beam {hex(id(self))}"]
        lines.append(f"  Exists               : {self.is_alive}")
        lines.append(
            f"  Start                : [{','.join([str(x) for x in self.start])}] in meters"
        )
        lines.append(f"  End                  : [{','.join([str(x) for x in self.end])}] in meters")
        lines.append(f"  Parent component     : {self.parent_component.name}")
        lines.extend(["\n", "  Beam Profile info", "  -----------------", str(self.profile)])
        return "\n".join(lines)
