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

"""Integration tests for the DatumPoint class."""

from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.sketch.sketch import Sketch


def test_delete_datum_point(modeler: Modeler):
    """Test deletion of datum points from a component."""
    design = modeler.create_design("DeleteDatumPoint_Test")

    # Create datum points on the design
    dp1 = design.create_datum_point("DP1", Point3D([1, 2, 3], UNITS.mm))
    dp2 = design.create_datum_point("DP2", Point3D([4, 5, 6], UNITS.mm))
    dp3 = design.create_datum_point("DP3", Point3D([7, 8, 9], UNITS.mm))

    # Verify all datum points exist
    assert len(design.datum_points) == 3
    assert dp1.is_alive
    assert dp2.is_alive
    assert dp3.is_alive

    # Delete by object
    design.delete_datum_point(dp1)
    assert not dp1.is_alive
    assert dp2.is_alive
    assert dp3.is_alive

    # Delete by ID
    design.delete_datum_point(dp2.id)
    assert not dp2.is_alive
    assert dp3.is_alive

    # Attempt deletion from wrong component (should not delete)
    comp = design.add_component("WrongComp")
    comp.delete_datum_point(dp3)
    assert dp3.is_alive

    # Delete from root design (correct scope)
    design.delete_datum_point(dp3)
    assert not dp3.is_alive

    # Create a datum point on a nested component and delete from there
    nested = design.add_component("NestedComp")
    dp_nested = nested.create_datum_point("DPNested", Point3D([10, 20, 30], UNITS.mm))
    assert dp_nested.is_alive
    assert len(nested.datum_points) == 1

    nested.delete_datum_point(dp_nested)
    assert not dp_nested.is_alive


def test_create_datum_point(modeler: Modeler):
    """Test creation of datum points and their basic properties.

    Combines creation, property validation, repr output, and nested-component
    scoping into a single test.
    """
    design = modeler.create_design("CreateDatumPoint_Test")

    # Create a datum point at the root design level
    point = Point3D([1, 2, 3], UNITS.mm)
    dp1 = design.create_datum_point("DP1", point)

    assert dp1.id is not None
    assert dp1.name == "DP1"
    assert dp1.value == point
    assert dp1.parent_component.id == design.id
    assert dp1.is_alive
    assert len(design.datum_points) == 1
    assert design.datum_points[0].id == dp1.id

    # Create a second datum point on a nested component
    nested = design.add_component("Nested")
    dp2 = nested.create_datum_point("DP2", Point3D([4, 5, 6], UNITS.mm))

    assert dp2.id is not None
    assert dp2.id != dp1.id
    assert dp2.name == "DP2"
    assert dp2.parent_component.id == nested.id
    assert dp2.is_alive
    assert len(nested.datum_points) == 1
    assert nested.datum_points[0] == dp2

    # The root design-level list does not include datum points from nested components
    assert len(design.datum_points) == 1

    # Verify repr output
    dp1_str = str(dp1)
    assert "ansys.geometry.core.designer.DatumPoint" in dp1_str
    assert "  Name                 : DP1" in dp1_str
    assert "  Datum Point          : " in dp1_str


def test_datum_point_get_named_selections(modeler: Modeler):
    """Test that DatumPoint.get_named_selections returns the correct named selections."""
    design = modeler.create_design("DatumPointNS_Test")

    box = design.extrude_sketch("Box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    dp = design.create_datum_point("DP1", Point3D([1, 0, 0], UNITS.m))

    # Not yet part of any named selection
    assert len(dp.get_named_selections()) == 0

    ns = design.create_named_selection("MyNS", bodies=[box])
    ns.add_members(datum_points=[dp])

    included = dp.get_named_selections()
    assert len(included) == 1
    assert included[0].name == "MyNS"

    # After removal the datum point is no longer linked to the named selection
    ns.remove_members(members=[dp])
    assert len(dp.get_named_selections()) == 0


def test_search_datum_point(modeler: Modeler):
    """Test recursive search for datum points across nested components."""
    design = modeler.create_design("SearchDatumPoint_Test")

    dp1 = design.create_datum_point("DP1", Point3D([1, 0, 0], UNITS.m))
    nested = design.add_component("Nested")
    dp2 = nested.create_datum_point("DP2", Point3D([2, 0, 0], UNITS.m))
    deep = nested.add_component("Deep")
    dp3 = deep.create_datum_point("DP3", Point3D([3, 0, 0], UNITS.m))

    # Root search finds datum points at all depths
    assert design.search_datum_point(dp1.id) is dp1
    assert design.search_datum_point(dp2.id) is dp2
    assert design.search_datum_point(dp3.id) is dp3

    # Nested search finds its own and deeper datum points but not the root one
    assert nested.search_datum_point(dp2.id) is dp2
    assert nested.search_datum_point(dp3.id) is dp3
    assert nested.search_datum_point(dp1.id) is None

    # Unknown id returns None
    assert design.search_datum_point("non_existent_id") is None
