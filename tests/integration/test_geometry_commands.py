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

import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core.designer.geometry_commands import (
    ExtrudeType,
    FillPatternType,
    OffsetMode,
)
from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.shapes.curves.line import Line
from ansys.geometry.core.sketch.sketch import Sketch

from .conftest import FILES_DIR, skip_if_core_service


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
        body.faces[1],
        1,
        None,
        ExtrudeType.ADD,
        OffsetMode.MOVE_FACES_TOGETHER,
        False,
        False,
        False,
    )
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # move apart, volume should double
    modeler.geometry_commands.extrude_faces(
        body.faces[1],
        0.5,
        None,
        ExtrudeType.ADD,
        OffsetMode.MOVE_FACES_APART,
        False,
        False,
        False,
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
        body.faces[1],
        up_to.edges[0],
        Point3D([0, 0, 0]),
        UnitVector3D([0, 0, 1]),
        ExtrudeType.ADD,
    )
    assert len(bodies) == 0
    assert len(design.bodies) == 1
    assert body.volume.m == pytest.approx(Quantity(5, UNITS.m**3).m, rel=1e-6, abs=1e-8)


def test_extrude_edges_and_up_to(modeler: Modeler):
    """Test extrude edges and up to."""
    design = modeler.create_design("extrude_edges")
    upto = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    upto.translate(UnitVector3D([0, 0, 1]), 5)
    assert upto.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    body = design.extrude_sketch("box2", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # extrude edge
    created_bodies = modeler.geometry_commands.extrude_edges(
        body.edges[0], 1, body.edges[0].faces[1]
    )
    assert len(created_bodies) == 1
    assert created_bodies[0].is_surface
    assert created_bodies[0].faces[0].area.m == pytest.approx(
        Quantity(1, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )

    # extrude edge up to face
    created_bodies = modeler.geometry_commands.extrude_edges_up_to(
        body.edges[0], upto.faces[0], Point3D([0, 0, 0]), UnitVector3D([0, 0, 1])
    )
    assert len(created_bodies) == 1
    assert created_bodies[0].is_surface
    assert created_bodies[0].faces[0].area.m == pytest.approx(
        Quantity(4, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )

    # extrude multiple edges up to
    created_bodies = modeler.geometry_commands.extrude_edges_up_to(
        body.edges, upto.faces[1], Point3D([0, 0, 0]), UnitVector3D([0, 0, 1])
    )
    assert created_bodies[0].is_surface
    assert created_bodies[0].faces[0].area.m == pytest.approx(
        Quantity(6, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )
    assert created_bodies[0].faces[1].area.m == pytest.approx(
        Quantity(6, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )
    assert created_bodies[0].faces[2].area.m == pytest.approx(
        Quantity(6, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )
    assert created_bodies[0].faces[3].area.m == pytest.approx(
        Quantity(6, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )


def test_rename_body_object(modeler: Modeler):
    """Test renaming body objects."""
    design = modeler.create_design("rename")
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    selection = [body]
    result = modeler.geometry_commands.rename_object(selection, "new_name")
    design._update_design_inplace()

    body = design.bodies[0]
    assert result
    assert body.name == "new_name"

    result = modeler.geometry_commands.rename_object(selection, "new_name2")
    design._update_design_inplace()

    body = design.bodies[0]
    assert result
    assert body.name == "new_name2"


def test_rename_component_object(modeler: Modeler):
    """Test renaming component objects."""
    design = modeler.create_design("rename_component")
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    selection = [body.parent_component]
    result = modeler.geometry_commands.rename_object(selection, "new_name")
    design._update_design_inplace()

    component = body.parent_component
    assert result
    assert component.name == "new_name"

    result = modeler.geometry_commands.rename_object(selection, "new_name2")
    design._update_design_inplace()

    component = body.parent_component
    assert result
    assert component.name == "new_name2"


def test_linear_pattern(modeler: Modeler):
    """Test linear pattern."""
    design = modeler.create_design("linear_pattern")
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    cutout = design.extrude_sketch("cylinder", Sketch().circle(Point2D([-0.4, -0.4]), 0.05), 1)
    body.subtract(cutout)

    # two dimensional
    success = modeler.geometry_commands.create_linear_pattern(
        body.faces[-1], body.edges[2], 5, 0.2, True, 5, 0.2
    )
    assert success
    assert body.volume.m == pytest.approx(
        Quantity(0.803650459151, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(body.faces) == 31

    # modify linear pattern
    success = modeler.geometry_commands.modify_linear_pattern(body.faces[-1], 8, 0.11, 8, 0.11)
    assert success
    assert body.volume.m == pytest.approx(
        Quantity(0.497345175426, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(body.faces) == 70

    # try keeping some old values
    success = modeler.geometry_commands.modify_linear_pattern(body.faces[-1], 4, 0, 4, 0, 1, 1)
    assert success
    assert body.volume.m == pytest.approx(
        Quantity(0.874336293856, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(body.faces) == 22

    # back to creating - one dimensional
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    cutout = design.extrude_sketch("cylinder", Sketch().circle(Point2D([-0.4, -0.4]), 0.05), 1)
    body.subtract(cutout)

    success = modeler.geometry_commands.create_linear_pattern(body.faces[-1], body.edges[2], 5, 0.2)
    assert success
    assert body.volume.m == pytest.approx(Quantity(0.96073009183, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(body.faces) == 11

    # intentional failure to create pattern
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    cutout = design.extrude_sketch("cylinder", Sketch().circle(Point2D([-0.4, -0.4]), 0.05), 1)
    body.subtract(cutout)

    success = modeler.geometry_commands.create_linear_pattern(body.faces[-1], body.edges[0], 5, 0.2)
    assert not success
    assert body.volume.m == pytest.approx(
        Quantity(0.992146018366, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(body.faces) == 7

    # input validation test
    with pytest.raises(
        ValueError,
        match="If the pattern is two dimensional, count_y and pitch_y must be provided.",
    ):
        modeler.geometry_commands.create_linear_pattern(body.faces[-1], body.edges[0], 5, 0.2, True)
    with pytest.raises(
        ValueError,
        match="If the pattern is two dimensional, count_y and pitch_y must be provided.",
    ):
        modeler.geometry_commands.create_linear_pattern(
            body.faces[-1], body.edges[0], 5, 0.2, True, 5
        )
    with pytest.raises(
        ValueError,
        match=(
            "You provided count_y and pitch_y. Ensure two_dimensional is True if a "
            "two-dimensional pattern is desired."
        ),
    ):
        modeler.geometry_commands.create_linear_pattern(
            body.faces[-1], body.edges[0], 5, 0.2, False, 5, 0.2
        )


def test_circular_pattern(modeler: Modeler):
    """Test circular pattern."""
    design = modeler.create_design("d1")
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    axis = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 0.01, 0.01), 1)
    base.subtract(axis)
    axis = base.edges[20]

    cutout = design.extrude_sketch("cylinder", Sketch().circle(Point2D([-0.2, 0]), 0.005), 1)
    base.subtract(cutout)

    assert base.volume.m == pytest.approx(
        Quantity(0.999821460184, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(base.faces) == 11

    # full two-dimensional test - creates 3 rings around the center
    success = modeler.geometry_commands.create_circular_pattern(
        base.faces[-1], axis, 12, np.pi * 2, True, 3, 0.05, UnitVector3D([1, 0, 0])
    )
    assert success
    assert base.volume.m == pytest.approx(
        Quantity(0.997072566612, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(base.faces) == 46

    # input validation test
    with pytest.raises(
        ValueError,
        match="If the pattern is two-dimensional, linear_count and linear_pitch must be provided.",
    ):
        modeler.geometry_commands.create_circular_pattern(base.faces[-1], axis, 12, np.pi * 2, True)
    with pytest.raises(
        ValueError,
        match=(
            "You provided linear_count and linear_pitch. Ensure two_dimensional is True if a "
            "two-dimensional pattern is desired."
        ),
    ):
        modeler.geometry_commands.create_circular_pattern(
            base.faces[-1], axis, 12, np.pi * 2, False, 3, 0.05
        )


def test_fill_pattern(modeler: Modeler):
    """Test fill pattern."""
    design = modeler.create_design("d1")

    # grid fill pattern
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    cutout = design.extrude_sketch("cylinder", Sketch().circle(Point2D([-0.4, -0.4]), 0.05), 1)
    base.subtract(cutout)
    assert base.volume.m == pytest.approx(
        Quantity(0.992146018366, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(base.faces) == 7

    success = modeler.geometry_commands.create_fill_pattern(
        base.faces[-1],
        base.edges[2],
        FillPatternType.GRID,
        0.01,
        0.1,
        0.1,
    )
    assert success
    assert base.volume.m == pytest.approx(
        Quantity(0.803650459151, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(base.faces) == 31

    # offset fill pattern
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    cutout = design.extrude_sketch("cylinder", Sketch().circle(Point2D([-0.4, -0.4]), 0.05), 1)
    base.subtract(cutout)
    assert base.volume.m == pytest.approx(
        Quantity(0.992146018366, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(base.faces) == 7

    success = modeler.geometry_commands.create_fill_pattern(
        base.faces[-1],
        base.edges[2],
        FillPatternType.OFFSET,
        0.01,
        0.05,
        0.05,
    )
    assert success
    assert base.volume.m == pytest.approx(
        Quantity(0.670132771373, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(base.faces) == 48

    # skewed fill pattern
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    cutout = design.extrude_sketch("cylinder", Sketch().circle(Point2D([-0.4, -0.4]), 0.05), 1)
    base.subtract(cutout)
    assert base.volume.m == pytest.approx(
        Quantity(0.992146018366, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(base.faces) == 7

    success = modeler.geometry_commands.create_fill_pattern(
        base.faces[-1],
        base.edges[2],
        FillPatternType.SKEWED,
        0.01,
        0.1,
        0.1,
        0.1,
        0.2,
        0.2,
        0.1,
    )
    assert success
    assert base.volume.m == pytest.approx(
        Quantity(0.787942495883, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(base.faces) == 33

    # update fill pattern
    base = design.extrude_sketch("update_fill", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    cutout = design.extrude_sketch("cylinder", Sketch().circle(Point2D([-0.4, -0.4]), 0.05), 1)
    base.subtract(cutout)
    base.translate(UnitVector3D([1, 0, 0]), 5)
    assert base.volume.m == pytest.approx(
        Quantity(0.992146018366, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(base.faces) == 7

    success = modeler.geometry_commands.create_fill_pattern(
        base.faces[-1],
        base.edges[2],
        FillPatternType.GRID,
        0.01,
        0.1,
        0.1,
    )
    assert success
    assert base.volume.m == pytest.approx(
        Quantity(0.803650459151, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(base.faces) == 31

    face = base.faces[3]
    modeler.geometry_commands.extrude_faces(face, 1, face.normal(0, 0))
    success = modeler.geometry_commands.update_fill_pattern(base.faces[-1])
    assert success
    assert base.volume.m == pytest.approx(Quantity(1.60730091830, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 56


def test_revolve_faces(modeler: Modeler):
    """Test revolve faces."""
    design = modeler.create_design("revolve_faces")
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    bodies = modeler.geometry_commands.revolve_faces(
        base.faces[2], Line([0.5, 0.5, 0], [0, 0, 1]), np.pi * 3 / 2
    )
    assert len(bodies) == 0
    assert base.volume.m == pytest.approx(Quantity(3.35619449019, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 5


def test_revolve_faces_up_to(modeler: Modeler):
    """Test revolve faces up to."""
    design = modeler.create_design("revolve_faces_up_to")
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    bodies = modeler.geometry_commands.revolve_faces_up_to(
        base.faces[2],
        base.faces[4],
        Line([0.5, 0.5, 0], [0, 0, 1]),
        UnitVector3D([1, 0, 0]),
        ExtrudeType.FORCE_ADD,
    )
    assert len(bodies) == 0
    assert base.volume.m == pytest.approx(Quantity(1.78539816340, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 6


def test_revolve_faces_by_helix(modeler: Modeler):
    """Test revolve faces by helix."""
    design = modeler.create_design("revolve_faces_by_helix")
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    bodies = modeler.geometry_commands.revolve_faces_by_helix(
        base.faces[2],
        Line([0.5, 0.5, 0], [0, 0, 1]),
        UnitVector3D([1, 0, 0]),
        5,
        1,
        np.pi / 4,
        True,
        True,
    )
    assert len(bodies) == 2
    assert base.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 6

    assert design.bodies[1].volume.m == pytest.approx(
        Quantity(86.2510674259, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(base.faces) == 6
    # raise tolerance to 1e-4 to account for windows/linux parasolid differences
    assert design.bodies[2].volume.m == pytest.approx(
        Quantity(86.2510735368, UNITS.m**3).m, rel=1e-4, abs=1e-8
    )
    assert len(base.faces) == 6


def test_replace_face(modeler: Modeler):
    """Test replacing a face with another face."""
    design = modeler.create_design("replace_face")
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    cutout = design.extrude_sketch("cylinder", Sketch().circle(Point2D([-0.4, -0.4]), 0.05), 1)
    base.subtract(cutout)

    # replace face with a new face
    new_face = design.extrude_sketch("new_face", Sketch().box(Point2D([0, 0]), 0.1, 0.1), 1)
    success = modeler.geometry_commands.replace_face(base.faces[-1], new_face.faces[0])
    assert success
    assert base.volume.m == pytest.approx(
        Quantity(0.992146018366, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(base.faces) == 7

    # replace face with an existing face
    success = modeler.geometry_commands.replace_face(base.faces[-1], base.faces[0])
    assert success
    assert base.volume.m == pytest.approx(
        Quantity(0.992146018366, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert len(base.faces) == 7


def test_split_body_by_plane(modeler: Modeler):
    """Test split body by plane"""
    design = modeler.create_design("split_body_by_plane")

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert len(body.faces) == 6
    assert len(body.edges) == 12
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    origin = Point3D([0, 0, 0.5])
    plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])

    success = modeler.geometry_commands.split_body([body], plane, None, None, True)
    assert success is True

    assert len(design.bodies) == 2

    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(0.5, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert design.bodies[1].volume.m == pytest.approx(
        Quantity(0.5, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


def test_split_body_by_slicer_face(modeler: Modeler):
    """Test split body by slicer face"""
    design = modeler.create_design("split_body_by_slicer_face")

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert len(body.faces) == 6
    assert len(body.edges) == 12
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    body2 = design.extrude_sketch("box2", Sketch().box(Point2D([3, 0]), 1, 1), 0.5)
    assert len(body2.faces) == 6
    assert len(body2.edges) == 12
    assert body2.volume.m == pytest.approx(Quantity(0.5, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    face_to_split = body2.faces[1]

    success = modeler.geometry_commands.split_body([body], None, [face_to_split], None, True)
    assert success is True

    assert len(design.bodies) == 3

    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(0.5, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert design.bodies[1].volume.m == pytest.approx(
        Quantity(0.5, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert design.bodies[2].volume.m == pytest.approx(
        Quantity(0.5, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


def test_split_body_by_slicer_edge(modeler: Modeler):
    """Test split body by slicer edge"""
    # Skip for Core service
    skip_if_core_service(
        modeler, test_split_body_by_slicer_edge.__name__, "split_body_by_slicer_edge"
    )

    design = modeler.open_file(FILES_DIR / "Edge_Slice_test.dsco")

    assert len(design.bodies) == 1
    body = design.bodies[0]
    assert len(body.faces) == 4
    assert len(body.edges) == 3
    assert body.volume.m == pytest.approx(
        Quantity(6.283185307179587e-06, UNITS.m**3).m, rel=1e-5, abs=1e-8
    )

    edge_to_split = body.edges[2]

    success = modeler.geometry_commands.split_body([body], None, [edge_to_split], None, True)
    assert success is True

    assert len(design.bodies) == 2

    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(3.1415927e-06, UNITS.m**3).m, rel=1e-5, abs=1e-8
    )
    assert design.bodies[1].volume.m == pytest.approx(
        Quantity(3.1415927e-06, UNITS.m**3).m, rel=1e-5, abs=1e-8
    )


def test_split_body_by_face(modeler: Modeler):
    """Test split body by face"""
    design = modeler.create_design("split_body_by_face")

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert len(body.faces) == 6
    assert len(body.edges) == 12
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    body2 = design.extrude_sketch("box2", Sketch().box(Point2D([3, 0]), 1, 1), 0.5)
    assert len(body2.faces) == 6
    assert len(body2.edges) == 12
    assert body2.volume.m == pytest.approx(Quantity(0.5, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    face_to_split = body2.faces[1]

    success = modeler.geometry_commands.split_body([body], None, None, [face_to_split], True)
    assert success is True

    assert len(design.bodies) == 3

    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(0.5, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert design.bodies[1].volume.m == pytest.approx(
        Quantity(0.5, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    assert design.bodies[2].volume.m == pytest.approx(
        Quantity(0.5, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


def test_get_round_info(modeler: Modeler):
    """Test getting the round info from a face"""
    design = modeler.create_design("full_fillet")

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

    _, radius = modeler.geometry_commands.get_round_info(body.faces[6])
    assert radius == pytest.approx(
        Quantity(0.1, UNITS.m).m, rel=1e-6, abs=1e-8
    )


def test_get_empty_round_info(modeler: Modeler):
    """Test getting the round info from a face that doesnt have any rounding"""
    design = modeler.create_design("full_fillet")

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert len(body.faces) == 6
    assert len(body.edges) == 12
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    _, radius = modeler.geometry_commands.get_round_info(body.faces[5])
    assert radius == 0.0


def test_get_closest_face_separation(modeler: Modeler):
    """Test getting the closest face separation."""
    design = modeler.create_design("closest_face_separation")

    body1 = design.extrude_sketch("box1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    body2 = design.extrude_sketch("box2", Sketch().box(Point2D([2, 0]), 1, 1), 1)

    distance, _, _ = body1.faces[0].get_closest_separation(body2.faces[0])
    assert distance == pytest.approx(1.0, rel=1e-6, abs=1e-8)

    body2.translate(UnitVector3D([0, 0, 1]), 1)
    distance, _, _ = body1.faces[0].get_closest_separation(body2.faces[0])
    assert distance == pytest.approx(1.41421356237, rel=1e-6, abs=1e-8)