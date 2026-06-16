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
"""Integration tests for BodySelectionBuilder."""

import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.selection_builder.selection_builder import SelectionBuilder

from .conftest import FILES_DIR

# ── Static factory (get) ──────────────────────────────────────────────────────

def test_get_all_visible_bodies(modeler: Modeler):
    """Verify that get_all_visible_bodies returns all visible bodies in the design."""
    pytest.skip("broken")
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    all_bodies = design.get_all_bodies()
    assert len(all_bodies) == 19

    sel_builder = SelectionBuilder(design)
    visible_bodies = sel_builder.bodies.get_all_visible_bodies()
    assert len(visible_bodies) == 18

def test_get_all_bodies(modeler: Modeler):
    """Verify that get_all_bodies returns every body regardless of visibility."""
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    all_bodies = design.get_all_bodies()
    assert len(all_bodies) == 19

    sel_builder = SelectionBuilder(design)
    visible_bodies = sel_builder.bodies.get_all_bodies()
    assert len(visible_bodies) == 19


def test_get_all_surface_bodies(modeler: Modeler):
    """Verify that get_all_surface_bodies returns only surface bodies."""
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    all_bodies = design.get_all_bodies()
    assert len([b for b in all_bodies if b.is_surface]) == 6

    sel_builder = SelectionBuilder(design)
    surface_bodies = sel_builder.bodies.get_all_surface_bodies()
    assert len(surface_bodies) == 6


def test_get_all_solid_bodies(modeler: Modeler):
    """Verify that get_all_solid_bodies returns only solid bodies."""
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    all_bodies = design.get_all_bodies()
    assert len([b for b in all_bodies if not b.is_surface]) == 13

    sel_builder = SelectionBuilder(design)
    solid_bodies = sel_builder.bodies.get_all_solid_bodies()
    assert len(solid_bodies) == 13

    solid_visible_bodies = sel_builder.bodies.get_all_solid_bodies()


def test_get_bodies_from_named_selection(modeler: Modeler):
    """Verify that get_bodies_from_named_selection returns bodies in the named selection."""
    pytest.skip("not implemented")


def test_get_bodies_with_name(modeler: Modeler):
    """Verify that get_bodies_with_name filters bodies by name pattern."""
    pytest.skip("not implemented")


def test_get_bodies_with_volume(modeler: Modeler):
    """Verify that get_bodies_with_volume returns bodies within a volume range."""
    pytest.skip("not implemented")


def test_get_bodies_with_surface_area(modeler: Modeler):
    """Verify that get_bodies_with_surface_area returns bodies within a surface area range."""
    pytest.skip("not implemented")


def test_get_bodies_with_x_location(modeler: Modeler):
    """Verify that get_bodies_with_x_location returns bodies within an X-location range."""
    pytest.skip("not implemented")


def test_get_bodies_with_y_location(modeler: Modeler):
    """Verify that get_bodies_with_y_location returns bodies within a Y-location range."""
    pytest.skip("not implemented")


def test_get_bodies_with_z_location(modeler: Modeler):
    """Verify that get_bodies_with_z_location returns bodies within a Z-location range."""
    pytest.skip("not implemented")


def test_get_bodies_with_color(modeler: Modeler):
    """Verify that get_bodies_with_color returns bodies matching a specific ARGB color."""
    pytest.skip("not implemented")


# ── Instance operations ───────────────────────────────────────────────────────


def test_invert_body_selection(modeler: Modeler):
    """Verify that invert_body_selection returns all bodies not in the input selection."""
    pytest.skip("not implemented")


# ── Filter ────────────────────────────────────────────────────────────────────


def test_filter_bodies_by_volume(modeler: Modeler):
    """Verify that filter_bodies_by_volume keeps only bodies within the volume range."""
    pytest.skip("not implemented")


def test_filter_bodies_max_volume(modeler: Modeler):
    """Verify that filter_bodies_max_volume returns the single body with the largest volume."""
    pytest.skip("not implemented")


def test_filter_bodies_min_volume(modeler: Modeler):
    """Verify that filter_bodies_min_volume returns the single body with the smallest volume."""
    pytest.skip("not implemented")


def test_filter_bodies_by_surface_area(modeler: Modeler):
    """Verify that filter_bodies_by_surface_area keeps bodies within the surface area range."""
    pytest.skip("not implemented")


def test_filter_bodies_max_surface_area(modeler: Modeler):
    """Verify that filter_bodies_max_surface_area returns the body with the largest surface area."""
    pytest.skip("not implemented")


def test_filter_bodies_min_surface_area(modeler: Modeler):
    """Verify that filter_bodies_min_surface_area returns the body with the smallest area."""
    pytest.skip("not implemented")


def test_filter_bodies_by_face_count(modeler: Modeler):
    """Verify that filter_bodies_by_face_count keeps bodies within the face count range."""
    pytest.skip("not implemented")


def test_filter_bodies_max_face_count(modeler: Modeler):
    """Verify that filter_bodies_max_face_count returns the body with the most faces."""
    pytest.skip("not implemented")


def test_filter_bodies_min_face_count(modeler: Modeler):
    """Verify that filter_bodies_min_face_count returns the body with the fewest faces."""
    pytest.skip("not implemented")


def test_filter_bodies_by_edge_count(modeler: Modeler):
    """Verify that filter_bodies_by_edge_count keeps bodies within the edge count range."""
    pytest.skip("not implemented")


def test_filter_bodies_max_edge_count(modeler: Modeler):
    """Verify that filter_bodies_max_edge_count returns the body with the most edges."""
    pytest.skip("not implemented")


def test_filter_bodies_min_edge_count(modeler: Modeler):
    """Verify that filter_bodies_min_edge_count returns the body with the fewest edges."""
    pytest.skip("not implemented")


def test_filter_bodies_by_loop_count(modeler: Modeler):
    """Verify that filter_bodies_by_loop_count keeps bodies within the loop count range."""
    pytest.skip("not implemented")


def test_filter_bodies_max_loop_count(modeler: Modeler):
    """Verify that filter_bodies_max_loop_count returns the body with the most loops."""
    pytest.skip("not implemented")


def test_filter_bodies_min_loop_count(modeler: Modeler):
    """Verify that filter_bodies_min_loop_count returns the body with the fewest loops."""
    pytest.skip("not implemented")


def test_filter_bodies_by_number_surfaces(modeler: Modeler):
    """Verify that filter_bodies_by_number_surfaces filters by surface type count range."""
    pytest.skip("not implemented")


def test_filter_bodies_by_number_curves(modeler: Modeler):
    """Verify that filter_bodies_by_number_curves filters by curve type count range."""
    pytest.skip("not implemented")


def test_filter_bodies_max_number_surfaces(modeler: Modeler):
    """Verify that filter_bodies_max_number_surfaces returns the body with the most surfaces."""
    pytest.skip("not implemented")


def test_filter_bodies_max_number_curves(modeler: Modeler):
    """Verify that filter_bodies_max_number_curves returns the body with the most curves."""
    pytest.skip("not implemented")


def test_filter_bodies_min_number_surfaces(modeler: Modeler):
    """Verify that filter_bodies_min_number_surfaces returns the body with the fewest surfaces."""
    pytest.skip("not implemented")


def test_filter_bodies_min_number_curves(modeler: Modeler):
    """Verify that filter_bodies_min_number_curves returns the body with the fewest curves."""
    pytest.skip("not implemented")


def test_filter_bodies_by_number_surfaces_percentile(modeler: Modeler):
    """Verify filter_bodies_by_number_surfaces_percentile filters by surface type percentile."""
    pytest.skip("not implemented")


def test_filter_bodies_by_number_curves_percentile(modeler: Modeler):
    """Verify that filter_bodies_by_number_curves_percentile filters by curve type percentile."""
    pytest.skip("not implemented")


def test_filter_bodies_by_color(modeler: Modeler):
    """Verify that filter_bodies_by_color keeps only bodies matching an ARGB color."""
    pytest.skip("not implemented")


def test_filter_bodies_by_name(modeler: Modeler):
    """Verify that filter_bodies_by_name keeps bodies whose name matches the filter."""
    pytest.skip("not implemented")


def test_filter_bodies_containing_surface_types(modeler: Modeler):
    """Verify that filter_bodies_containing_surface_types keeps bodies with the given types."""
    pytest.skip("not implemented")


def test_filter_bodies_containing_curve_types(modeler: Modeler):
    """Verify that filter_bodies_containing_curve_types keeps bodies with the given curve types."""
    pytest.skip("not implemented")


def test_filter_bodies_volume_percentile(modeler: Modeler):
    """Verify that filter_bodies_volume_percentile keeps bodies in the volume percentile range."""
    pytest.skip("not implemented")


def test_filter_bodies_surface_area_percentile(modeler: Modeler):
    """Verify that filter_bodies_surface_area_percentile keeps bodies in the surface area range."""
    pytest.skip("not implemented")


def test_filter_bodies_face_count_percentile(modeler: Modeler):
    """Verify that filter_bodies_face_count_percentile keeps bodies in the face count percentile."""
    pytest.skip("not implemented")


def test_filter_bodies_edge_count_percentile(modeler: Modeler):
    """Verify that filter_bodies_edge_count_percentile keeps bodies in the edge count percentile."""
    pytest.skip("not implemented")


def test_filter_bodies_loop_count_percentile(modeler: Modeler):
    """Verify that filter_bodies_loop_count_percentile keeps bodies in the loop count percentile."""
    pytest.skip("not implemented")


def test_filter_surface_bodies(modeler: Modeler):
    """Verify that filter_surface_bodies keeps only surface bodies from the input."""
    pytest.skip("not implemented")


def test_filter_solid_bodies(modeler: Modeler):
    """Verify that filter_solid_bodies keeps only solid bodies from the input."""
    pytest.skip("not implemented")


# ── Extend ────────────────────────────────────────────────────────────────────


def test_extend_to_same_volume(modeler: Modeler):
    """Verify that extend_to_same_volume adds bodies with matching volumes."""
    pytest.skip("not implemented")


def test_extend_to_same_surface_area(modeler: Modeler):
    """Verify that extend_to_same_surface_area adds bodies with matching surface areas."""
    pytest.skip("not implemented")


def test_extend_to_same_number_of_faces(modeler: Modeler):
    """Verify that extend_to_same_number_of_faces adds bodies with the same face count."""
    pytest.skip("not implemented")


def test_extend_to_same_number_of_edges(modeler: Modeler):
    """Verify that extend_to_same_number_of_edges adds bodies with the same edge count."""
    pytest.skip("not implemented")


def test_extend_to_same_color(modeler: Modeler):
    """Verify that extend_to_same_color adds bodies sharing the same color."""
    pytest.skip("not implemented")


def test_extend_to_same_name(modeler: Modeler):
    """Verify that extend_to_same_name adds bodies sharing the same name."""
    pytest.skip("not implemented")


def test_extend_nearby_bodies(modeler: Modeler):
    """Verify that extend_nearby_bodies adds bodies within the specified distance."""
    pytest.skip("not implemented")


# ── OrderBy ───────────────────────────────────────────────────────────────────


def test_order_bodies_by_volume(modeler: Modeler):
    """Verify that order_bodies_by_volume returns bodies sorted ascending by volume."""
    pytest.skip("not implemented")


def test_order_bodies_by_surface_area(modeler: Modeler):
    """Verify that order_bodies_by_surface_area returns bodies sorted ascending by surface area."""
    pytest.skip("not implemented")


def test_order_bodies_by_face_count(modeler: Modeler):
    """Verify that order_bodies_by_face_count returns bodies sorted ascending by face count."""
    pytest.skip("not implemented")


def test_order_bodies_by_edge_count(modeler: Modeler):
    """Verify that order_bodies_by_edge_count returns bodies sorted ascending by edge count."""
    pytest.skip("not implemented")


def test_order_bodies_by_loop_count(modeler: Modeler):
    """Verify that order_bodies_by_loop_count returns bodies sorted ascending by loop count."""
    pytest.skip("not implemented")


def test_order_bodies_by_number_of_surfaces(modeler: Modeler):
    """Verify that order_bodies_by_number_of_surfaces sorts ascending by total surface count."""
    pytest.skip("not implemented")


def test_order_bodies_by_number_of_curves(modeler: Modeler):
    """Verify that order_bodies_by_number_of_curves sorts ascending by total curve count."""
    pytest.skip("not implemented")


# ── GroupBy ───────────────────────────────────────────────────────────────────


def test_group_bodies_by_volume(modeler: Modeler):
    """Verify that group_bodies_by_volume partitions bodies into equal-volume groups."""
    pytest.skip("not implemented")


def test_group_bodies_by_surface_area(modeler: Modeler):
    """Verify that group_bodies_by_surface_area partitions bodies into equal-surface-area groups."""
    pytest.skip("not implemented")


def test_group_bodies_by_face_count(modeler: Modeler):
    """Verify that group_bodies_by_face_count partitions bodies by face count."""
    pytest.skip("not implemented")


def test_group_bodies_by_edge_count(modeler: Modeler):
    """Verify that group_bodies_by_edge_count partitions bodies by edge count."""
    pytest.skip("not implemented")


def test_group_bodies_by_loop_count(modeler: Modeler):
    """Verify that group_bodies_by_loop_count partitions bodies by loop count."""
    pytest.skip("not implemented")


def test_group_bodies_by_color(modeler: Modeler):
    """Verify that group_bodies_by_color partitions bodies by color."""
    pytest.skip("not implemented")


def test_group_bodies_by_name(modeler: Modeler):
    """Verify that group_bodies_by_name partitions bodies by name."""
    pytest.skip("not implemented")

