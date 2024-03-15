# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

import numpy as np
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.shapes.curves.circle import Circle
from ansys.geometry.core.shapes.curves.ellipse import Ellipse
from ansys.geometry.core.shapes.parameterization import Interval
from ansys.geometry.core.sketch.sketch import Sketch


def test_sweep_sketch(modeler: Modeler):
    """Test the sweep_sketch method by creating a revolving a circle profile around an
    circular axis to make a donut."""

    design_sketch = modeler.create_design("donut")

    path_radius = 5
    profile_radius = 2

    # create a circle on the XZ-plane centered at (5, 0, 0) with radius 2
    profile = Sketch(plane=Plane(direction_x=[1, 0, 0], direction_y=[0, 0, 1])).circle(
        Point2D([path_radius, 0]), profile_radius
    )

    # create a circle on the XY-plane centered at (0, 0, 0) with radius 5
    path = [Circle(Point3D([0, 0, 0]), path_radius).trim(Interval(0, 2 * np.pi))]

    body = design_sketch.sweep_sketch("donutsweep", profile, path)

    assert body.is_surface == True

    # check edges
    assert len(body.edges) == 0

    # check faces
    assert len(body.faces) == 1

    # check area of face
    # compute expected area (torus with r < R) where r is inner radius and R is outer radius
    R = path_radius + profile_radius
    r = path_radius - profile_radius
    expected_face_area = (np.pi**2) * (R**2 - r**2)
    assert body.faces[0].area.m == pytest.approx(expected_face_area)

    # check volume of face
    # expected is 0 since it has 0 thickness
    assert body.volume.m == 0


def test_sweep_chain(modeler: Modeler):
    """Test the sweep_chain method by revolving a semi-elliptical profile around an
    circular axis to make a bowl."""
    design_chain = modeler.create_design("bowl")

    radius = 10

    # create quarter-ellipse profile with major radius = 10, minor radius = 5
    profile = [
        Ellipse(
            Point3D([0, 0, radius / 2]), radius, radius / 2, reference=[1, 0, 0], axis=[0, 1, 0]
        ).trim(Interval(0, np.pi / 2))
    ]

    # create circle on the plane parallel to the XY-plane but moved up by 5 units with radius 10
    path = [Circle(Point3D([0, 0, radius / 2]), radius).trim(Interval(0, 2 * np.pi))]

    # create the bowl body
    body = design_chain.sweep_chain("bowlsweep", path, profile)

    assert body.is_surface == False

    # check edges
    assert len(body.edges) == 1

    # check length of edge
    # compute expected circumference (circle with radius 10)
    expected_edge_cirumference = 2 * np.pi * 10
    assert body.edges[0].length.m == pytest.approx(expected_edge_cirumference)

    # check faces
    assert len(body.faces) == 1

    # check area of face
    # compute expected area (half a spheroid)
    minor_rad = radius / 2
    e_squared = 1 - (minor_rad**2 / radius**2)
    e = np.sqrt(e_squared)
    expected_face_area = (
        2 * np.pi * radius**2 + (minor_rad**2 / e) * np.pi * np.log((1 + e) / (1 - e))
    ) / 2
    assert body.faces[0].area.m == pytest.approx(expected_face_area)

    # check volume of face
    # expected is 0 since it's not a closed surface
    assert body.volume.m == 0
