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

"""Integration tests for BodySelectionBuilder."""

import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.designer.edge import CurveType
from ansys.geometry.core.designer.face import SurfaceType
from ansys.geometry.core.selection_builder.selection_builder import RangeType

from .conftest import FILES_DIR


def test_get_all_visible_bodies(modeler: Modeler):
    """Verify that get_all_visible_bodies returns all visible bodies in the design."""
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    all_bodies = design.get_all_bodies()
    assert len(all_bodies) == 19

    sel_builder = modeler.create_selection_builder()
    visible_bodies = sel_builder.bodies.get_all_visible_bodies()
    assert len(visible_bodies.items) == 18


def test_get_all_bodies(modeler: Modeler):
    """Verify that get_all_bodies returns every body regardless of visibility."""
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    all_bodies = design.get_all_bodies()
    assert len(all_bodies) == 19

    sel_builder = modeler.create_selection_builder()
    visible_bodies = sel_builder.bodies.get_all_bodies()
    assert len(visible_bodies.items) == 19


def test_get_all_surface_bodies(modeler: Modeler):
    """Verify that get_all_surface_bodies returns only surface bodies."""
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    all_bodies = design.get_all_bodies()
    assert len([b for b in all_bodies if b.is_surface]) == 6

    sel_builder = modeler.create_selection_builder()
    surface_bodies = sel_builder.bodies.get_all_surface_bodies()
    assert len(surface_bodies.items) == 6


def test_get_all_solid_bodies(modeler: Modeler):
    """Verify that get_all_solid_bodies returns only solid bodies."""
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    all_bodies = design.get_all_bodies()
    assert len([b for b in all_bodies if not b.is_surface]) == 13

    sel_builder = modeler.create_selection_builder()
    solid_bodies = sel_builder.bodies.get_all_solid_bodies()
    assert len(solid_bodies.items) == 13

    solid_bodies &= solid_bodies.get_all_visible_bodies()
    assert len(solid_bodies.items) == 12


def test_get_bodies_from_named_selection(modeler: Modeler):
    """Verify that get_bodies_from_named_selection returns bodies in the named selection."""
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    all_bodies = design.get_all_bodies()
    assert len([b for b in all_bodies if b.name == "Wheel"]) == 8

    design.create_named_selection("Wheels", [b for b in all_bodies if b.name == "Wheel"])

    sel_builder = modeler.create_selection_builder()
    named_bodies = sel_builder.bodies.get_bodies_from_named_selection("Wheels")
    assert len(named_bodies.items) == 8


def test_get_bodies_with_name(modeler: Modeler):
    """Verify that get_bodies_with_name filters bodies by name pattern."""
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    all_bodies = design.get_all_bodies()
    assert len([b for b in all_bodies if b.name == "Wheel"]) == 8

    sel_builder = modeler.create_selection_builder()
    named_bodies = sel_builder.bodies.get_bodies_with_name("Wheel")
    assert len(named_bodies.items) == 8


def test_get_bodies_with_volume(modeler: Modeler):
    """Verify that get_bodies_with_volume returns bodies within a volume range."""
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    all_bodies = design.get_all_bodies()
    assert len([b for b in all_bodies if 200 < b.volume.m < 300]) == 2

    sel_builder = modeler.create_selection_builder()
    volume_bodies = sel_builder.bodies.get_bodies_with_volume(200, 300)

    assert len(volume_bodies.items) == 2


def test_get_bodies_with_surface_area(modeler: Modeler):
    """Verify that get_bodies_with_surface_area returns bodies within a surface area range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    result = sel_builder.bodies.get_bodies_with_surface_area(500, 1000)
    assert len(result.items) == 2


def test_get_bodies_with_x_location(modeler: Modeler):
    """Verify that get_bodies_with_x_location returns bodies whose centroid X is in range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    result = sel_builder.bodies.get_bodies_with_x_location(
        range_type=RangeType.RANGETYPE_INTERSECT, min=0.001, max=30.0
    )
    assert len(result.items) == 13


def test_get_bodies_with_y_location(modeler: Modeler):
    """Verify that get_bodies_with_y_location returns bodies whose centroid Y is in range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    result = sel_builder.bodies.get_bodies_with_y_location(
        range_type=RangeType.RANGETYPE_INTERSECT, min=5.0, max=10.0
    )
    assert len(result.items) == 14


def test_get_bodies_with_z_location(modeler: Modeler):
    """Verify that get_bodies_with_z_location returns bodies whose centroid Z is in range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    result = sel_builder.bodies.get_bodies_with_z_location(
        range_type=RangeType.RANGETYPE_INTERSECT, min=6.0, max=10.0
    )
    assert len(result.items) == 9


def test_get_bodies_with_color(modeler: Modeler):
    """Verify that get_bodies_with_color returns bodies matching a specific ARGB color."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    result = sel_builder.bodies.get_bodies_with_color((255, 0, 0))
    assert len(result.items) == 1


def test_invert_body_selection(modeler: Modeler):
    """Verify that invert_body_selection returns all bodies not in the input selection."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    result = sel_builder.bodies.get_bodies_with_color((255, 0, 0)).invert_body_selection()
    assert len(result.items) == 18


def test_filter_bodies_by_volume(modeler: Modeler):
    """Verify that filter_bodies_by_volume keeps only bodies within the volume range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # With max bound: 2 bodies named "Top" have volume == 250
    result = all_bodies.filter_bodies_by_volume(200, 300)
    assert len(result.items) == 2
    assert all(b.name == "Top" for b in result.items)

    # Without max bound: all solids with volume >= 200 (Top×2, Wheel×8, Solid×1, BaseBody×2)
    result_no_max = all_bodies.filter_bodies_by_volume(200)
    assert len(result_no_max.items) == 13


def test_filter_bodies_max_volume(modeler: Modeler):
    """Verify that filter_bodies_max_volume returns bodies with the largest volume."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.filter_bodies_max_volume()
    assert len(result.items) == 2
    assert all(b.name == "BaseBody" for b in result.items)


def test_filter_bodies_min_volume(modeler: Modeler):
    """Verify that filter_bodies_min_volume returns bodies with the smallest volume."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.filter_bodies_min_volume()
    assert len(result.items) == 6
    assert all(b.name == "Surface" for b in result.items)


def test_filter_bodies_by_surface_area(modeler: Modeler):
    """Verify that filter_bodies_by_surface_area keeps bodies within the surface area range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # 8 Wheel bodies have surface area ≈ 314.16; filter 300-350 captures only them
    result = all_bodies.filter_bodies_by_surface_area(300, 350)
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)

    # Without max: all bodies with surface area >= 300 (Wheel×8, Solid×1, BaseBody×2)
    result_no_max = all_bodies.filter_bodies_by_surface_area(300)
    assert len(result_no_max.items) == 11


def test_filter_bodies_max_surface_area(modeler: Modeler):
    """Verify that filter_bodies_max_surface_area returns bodies with the largest surface area."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.filter_bodies_max_surface_area()
    assert len(result.items) == 2
    assert all(b.name == "BaseBody" for b in result.items)


def test_filter_bodies_min_surface_area(modeler: Modeler):
    """Verify that filter_bodies_min_surface_area returns bodies with the smallest surface area."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # 4 Surface bodies share the smallest surface area (≈12.5)
    result = all_bodies.filter_bodies_min_surface_area()
    assert len(result.items) == 4
    assert all(b.name == "Surface" for b in result.items)


def test_filter_bodies_by_face_count(modeler: Modeler):
    """Verify that filter_bodies_by_face_count keeps bodies within the face count range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # 8 Wheel bodies have exactly 3 faces
    result = all_bodies.filter_bodies_by_face_count(3, 3)
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)

    # Bodies with >= 6 faces: Solid×1 + Top×2 + BaseBody×2
    result_min_only = all_bodies.filter_bodies_by_face_count(6)
    assert len(result_min_only.items) == 5


def test_filter_bodies_max_face_count(modeler: Modeler):
    """Verify that filter_bodies_max_face_count returns bodies with the most faces."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # Solid×1, Top×2, BaseBody×2 all have 6 faces
    result = all_bodies.filter_bodies_max_face_count()
    assert len(result.items) == 5


def test_filter_bodies_min_face_count(modeler: Modeler):
    """Verify that filter_bodies_min_face_count returns bodies with the fewest faces."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # 6 Surface bodies each have 1 face
    result = all_bodies.filter_bodies_min_face_count()
    assert len(result.items) == 6
    assert all(b.name == "Surface" for b in result.items)


def test_filter_bodies_by_edge_count(modeler: Modeler):
    """Verify that filter_bodies_by_edge_count keeps bodies within the edge count range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # 8 Wheel bodies have exactly 2 edges
    result = all_bodies.filter_bodies_by_edge_count(2, 2)
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)

    # Bodies with >= 12 edges: Solid×1 + Top×2 + BaseBody×2
    result_min_only = all_bodies.filter_bodies_by_edge_count(12)
    assert len(result_min_only.items) == 5


def test_filter_bodies_max_edge_count(modeler: Modeler):
    """Verify that filter_bodies_max_edge_count returns bodies with the most edges."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # Solid×1, Top×2, BaseBody×2 all have 12 edges
    result = all_bodies.filter_bodies_max_edge_count()
    assert len(result.items) == 5


def test_filter_bodies_min_edge_count(modeler: Modeler):
    """Verify that filter_bodies_min_edge_count returns bodies with the fewest edges."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # 8 Wheel bodies have 2 edges each
    result = all_bodies.filter_bodies_min_edge_count()
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)


def test_filter_bodies_by_loop_count(modeler: Modeler):
    """Verify that filter_bodies_by_loop_count keeps bodies within the loop count range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # 8 Wheel bodies have exactly 4 loops
    result = all_bodies.filter_bodies_by_loop_count(4, 4)
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)

    # Bodies with >= 6 loops: Solid×1 + Top×2 + BaseBody×2
    result_min_only = all_bodies.filter_bodies_by_loop_count(6)
    assert len(result_min_only.items) == 5


def test_filter_bodies_max_loop_count(modeler: Modeler):
    """Verify that filter_bodies_max_loop_count returns bodies with the most loops."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # Solid×1, Top×2, BaseBody×2 all have 6 loops
    result = all_bodies.filter_bodies_max_loop_count()
    assert len(result.items) == 5


def test_filter_bodies_min_loop_count(modeler: Modeler):
    """Verify that filter_bodies_min_loop_count returns bodies with the fewest loops."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # 6 Surface bodies each have 1 loop
    result = all_bodies.filter_bodies_min_loop_count()
    assert len(result.items) == 6
    assert all(b.name == "Surface" for b in result.items)


def test_filter_bodies_by_number_surfaces(modeler: Modeler):
    """Verify that filter_bodies_by_number_surfaces filters by surface type count range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # Only the 8 Wheel bodies have at least 1 cylinder face
    result = all_bodies.filter_bodies_by_number_surfaces(SurfaceType.SURFACETYPE_CYLINDER, 1)
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)


def test_filter_bodies_by_number_curves(modeler: Modeler):
    """Verify that filter_bodies_by_number_curves filters by curve type count range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # Only the 8 Wheel bodies have at least 1 circle edge
    result = all_bodies.filter_bodies_by_number_curves(CurveType.CURVETYPE_CIRCLE, 1)
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)


def test_filter_bodies_max_number_surfaces(modeler: Modeler):
    """Verify that filter_bodies_max_number_surfaces returns bodies with the most of a surface
    type."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # All 8 Wheels tie for the most cylinder faces (1 each)
    result = all_bodies.filter_bodies_max_number_surfaces(SurfaceType.SURFACETYPE_CYLINDER)
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)


def test_filter_bodies_max_number_curves(modeler: Modeler):
    """Verify that filter_bodies_max_number_curves returns bodies with the most of a curve type."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # All 8 Wheels tie for the most circle edges (2 each)
    result = all_bodies.filter_bodies_max_number_curves(CurveType.CURVETYPE_CIRCLE)
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)


def test_filter_bodies_min_number_surfaces(modeler: Modeler):
    """Verify that filter_bodies_min_number_surfaces returns bodies with the fewest of a surface
    type."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # 11 non-Wheel bodies have 0 cylinder faces (minimum)
    result = all_bodies.filter_bodies_min_number_surfaces(SurfaceType.SURFACETYPE_CYLINDER)
    assert len(result.items) == 11
    assert all(b.name != "Wheel" for b in result.items)


def test_filter_bodies_min_number_curves(modeler: Modeler):
    """Verify that filter_bodies_min_number_curves returns bodies with the fewest of a curve
    type."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # 11 non-Wheel bodies have 0 circle edges (minimum)
    result = all_bodies.filter_bodies_min_number_curves(CurveType.CURVETYPE_CIRCLE)
    assert len(result.items) == 11
    assert all(b.name != "Wheel" for b in result.items)


def test_filter_bodies_by_number_surfaces_percentile(modeler: Modeler):
    """Verify filter_bodies_by_number_surfaces_percentile filters by surface type percentile."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # Top 50th percentile by cylinder face count returns the 8 Wheels
    result = all_bodies.filter_bodies_by_number_surfaces_percentile(
        SurfaceType.SURFACETYPE_CYLINDER, 50, 100
    )
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)


def test_filter_bodies_by_number_curves_percentile(modeler: Modeler):
    """Verify that filter_bodies_by_number_curves_percentile filters by curve type percentile."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # Top 50th percentile by circle edge count returns the 8 Wheels
    result = all_bodies.filter_bodies_by_number_curves_percentile(
        CurveType.CURVETYPE_CIRCLE, 50, 100
    )
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)


def test_filter_bodies_by_color(modeler: Modeler):
    """Verify that filter_bodies_by_color keeps only bodies matching an ARGB color."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.filter_bodies_by_color((255, 0, 0))
    assert len(result.items) == 1


def test_filter_bodies_by_name(modeler: Modeler):
    """Verify that filter_bodies_by_name keeps bodies whose name matches the filter."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.filter_bodies_by_name("Wheel")
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)


def test_filter_bodies_containing_surface_types(modeler: Modeler):
    """Verify that filter_bodies_containing_surface_types keeps bodies with the given types."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # 8 Wheel bodies contain cylinder faces
    result = all_bodies.filter_bodies_containing_surface_types(SurfaceType.SURFACETYPE_CYLINDER)
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)


def test_filter_bodies_containing_curve_types(modeler: Modeler):
    """Verify that filter_bodies_containing_curve_types keeps bodies with the given curve types."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # 8 Wheel bodies contain circle edges
    result = all_bodies.filter_bodies_containing_curve_types(CurveType.CURVETYPE_CIRCLE)
    assert len(result.items) == 8
    assert all(b.name == "Wheel" for b in result.items)


def test_filter_bodies_volume_percentile(modeler: Modeler):
    """Verify that filter_bodies_volume_percentile keeps bodies in the volume percentile range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # Top 50th percentile by volume: BaseBody×2 + Solid×1
    result = all_bodies.filter_bodies_volume_percentile(50, 100)
    assert len(result.items) == 3
    assert {b.name for b in result.items} == {"BaseBody", "Solid"}


def test_filter_bodies_surface_area_percentile(modeler: Modeler):
    """Verify that filter_bodies_surface_area_percentile keeps bodies in the surface area range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # Top 50th percentile by surface area: BaseBody×2 + Solid×1
    result = all_bodies.filter_bodies_surface_area_percentile(50, 100)
    assert len(result.items) == 3
    assert {b.name for b in result.items} == {"BaseBody", "Solid"}


def test_filter_bodies_face_count_percentile(modeler: Modeler):
    """Verify that filter_bodies_face_count_percentile keeps bodies in the face count
    percentile."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # Top 50th percentile by face count: Solid×1 + Top×2 + BaseBody×2
    result = all_bodies.filter_bodies_face_count_percentile(50, 100)
    assert len(result.items) == 5
    assert {b.name for b in result.items} == {"BaseBody", "Solid", "Top"}


def test_filter_bodies_edge_count_percentile(modeler: Modeler):
    """Verify that filter_bodies_edge_count_percentile keeps bodies in the edge count
    percentile."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # Top 50th percentile by edge count: Solid×1 + Top×2 + BaseBody×2 + some Surface bodies
    result = all_bodies.filter_bodies_edge_count_percentile(50, 100)
    assert len(result.items) == 7


def test_filter_bodies_loop_count_percentile(modeler: Modeler):
    """Verify that filter_bodies_loop_count_percentile keeps bodies in the loop count
    percentile."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    # Top 50th percentile by loop count: Solid×1 + Top×2 + BaseBody×2
    result = all_bodies.filter_bodies_loop_count_percentile(50, 100)
    assert len(result.items) == 5
    assert {b.name for b in result.items} == {"BaseBody", "Solid", "Top"}


def test_filter_surface_bodies(modeler: Modeler):
    """Verify that filter_surface_bodies keeps only surface bodies from the input."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.filter_surface_bodies()
    assert len(result.items) == 6
    assert all(b.is_surface for b in result.items)


def test_filter_solid_bodies(modeler: Modeler):
    """Verify that filter_solid_bodies keeps only solid bodies from the input."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.filter_solid_bodies()
    assert len(result.items) == 13
    assert all(not b.is_surface for b in result.items)


def test_extend_to_same_volume(modeler: Modeler):
    """Verify that extend_to_same_volume expands the selection to include all bodies
    that share the same volume as any body in the seed selection.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    left_wheels = modeler.create_selection_builder().bodies.get_bodies_with_x_location(
        min=-0.005, max=-0.001, range_type=RangeType.RANGETYPE_INTERSECT
    )
    assert len(left_wheels.items) == 2

    result = left_wheels.extend_to_same_volume()
    assert len(result.items) == 8


def test_extend_to_same_surface_area(modeler: Modeler):
    """Verify that extend_to_same_surface_area expands the selection to include all bodies
    that share the same surface area as any body in the seed selection.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    left_wheels = modeler.create_selection_builder().bodies.get_bodies_with_x_location(
        min=-0.005, max=-0.001, range_type=RangeType.RANGETYPE_INTERSECT
    )
    assert len(left_wheels.items) == 2

    result = left_wheels.extend_to_same_surface_area()
    assert len(result.items) == 8


def test_extend_to_same_number_of_faces(modeler: Modeler):
    """Verify that extend_to_same_number_of_faces expands the selection to all bodies
    that share the same face count as any body in the seed selection.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    left_wheels = modeler.create_selection_builder().bodies.get_bodies_with_x_location(
        min=-0.005, max=-0.001, range_type=RangeType.RANGETYPE_INTERSECT
    )
    assert len(left_wheels.items) == 2

    result = left_wheels.extend_to_same_number_of_faces()
    assert len(result.items) == 8


def test_extend_to_same_number_of_edges(modeler: Modeler):
    """Verify that extend_to_same_number_of_edges expands the selection to all bodies
    that share the same edge count as any body in the seed selection.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    left_wheels = modeler.create_selection_builder().bodies.get_bodies_with_x_location(
        min=-0.005, max=-0.001, range_type=RangeType.RANGETYPE_INTERSECT
    )
    assert len(left_wheels.items) == 2

    result = left_wheels.extend_to_same_number_of_edges()
    assert len(result.items) == 8


def test_extend_to_same_color(modeler: Modeler):
    """TODO: Verify that extend_to_same_color expands the selection to all bodies with the
    same color as any body in the seed selection.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    wheel_bodies = modeler.create_selection_builder().bodies.get_bodies_with_name("Wheel")

    assert len(wheel_bodies.items) == 8

    result = wheel_bodies.extend_to_same_color()
    assert len(result.items) == 18


def test_extend_to_same_name(modeler: Modeler):
    """Verify that extend_to_same_name expands the selection to all bodies sharing the
    same name as any body in the seed selection.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    x_loc_bodies = modeler.create_selection_builder().bodies.get_bodies_with_x_location(
        range_type=RangeType.RANGETYPE_INTERSECT, min=0.001, max=0.03
    )
    assert len(x_loc_bodies.items) == 3

    same_name = x_loc_bodies.extend_to_same_name()
    assert len(same_name.items) == 10


def test_extend_nearby_bodies(modeler: Modeler):
    """Verify that extend_nearby_bodies adds all bodies within the specified distance
    of any body in the seed selection.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    base_bodies = modeler.create_selection_builder().bodies.get_bodies_with_name("BaseBody")
    assert len(base_bodies.items) == 2

    # A very large distance should capture all 19 bodies in the model
    if BackendType.is_core_service(modeler.client.backend_type):
        with pytest.raises(NotImplementedError):
            base_bodies.extend_nearby_bodies(5000)
        return

    result = base_bodies.extend_nearby_bodies(5000)
    assert len(result.items) == 18


def test_order_bodies_by_volume(modeler: Modeler):
    """Verify that order_bodies_by_volume returns bodies sorted ascending by volume."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.order_bodies_by_volume()
    assert len(result.items) == 19

    # Surface bodies have volume 0 — they must come first (ascending)
    assert all(b.name == "Surface" for b in result.items[:6])
    # BaseBody bodies have the largest volume — they must come last
    assert all(b.name == "BaseBody" for b in result.items[-2:])


def test_order_bodies_by_surface_area(modeler: Modeler):
    """Verify that order_bodies_by_surface_area returns bodies sorted ascending by surface area."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.order_bodies_by_surface_area()
    assert len(result.items) == 19
    # 4 Surface bodies have the smallest surface area (~12.5) — must come first
    assert all(b.name == "Surface" for b in result.items[:4])
    # BaseBody bodies have the largest surface area (700) — must come last
    assert all(b.name == "BaseBody" for b in result.items[-2:])


def test_order_bodies_by_face_count(modeler: Modeler):
    """Verify that order_bodies_by_face_count returns bodies sorted ascending by face count."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.order_bodies_by_face_count()
    assert len(result.items) == 19
    # Surface bodies have 1 face — must come first
    assert all(b.name == "Surface" for b in result.items[:6])
    # Solid×1 + Top×2 + BaseBody×2 have 6 faces — must come last
    assert {b.name for b in result.items[-5:]} == {"BaseBody", "Solid", "Top"}


def test_order_bodies_by_edge_count(modeler: Modeler):
    """Verify that order_bodies_by_edge_count returns bodies sorted ascending by edge count."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.order_bodies_by_edge_count()
    assert len(result.items) == 19
    # Wheel bodies have 2 edges — must come first
    assert all(b.name == "Wheel" for b in result.items[:8])
    # Solid×1 + Top×2 + BaseBody×2 have 12 edges — must come last
    assert {b.name for b in result.items[-5:]} == {"BaseBody", "Solid", "Top"}


def test_order_bodies_by_loop_count(modeler: Modeler):
    """Verify that order_bodies_by_loop_count returns bodies sorted ascending by loop count."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.order_bodies_by_loop_count()
    assert len(result.items) == 19
    # Surface bodies have 1 loop — must come first
    assert all(b.name == "Surface" for b in result.items[:6])
    # Solid×1 + Top×2 + BaseBody×2 have 6 loops — must come last
    assert {b.name for b in result.items[-5:]} == {"BaseBody", "Solid", "Top"}


def test_order_bodies_by_number_of_surfaces(modeler: Modeler):
    """Verify that order_bodies_by_number_of_surfaces sorts ascending by total surface count."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.order_bodies_by_number_of_surfaces()
    assert len(result.items) == 19
    # Surface bodies have 1 face — must come first
    assert all(b.name == "Surface" for b in result.items[:6])
    # Solid×1 + Top×2 + BaseBody×2 have 6 faces — must come last
    assert {b.name for b in result.items[-5:]} == {"BaseBody", "Solid", "Top"}


def test_order_bodies_by_number_of_curves(modeler: Modeler):
    """Verify that order_bodies_by_number_of_curves sorts ascending by total curve count."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    result = all_bodies.order_bodies_by_number_of_curves()
    assert len(result.items) == 19
    # Wheel bodies have 2 edges (fewest) — must come first
    assert all(b.name == "Wheel" for b in result.items[:8])
    # Solid×1 + Top×2 + BaseBody×2 have 12 edges — must come last
    assert {b.name for b in result.items[-5:]} == {"BaseBody", "Solid", "Top"}


def test_group_bodies_by_volume(modeler: Modeler):
    """Verify that group_bodies_by_volume partitions bodies into equal-volume groups."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    groups = all_bodies.group_bodies_by_volume()
    # 5 distinct volume values: 0 (Surface×6), 250 (Top×2), ~392.7 (Wheel×8),
    # ~558 (Solid×1), 1000 (BaseBody×2)
    assert len(groups) == 5
    sizes = sorted(len(g.items) for g in groups)
    assert sizes == [1, 2, 2, 6, 8]
    name_sets = {frozenset(b.name for b in g.items) for g in groups}
    assert frozenset({"Solid"}) in name_sets
    assert frozenset({"Top"}) in name_sets
    assert frozenset({"Wheel"}) in name_sets
    assert frozenset({"Surface"}) in name_sets
    assert frozenset({"BaseBody"}) in name_sets


def test_group_bodies_by_surface_area(modeler: Modeler):
    """Verify that group_bodies_by_surface_area partitions bodies into equal-surface-area
    groups."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    groups = all_bodies.group_bodies_by_surface_area()
    # 6 distinct surface area values: 12.5 (Surface×4), ~70.7 (Surface×2),
    # 250 (Top×2), ~314.16 (Wheel×8), ~416 (Solid×1), 700 (BaseBody×2)
    assert len(groups) == 6
    sizes = sorted(len(g.items) for g in groups)
    assert sizes == [1, 2, 2, 2, 4, 8]


def test_group_bodies_by_face_count(modeler: Modeler):
    """Verify that group_bodies_by_face_count partitions bodies by face count."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    groups = all_bodies.group_bodies_by_face_count()
    # 3 distinct face counts: 1 (Surface×6), 3 (Wheel×8), 6 (Solid+Top+BaseBody = 5)
    assert len(groups) == 3
    sizes = sorted(len(g.items) for g in groups)
    assert sizes == [5, 6, 8]
    name_sets = {frozenset(b.name for b in g.items) for g in groups}
    assert frozenset({"Surface"}) in name_sets
    assert frozenset({"Wheel"}) in name_sets
    assert frozenset({"BaseBody", "Solid", "Top"}) in name_sets


def test_group_bodies_by_edge_count(modeler: Modeler):
    """Verify that group_bodies_by_edge_count partitions bodies by edge count."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    groups = all_bodies.group_bodies_by_edge_count()
    # 4 distinct edge counts: 2 (Wheel×8), 3 (Surface×4), 4 (Surface×2),
    # 12 (Solid+Top+BaseBody = 5)
    assert len(groups) == 4
    sizes = sorted(len(g.items) for g in groups)
    assert sizes == [2, 4, 5, 8]
    name_sets = {frozenset(b.name for b in g.items) for g in groups}
    assert frozenset({"Wheel"}) in name_sets
    assert frozenset({"BaseBody", "Solid", "Top"}) in name_sets


def test_group_bodies_by_loop_count(modeler: Modeler):
    """Verify that group_bodies_by_loop_count partitions bodies by loop count."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    groups = all_bodies.group_bodies_by_loop_count()
    # 3 distinct loop counts: 1 (Surface×6), 4 (Wheel×8), 6 (Solid+Top+BaseBody = 5)
    assert len(groups) == 3
    sizes = sorted(len(g.items) for g in groups)
    assert sizes == [5, 6, 8]
    name_sets = {frozenset(b.name for b in g.items) for g in groups}
    assert frozenset({"Surface"}) in name_sets
    assert frozenset({"Wheel"}) in name_sets
    assert frozenset({"BaseBody", "Solid", "Top"}) in name_sets


def test_group_bodies_by_color(modeler: Modeler):
    """Verify that group_bodies_by_color partitions bodies by color."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    groups = all_bodies.group_bodies_by_color()
    # 2 distinct colors: 1 red body (Solid), 18 bodies sharing the default color
    assert len(groups) == 2
    sizes = sorted(len(g.items) for g in groups)
    assert sizes == [1, 18]
    lone_group = next(g for g in groups if len(g.items) == 1)
    assert lone_group.items[0].name == "Solid"


def test_group_bodies_by_name(modeler: Modeler):
    """Verify that group_bodies_by_name partitions bodies by name."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_bodies = modeler.create_selection_builder().bodies.get_all_bodies()

    groups = all_bodies.group_bodies_by_name()
    # 5 distinct names: Solid (1), Top (2), BaseBody (2), Surface (6), Wheel (8)
    assert len(groups) == 5
    sizes = sorted(len(g.items) for g in groups)
    assert sizes == [1, 2, 2, 6, 8]
    name_sets = {frozenset(b.name for b in g.items) for g in groups}
    assert frozenset({"Solid"}) in name_sets
    assert frozenset({"Top"}) in name_sets
    assert frozenset({"BaseBody"}) in name_sets
    assert frozenset({"Surface"}) in name_sets
    assert frozenset({"Wheel"}) in name_sets
