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

"""Unit tests for beam entities."""

from types import SimpleNamespace
from unittest.mock import patch

from ansys.geometry.core.designer.beam import (
    Beam,
    BeamCircularProfile,
    BeamCrossSectionInfo,
    BeamProfile,
    BeamProperties,
    BeamType,
    SectionAnchorType,
)
from ansys.geometry.core.math import UNITVECTOR3D_X, UNITVECTOR3D_Y, Frame, Point3D
from ansys.geometry.core.misc import UNITS, Distance
from ansys.geometry.core.shapes import ParamUV


class _DummyParent:
    def __init__(self, name: str = "ParentComponent"):
        self.name = name


def test_beam_enums_are_stable():
    """Test beam-related enums and values."""
    assert BeamType.BEAM.value == 0
    assert BeamType.SPRING.value == 1
    assert BeamType.LINK_TRUSS.value == 2
    assert BeamType.CABLE.value == 3
    assert BeamType.PIPE.value == 4
    assert BeamType.THERMALFLUID.value == 5
    assert BeamType.UNKNOWN.value == 6

    assert SectionAnchorType.CENTROID.value == 0
    assert SectionAnchorType.SHEAR_CENTER.value == 1
    assert SectionAnchorType.ANCHOR_LOCATION.value == 2


def test_beam_profile_getters():
    """Test BeamProfile simple property accessors."""
    profile = BeamProfile("profile-id", "profile-name")

    assert profile.id == "profile-id"
    assert profile.name == "profile-name"


def test_beam_circular_profile_getters_and_repr():
    """Test BeamCircularProfile state and repr output."""
    profile = BeamCircularProfile(
        id="circular-id",
        name="CircleProfile",
        radius=Distance(10, UNITS.mm),
        center=Point3D([0, 0, 0]),
        direction_x=UNITVECTOR3D_X,
        direction_y=UNITVECTOR3D_Y,
    )

    assert profile.id == "circular-id"
    assert profile.name == "CircleProfile"
    assert profile.radius.value.m_as(UNITS.mm) == 10
    assert profile.center == Point3D([0, 0, 0])
    assert profile.direction_x == UNITVECTOR3D_X
    assert profile.direction_y == UNITVECTOR3D_Y

    profile_repr = repr(profile)
    assert "ansys.geometry.core.designer.BeamCircularProfile" in profile_repr
    assert "Name                 : CircleProfile" in profile_repr
    assert "Radius" in profile_repr
    assert "Center               : [0.0,0.0,0.0] in meters" in profile_repr
    assert "Direction x          : [1.0,0.0,0.0]" in profile_repr
    assert "Direction y          : [0.0,1.0,0.0]" in profile_repr


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


def test_beam_getters_and_repr_with_profile():
    """Test Beam properties and repr when a profile exists."""
    profile = BeamProfile("profile-id", "profile-name")
    parent = _DummyParent("BeamParent")

    with patch("ansys.geometry.core.designer.beam.check_type"):
        beam = Beam(
            id="beam-id",
            start=Point3D([0, 0, 0]),
            end=Point3D([1, 2, 3]),
            profile=profile,
            parent_component=parent,
            name="BeamName",
            is_deleted=False,
            is_reversed=True,
            is_rigid=False,
            beam_type=BeamType.BEAM,
        )

    assert beam.id == "beam-id"
    assert beam.start == Point3D([0, 0, 0])
    assert beam.end == Point3D([1, 2, 3])
    assert beam.profile == profile
    assert beam.parent_component == parent
    assert beam.is_alive is True

    beam_repr = repr(beam)
    assert "ansys.geometry.core.designer.Beam" in beam_repr
    assert "Exists               : True" in beam_repr
    assert "Start                : [0.0,0.0,0.0] in meters" in beam_repr
    assert "End                  : [1.0,2.0,3.0] in meters" in beam_repr
    assert "Parent component     : BeamParent" in beam_repr
    assert "Beam Profile info" in beam_repr
    assert "BeamProfile object" in beam_repr


def test_beam_get_named_selections_filters_membership():
    """Test that get_named_selections() only returns matching selections."""
    profile = BeamProfile("profile-id", "profile-name")
    parent = _DummyParent("SelectionParent")

    with patch("ansys.geometry.core.designer.beam.check_type"):
        target_beam = Beam(
            id="beam-target",
            start=Point3D([0, 0, 0]),
            end=Point3D([1, 0, 0]),
            profile=profile,
            parent_component=parent,
        )
        other_beam = Beam(
            id="beam-other",
            start=Point3D([0, 1, 0]),
            end=Point3D([1, 1, 0]),
            profile=profile,
            parent_component=parent,
        )

    ns1 = SimpleNamespace(name="ns1", beams=[target_beam])
    ns2 = SimpleNamespace(name="ns2", beams=[other_beam])
    ns3 = SimpleNamespace(name="ns3", beams=[target_beam, other_beam])
    fake_design = SimpleNamespace(named_selections=[ns1, ns2, ns3])

    with patch(
        "ansys.geometry.core.designer.beam.get_design_from_component", return_value=fake_design
    ):
        selected = target_beam.get_named_selections()

    assert selected == [ns1, ns3]


def test_beam_get_named_selections_returns_empty_when_no_match():
    """Test that get_named_selections() returns an empty list when there is no match."""
    profile = BeamProfile("profile-id", "profile-name")
    parent = _DummyParent("SelectionParent")

    with patch("ansys.geometry.core.designer.beam.check_type"):
        target_beam = Beam(
            id="beam-target",
            start=Point3D([0, 0, 0]),
            end=Point3D([1, 0, 0]),
            profile=profile,
            parent_component=parent,
        )
        other_beam = Beam(
            id="beam-other",
            start=Point3D([0, 1, 0]),
            end=Point3D([1, 1, 0]),
            profile=profile,
            parent_component=parent,
        )

    ns1 = SimpleNamespace(name="ns1", beams=[other_beam])
    fake_design = SimpleNamespace(named_selections=[ns1])

    with patch(
        "ansys.geometry.core.designer.beam.get_design_from_component", return_value=fake_design
    ):
        selected = target_beam.get_named_selections()

    assert selected == []


def test_beam_repr_with_none_profile():
    """Test Beam repr output when the profile is None."""
    parent = _DummyParent("NoProfileParent")

    with patch("ansys.geometry.core.designer.beam.check_type"):
        beam = Beam(
            id="beam-id",
            start=Point3D([0, 0, 0]),
            end=Point3D([1, 2, 3]),
            profile=None,
            parent_component=parent,
            beam_type=BeamType.CABLE,
        )

    assert beam.profile is None
    assert beam.parent_component == parent

    beam_repr = repr(beam)
    assert "Parent component     : NoProfileParent" in beam_repr
    assert "Beam Profile info" in beam_repr
    assert "None" in beam_repr
