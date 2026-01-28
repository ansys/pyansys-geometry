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
"""Testing of rayfire tools."""

import pytest

from ansys.geometry.core.math import Point2D, Point3D, UnitVector3D
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.sketch import Sketch


@pytest.mark.skip(reason="Currently failing due to backend issue with rayfire operation")
def test_rayfire_simple_case(modeler: Modeler):
    """Test the rayfire operation with a simple case."""
    design = modeler.create_design("rayfire_simple_case")

    box = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)
    face = box.faces[1]
    direction = UnitVector3D([1, 0, 0])
    points = [Point3D([-2, 0, 1])]

    result = modeler.rayfire_tools.rayfire(
        body=box, faces=[face], direction=direction, points=points, max_distance=10.0
    )

    assert result is not None
    assert len(result) == 2
    
    # TODO: Issue #2037 
    # test the actual intersection points returned by the rayfire operation


def test_rayfire_faces(modeler: Modeler):
    """Test the rayfire faces operation."""
    design = modeler.create_design("rayfire_simple_case")

    box = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)
    face = box.faces[1]
    points = [Point3D([-2, 0, 1])]

    result = modeler.rayfire_tools.rayfire_faces(
        body=box, faces=[face], points=points,
    )

    assert result is not None
    assert len(result) == 2


def test_rayfire_ordered(modeler: Modeler):
    """Test the rayfire ordered operation."""
    design = modeler.create_design("rayfire_simple_case")

    box = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)
    face = box.faces[1]
    direction = UnitVector3D([1, 0, 0])
    points = [Point3D([-2, 0, 1])]

    result = modeler.rayfire_tools.rayfire_ordered(
        body=box, faces=[face], direction=direction, ray_radius=2, points=points, max_distance=10.0
    )

    assert result is not None
    assert len(result) == 2


def test_rayfire_ordered_uv(modeler: Modeler):
    """Test the rayfire ordered uv operation."""
    design = modeler.create_design("rayfire_simple_case")

    box = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)
    face = box.faces[1]
    direction = UnitVector3D([1, 0, 0])
    points = [Point3D([-2, 0, 1])]

    result = modeler.rayfire_tools.rayfire_ordered_uv(
        body=box, faces=[face], direction=direction, ray_radius=2, points=points, max_distance=10.0
    )

    assert result is not None
    assert len(result) == 2