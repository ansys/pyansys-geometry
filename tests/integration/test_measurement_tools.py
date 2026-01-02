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
""" "Testing of measurement tools."""

import numpy as np

from ansys.geometry.core.math import Point2D, UnitVector3D
from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.sketch.sketch import Sketch
from ansys.geometry.core.tools.measurement_tools import Gap

from .conftest import FILES_DIR


def test_distance_property(modeler: Modeler):
    """Test if the gap object is being constructed properly."""
    gap = Gap(distance=Distance(10))
    assert gap.distance._value == 10.0


def test_min_distance_between_bodies(modeler: Modeler):
    """Test if split edge problem areas are detectable."""
    design = modeler.open_file(FILES_DIR / "MixingTank.scdocx")
    gap = modeler.measurement_tools.min_distance_between_objects(design.bodies[2], design.bodies[1])
    assert abs(gap.distance._value - 0.0892) <= 0.01


def test_min_distance_between_faces(modeler: Modeler):
    """Test the distance between two faces."""
    design = modeler.create_design("closest_face_separation")

    body1 = design.extrude_sketch("box1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    body2 = design.extrude_sketch("box2", Sketch().box(Point2D([2, 0]), 1, 1), 1)

    gap = modeler.measurement_tools.min_distance_between_objects(body1.faces[0], body2.faces[0])
    assert np.isclose(1.0, gap.distance._value)

    body2.translate(UnitVector3D([0, 0, 1]), 1)
    gap = modeler.measurement_tools.min_distance_between_objects(body1.faces[0], body2.faces[0])
    assert np.isclose(1.41421356237, gap.distance._value)


def test_min_distance_between_edges(modeler: Modeler):
    """Test the distance between two edges."""
    design = modeler.create_design("closest_edge_separation")

    body1 = design.extrude_sketch("box1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    body2 = design.extrude_sketch("box2", Sketch().box(Point2D([2, 0]), 1, 1), 1)

    gap = modeler.measurement_tools.min_distance_between_objects(body1.edges[0], body2.edges[0])
    assert np.isclose(1.0, gap.distance._value)

    body2.translate(UnitVector3D([0, 0, 1]), 1)
    gap = modeler.measurement_tools.min_distance_between_objects(body1.edges[0], body2.edges[0])
    assert np.isclose(1.41421356237, gap.distance._value)


def test_min_distance_between_face_and_body(modeler: Modeler):
    """Test the distance between a face and a body."""
    design = modeler.create_design("closest_face_body_separation")

    body1 = design.extrude_sketch("box1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    body2 = design.extrude_sketch("box2", Sketch().box(Point2D([2, 0]), 1, 1), 1)

    gap = modeler.measurement_tools.min_distance_between_objects(body1.faces[0], body2)
    assert np.isclose(1.0, gap.distance._value)

    body2.translate(UnitVector3D([0, 0, 1]), 1)
    gap = modeler.measurement_tools.min_distance_between_objects(body1.faces[0], body2)
    assert np.isclose(1.41421356237, gap.distance._value)
