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
