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
"""Testing module for generally raised issues"""

from pathlib import Path

import numpy as np

from ansys.geometry.core.math import (
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    UNITVECTOR3D_Z,
    Plane,
    Point2D,
    Point3D,
)
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Angle, Distance
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.sketch import Sketch

from .conftest import FILES_DIR, skip_if_core_service


def test_issue_834_design_import_with_surfaces(modeler: Modeler):
    """Import a Design which is expected to contain surfaces.

    For more info see
    https://github.com/ansys/pyansys-geometry/issues/834
    """
    # TODO: to be reactivated
    # https://github.com/ansys/pyansys-geometry/issues/799
    skip_if_core_service(modeler, test_issue_834_design_import_with_surfaces.__name__, "open_file")

    # Open the design
    design = modeler.open_file(Path(FILES_DIR, "DuplicateFacesDesignBefore.scdocx"))

    # Check that there are two bodies
    assert len(design.bodies) == 2

    # Check some basic properties - whether they are surfaces or not!
    assert design.bodies[0].name == "BoxBody"
    assert design.bodies[0].is_surface is False
    assert design.bodies[1].name == "DuplicatesSurface"
    assert design.bodies[1].is_surface is True


def test_issue_1195_sketch_pyconus2024_voglster():
    """Test sketching unexpected behavior observed in PyConUS 2024 by
    @voglster.

    For more info see
    https://github.com/ansys/pyansys-geometry/issues/1195
    """
    sketch = Sketch()
    p_start, p_end, p_center = Point2D([1, 0]), Point2D([-1, 0]), Point2D([0, 0])
    sketch.arc(p_start, p_end, p_center)

    # Check that the arc is correctly defined
    assert sketch.edges[0].start == p_start
    assert sketch.edges[0].end == p_end
    assert sketch.edges[0].center == p_center


def test_issue_1184_sphere_creation_crashes(modeler: Modeler):
    """Test that creating a sphere after a box does not crash the program.

    For more info see
    https://github.com/ansys/pyansys-geometry/issues/1184
    """
    # Skip this test on CoreService since it is not implemented yet
    skip_if_core_service(modeler, test_issue_1184_sphere_creation_crashes.__name__, "create_sphere")

    design = modeler.create_design("SphereCreationIssue")

    plane = Plane(
        Point3D([1 / 2, 1 / 2, 0.0]),
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )
    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0]), width=1, height=1)

    box = design.extrude_sketch("Matrix", box_plane, 1)
    sphere_body = design.create_sphere("particle", Point3D([0.0, 0.0, 0.0]), Distance(0.5))

    assert len(design.bodies) == 2
    assert design.bodies[0].name == box.name
    assert design.bodies[1].name == sphere_body.name


def test_issue_1304_arc_sketch_creation():
    """Test that creating an arc sketch does not crash the program.

    For more info see
    https://github.com/ansys/pyansys-geometry/issues/1304
    """

    try:
        # Change the default units to mm
        DEFAULT_UNITS.LENGTH = UNITS.mm

        # Draw the sketch
        sketch = Sketch()
        p_start, p_end, p_radius = Point2D([0, 0]), Point2D([4.7, 4.7]), Distance(4.7)
        sketch.arc_from_start_end_and_radius(
            start=p_start,
            end=p_end,
            radius=p_radius,
            clockwise=False,
        )

        # Perform some assertions
        assert len(sketch.edges) == 1
        assert sketch.edges[0].start == p_start
        assert sketch.edges[0].end == p_end
        # 3/4 * 2piR --> piR 3 / 2 (3/4 of the circumference)
        assert np.isclose(sketch.edges[0].length, (np.pi * p_radius.value * 1.5))
    finally:
        # Reverse the default units to meter
        DEFAULT_UNITS.LENGTH = UNITS.meter


def test_issue_1192_temp_body_on_empty_intersect(modeler: Modeler):
    """Test demonstrating the issue when intersecting two bodies that do not intersect
    and the empty temporal body that gets created."""
    # When attempting to intersect two bodies that do not intersect, no body should be
    # created. However, in the past, a temporary body was created and added to the
    # component. This test checks if this issue has been resolved.
    design = modeler.create_design("temp-body-intersect-issue")

    # Create two bodies that do not intersect
    plane = Plane(
        Point3D([1 / 2, 1 / 2, 0.0]),
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )
    matrix_plane = Sketch(plane)
    matrix_plane.box(Point2D([0.0, 0.0]), width=1, height=1)
    matrix = design.extrude_sketch("Matrix", matrix_plane, 1)

    p = Point3D([1.0, 1.0, 1.5])
    plane = Plane(p, UNITVECTOR3D_X, UNITVECTOR3D_Y)
    sketch_fibres = Sketch(plane)
    sketch_fibres.circle(Point2D([0.0, 0.0]), radius=0.5)
    fibre = design.extrude_sketch("fibre", sketch_fibres, 1)

    # Attempt intersection - which fails and thus deletes copy
    matrix_copy = matrix.copy(design)
    try:
        fibre.intersect(matrix_copy)
    except Exception:
        design.delete_body(matrix_copy)

    # No intersection took place... so no body should be created
    # Let's read the design and check that only the two bodies are present
    read_design = modeler.read_existing_design()

    # Verify the design
    assert len(read_design.bodies) == 2
    assert len(read_design.bodies) == 2
    assert len(read_design.bodies[0].faces) == 6
    assert len(read_design.bodies[1].faces) == 3
    assert read_design.bodies[0].name == "Matrix"
    assert read_design.bodies[1].name == "fibre"
    assert len(read_design.components) == 0


def test_issue_1309_revolve_operation_with_coincident_origins(modeler: Modeler):
    """Test that revolving a sketch with coincident origins (sketch and rotation origin)
    does not crash the program.

    For more info see
    https://github.com/ansys/pyansys-geometry/issues/1309
    """
    # Sketch Plane
    sketch_plane = Plane(
        origin=Point3D([0, 0, 5]), direction_x=UNITVECTOR3D_X, direction_y=UNITVECTOR3D_Z
    )

    # Create Base
    sketch = Sketch(sketch_plane)

    (
        sketch.arc(
            start=Point2D([0, 0]),
            end=Point2D([4.7, 4.7]),
            center=Point2D([0, 4.7]),
            clockwise=False,
        )
        .segment_to_point(Point2D([4.7, 12]))
        .segment_to_point(Point2D([-25.3, 12]))
        .segment_to_point(Point2D([-25.3, 0]))
        .segment_to_point(Point2D([0, 0]))
    )

    # Create Component (Revolve sketch)
    design = modeler.create_design("cylinder")
    component = design.add_component("cylinder_toroid")
    revolved_body = component.revolve_sketch(
        "toroid",
        sketch=sketch,
        axis=UNITVECTOR3D_X,
        angle=Angle(360, UNITS.degrees),
        rotation_origin=Point3D([-10.3, 0, 0]),
    )

    assert revolved_body.name == "toroid"


def test_issue_1724_intersect_failures(modeler: Modeler):
    """Test that intersecting two bodies that overlap does not crash the program.

    For more info see
    https://github.com/ansys/pyansys-geometry/issues/1724
    """
    wx = 10
    wy = 10
    wz = 2
    radius = 1
    unit = DEFAULT_UNITS.LENGTH

    design = modeler.create_design("Test")

    start_at = Point3D([wx / 2, wy / 2, 0.0], unit=unit)

    plane = Plane(
        start_at,
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )
    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0], unit=unit), width=wx, height=wy)

    box = design.extrude_sketch("box", box_plane, wz)

    point = Point3D([wx / 2, wx / 2, 0.0], unit=unit)
    plane = Plane(point, UNITVECTOR3D_X, UNITVECTOR3D_Y)
    sketch_cylinder = Sketch(plane)
    sketch_cylinder.circle(Point2D([0.0, 0.0], unit=unit), radius=radius)
    cylinder = design.extrude_sketch("cylinder", sketch_cylinder, wz - 0.1)

    # Request the intersection
    cylinder.intersect(box)

    # Only the cylinder should be present
    assert len(design.bodies) == 1
    assert design.bodies[0].name == "cylinder"

    # Verify that the volume of the cylinder is the same (the intersect is the same as the cylinder)
    assert np.isclose(design.bodies[0].volume.m, np.pi * radius**2 * (wz - 0.1))
