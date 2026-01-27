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
"""Testing of geometry commands."""

import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core.designer.geometry_commands import (
    DraftSide,
    ExtrudeType,
    FillPatternType,
    GeometryCommands,
    OffsetMode,
)
from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
from ansys.geometry.core.math.constants import UNITVECTOR3D_Y, UNITVECTOR3D_Z
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.misc.measurements import Angle, Distance
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.shapes.curves.line import Line
from ansys.geometry.core.shapes.surfaces.sphere import Sphere
from ansys.geometry.core.sketch.sketch import Sketch

from .conftest import FILES_DIR


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


def test_circular_pattern_about_line(modeler: Modeler):
    """Test circular pattern about line."""
    design = modeler.create_design("d1")
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 20, 20), 20)

    cutout = design.extrude_sketch("cylinder", Sketch().circle(Point2D([-5, -5]), 1), 20)
    base.subtract(cutout)

    assert base.volume.m == pytest.approx(Quantity(7937.1681, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 7

    # full two-dimensional test - creates 3 rings around the center
    axis = Line(Point3D([0, 0, 0]), UNITVECTOR3D_Z)
    success = modeler.geometry_commands.create_circular_pattern(base.faces[-1], axis, 8, np.pi * 2)

    assert success
    assert base.volume.m == pytest.approx(Quantity(7497.3452, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 14


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


def test_revolve_faces_with_options(modeler: Modeler):
    # Parameters
    pitch = 0.7
    inner_diameter = 4
    width = 7
    height = 3.2

    # Cylinder Creation
    design = modeler.create_design("SquareNut")
    sketch = Sketch()
    sketch.circle(Point2D([0, 0], UNITS.mm), Quantity(inner_diameter / 2, UNITS.mm))
    cylinder0 = design.extrude_sketch("SquareNut", sketch, Quantity(height, UNITS.mm))

    # Create HexNut
    sketch1 = Sketch()
    sketch1.polygon(Point2D([0, 0]), Distance(width / 2, UNITS.mm), 4, Angle(45))
    hex_nut = design.extrude_sketch("HexNut", sketch1, Quantity(height, UNITS.mm), "+", False)

    copy1 = cylinder0.copy(design, "SquareNut")
    copy2 = hex_nut.copy(design, "SquareNut")
    copy2.subtract(copy1, False)
    design.delete_body(design.bodies[0].id)
    design.delete_body(design.bodies[0].id)

    plane2 = Plane(
        Point3D([0, (width) / 2, height], UNITS.mm),
        direction_x=UnitVector3D([0, 1, 0]),
        direction_y=UnitVector3D([0, 0, 1]),
    )
    sketch2 = Sketch(plane2)
    sketch2.segment(Point2D([-2 * pitch, pitch], UNITS.mm), Point2D([3 * pitch, 0], UNITS.mm))
    sketch2.segment(Point2D([3 * pitch, 0], UNITS.mm), Point2D([3 * pitch, -3 * pitch], UNITS.mm))
    sketch2.segment(
        Point2D([3 * pitch, -3 * pitch], UNITS.mm), Point2D([-2 * pitch, pitch], UNITS.mm)
    )
    cut_surface = design.create_surface("Cut", sketch2)

    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(1.16587614e-7, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )

    modeler.geometry_commands.revolve_faces(
        cut_surface.faces,
        Line(Point3D([0, 0, 0], UNITS.mm), UNITVECTOR3D_Z),
        np.pi * 2,
        ExtrudeType.CUT,
    )

    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(1.06173048542e-07, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


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


def test_revolve_faces_by_helix_with_options(modeler: Modeler):
    # Parameters
    pitch = 0.7
    inner_diameter = 4
    width = 7
    height = 3.2

    thread_length = height - pitch / 2

    # Cylinder Creation
    design = modeler.create_design("SquareNut")
    sketch = Sketch()
    sketch.circle(Point2D([0, 0], UNITS.mm), Quantity(inner_diameter / 2, UNITS.mm))
    cylinder0 = design.extrude_sketch("SquareNut", sketch, Quantity(height, UNITS.mm))

    # Create HexNut
    sketch1 = Sketch()
    sketch1.polygon(Point2D([0, 0]), Distance(width / 2, UNITS.mm), 4, Angle(45))
    hex_nut = design.extrude_sketch("HexNut", sketch1, Quantity(height, UNITS.mm), "+", False)

    copy1 = cylinder0.copy(design, "SquareNut")
    copy2 = hex_nut.copy(design, "SquareNut")
    copy2.subtract(copy1, False)
    design.delete_body(design.bodies[0].id)
    design.delete_body(design.bodies[0].id)

    plane2 = Plane(
        Point3D([0, (width) / 2, height], UNITS.mm),
        direction_x=UnitVector3D([0, 1, 0]),
        direction_y=UnitVector3D([0, 0, 1]),
    )
    sketch2 = Sketch(plane2)
    sketch2.segment(Point2D([-2 * pitch, pitch], UNITS.mm), Point2D([3 * pitch, 0], UNITS.mm))
    sketch2.segment(Point2D([3 * pitch, 0], UNITS.mm), Point2D([3 * pitch, -3 * pitch], UNITS.mm))
    sketch2.segment(
        Point2D([3 * pitch, -3 * pitch], UNITS.mm), Point2D([-2 * pitch, pitch], UNITS.mm)
    )
    cut_surface = design.create_surface("Cut", sketch2)

    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(1.16587614e-7, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )

    modeler.geometry_commands.revolve_faces(
        cut_surface.faces,
        Line(Point3D([0, 0, 0], UNITS.mm), UNITVECTOR3D_Z),
        np.pi * 2,
        ExtrudeType.CUT,
    )
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(1.06173048542e-07, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )

    starting_face_count = len(design.bodies[0].faces)
    current_face_count = len(design.bodies[0].faces)
    x = 0
    while starting_face_count == current_face_count:
        if x > 1000:
            break
        modeler.geometry_commands.extrude_faces(design.bodies[0].faces[-1], (0.05) / 1000)
        current_face_count = len(design.bodies[0].faces)
        x += 1

    thread_height = pitch * (3**0.5 / 2)
    thread_plane = Plane(
        Point3D([0, (inner_diameter) / 2, 0], UNITS.mm),
        direction_x=UNITVECTOR3D_Y,
        direction_y=UNITVECTOR3D_Z,
    )
    thread_sketch = Sketch(thread_plane)
    thread_sketch.segment(Point2D([0, 0], UNITS.mm), Point2D([0, pitch / 2], UNITS.mm))
    thread_sketch.segment(
        Point2D([0, pitch / 2], UNITS.mm),
        Point2D([thread_height * (3 / 8), (pitch / 2 - pitch / 8)], UNITS.mm),
    )
    thread_sketch.segment(
        Point2D([thread_height * (3 / 8), (pitch / 2 - pitch / 8)], UNITS.mm),
        Point2D([thread_height * (3 / 8), ((pitch / 4) / 2)], UNITS.mm),
    )
    thread_sketch.segment(
        Point2D([0, 0], UNITS.mm), Point2D([thread_height * (3 / 8), ((pitch / 4) / 2)], UNITS.mm)
    )
    thread_surface = design.create_surface("Thread", thread_sketch)
    dir = UNITVECTOR3D_Z
    axs = UNITVECTOR3D_Z
    modeler.geometry_commands.revolve_faces_by_helix(
        thread_surface.faces[0],
        Line(Point3D([0, 0, 0], UNITS.mm), axs),
        dir,
        2 * thread_length / 1000,
        pitch / 1000,
        0,
        True,
        True,
        ExtrudeType.CUT,
    )

    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(1.06173048542e-07, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


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
    design = modeler.open_file(FILES_DIR / "Edge_Slice_Test.dsco")

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
    assert radius == pytest.approx(Quantity(0.1, UNITS.m).m, rel=1e-6, abs=1e-8)


def test_get_empty_round_info(modeler: Modeler):
    """Test getting the round info from a face that does not have any rounding"""
    design = modeler.create_design("full_fillet")

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert len(body.faces) == 6
    assert len(body.edges) == 12
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    _, radius = modeler.geometry_commands.get_round_info(body.faces[5])
    assert radius == 0.0


def test_linear_pattern_on_imported_geometry_faces(modeler: Modeler):
    """Test create a linear pattern on imported geometry"""
    design = modeler.open_file(FILES_DIR / "LinearPatterns.scdocx")
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 11
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(7.227e-6, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    success = modeler.geometry_commands.create_linear_pattern(
        [
            design.bodies[0].faces[1],
            design.bodies[0].faces[2],
            design.bodies[0].faces[0],
            design.bodies[0].faces[4],
            design.bodies[0].faces[3],
        ],
        design.bodies[0].edges[12],
        13,
        0.004,
        True,
        7,
        0.007,
    )
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 266
    assert success
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(1.08992e-5, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


def test_modify_linear_pattern_on_imported_geometry_faces(modeler: Modeler):
    """Test modifying a linear pattern on an imported geometry"""
    design = modeler.open_file(FILES_DIR / "LinearPatternsModify.scdocx")
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 266
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(1.08992e-5, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    success = modeler.geometry_commands.modify_linear_pattern(
        [
            design.bodies[0].faces[1],
            design.bodies[0].faces[2],
            design.bodies[0].faces[0],
            design.bodies[0].faces[4],
            design.bodies[0].faces[3],
        ],
        10,
        0.004,
        3,
        0.0105,
        0,
        0,
    )
    assert success
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 156
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(9.3152e-6, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


def test_circular_pattern_on_imported_geometry_faces(modeler: Modeler):
    """Test creating a circular pattern out of imported geometry"""
    design = modeler.open_file(FILES_DIR / "Fan_OneBlade_CircularPatter.scdocx")
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 13
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(0.00019496, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    success = modeler.geometry_commands.create_circular_pattern(
        [
            design.bodies[0].faces[10],
            design.bodies[0].faces[11],
            design.bodies[0].faces[7],
            design.bodies[0].faces[9],
            design.bodies[0].faces[8],
            design.bodies[0].faces[12],
        ],
        design.bodies[0].edges[3],
        8,
        np.pi * 2,
        False,
        None,
        None,
        None,
    )
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 55
    assert success
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(0.0002373, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


def test_circular_pattern_on_imported_geometry_faces_modify(modeler: Modeler):
    """Test creating a circular pattern out of imported geometry and modifying it"""
    design = modeler.open_file(FILES_DIR / "Fan_OneBlade_CircularPatter.scdocx")
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 13
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(0.00019496, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    success = modeler.geometry_commands.create_circular_pattern(
        [
            design.bodies[0].faces[10],
            design.bodies[0].faces[11],
            design.bodies[0].faces[7],
            design.bodies[0].faces[9],
            design.bodies[0].faces[8],
            design.bodies[0].faces[12],
        ],
        design.bodies[0].edges[3],
        8,
        np.pi * 2,
        False,
        None,
        None,
        None,
    )
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 55
    assert success
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(0.0002373, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    success = modeler.geometry_commands.modify_circular_pattern(
        [design.bodies[0].faces[30]], 12, 0, 0.523598775598
    )
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 79
    assert success
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(0.0002615594337, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


def test_fill_pattern_on_imported_geometry_faces(modeler: Modeler):
    """Test create a fill pattern on imported geometry"""
    design = modeler.open_file(FILES_DIR / "FillPattern.scdocx")
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 12
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(8.267e-6, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    success = modeler.geometry_commands.create_fill_pattern(
        [
            design.bodies[0].faces[3],
            design.bodies[0].faces[4],
            design.bodies[0].faces[2],
            design.bodies[0].faces[5],
            design.bodies[0].faces[1],
            design.bodies[0].faces[0],
        ],
        design.bodies[0].edges[0],
        FillPatternType.GRID,
        0.0005,
        0.00075,
        0.001,
    )
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 294
    assert success
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(4.40535e-6, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


def test_update_fill_pattern_on_imported_geometry_faces(modeler: Modeler):
    """Test modify a fill pattern on imported geometry"""
    design = modeler.open_file(FILES_DIR / "FillPatternUpdate.scdocx")
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 294
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(4.40535e-6, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    face = design.bodies[0].faces[3]
    modeler.geometry_commands.extrude_faces(face, 0.001, face.normal(0, 0))
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 294
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(5.2270374e-6, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )
    success = modeler.geometry_commands.update_fill_pattern(design.bodies[0].faces[3])
    assert success
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 342
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(4.70663693e-6, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


def test_move_translate(modeler: Modeler):
    design = modeler.create_design("move_translate_box")
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)

    # Create a named selection of 2 faces
    ns = design.create_named_selection("ns1", faces=[body.faces[0], body.faces[1]])
    assert len(ns.faces) == 2

    # Verify the original vertices
    expected_vertices = [
        Point3D([-1.0, -1.0, 0.0]),
        Point3D([1.0, -1.0, 0.0]),
        Point3D([-1.0, 1.0, 0.0]),
        Point3D([1.0, 1.0, 0.0]),
    ]

    original_vertices = []
    for edge in body.faces[0].edges:
        original_vertices.extend([edge.start, edge.end])

    assert np.isin(expected_vertices, original_vertices).all()

    # Translate the named selection
    success = modeler.geometry_commands.move_translate(ns, UNITVECTOR3D_Z, Distance(2, UNITS.m))
    assert success

    # Verify the translation
    expected_vertices = [
        Point3D([-1.0, -1.0, 2.0]),
        Point3D([1.0, -1.0, 2.0]),
        Point3D([-1.0, 1.0, 2.0]),
        Point3D([1.0, 1.0, 2.0]),
    ]

    translated_vertices = []
    for edge in body.faces[0].edges:
        translated_vertices.extend([edge.start, edge.end])

    # Check that the faces have been translated
    assert np.isin(expected_vertices, translated_vertices).all()


def test_move_translate_component(modeler: Modeler):
    # Create a design and a component, then add a box to the component
    design = modeler.create_design("MyDesign")
    component = design.add_component("MyComponent")

    # Create a sketch and extrude
    sketch = Sketch().box(Point2D([0, 0]), 1, 1)
    box_body = component.extrude_sketch("BoxBody", sketch, 1)

    # Add the component to a named selection
    ns = design.create_named_selection("ComponentNS", components=[component])

    # Move the component
    success = modeler.geometry_commands.move_translate(
        ns,
        UNITVECTOR3D_Z,
        Distance(2, UNITS.m),
    )
    assert success

    # Check the new location of the box body
    expected_vertices = [
        Point3D([-0.5, -0.5, 2.0]),
        Point3D([0.5, -0.5, 2.0]),
        Point3D([-0.5, 0.5, 2.0]),
        Point3D([0.5, 0.5, 2.0]),
        Point3D([-0.5, -0.5, 3.0]),
        Point3D([0.5, -0.5, 3.0]),
        Point3D([-0.5, 0.5, 3.0]),
        Point3D([0.5, 0.5, 3.0]),
    ]

    translated_vertices = []
    for edge in box_body.edges:
        translated_vertices.extend([edge.start, edge.end])

    # Check that the vertices have been translated
    assert np.isin(expected_vertices, translated_vertices).all()


def test_move_rotate(modeler: Modeler):
    design = modeler.create_design("move_rotate_box")
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)

    # Create a named selection of 2 faces
    ns = design.create_named_selection("ns1", bodies=[body])
    assert len(ns.bodies) == 1

    # Verify the original vertices
    expected_vertices = [
        Point3D([-1.0, -1.0, 0.0]),
        Point3D([1.0, -1.0, 0.0]),
        Point3D([-1.0, 1.0, 0.0]),
        Point3D([1.0, 1.0, 0.0]),
        Point3D([-1.0, -1.0, 2.0]),
        Point3D([1.0, -1.0, 2.0]),
        Point3D([-1.0, 1.0, 2.0]),
        Point3D([1.0, 1.0, 2.0]),
    ]

    original_vertices = []
    for edge in body.edges:
        original_vertices.extend([edge.start, edge.end])

    assert np.isin(expected_vertices, original_vertices).all()

    # Rotate the named selection
    success = modeler.geometry_commands.move_rotate(
        ns, Line([0, 1, 2], [1, 0, 0]), Angle(np.pi / 2, UNITS.rad)
    )
    assert success

    # Verify the rotation
    expected_vertices = [
        Point3D([-1.0, 1.0, 0.0]),
        Point3D([1.0, 1.0, 0.0]),
        Point3D([-1.0, 1.0, 2.0]),
        Point3D([1.0, 1.0, 2.0]),
        Point3D([-1.0, 3.0, 0.0]),
        Point3D([1.0, 3.0, 0.0]),
        Point3D([-1.0, 3.0, 2.0]),
        Point3D([1.0, 3.0, 2.0]),
    ]

    rotated_vertices = []
    for edge in body.edges:
        rotated_vertices.extend([edge.start, edge.end])

    # Check that the faces have been rotated
    assert np.isin(expected_vertices, rotated_vertices).all()


def test_offset_face_set_radius(modeler: Modeler):
    """Test offsetting a face with a set radius"""
    design = modeler.create_design("offset_face_set_radius")
    box = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)
    assert len(box.faces) == 6
    assert box.volume.m == pytest.approx(Quantity(8, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # Add a hole to a box
    hole = design.extrude_sketch("hole", Sketch().circle(Point2D([0, 0]), 0.5), 2)
    box.subtract(hole)
    assert box.volume.m == pytest.approx(Quantity(6.4292, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # Change radius of hole
    success = modeler.geometry_commands.offset_faces_set_radius(box.faces[6], 0.25)
    assert success

    assert box.volume.m == pytest.approx(Quantity(7.6073, UNITS.m**3).m, rel=1e-6, abs=1e-8)


def test_move_imprint_edges(modeler: Modeler):
    """Test moving imprint edges."""
    design = modeler.create_design("move_imprint_edges")
    box = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)

    # Create a cylinder cutting through the box
    cylinder = design.extrude_sketch("cylinder", Sketch().circle(Point2D([0, 0]), 0.5), 2)

    # Imprint the top edge of the cylindrical hole
    edges = cylinder.faces[1].edges
    trimmed_curves = [edges[0].shape]
    new_edges, new_faces = box.imprint_curves(faces=[box.faces[1]], trimmed_curves=trimmed_curves)

    assert len(new_edges) == 1
    assert len(new_faces) == 1

    # Move the imprinted edge to create new face and edge
    modeler.geometry_commands.move_imprint_edges([edges[0]], UNITVECTOR3D_Y, 0.1)

    # Verify the new edges and faces
    assert len(box.edges) == 13
    assert len(box.faces) == 7


def test_offset_edges(modeler: Modeler):
    """Test offsetting edges of a surface body."""
    design = modeler.create_design("offset_edges")

    # Create rectangular surface
    sketch = Sketch().box(Point2D([0, 0]), 2, 2)
    surface = design.create_surface("surface", sketch)

    assert (
        modeler.measurement_tools.min_distance_between_objects(
            surface.edges[0], surface.edges[2]
        ).distance.value.m
        == 2
    )
    assert len(surface.faces) == 1
    assert len(surface.edges) == 4

    # Offset the imprinted edge to create new face and edge
    modeler.geometry_commands.offset_edges([surface.edges[0], surface.edges[2]], 5)

    # Verify the new edges and faces
    assert (
        modeler.measurement_tools.min_distance_between_objects(
            surface.edges[0], surface.edges[2]
        ).distance.value.m
        == 12
    )
    assert len(surface.faces) == 1
    assert len(surface.edges) == 4


def test_draft_faces(modeler: Modeler):
    """Test drafting faces."""
    design = modeler.create_design("draft_faces")
    box = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)

    assert box.faces[2].area.m == pytest.approx(Quantity(4, UNITS.m**2).m, rel=1e-6, abs=1e-8)

    # Create a face to draft
    faces = box.faces[2:]
    ref_faces = [box.faces[1]]

    # Draft the face
    drafted_faces = modeler.geometry_commands.draft_faces(
        faces, ref_faces, DraftSide.NO_SPLIT, Angle(10, UNITS.deg), ExtrudeType.ADD
    )

    assert len(drafted_faces) == 0
    assert box.faces[2].area.m == pytest.approx(
        Quantity(4.777895, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )


def test_thicken_faces(modeler: Modeler):
    """Test thickening faces."""
    design = modeler.create_design("thicken_faces")
    box = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)

    assert len(box.faces) == 6
    assert box.volume.m == pytest.approx(Quantity(8, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # Thicken the top face
    success = modeler.geometry_commands.thicken_faces(
        [box.faces[1]], UNITVECTOR3D_Z, 0.1, ExtrudeType.ADD, False, False
    )
    assert success

    assert box.volume.m == pytest.approx(Quantity(8.4, UNITS.m**3).m, rel=1e-6, abs=1e-8)


def test_thicken_surface_body(modeler: Modeler):
    """Test thickening a surface body."""
    design = modeler.create_design("thicken_surface_body")

    # Create rectangular surface
    sketch = Sketch().box(Point2D([0, 0]), 2, 2)
    surface = design.create_surface("surface", sketch)

    assert len(surface.faces) == 1
    assert len(surface.edges) == 4
    assert surface.is_surface

    # Thicken the surface body
    success = modeler.geometry_commands.thicken_faces(
        [surface.faces[0]], UNITVECTOR3D_Z, 0.1, ExtrudeType.ADD, False, False
    )
    assert success

    assert len(design.bodies) == 1
    assert design.bodies[0].volume.m == pytest.approx(
        Quantity(0.4, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )


def test_failures_to_extrude(modeler: Modeler):
    """Add test that covers code for failing to extrude in different ways."""
    # First need to create surface to extrude from
    sketch = Sketch()
    p1 = Point2D([0, 0])
    p2 = Point2D([10, 0])
    p3 = Point2D([10, 5])
    p4 = Point2D([0, 5])
    sketch.segment(p1, p2)
    sketch.segment(p2, p3)
    sketch.segment(p3, p4)
    sketch.segment(p4, p1)
    design = modeler.create_design("SimpleFaceDesign")
    surface = design.create_surface("SimpleFace", sketch)
    grpc_client = modeler.client
    geometry_commands = GeometryCommands(grpc_client, _internal_use=True)

    # Failing to extrude single face
    results = geometry_commands.extrude_faces(
        faces=surface.faces[0],
        distance=10,
        direction=UnitVector3D([1, 0, 0]),
        extrude_type=ExtrudeType.ADD,
        pull_symmetric=False,
    )
    assert results == []
    # Then adding a check to ensure no new faces were made
    assert len(design.bodies[0].faces) == 1
    # For the rest of the failures, we need a 2nd surface so here is creating the circle
    circle_sketch = Sketch()
    circle_sketch.circle(Point2D([20, 20]), 5.0)
    circle_surface = design.create_surface("CircleSurface", circle_sketch)
    # The square surface needs to be rotate to make some of the extrustion not valid
    surface.rotate(Point3D([0, 0, 0]), UnitVector3D([0, 1, 0]), np.pi / 2)
    # Failing to extrude edge
    results = geometry_commands.extrude_edges(
        edges=circle_surface.edges[0],
        distance=10,
        from_face=surface.faces[0],
    )
    assert results == []
    assert len(design.bodies[0].faces) == 1
    assert len(design.bodies[1].faces) == 1
    # Failing to extrude edge up to
    results = geometry_commands.extrude_edges_up_to(
        circle_surface.edges[0],
        surface.faces[0],
        Point3D([0, 0, 0]),
        UnitVector3D([1, 0, 0]),
    )
    assert results == []
    assert len(design.bodies[0].faces) == 1
    assert len(design.bodies[1].faces) == 1
    # Failing to revolve face
    results = geometry_commands.revolve_faces(
        selection=circle_surface.faces[0],
        axis=Line([0, 0, 1], [0, 0, 1]),
        angle=-np.pi * 3 / 2,
    )
    assert results == []
    assert len(design.bodies[0].faces) == 1
    assert len(design.bodies[1].faces) == 1
    # Failing to revolve face up to
    results = modeler.geometry_commands.revolve_faces_up_to(
        circle_surface.faces[0],
        surface.faces[0],
        Line([0.5, 0.5, 0], [0, 0, 1]),
        UnitVector3D([1, 0, 0]),
        ExtrudeType.FORCE_ADD,
    )
    assert results == []
    assert len(design.bodies[0].faces) == 1
    assert len(design.bodies[1].faces) == 1
    # Failing to revolve face by helix
    # Commenting out test due to it causing a segfault inside the container
    # modeler.geometry_commands.revolve_faces_by_helix(
    #     circle_surface.faces[0],
    #     Line([0.5, 0.5, 0], [0, 0, 1]),
    #     UnitVector3D([1, 0, 0]),
    #     5,
    #     1,
    #     np.pi / 4,
    #     True,
    #     True,
    # )
    # assert len(design.bodies[0].faces) == 1
    # # Only in 252 does the revolve not fail. This is reproducible in 252 SpaceClaim and latest
    # if modeler._grpc_client.backend_version == "25.2.0":
    #     assert len(design.bodies[1].faces) == 4
    # else:
    #     assert len(design.bodies[1].faces) == 1


def test_offset_faces(modeler: Modeler):
    """Test offsetting faces."""
    design = modeler.create_design("offset_faces")
    box = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)

    assert len(box.faces) == 6
    assert box.volume.m == pytest.approx(Quantity(8, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # Offset the top face
    modeler.geometry_commands.offset_faces([box.faces[1]], 0.1, UNITVECTOR3D_Z, ExtrudeType.ADD)

    assert box.volume.m == pytest.approx(Quantity(8.4, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # Test with two boxes
    box2 = design.extrude_sketch("box2", Sketch().box(Point2D([3, 0]), 2, 2), 2)

    assert len(box2.faces) == 6
    assert box2.volume.m == pytest.approx(Quantity(8, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # Offset the top face of both boxes
    modeler.geometry_commands.offset_faces(
        [box.faces[1], box2.faces[1]], 0.1, UNITVECTOR3D_Z, ExtrudeType.ADD
    )

    assert box.volume.m == pytest.approx(Quantity(8.8, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert box2.volume.m == pytest.approx(Quantity(8.4, UNITS.m**3).m, rel=1e-6, abs=1e-8)


def test_revolve_edges(modeler: Modeler):
    """Test revolving edges."""
    design = modeler.create_design("revolve_edges")
    box = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)

    assert len(box.faces) == 6
    assert box.volume.m == pytest.approx(Quantity(8, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # Revolve one edge of the box
    edge = box.faces[2].edges[0]
    axis = Line(Point3D([0, 0, 0], UNITS.m), UNITVECTOR3D_Z)
    modeler.geometry_commands.revolve_edges(edge, axis, Angle(np.pi / 2, UNITS.rad), True)

    assert len(design.bodies) == 2
    assert design.bodies[0].volume.m == pytest.approx(Quantity(8, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert design.bodies[1].is_surface
    assert design.bodies[1].faces[0].area.m == pytest.approx(
        Quantity(8.88576587632, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )


def test_intersect_curve_and_surface(modeler: Modeler):
    """Test intersection of curves and surfaces."""
    curve = Line(Point3D([0, 0, 0]), [1, 0, 0])
    surface = Sphere([0, 0, 0], 1)

    points = modeler.geometry_commands.intersect_curve_and_surface(curve, surface)

    assert len(points) == 2
    assert np.allclose(points[0], Point3D([-1, 0, 0]))
    assert np.allclose(points[1], Point3D([1, 0, 0]))