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
import pytest

from ansys.geometry.core.designer.geometry_commands import GeometryCommands
from ansys.geometry.core.errors import GeometryRuntimeError
from ansys.geometry.core.math import (
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    UNITVECTOR3D_Z,
    Plane,
    Point2D,
    Point3D,
)
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Angle, Distance
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.sketch import Sketch
from ansys.geometry.core.sketch.arc import Arc
from ansys.geometry.core.tools import (
    MeasurementTools,
    PrepareTools,
    RepairTools,
    UnsupportedCommands,
)

from .conftest import FILES_DIR


def test_issue_834_design_import_with_surfaces(modeler: Modeler):
    """Import a Design which is expected to contain surfaces.

    For more info see
    https://github.com/ansys/pyansys-geometry/issues/834
    """
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


def test_issue_1807_translate_sketch_non_default_units():
    """Test that translating a sketch with non-default units is handled properly.

    For more info see
    https://github.com/ansys/pyansys-geometry/issues/1807
    """
    try:
        # Set the default units to mm
        DEFAULT_UNITS.LENGTH = UNITS.mm

        # Draw a box sketch
        sketch = Sketch()
        sketch.box(Point2D([0, 0]), 10, 10)

        # Verify the sketch plane origin
        assert sketch.plane.origin == Point3D([0, 0, 0])

        # Translate the sketch
        sketch.translate_sketch_plane_by_distance(UnitVector3D([0, 0, 1]), Distance(10, UNITS.mm))

        # Verify the new sketch plane origin
        assert sketch.plane.origin == Point3D([0, 0, 10], unit=UNITS.mm)

    finally:
        # Reset the default units to meters
        DEFAULT_UNITS.LENGTH = UNITS.meter


def test_issue_1813_edge_start_end_non_default_units(modeler: Modeler):
    """Test that creating an edge with non-default units is handled properly.

    Notes
    -----
    Apparently there are some issues on the start and end locations when
    using non-default units. This test is to verify that the issue has been
    resolved.

    For more info see
    https://github.com/ansys/pyansys-geometry/issues/1813
    """
    try:
        # Create initial design and set default units to millimeters
        design = modeler.create_design("MillimetersEdgeIssue")
        DEFAULT_UNITS.LENGTH = UNITS.mm

        # Sketch and extrude box
        box = design.extrude_sketch("box", Sketch().box(Point2D([0.5, 0.5]), 1, 1), 1)

        # Perform some assertions like...
        # 1) The edge lengths should be 1 mm
        for face in box.faces:
            for edge in face.edges:
                assert np.isclose(edge.length, 1 * UNITS.mm)
                length_vec = edge.start - edge.end
                assert np.isclose(np.linalg.norm(length_vec) * length_vec.base_unit, 1 * UNITS.mm)

        # 2) Verify the box volume
        assert np.isclose(box.volume, 1 * UNITS.mm * UNITS.mm * UNITS.mm)

    finally:
        # Reset the default units to meters
        DEFAULT_UNITS.LENGTH = UNITS.meter


def test_issue_2184_prevent_raw_instantiation_of_tools_and_commands():
    """Test that raw instantiation of tools and commands is prevented.

    For more info see
    https://github.com/ansys/pyansys-geometry/issues/2184
    """
    # Test UnsupportedCommands
    with pytest.raises(
        GeometryRuntimeError, match="UnsupportedCommands should not be instantiated directly"
    ):
        UnsupportedCommands(None, None)

    # Test RepairTools
    with pytest.raises(
        GeometryRuntimeError, match="RepairTools should not be instantiated directly"
    ):
        RepairTools(None, None)

    # Test PrepareTools
    with pytest.raises(
        GeometryRuntimeError, match="PrepareTools should not be instantiated directly"
    ):
        PrepareTools(None)

    # Test MeasurementTools
    with pytest.raises(
        GeometryRuntimeError, match="MeasurementTools should not be instantiated directly"
    ):
        MeasurementTools(None)

    # Test GeometryCommands
    with pytest.raises(
        GeometryRuntimeError, match="GeometryCommands should not be instantiated directly"
    ):
        GeometryCommands(None)


def test_issue_2074_rounding_math_errors():
    """Test that rounding errors in math operations do not cause issues.

    For more info see
    https://github.com/ansys/pyansys-geometry/issues/2074
    """
    sketch1 = Sketch()
    width = 7
    start = Point2D([width / 2, 0], UNITS.mm)
    end = Point2D([-width / 2, 0], UNITS.mm)
    radius = width / 2 * UNITS.mm
    sketch1.arc_from_start_end_and_radius(start, end, radius)

    arc: Arc = sketch1.edges[-1]

    assert arc.center is not None
    assert np.allclose(arc.center, Point2D([0, 0], UNITS.mm))
    assert np.isclose(arc.radius.to_base_units().m, radius.to_base_units().m)
    assert arc.start == start
    assert arc.end == end


def test_issue_2251_double_import_crash(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test that importing a file twice does not crash the program.

    For more info see
    https://github.com/ansys/pyansys-geometry/issues/2251
    """
    # Open the design file
    design = modeler.open_file(Path(FILES_DIR, "pipe_split_small_edge.dsco"))

    # Export to stride
    location = tmp_path_factory.mktemp("test_issue_2251_loc1")
    file_location = location / f"{design.name}.stride"
    design.export_to_stride(location)
    assert file_location.exists()

    # Open the design file
    design = modeler.open_file(Path(FILES_DIR, "pipe_split_small_edge.dsco"))

    # Export to stride
    location = tmp_path_factory.mktemp("test_issue_2251_loc2")
    file_location = location / f"{design.name}.stride"
    design.export_to_stride(location)  # --> crash
    assert file_location.exists()
