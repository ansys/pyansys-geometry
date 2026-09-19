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

"""Testing of rayfire tools."""

import pytest

from ansys.geometry.core.math import Point2D, Point3D
from ansys.geometry.core.math.constants import UNITVECTOR3D_Z
from ansys.geometry.core.misc.options import RayfireOptions
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.sketch import Sketch


def test_rayfire_constructor_error_raised(modeler: Modeler):
    """Test that the RayfireTools constructor raises an error when instantiated directly."""
    from ansys.geometry.core.tools.rayfire_tools import GeometryRuntimeError, RayfireTools

    with pytest.raises(GeometryRuntimeError, match="RayfireTools should not be instantiated"):
        RayfireTools(grpc_client=modeler._grpc_client, modeler=modeler)


def test_rayfire_simple_case(modeler: Modeler):
    """Test the rayfire operation with a simple case."""
    design = modeler.create_design("rayfire_simple_case")

    # Create a box from (0, 0, 0) to (1, 1, 1) and a point centered below it
    box = design.extrude_sketch("box", Sketch().box(Point2D([0.5, 0.5]), 1, 1), 1)
    points = [Point3D([0.5, 0.5, -1])]

    result = modeler.rayfire_tools.rayfire(box, [], UNITVECTOR3D_Z, points, 2e-8)

    # Take the distinct points from the result
    distinct_points = []
    for impact in result:
        if impact.point not in distinct_points:
            distinct_points.append(impact.point)
    assert len(distinct_points) == 2


def test_rayfire_faces(modeler: Modeler):
    """Test the rayfire faces operation with a simple case."""
    design = modeler.create_design("rayfire_faces_simple_case")

    # Create a box from (0, 0, 0) to (1, 1, 1) and a point centered below it
    box = design.extrude_sketch("box", Sketch().box(Point2D([0.5, 0.5]), 1, 1), 1)
    points = [Point3D([0.5, 0.5, -1])]
    options = RayfireOptions(
        radius=2e-8,
        direction=UNITVECTOR3D_Z,
        max_distance=10,
        min_distance=0,
        tight_tolerance=True,
        pick_back_faces=True,
        max_hits=16,
        request_params=True,
        request_secondary=True,
    )

    result = modeler.rayfire_tools.rayfire_faces(
        body=box, faces=box.faces, points=points, options=options
    )

    assert len(result) == 2
    assert result[0].face_id == box.faces[0].id
    assert result[0].point == Point3D([0.5, 0.5, 0])
    assert result[1].face_id == box.faces[1].id
    assert result[1].point == Point3D([0.5, 0.5, 1])


def test_rayfire_ordered(modeler: Modeler):
    """Test the rayfire ordered operation."""
    design = modeler.create_design("rayfire_simple_case")

    # Create a box from (0, 0, 0) to (1, 1, 1) and a point centered below it
    box = design.extrude_sketch("box", Sketch().box(Point2D([0.5, 0.5]), 1, 1), 1)
    points = [Point3D([0.25, 0.25, -1]), Point3D([0.75, 0.6, -1]), Point3D([5, 5, -1])]

    result = modeler.rayfire_tools.rayfire_ordered(box, box.faces, UNITVECTOR3D_Z, 2e-8, points, 10)
    assert len(result) == 3

    # Check that point 0/1 hits twice and point 2 hits zero times
    assert len(result[0]) == 2
    assert len(result[1]) == 2
    assert len(result[2]) == 0

    # Check that the impacts belong to the box body
    assert result[0][0].body_id == box.id
    assert result[1][0].body_id == box.id


def test_rayfire_ordered_uv(modeler: Modeler):
    """Test the rayfire ordered uv operation."""
    design = modeler.create_design("rayfire_simple_case")

    # Create a box from (0, 0, 0) to (1, 1, 1) and a point centered below it
    box = design.extrude_sketch("box", Sketch().box(Point2D([0.5, 0.5]), 1, 1), 1)
    points = [Point3D([0.25, 0.25, -1]), Point3D([0.75, 0.6, -1]), Point3D([5, 5, -1])]

    result = modeler.rayfire_tools.rayfire_ordered_uv(
        box, box.faces, UNITVECTOR3D_Z, 2e-8, points, 10.0
    )

    # Check that point 0/1 hits twice and point 2 hits zero times
    assert len(result[0]) == 2
    assert len(result[1]) == 2
    assert len(result[2]) == 0

    # Check that the uv impacts are correct
    assert result[0][0].u == 0.25
    assert result[0][0].v == 0.25
    assert result[0][1].u == 0.75
    assert result[0][1].v == 0.6
