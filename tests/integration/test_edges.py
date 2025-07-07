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
"""Test edges."""

import numpy as np

from ansys.geometry.core import Modeler
from ansys.geometry.core.math import Point2D, Vector3D
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.misc.units import UNITS, Quantity
from ansys.geometry.core.sketch import Sketch


def test_edges_startend_prism(modeler: Modeler):
    # init modeler
    design = modeler.create_design("Prism")

    # define body
    body_sketch = Sketch()
    body_sketch.box(Point2D([10, 10], UNITS.m), Quantity(5, UNITS.m), Quantity(3, UNITS.m))
    prism_body = design.extrude_sketch("JustAPrism", body_sketch, Quantity(13, UNITS.m))
    for edge in prism_body.edges:
        vec = Vector3D.from_points(edge.shape.start, edge.shape.end)
        assert vec.magnitude == edge.length.magnitude


def test_edges_startend_cylinder(modeler: Modeler):
    # init modeler
    design = modeler.create_design("cylinder")

    # define body
    cylinder = Sketch()
    cylinder.circle(Point2D([10, 10], UNITS.m), 1.0)
    cylinder_body = design.extrude_sketch("JustACyl", cylinder, Quantity(10, UNITS.m))
    for edge in cylinder_body.edges:
        assert edge.shape.start == edge.shape.end


def test_edges_get_vertices(modeler: Modeler):
    # Create a simple design with a box
    design = modeler.create_design("BoxVertices")
    sketch = Sketch()
    sketch.box(Point2D([0, 0], UNITS.m), Quantity(1, UNITS.m), Quantity(1, UNITS.m))
    body = design.extrude_sketch("BoxBody", sketch, Quantity(1, UNITS.m))

    # Create array of vertices to match with vertices from edges
    body_vertices = []
    for x in [-1, 1]:
        for y in [-1, 1]:
            for z in [0, 1]:
                body_vertices.append(Point3D([x / 2, y / 2, z]))

    # For each edge, get its vertices and check their types and positions
    for edge in body.edges:
        vertices = edge.vertices
        # Should be two vertices per edge for a box
        assert len(vertices) == 2

        # Check the location of each vertex
        for vertex in vertices:
            print(vertex.position)
            assert any(np.allclose(vertex.position, v.position) for v in body_vertices)
