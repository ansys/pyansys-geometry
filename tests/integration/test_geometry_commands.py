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
"""Testing of geometry commands."""

from pint import Quantity
import pytest

from ansys.geometry.core.designer.geometry_commands import ExtrudeType, OffsetMode
from ansys.geometry.core.math import Point3D, UnitVector3D
from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.sketch.sketch import Sketch


def test_chamfer(modeler: Modeler):
    """Test chamfer on edges and faces."""
    design = modeler.create_design("chamfer")

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert len(body.faces) == 6
    assert len(body.edges) == 12
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    modeler.geometry_commands.chamfer(body.edges[0], 0.1)
    assert len(body.faces) == 7
    assert len(body.edges) == 15
    assert body.volume.m == pytest.approx(Quantity(0.995, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    modeler.geometry_commands.chamfer(body.faces[-1], 0.5)
    assert len(body.faces) == 7
    assert len(body.edges) == 15
    assert body.volume.m == pytest.approx(Quantity(0.875, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # multiple edges
    body2 = design.extrude_sketch("box2", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert len(body2.faces) == 6
    assert len(body2.edges) == 12
    assert body2.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    modeler.geometry_commands.chamfer(body2.edges, 0.1)
    assert len(body2.faces) == 26
    assert len(body2.edges) == 48
    assert body2.volume.m == pytest.approx(
        Quantity(0.945333333333333333, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


def test_fillet(modeler: Modeler):
    """Test fillet on edge and face."""
    design = modeler.create_design("fillet")

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert len(body.faces) == 6
    assert len(body.edges) == 12
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    modeler.geometry_commands.fillet(body.edges[0], 0.1)
    assert len(body.faces) == 7
    assert len(body.edges) == 15
    assert body.volume.m == pytest.approx(
        Quantity(0.9978539816339744, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )

    modeler.geometry_commands.fillet(body.faces[-1], 0.5)
    assert len(body.faces) == 7
    assert len(body.edges) == 15
    assert body.volume.m == pytest.approx(
        Quantity(0.946349540849362, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )

    # multiple edges
    body2 = design.extrude_sketch("box2", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert len(body2.faces) == 6
    assert len(body2.edges) == 12
    assert body2.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    modeler.geometry_commands.fillet(body2.edges, 0.1)
    assert len(body2.faces) == 26
    assert len(body2.edges) == 48
    assert body2.volume.m == pytest.approx(
        Quantity(0.9755870138909422, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )

    modeler.geometry_commands.fillet(body2.faces, 0.3)
    assert len(body2.faces) == 26
    assert len(body2.edges) == 48
    assert body2.volume.m == pytest.approx(
        Quantity(0.8043893421169303, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )

    modeler.geometry_commands.fillet(body2.faces, 0.05)
    assert len(body2.faces) == 26
    assert len(body2.edges) == 48
    assert body2.volume.m == pytest.approx(
        Quantity(0.9937293491873294, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


def test_full_fillet(modeler: Modeler):
    """Test full fillet on faces."""
    design = modeler.create_design("full_fillet")

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert len(body.faces) == 6
    assert len(body.edges) == 12
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    modeler.geometry_commands.full_fillet(body.faces[0:3])
    assert len(body.faces) == 6
    assert len(body.edges) == 12
    assert body.volume.m == pytest.approx(
        Quantity(0.8926990816987, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


def test_extrude_faces_and_offset_relationships(modeler: Modeler):
    """Test extrude faces and offset relationships."""
    design = modeler.create_design("extrude_faces")
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # extrude out, double volume
    modeler.geometry_commands.extrude_faces(body.faces[1], 1)
    assert body.volume.m == pytest.approx(Quantity(2, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # extrude in, cut in half
    modeler.geometry_commands.extrude_faces(
        body.faces[1],
        -1,
        None,
        ExtrudeType.FORCE_CUT,
        OffsetMode.IGNORE_RELATIONSHIPS,
        False,
        False,
        True,
    )
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # setup offset relationship, faces will move together, volume won't change
    body.faces[0].setup_offset_relationship(body.faces[1], True)
    modeler.geometry_commands.extrude_faces(
        body.faces[1], 1, None, ExtrudeType.ADD, OffsetMode.MOVE_FACES_TOGETHER, False, False, False
    )
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # move apart, volume should double
    modeler.geometry_commands.extrude_faces(
        body.faces[1], 0.5, None, ExtrudeType.ADD, OffsetMode.MOVE_FACES_APART, False, False, False
    )
    assert body.volume.m == pytest.approx(Quantity(2, UNITS.m**3).m, rel=1e-6, abs=1e-8)


def test_extrude_faces_up_to(modeler: Modeler):
    """Test extrude faces up to."""
    design = modeler.create_design("extrude_faces_up_to")
    up_to = design.extrude_sketch("up_to", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    up_to.translate(UnitVector3D([0, 0, 1]), 4)
    assert up_to.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # extrude up to other block's face, force independent or else they would merge into one body
    bodies = modeler.geometry_commands.extrude_faces_up_to(
        body.faces[1],
        up_to.faces[0],
        Point3D([0, 0, 0]),
        UnitVector3D([0, 0, 1]),
        ExtrudeType.FORCE_INDEPENDENT,
        OffsetMode.IGNORE_RELATIONSHIPS,
    )
    assert len(bodies) == 0
    assert len(design.bodies) == 2
    assert body.volume.m == pytest.approx(Quantity(4, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    body.parent_component.delete_body(body)

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # extrude up to other block's edge, add so they merge into one body
    bodies = modeler.geometry_commands.extrude_faces_up_to(
        body.faces[1], up_to.edges[0], Point3D([0, 0, 0]), UnitVector3D([0, 0, 1]), ExtrudeType.ADD
    )
    assert len(bodies) == 0
    assert len(design.bodies) == 1
    assert body.volume.m == pytest.approx(Quantity(5, UNITS.m**3).m, rel=1e-6, abs=1e-8)
