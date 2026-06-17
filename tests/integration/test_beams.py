# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
"""Test beam interaction."""

from pint import Quantity
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.designer.beam import (
    BeamCrossSectionInfo,
    BeamProperties,
    SectionAnchorType,
)
from ansys.geometry.core.math import (
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    Frame,
    Point3D,
    UnitVector3D,
)
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Distance
from ansys.geometry.core.shapes import ParamUV


def test_beams(modeler: Modeler):
    """Test beam creation."""
    design = modeler.create_design("BeamCreation")

    circle_profile_1 = design.add_beam_circular_profile(
        "CircleProfile1", Quantity(10, UNITS.mm), Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_Y
    )

    assert circle_profile_1.id is not None
    assert circle_profile_1.center == Point3D([0, 0, 0])
    assert circle_profile_1.radius.value.m_as(DEFAULT_UNITS.LENGTH) == 0.01
    assert circle_profile_1.direction_x == UNITVECTOR3D_X
    assert circle_profile_1.direction_y == UNITVECTOR3D_Y

    circle_profile_2 = design.add_beam_circular_profile(
        "CircleProfile2",
        Distance(20, UNITS.mm),
        Point3D([10, 20, 30], UNITS.mm),
        UnitVector3D([1, 1, 1]),
        UnitVector3D([0, -1, 1]),
    )

    assert circle_profile_2.id is not None
    assert circle_profile_2.id is not circle_profile_1.id

    with pytest.raises(ValueError, match="Radius must be a real positive value."):
        design.add_beam_circular_profile(
            "InvalidProfileRadius",
            Quantity(-10, UNITS.mm),
            Point3D([0, 0, 0]),
            UNITVECTOR3D_X,
            UNITVECTOR3D_Y,
        )

    with pytest.raises(ValueError, match="Direction X and direction Y must be perpendicular."):
        design.add_beam_circular_profile(
            "InvalidUnitVectorAlignment",
            Quantity(10, UNITS.mm),
            Point3D([0, 0, 0]),
            UNITVECTOR3D_X,
            UnitVector3D([-1, -1, -1]),
        )

    beam_1 = design.create_beam(
        Point3D([9, 99, 999], UNITS.mm), Point3D([8, 88, 888], UNITS.mm), circle_profile_1
    )

    assert beam_1.id is not None
    assert beam_1.start == Point3D([9, 99, 999], UNITS.mm)
    assert beam_1.end == Point3D([8, 88, 888], UNITS.mm)
    assert beam_1.profile == circle_profile_1
    assert beam_1.parent_component.id == design.id
    assert beam_1.is_alive
    assert len(design.beams) == 1
    assert design.beams[0] == beam_1

    beam_1_str = str(beam_1)
    assert "ansys.geometry.core.designer.Beam" in beam_1_str
    assert "  Exists               : True" in beam_1_str
    assert "  Start                : [0.009" in beam_1_str
    assert "  End                  : [0.008" in beam_1_str
    assert "  Parent component     : BeamCreation" in beam_1_str
    assert "  Beam Profile info" in beam_1_str
    assert "  -----------------" in beam_1_str
    assert "ansys.geometry.core.designer.BeamCircularProfile " in beam_1_str
    assert "  Name                 : CircleProfile1" in beam_1_str
    assert "  Radius               : 10.0 millimeter" in beam_1_str
    assert "  Center               : [0.0,0.0,0.0] in meters" in beam_1_str
    assert "  Direction x          : [1.0,0.0,0.0]" in beam_1_str
    assert "  Direction y          : [0.0,1.0,0.0]" in beam_1_str

    nested_component = design.add_component("NestedComponent")
    beam_2 = nested_component.create_beam(
        Point3D([7, 77, 777], UNITS.mm), Point3D([6, 66, 666], UNITS.mm), circle_profile_2
    )
    beam_3 = nested_component.create_beam(
        Point3D([8, 88, 888], UNITS.mm), Point3D([7, 77, 777], UNITS.mm), circle_profile_2
    )

    assert beam_2.id is not None
    assert beam_2.profile == circle_profile_2
    assert beam_2.parent_component.id == nested_component.id
    assert beam_2.is_alive
    assert beam_3.id is not None
    assert beam_3.profile == circle_profile_2
    assert beam_3.parent_component.id == nested_component.id
    assert beam_3.is_alive
    assert beam_2.id != beam_3.id
    assert len(nested_component.beams) == 2
    assert nested_component.beams[0] == beam_2
    assert nested_component.beams[1] == beam_3

    nested_component.delete_beam(beam_1)

    assert beam_2.is_alive
    assert nested_component.beams[0].is_alive
    assert beam_3.is_alive
    assert nested_component.beams[1].is_alive
    assert beam_1.is_alive
    assert design.beams[0].is_alive

    nested_component.delete_beam(beam_2)
    assert not beam_2.is_alive
    assert not nested_component.beams[0].is_alive
    assert beam_3.is_alive
    assert nested_component.beams[1].is_alive
    assert beam_1.is_alive
    assert design.beams[0].is_alive

    design.delete_beam(beam_3)
    assert not beam_2.is_alive
    assert not nested_component.beams[0].is_alive
    assert not beam_3.is_alive
    assert not nested_component.beams[1].is_alive
    assert beam_1.is_alive
    assert design.beams[0].is_alive

    design.delete_beam(beam_1)
    assert not beam_2.is_alive
    assert not nested_component.beams[0].is_alive
    assert not beam_3.is_alive
    assert not nested_component.beams[1].is_alive
    assert not beam_1.is_alive
    assert not design.beams[0].is_alive

    assert len(design.beam_profiles) == 2
    design.delete_beam_profile("MyInventedBeamProfile")
    assert len(design.beam_profiles) == 2
    design.delete_beam_profile(circle_profile_1)
    assert len(design.beam_profiles) == 1
    design.delete_beam_profile(circle_profile_2)
    assert len(design.beam_profiles) == 0


def test_named_selections_beams(modeler: Modeler):
    """Test for verifying the correct creation of ``NamedSelection`` with beams."""
    design = modeler.create_design("NamedSelectionBeams_Test")

    circle_profile_1 = design.add_beam_circular_profile(
        "CircleProfile1", Quantity(10, UNITS.mm), Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_Y
    )
    beam_1 = design.create_beam(
        Point3D([9, 99, 999], UNITS.mm), Point3D([8, 88, 888], UNITS.mm), circle_profile_1
    )
    ns_beams = design.create_named_selection("CircleProfile", beams=[beam_1])
    assert len(design.named_selections) == 1
    assert design.named_selections[0].name == "CircleProfile"

    design.delete_named_selection(ns_beams)
    assert len(design.named_selections) == 0


def test_beam_cross_section_info_properties_and_repr():
    """Test BeamCrossSectionInfo property accessors and repr output."""
    section_frame = Frame(Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_Y)
    section_info = BeamCrossSectionInfo(
        SectionAnchorType.CENTROID,
        15.0,
        section_frame,
        None,
    )

    assert section_info.section_anchor == SectionAnchorType.CENTROID
    assert section_info.section_angle == 15.0
    assert section_info.section_frame == section_frame
    assert section_info.section_profile is None

    section_repr = repr(section_info)
    assert "ansys.geometry.core.designer.BeamCrossSectionInfo" in section_repr
    assert "Section Anchor       : CENTROID" in section_repr
    assert "Section Angle        : 15.0" in section_repr
    assert f"Section Frame        : {section_frame}" in section_repr
    assert "Section Profile info" in section_repr
    assert "None" in section_repr


def test_beam_properties_getters():
    """Test BeamProperties property accessors."""
    centroid = ParamUV(0.1, 0.2)
    shear_center = ParamUV(0.3, 0.4)
    properties = BeamProperties(
        area=1.0,
        centroid=centroid,
        warping_constant=2.0,
        ixx=3.0,
        ixy=4.0,
        iyy=5.0,
        shear_center=shear_center,
        torsion_constant=6.0,
    )

    assert properties.area == 1.0
    assert properties.centroid == centroid
    assert properties.warping_constant == 2.0
    assert properties.ixx == 3.0
    assert properties.ixy == 4.0
    assert properties.iyy == 5.0
    assert properties.shear_center == shear_center
    assert properties.torsion_constant == 6.0


def test_beams_get_named_selections(modeler: Modeler):
    """Test getting named selections associated with beams."""
    design = modeler.create_design("beam_named_selections")
    profile = design.add_beam_circular_profile("profile1", Distance(0.1, UNITS.m))
    beam1 = design.create_beam(Point3D([0, 0, 0]), Point3D([1, 0, 0]), profile)
    beam2 = design.create_beam(Point3D([0, 1, 0]), Point3D([1, 1, 0]), profile)

    design.create_named_selection("beam_ns_1", beams=[beam1])
    design.create_named_selection("beam_ns_2", beams=[beam2])

    for beam in design.beams:
        ns_list = beam.get_named_selections()
        if beam.id == beam1.id:
            assert len(ns_list) == 1
            assert any(ns.name == "beam_ns_1" for ns in ns_list)
        elif beam.id == beam2.id:
            assert len(ns_list) == 1
            assert any(ns.name == "beam_ns_2" for ns in ns_list)
        else:
            assert len(ns_list) == 0
