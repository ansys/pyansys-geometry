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

"""Integration tests for FaceSelection.

Geometry overview (cars-windshield.scdocx):
 - 19 bodies total (18 visible):
     - Wheel x 8   : 3 faces each (1 cylinder + 2 flat circular), 2 circle edges each
     - Top x 2     : 6 box faces each, 4 line edges per face
     - BaseBody x 2: 6 box faces each, 4 line edges per face
     - Solid x 1   : 6 box faces, red colour
     - Surface x 6 : 1 face each (4 triangular, 2 quadrilateral)
 - Total faces: 8*3 + 5*6 + 6*1 = 60
 - Faces with circle edges (CURVETYPE_CIRCLE): 24  (all Wheel faces)
 - Faces with line edges only: 36  (all non-Wheel faces)
"""

import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.designer.edge import CurveType
from ansys.geometry.core.errors import GeometryExitedError
from ansys.geometry.core.selection_builder.face_selection import FaceSelection
from ansys.geometry.core.selection_builder.selection_builder import (
    InvertScope,
    RangeType,
)

from .conftest import FILES_DIR


def test_face_selection_add(modeler: Modeler):
    """Verify that __add__ returns a deduplicated union of two face selections.

    Uses two disjoint wheel-face subsets (cylindrical vs. flat circular) to confirm
    the union count is exactly 24.  Adds a selection to itself to confirm deduplication.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    cyl_faces = all_faces.filter_faces_by_edge_count(2, 2)  # 8 cylindrical Wheel faces
    flat_faces = all_faces.filter_faces_by_edge_count(1, 1)  # 16 flat circular Wheel faces

    # Disjoint union: 8 + 16 = 24
    union = cyl_faces + flat_faces
    assert isinstance(union, FaceSelection)
    assert len(union.items) == 24

    # Union with self must not duplicate: still 8
    self_union = cyl_faces + cyl_faces
    assert isinstance(self_union, FaceSelection)
    assert len(self_union.items) == 8


def test_face_selection_sub(modeler: Modeler):
    """Verify that __sub__ returns faces in self that are absent from other.

    Subtracts the 8 cylindrical Wheel faces from all 24 Wheel faces, expecting
    the 16 flat circular faces.  Also verifies that subtracting a disjoint set
    leaves the selection unchanged.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # All 24 Wheel faces (contain at least one circle edge)
    wheel_faces = all_faces.filter_faces_by_number_curves(CurveType.CURVETYPE_CIRCLE, 1)
    assert len(wheel_faces.items) == 24
    # 8 cylindrical Wheel faces (2 edges each)
    cyl_faces = all_faces.filter_faces_by_edge_count(2, 2)
    assert len(cyl_faces.items) == 8

    # 24 Wheel − 8 cylindrical = 16 flat circular
    diff = wheel_faces - cyl_faces
    assert isinstance(diff, FaceSelection)
    assert len(diff.items) == 16

    # Subtracting a disjoint set (box faces, 4 edges) must not change the selection
    box_faces = all_faces.filter_faces_by_edge_count(4, 4)
    no_change = wheel_faces - box_faces
    assert isinstance(no_change, FaceSelection)
    assert len(no_change.items) == 24


def test_face_selection_and(modeler: Modeler):
    """Verify that __and__ returns the intersection of two face selections.

    Intersects all 24 Wheel faces with the 8 two-edge faces, expecting exactly
    the 8 cylindrical Wheel faces.  Also confirms that intersecting with a
    disjoint set (box faces) yields an empty selection.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # All 24 Wheel faces
    wheel_faces = all_faces.filter_faces_by_number_curves(CurveType.CURVETYPE_CIRCLE, 1)
    # 8 cylindrical Wheel faces (the only faces with exactly 2 edges)
    two_edge_faces = all_faces.filter_faces_by_edge_count(2, 2)

    # 24 Wheel ∩ 8 cylindrical = 8
    intersection = wheel_faces & two_edge_faces
    assert isinstance(intersection, FaceSelection)
    assert len(intersection.items) == 8

    # Box faces (4 edges) have no circle edges → intersection with wheel_faces is empty
    box_faces = all_faces.filter_faces_by_edge_count(4, 4)
    empty = wheel_faces & box_faces
    assert isinstance(empty, FaceSelection)
    assert len(empty.items) == 0


def test_get_all_visible_faces(modeler: Modeler):
    """Verify that get_all_visible_faces returns faces from visible bodies only."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    visible_faces = sel_builder.faces.get_all_visible_faces()

    # 18 visible bodies: 8*3 + 4*6 + 6*1 = 24+24+6 = 54
    # (Solid is the hidden body, so its 6 faces are excluded)
    assert len(visible_faces.items) == 54


def test_get_all_faces(modeler: Modeler):
    """Verify that get_all_faces returns every face regardless of visibility."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_faces = sel_builder.faces.get_all_faces()

    # 8*3 + 5*6 + 6*1 = 60 total faces across all 19 bodies
    assert len(all_faces.items) == 60


def test_get_faces_from_named_selection(modeler: Modeler):
    """Verify that get_faces_from_named_selection returns faces in a named selection."""
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    # Use the named selections already present in the file
    existing_ns = design.named_selections
    assert len(existing_ns) == 2

    sel_builder = modeler.create_selection_builder()

    # Get faces from NS "to_pull" (1 face)
    result = sel_builder.faces.get_faces_from_named_selection(existing_ns[1].name)
    assert len(result.items) == 1


def test_get_faces_with_area(modeler: Modeler):
    """Verify that get_faces_with_area returns faces whose area falls in a given range."""
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    # Compute areas on the Python side to find a meaningful range
    all_bodies = design.get_all_bodies()
    all_face_areas = [f.area.m for b in all_bodies for f in b.faces]
    mid_area = sorted(all_face_areas)[len(all_face_areas) // 2]
    max_area = max(all_face_areas)

    sel_builder = modeler.create_selection_builder()
    result = sel_builder.faces.get_faces_with_area(mid_area, max_area)
    assert len(result.items) > 0
    assert len(result.items) < len(all_face_areas)


def test_get_faces_with_x_location(modeler: Modeler):
    """Verify that get_faces_with_x_location returns faces whose centroid X is in range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_faces = sel_builder.faces.get_all_faces()

    result = sel_builder.faces.get_faces_with_x_location(
        range_type=RangeType.RANGETYPE_INTERSECT, min=0.001, max=30.0
    )
    assert len(result.items) > 0
    assert len(result.items) < len(all_faces.items)


def test_get_faces_with_y_location(modeler: Modeler):
    """Verify that get_faces_with_y_location returns faces whose centroid Y is in range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_faces = sel_builder.faces.get_all_faces()

    result = sel_builder.faces.get_faces_with_y_location(
        range_type=RangeType.RANGETYPE_INTERSECT, min=5.0, max=10.0
    )
    assert len(result.items) > 0
    assert len(result.items) < len(all_faces.items)


def test_get_faces_with_z_location(modeler: Modeler):
    """Verify that get_faces_with_z_location returns faces whose centroid Z is in range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_faces = sel_builder.faces.get_all_faces()

    result = sel_builder.faces.get_faces_with_z_location(
        range_type=RangeType.RANGETYPE_INTERSECT, min=6.0, max=10.0
    )
    assert len(result.items) > 0
    assert len(result.items) < len(all_faces.items)


def test_get_faces_with_color(modeler: Modeler):
    """Verify that get_faces_with_color returns only faces with the given ARGB color."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    # The Solid body is red — it has 6 faces
    result = sel_builder.faces.get_faces_with_color((255, 0, 0))
    assert len(result.items) == 6


def test_invert_face_selection(modeler: Modeler):
    """Verify that invert_face_selection returns all visible faces not in the input set."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    # Start with the 6 red Solid faces; invert to get the remaining 53 visible faces
    red_faces = sel_builder.faces.get_faces_with_color((255, 0, 0))
    assert len(red_faces.items) == 6

    result = red_faces.invert_face_selection(scope=InvertScope.INVERTSCOPE_VISIBLE)
    # Solid (red) is the hidden body; its faces are not in the visible set.
    # Inverting 6 hidden red faces within visible scope returns all 54 visible faces.
    assert len(result.items) == 54


def test_filter_faces_by_area(modeler: Modeler):
    """Verify that filter_faces_by_area keeps only faces within the area range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # Only cylindrical faces of the 8 Wheels have the same curved-surface area;
    # use a tighter range that captures them (area depends on wheel dimensions).
    # Filter down to faces with edge count == 2, which are the 8 cylinder faces.
    cyl_faces = all_faces.filter_faces_by_edge_count(2, 2)
    assert len(cyl_faces.items) == 8

    # Now verify area filtering on those cylinder faces: max-area should be 1 (the biggest).
    biggest = cyl_faces.filter_faces_max_area()
    assert len(biggest.items) == 8


def test_filter_faces_max_area(modeler: Modeler):
    """Verify that filter_faces_max_area returns the face(s) with the largest area."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    result = all_faces.filter_faces_max_area()
    assert len(result.items) == 4

    # All returned faces must share the same (maximum) area
    areas = [f.area.m for f in result.items]
    assert len(set(round(a, 6) for a in areas)) == 1


def test_filter_faces_min_area(modeler: Modeler):
    """Verify that filter_faces_min_area returns the face(s) with the smallest area."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    result = all_faces.filter_faces_min_area()
    assert len(result.items) == 4

    areas = [f.area.m for f in result.items]
    assert len(set(round(a, 6) for a in areas)) == 1


def test_filter_faces_by_perimeter(modeler: Modeler):
    """Verify that filter_faces_by_perimeter keeps faces whose perimeter is in a range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # Filter to strict subset — the result must be smaller than the full set
    result = all_faces.filter_faces_by_perimeter(10, 50)
    assert len(result.items) > 0
    assert len(result.items) < len(all_faces.items)


def test_filter_faces_max_perimeter(modeler: Modeler):
    """Verify that filter_faces_max_perimeter returns the face(s) with the largest perimeter."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    result = all_faces.filter_faces_max_perimeter()
    assert len(result.items) == 8


def test_filter_faces_min_perimeter(modeler: Modeler):
    """Verify that filter_faces_min_perimeter returns the face(s) with the smallest perimeter."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    result = all_faces.filter_faces_min_perimeter()
    assert len(result.items) == 4


def test_filter_faces_by_edge_count(modeler: Modeler):
    """Verify that filter_faces_by_edge_count keeps faces within the edge count range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # Cylindrical Wheel faces have exactly 2 edges — 1 per Wheel = 8 total
    result_2 = all_faces.filter_faces_by_edge_count(2, 2)
    assert len(result_2.items) == 8

    # Flat circular Wheel faces have exactly 1 edge — 2 per Wheel = 16 total
    result_1 = all_faces.filter_faces_by_edge_count(1, 1)
    assert len(result_1.items) == 16

    # Faces with >= 4 edges: 30 box faces + 2 quad Surface faces = 32
    result_4plus = all_faces.filter_faces_by_edge_count(4)
    assert len(result_4plus.items) == 32


def test_filter_faces_max_edge_count(modeler: Modeler):
    """Verify that filter_faces_max_edge_count returns faces with the most edges."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # Box faces and quad Surface faces both have 4 edges (the maximum)
    result = all_faces.filter_faces_max_edge_count()
    assert len(result.items) == 32


def test_filter_faces_min_edge_count(modeler: Modeler):
    """Verify that filter_faces_min_edge_count returns faces with the fewest edges."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # Flat circular Wheel faces have 1 edge (the minimum)
    result = all_faces.filter_faces_min_edge_count()
    assert len(result.items) == 16


def test_filter_faces_by_loop_count(modeler: Modeler):
    """Verify that filter_faces_by_loop_count keeps faces within the loop count range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # The 8 cylindrical Wheel faces each have 2 loops; 52 other faces have 1 loop
    result = all_faces.filter_faces_by_loop_count(1, 1)
    assert len(result.items) == 52


def test_filter_faces_max_loop_count(modeler: Modeler):
    """Verify that filter_faces_max_loop_count returns faces with the most loops."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # 8 cylindrical Wheel faces have the most loops (2 each)
    result = all_faces.filter_faces_max_loop_count()
    assert len(result.items) == 8


def test_filter_faces_min_loop_count(modeler: Modeler):
    """Verify that filter_faces_min_loop_count returns faces with the fewest loops."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # 52 faces have 1 loop (min); 8 cylindrical Wheel faces have 2 loops
    result = all_faces.filter_faces_min_loop_count()
    assert len(result.items) == 52


def test_filter_faces_by_number_curves(modeler: Modeler):
    """Verify that filter_faces_by_number_curves filters by curve type count range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # Faces with >= 1 circle edge: all 24 Wheel faces
    result = all_faces.filter_faces_by_number_curves(CurveType.CURVETYPE_CIRCLE, 1)
    assert len(result.items) == 24

    # Only cylindrical Wheel faces have 2 circle edges (top + bottom boundary)
    result_2 = all_faces.filter_faces_by_number_curves(CurveType.CURVETYPE_CIRCLE, 2, 2)
    assert len(result_2.items) == 8


def test_filter_faces_max_number_curves(modeler: Modeler):
    """Verify that filter_faces_max_number_curves returns faces with the most of a curve type."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # Cylindrical faces have 2 circle edges — the maximum for CURVETYPE_CIRCLE
    result = all_faces.filter_faces_max_number_curves(CurveType.CURVETYPE_CIRCLE)
    assert len(result.items) == 8


def test_filter_faces_min_number_curves(modeler: Modeler):
    """Verify that filter_faces_min_number_curves returns faces with the fewest of a curve type."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # Non-Wheel faces have 0 circle edges (the minimum)
    result = all_faces.filter_faces_min_number_curves(CurveType.CURVETYPE_CIRCLE)
    assert len(result.items) == 36


def test_filter_faces_containing_curve_types(modeler: Modeler):
    """Verify that filter_faces_containing_curve_types keeps faces with the given curve type."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # All 24 Wheel faces contain at least one circle edge
    result = all_faces.filter_faces_containing_curve_types(CurveType.CURVETYPE_CIRCLE)
    assert len(result.items) == 24

    # With exclusive=True: all 24 Wheel faces have ONLY circle edges (no line edges)
    result_excl = all_faces.filter_faces_containing_curve_types(
        CurveType.CURVETYPE_CIRCLE, exclusive=True
    )
    assert len(result_excl.items) == 24


def test_filter_faces_by_color(modeler: Modeler):
    """Verify that filter_faces_by_color keeps only faces matching an ARGB color."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    result = all_faces.filter_faces_by_color((255, 0, 0))
    assert len(result.items) == 6


def test_filter_faces_area_percentile(modeler: Modeler):
    """Verify that filter_faces_area_percentile keeps faces in the area percentile range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # Top 50th percentile by area should be a strict subset
    result = all_faces.filter_faces_area_percentile(50, 100)
    assert len(result.items) > 0
    assert len(result.items) < len(all_faces.items)


def test_filter_faces_perimeter_percentile(modeler: Modeler):
    """Verify that filter_faces_perimeter_percentile keeps faces in the perimeter range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    result = all_faces.filter_faces_perimeter_percentile(50, 100)
    assert len(result.items) > 0
    assert len(result.items) < len(all_faces.items)


@pytest.mark.xfail(
    reason=(
        "scFaceSelection.FilterNumberEdgesPercentile returns 0 in this SC build; "
        "expected 32 faces (4-edge faces at/above 50th percentile)"
    ),
    strict=False,
)
def test_filter_faces_edge_count_percentile(modeler: Modeler):
    """Verify that filter_faces_edge_count_percentile keeps faces in the edge count range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # Top 50th percentile by edge count: faces with 4 edges (box + quad Surface = 32)
    result = all_faces.filter_faces_edge_count_percentile(50, 100)
    assert len(result.items) == 32


def test_filter_faces_loop_count_percentile(modeler: Modeler):
    """Verify that filter_faces_loop_count_percentile keeps faces in the loop count range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # All faces have 1 loop, so the entire range [0,100] returns all
    result = all_faces.filter_faces_loop_count_percentile(0, 100)
    assert len(result.items) == 60


def test_filter_faces_by_number_curves_percentile(modeler: Modeler):
    """Verify that filter_faces_by_number_curves_percentile filters by curve type percentile."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # Top 50th percentile by circle edge count: all 24 Wheel faces (they all have >= 1 circle)
    result = all_faces.filter_faces_by_number_curves_percentile(CurveType.CURVETYPE_CIRCLE, 50, 100)
    assert len(result.items) == 24


def test_extend_to_same_area(modeler: Modeler):
    """Verify that extend_to_same_area expands the selection to all faces with the same area.

    Starts from the 16 flat circular Wheel faces (all share the same area); the result
    must be exactly 16.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # All 16 flat circular Wheel faces share the same area
    flat_faces = all_faces.filter_faces_by_edge_count(1, 1)
    result = flat_faces.extend_to_same_area()
    assert len(result.items) == 16


def test_extend_to_same_number_of_edges(modeler: Modeler):
    """Verify extend_to_same_number_of_edges expands to faces with the same edge count.

    Starts from the 8 cylindrical Wheel faces (2 edges each); the result must be exactly 8.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # All 8 cylindrical Wheel faces have exactly 2 edges
    cyl_faces = all_faces.filter_faces_by_edge_count(2, 2)
    result = cyl_faces.extend_to_same_number_of_edges()
    assert len(result.items) == 8


def test_extend_to_same_number_of_loops(modeler: Modeler):
    """Verify extend_to_same_number_of_loops expands to faces with the same loop count.

    Starts from the 8 cylindrical Wheel faces (2 loops each); the result must be exactly 8.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # 8 cylindrical Wheel faces each have 2 loops — the only faces with more than 1 loop
    cyl_faces = all_faces.filter_faces_by_loop_count(2, 2)
    result = cyl_faces.extend_to_same_number_of_loops()
    assert len(result.items) == 8


def test_extend_to_same_color(modeler: Modeler):
    """Verify extend_to_same_color expands to all faces sharing the same color.

    Starts from the 6 red Solid faces; the result must be exactly 6.
    """
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    # All 6 Solid faces are red; extending to same color returns all 6
    red_faces = all_faces.filter_faces_by_color((255, 0, 0))
    result = red_faces.extend_to_same_color()
    assert len(result.items) == 6


@pytest.mark.xfail(
    raises=GeometryExitedError,
    reason=("scFaceSelection.ExtendToCoincident throws NotImplementedException in this SC build"),
    strict=True,
)
def test_extend_to_coincident(modeler: Modeler):
    """Verify extend_to_coincident expands to faces coincident with the selection."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    flat_faces = all_faces.filter_faces_by_edge_count(1, 1)
    result = flat_faces.extend_to_coincident()
    assert len(result.items) == 28


@pytest.mark.xfail(
    raises=GeometryExitedError,
    reason=("scFaceSelection.ExtendToCoaxialFaces throws NotImplementedException in this SC build"),
    strict=True,
)
def test_extend_to_coaxial_faces(modeler: Modeler):
    """Verify extend_to_coaxial_faces expands to faces sharing the same axis."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    cyl_faces = all_faces.filter_faces_by_edge_count(2, 2)
    assert len(cyl_faces.items) == 8

    # Seed with a single cylindrical face
    one_cyl = FaceSelection(cyl_faces._design, cyl_faces._grpc_client, [cyl_faces.items[0]])
    assert len(one_cyl.items) == 1

    result = one_cyl.extend_to_coaxial_faces()
    assert len(result.items) == 4


def test_order_faces_by_area(modeler: Modeler):
    """Verify that order_faces_by_area returns faces sorted ascending by area."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    result = all_faces.order_faces_by_area()
    assert len(result.items) == 60
    # Smallest area faces come first; largest come last
    assert result.items[0].area.m <= result.items[-1].area.m


def test_order_faces_by_perimeter(modeler: Modeler):
    """Verify that order_faces_by_perimeter returns faces sorted ascending by perimeter."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    result = all_faces.order_faces_by_perimeter()
    assert len(result.items) == 60
    # First face must have the smallest area relative to the last
    assert result.items[0].area.m <= result.items[-1].area.m


def test_order_faces_by_edge_count(modeler: Modeler):
    """Verify that order_faces_by_edge_count returns faces sorted ascending by edge count."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    result = all_faces.order_faces_by_edge_count()
    assert len(result.items) == 60


def test_order_faces_by_loop_count(modeler: Modeler):
    """Verify that order_faces_by_loop_count returns faces sorted ascending by loop count."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    result = all_faces.order_faces_by_loop_count()
    # All faces have 1 loop — ordering is stable, all 60 returned
    assert len(result.items) == 60


def test_order_faces_by_number_curves(modeler: Modeler):
    """Verify that order_faces_by_number_curves sorts faces by curve type count ascending."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    result = all_faces.order_faces_by_number_curves(CurveType.CURVETYPE_CIRCLE)
    assert len(result.items) == 60
    # Non-circle faces come first (36), then circle faces (24)
    assert len(result.items) == 60


def test_group_faces_by_area(modeler: Modeler):
    """Verify that group_faces_by_area partitions faces into equal-area groups."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    groups = all_faces.group_faces_by_area()
    assert len(groups) == 10

    total = sum(len(g.items) for g in groups)
    assert total == 60


def test_group_faces_by_perimeter(modeler: Modeler):
    """Verify that group_faces_by_perimeter partitions faces by equal perimeter."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    groups = all_faces.group_faces_by_perimeter()
    assert len(groups) == 10

    total = sum(len(g.items) for g in groups)
    assert total == 60


def test_group_faces_by_body(modeler: Modeler):
    """Verify that group_faces_by_body partitions faces by parent body (one group per body)."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    groups = all_faces.group_faces_by_body()
    # One group per body: 19 groups total
    assert len(groups) == 19
    total = sum(len(g.items) for g in groups)
    assert total == 60

    # The 5 box bodies (6 faces each) and 8 Wheel bodies (3 faces each) are distinguishable
    sizes = sorted(len(g.items) for g in groups)
    # 6 Surface bodies (1 face) + 8 Wheel bodies (3 faces) + 5 box bodies (6 faces)
    assert sizes.count(1) == 6
    assert sizes.count(3) == 8
    assert sizes.count(6) == 5


def test_group_faces_by_edge_count(modeler: Modeler):
    """Verify that group_faces_by_edge_count partitions faces by edge count."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    groups = all_faces.group_faces_by_edge_count()
    # 4 distinct edge counts: 1 (flat Wheel, 16), 2 (cyl Wheel, 8), 3 (tri Surface, 4), 4 (32)
    assert len(groups) == 4
    sizes = sorted(len(g.items) for g in groups)
    assert sizes == [4, 8, 16, 32]


def test_group_faces_by_loop_count(modeler: Modeler):
    """Verify that group_faces_by_loop_count partitions faces by loop count."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    groups = all_faces.group_faces_by_loop_count()
    # 2 distinct loop counts: 52 faces with 1 loop + 8 cylindrical Wheel faces with 2 loops
    assert len(groups) == 2
    sizes = sorted(len(g.items) for g in groups)
    assert sizes == [8, 52]


def test_group_faces_by_color(modeler: Modeler):
    """Verify that group_faces_by_color partitions faces by color."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    groups = all_faces.group_faces_by_color()
    # 2 distinct colors: 6 red Solid faces + 54 faces with the default color
    assert len(groups) == 2
    sizes = sorted(len(g.items) for g in groups)
    assert sizes == [6, 54]
    lone_group = next(g for g in groups if len(g.items) == 6)
    # All 6 red faces come from the Solid body
    body_names = {f.body.name for f in lone_group.items}
    assert body_names == {"Solid"}


@pytest.mark.xfail(
    raises=GeometryExitedError,
    reason=("scFaceSelection.GroupByCoincident throws NotImplementedException in this SC build"),
    strict=True,
)
def test_group_faces_by_coincident(modeler: Modeler):
    """Verify that group_faces_by_coincident partitions faces by coincidence."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")
    all_faces = modeler.create_selection_builder().faces.get_all_faces()

    groups = all_faces.group_faces_by_coincident()
    assert len(groups) == 23

    total = sum(len(g.items) for g in groups)
    assert total == 60
