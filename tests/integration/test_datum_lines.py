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

"""Integration tests for the DatumLine class."""

from pathlib import Path

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.shapes.curves.line import Line
from tests.integration.conftest import FILES_DIR


def test_create_datum_line(modeler: Modeler):
    """Test creation of datum lines and their basic properties.

    Combines creation, property validation, repr output, and nested-component
    scoping into a single test.
    """
    design = modeler.create_design("CreateDatumLine_Test")

    # Create a datum line at the root design level
    line = Line(Point3D([0, 0, 0]), UnitVector3D([1, 0, 0]))
    dl1 = design.create_datum_line("DL1", line)

    assert dl1.id is not None
    assert dl1.name == "DL1"
    assert dl1.line == line
    assert dl1.parent_component.id == design.id
    assert dl1.is_alive
    assert len(design.datum_lines) == 1
    assert design.datum_lines[0].id == dl1.id

    # Create a second datum line on a nested component
    nested = design.add_component("Nested")
    line2 = Line(Point3D([1, 0, 0]), UnitVector3D([0, 1, 0]))
    dl2 = nested.create_datum_line("DL2", line2)

    assert dl2.id is not None
    assert dl2.id != dl1.id
    assert dl2.name == "DL2"
    assert dl2.parent_component.id == nested.id
    assert dl2.is_alive
    assert len(nested.datum_lines) == 1
    assert nested.datum_lines[0] == dl2

    # The root design-level list does not include datum lines from nested components
    assert len(design.datum_lines) == 1

    # Verify repr output
    dl1_str = str(dl1)
    assert "ansys.geometry.core.designer.DatumLine" in dl1_str
    assert "  Name                 : DL1" in dl1_str
    assert "  Line           : " in dl1_str


def test_delete_datum_line(modeler: Modeler):
    """Test deletion of datum lines from a component.

    Covers deletion by object, deletion by ID, wrong-component scoping,
    and nested component scoping.
    """
    design = modeler.create_design("DeleteDatumLine_Test")

    line1 = Line(Point3D([0, 0, 0]), UnitVector3D([1, 0, 0]))
    line2 = Line(Point3D([1, 0, 0]), UnitVector3D([0, 1, 0]))
    line3 = Line(Point3D([0, 1, 0]), UnitVector3D([0, 0, 1]))

    dl1 = design.create_datum_line("DL1", line1)
    dl2 = design.create_datum_line("DL2", line2)
    dl3 = design.create_datum_line("DL3", line3)

    # Verify all datum lines exist
    assert len(design.datum_lines) == 3
    assert dl1.is_alive
    assert dl2.is_alive
    assert dl3.is_alive

    # Delete by object
    design.delete_datum_line(dl1)
    assert not dl1.is_alive
    assert dl2.is_alive
    assert dl3.is_alive

    # Delete by ID
    design.delete_datum_line(dl2.id)
    assert not dl2.is_alive
    assert dl3.is_alive

    # Attempt deletion from wrong component (should not delete)
    comp = design.add_component("WrongComp")
    comp.delete_datum_line(dl3)
    assert dl3.is_alive

    # Delete from root design (correct scope)
    design.delete_datum_line(dl3)
    assert not dl3.is_alive

    # Create a datum line on a nested component and delete from there
    nested = design.add_component("NestedComp")
    dl_nested = nested.create_datum_line("DLNested", line1)
    assert dl_nested.is_alive
    assert len(nested.datum_lines) == 1

    nested.delete_datum_line(dl_nested)
    assert not dl_nested.is_alive


def test_search_datum_line(modeler: Modeler):
    """Test recursive search for datum lines across nested components."""
    design = modeler.create_design("SearchDatumLine_Test")

    line1 = Line(Point3D([0, 0, 0]), UnitVector3D([1, 0, 0]))
    line2 = Line(Point3D([1, 0, 0]), UnitVector3D([0, 1, 0]))
    line3 = Line(Point3D([0, 1, 0]), UnitVector3D([0, 0, 1]))

    dl1 = design.create_datum_line("DL1", line1)
    nested = design.add_component("Nested")
    dl2 = nested.create_datum_line("DL2", line2)
    deep = nested.add_component("Deep")
    dl3 = deep.create_datum_line("DL3", line3)

    # Root search finds datum lines at all depths
    assert design.search_datum_line(dl1.id) is dl1
    assert design.search_datum_line(dl2.id) is dl2
    assert design.search_datum_line(dl3.id) is dl3

    # Nested search finds its own and deeper datum lines but not the root one
    assert nested.search_datum_line(dl2.id) is dl2
    assert nested.search_datum_line(dl3.id) is dl3
    assert nested.search_datum_line(dl1.id) is None

    # Unknown id returns None
    assert design.search_datum_line("non_existent_id") is None


def test_import_datum_lines(modeler: Modeler):
    """Test importing datum lines from a file."""
    design = modeler.open_file(Path(FILES_DIR, "Axes.dsco"))

    # Verify that datum lines are present in the imported design
    assert len(design.components) == 1
    assert len(design.datum_lines) == 2
    assert len(design.components[0].datum_lines) == 1

    # Test the properties of the imported datum lines
    dl1 = design.datum_lines[0]
    assert dl1.name == "DatumLine1"
    assert dl1.line.origin == Point3D([-0.01, -0.01, 0.02])
    assert dl1.line.direction == UnitVector3D([0, 1, 0])

    dl2 = design.datum_lines[1]
    assert dl2.name == "DatumLine2"
    assert dl2.line.origin == Point3D([0.04678, -0.01, 0.02])
    assert dl2.line.direction == UnitVector3D([0, -1, 0])

    dl3 = design.components[0].datum_lines[0]
    assert dl3.name == "NestedLine"
    assert dl3.line.origin == Point3D([-0.01, -0.01, 0])
    assert dl3.line.direction == UnitVector3D([0, 0, 1])
