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

"""Integration tests for EdgeSelectionBuilder."""

import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.designer.edge import CurveType
from ansys.geometry.core.selection_builder.selection_builder import (
    ExtendScope,
    InvertScope,
    RangeType,
)

from .conftest import FILES_DIR


def test_get_all_visible_edges(modeler: Modeler):
    """Verify that get_all_visible_edges returns all visible edges in the design."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    result = sel_builder.edges.get_all_visible_edges()
    assert len(result.items) > 0


def test_get_all_edges(modeler: Modeler):
    """Verify that get_all_edges returns every edge regardless of visibility."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()
    visible_edges = sel_builder.edges.get_all_visible_edges()

    # All includes hidden edges so count must be >= visible
    assert len(all_edges.items) >= len(visible_edges.items)
    assert len(all_edges.items) > 0


def test_get_edges_from_named_selection(modeler: Modeler):
    """Verify that get_edges_from_named_selection returns edges in the named selection."""
    design = modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()

    # Create a named selection with the first 5 edges
    sample_edges = all_edges.items[:5]
    design.create_named_selection("test_edges_ns", edges=sample_edges)

    ns_edges = sel_builder.edges.get_edges_from_named_selection("test_edges_ns")
    assert len(ns_edges.items) == 5


def test_get_edges_with_length(modeler: Modeler):
    """Verify that get_edges_with_length returns edges within a length range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    # Get all edges with length between 1 mm and 5 mm
    result = sel_builder.edges.get_edges_with_length(1.0, 5.0)
    # All returned edges should be within the range
    assert len(result.items) > 0


def test_get_edges_with_length_no_max(modeler: Modeler):
    """Verify that get_edges_with_length works without an upper bound."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()
    result = sel_builder.edges.get_edges_with_length(0.001)
    # With a very small min, almost all edges should be returned
    assert len(result.items) <= len(all_edges.items)
    assert len(result.items) > 0


def test_get_edges_with_x_location(modeler: Modeler):
    """Verify that get_edges_with_x_location returns edges whose X-location is in range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    result = sel_builder.edges.get_edges_with_x_location(
        range_type=RangeType.RANGETYPE_INTERSECT, min=0.001, max=30.0
    )
    assert len(result.items) > 0


def test_get_edges_with_y_location(modeler: Modeler):
    """Verify that get_edges_with_y_location returns edges whose Y-location is in range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    result = sel_builder.edges.get_edges_with_y_location(
        range_type=RangeType.RANGETYPE_INTERSECT, min=5.0, max=10.0
    )
    assert len(result.items) > 0


def test_get_edges_with_z_location(modeler: Modeler):
    """Verify that get_edges_with_z_location returns edges whose Z-location is in range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    result = sel_builder.edges.get_edges_with_z_location(
        range_type=RangeType.RANGETYPE_INTERSECT, min=6.0, max=10.0
    )
    assert len(result.items) > 0


def test_invert_edge_selection(modeler: Modeler):
    """Verify that invert_edge_selection returns all edges not in the input selection."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()
    total = len(all_edges.items)

    # Take a small subset and invert it
    subset = sel_builder.edges.get_edges_with_length(1.0, 5.0)
    inverted = subset.invert_edge_selection(scope=InvertScope.INVERTSCOPE_ALL)

    # |subset| + |inverted| == total
    assert len(subset.items) + len(inverted.items) == total


def test_filter_edges_by_length(modeler: Modeler):
    """Verify that filter_edges_by_length keeps only edges within the length range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()

    result = all_edges.filter_edges_by_length(1.0, 5.0)
    assert len(result.items) > 0
    assert len(result.items) <= len(all_edges.items)


def test_filter_edges_max_length(modeler: Modeler):
    """Verify that filter_edges_max_length returns only the edge(s) with maximum length."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()

    result = all_edges.filter_edges_max_length()
    assert len(result.items) >= 1
    assert len(result.items) < len(all_edges.items)


def test_filter_edges_min_length(modeler: Modeler):
    """Verify that filter_edges_min_length returns only the edge(s) with minimum length."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()

    result = all_edges.filter_edges_min_length()
    assert len(result.items) >= 1
    assert len(result.items) < len(all_edges.items)


def test_filter_edges_by_curve_type(modeler: Modeler):
    """Verify that filter_edges_by_curve_type keeps only edges of the given curve type."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()

    # The cars-windshield model has circular/arc edges (wheels)
    circular_edges = all_edges.filter_edges_by_curve_type(CurveType.CURVETYPE_CIRCLE)
    assert len(circular_edges.items) > 0
    assert len(circular_edges.items) < len(all_edges.items)


def test_filter_edges_length_percentile(modeler: Modeler):
    """Verify that filter_edges_length_percentile keeps edges in the percentile range."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()

    result = all_edges.filter_edges_length_percentile(50.0, 100.0)
    assert len(result.items) > 0
    assert len(result.items) <= len(all_edges.items)


@pytest.mark.xfail(
    reason="Spatial partitioning is not yet implemented in the backend.",
    strict=True
)
def test_extend_nearby_edges(modeler: Modeler):
    """Verify that extend_nearby_edges increases the selection within a given distance."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    # Start with a small subset
    subset = sel_builder.edges.get_edges_with_length(10.0, 20.0)
    if len(subset.items) == 0:
        pytest.skip("No edges in the 10–20 mm length range in this fixture.")

    extended = subset.extend_nearby_edges(distance=5.0, scope=ExtendScope.EXTENDSCOPE_ALL)
    assert len(extended.items) >= len(subset.items)


def test_extend_to_connected(modeler: Modeler):
    """Verify that extend_to_connected expands to topologically connected edges."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    subset = sel_builder.edges.filter_edges_min_length()

    extended = subset.extend_to_connected(scope=ExtendScope.EXTENDSCOPE_ALL)
    assert len(extended.items) >= len(subset.items)


def test_extend_to_tangent_chain(modeler: Modeler):
    """Verify that extend_to_tangent_chain expands to tangentially chained edges."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()
    # Start from circular edges — likely part of tangent chains
    circular_edges = all_edges.filter_edges_by_curve_type(CurveType.CURVETYPE_CIRCLE)
    if len(circular_edges.items) == 0:
        pytest.skip("No circular edges in this fixture.")

    extended = circular_edges.extend_to_tangent_chain(scope=ExtendScope.EXTENDSCOPE_ALL)
    assert len(extended.items) >= len(circular_edges.items)


def test_extend_to_coaxial_edges(modeler: Modeler):
    """Verify that extend_to_coaxial_edges expands to coaxial edges."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()
    circular_edges = all_edges.filter_edges_by_curve_type(CurveType.CURVETYPE_CIRCLE)
    if len(circular_edges.items) == 0:
        pytest.skip("No circular edges in this fixture.")

    extended = circular_edges.extend_to_coaxial_edges(scope=ExtendScope.EXTENDSCOPE_ALL)
    assert len(extended.items) >= len(circular_edges.items)


def test_order_edges_by_length(modeler: Modeler):
    """Verify that order_edges_by_length returns edges in ascending length order."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()

    ordered = all_edges.order_edges_by_length()
    assert len(ordered.items) == len(all_edges.items)

    lengths = [e.length.m for e in ordered.items]
    assert lengths == sorted(lengths)


def test_group_edges_by_curve_type(modeler: Modeler):
    """Verify that group_edges_by_curve_type partitions edges by curve type."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()

    groups = all_edges.group_edges_by_curve_type()
    assert len(groups) > 0

    # All groups combined should equal the total edge count
    total_in_groups = sum(len(g.items) for g in groups)
    assert total_in_groups == len(all_edges.items)


def test_set_operations(modeler: Modeler):
    """Verify union, difference, and intersection set operations on EdgeSelection."""
    modeler.open_file(FILES_DIR / "cars-windshield.scdocx")

    sel_builder = modeler.create_selection_builder()
    all_edges = sel_builder.edges.get_all_edges()

    circular = all_edges.filter_edges_by_curve_type(CurveType.CURVETYPE_CIRCLE)
    non_circular = all_edges.filter_edges_by_curve_type(CurveType.CURVETYPE_LINE)

    if len(circular.items) == 0 or len(non_circular.items) == 0:
        pytest.skip("Model lacks both circular and linear edges.")

    # Union
    union = circular + non_circular
    assert len(union.items) == len(circular.items) + len(non_circular.items)

    # Intersection (disjoint sets should be empty)
    intersection = circular & non_circular
    assert len(intersection.items) == 0

    # Difference
    diff = (circular + non_circular) - non_circular
    assert len(diff.items) == len(circular.items)
