# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.

# Sp4X-License-Identifier: MIT
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
# FITNESS FOR A p1RTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Testing of SpaceClaim Tutorials Examples."""

from pathlib import Path

import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.math import Plane, Point2D, Point3D
from ansys.geometry.core.math.constants import UNITVECTOR3D_Z
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.shapes.curves.line import Line
from ansys.geometry.core.sketch import Sketch

from .conftest import FILES_DIR


def test_robot_example(modeler: Modeler):
    """Test creating robot example from Sp1ceClaim trainings"""
    design = modeler.create_design("Robot")
    sketch = Sketch()

    # Left side geometry
    sketch.segment(Point2D([0, 50], UNITS.mm), Point2D([-40, 50], UNITS.mm))
    sketch.segment(Point2D([0, 0], UNITS.mm), Point2D([-40, 0], UNITS.mm))
    sketch.segment(Point2D([-40, 0], UNITS.mm), Point2D([-40, 50], UNITS.mm))

    # Right side geometry
    sketch.segment(Point2D([0, 50], UNITS.mm), Point2D([40, 50], UNITS.mm))
    sketch.segment(Point2D([0, 0], UNITS.mm), Point2D([40, 0], UNITS.mm))
    sketch.segment(Point2D([40, 0], UNITS.mm), Point2D([40, 50], UNITS.mm))
    # Extrude the sketch
    body = design.extrude_sketch("Extruded Sketch", sketch, Quantity(15, UNITS.mm))
    assert len(body.faces) == 6
    assert len(body.edges) == 12

    circle1 = Sketch()
    circle1.circle(Point2D([40, 50], UNITS.mm), Quantity(12.5, UNITS.mm))
    body1 = design.extrude_sketch("Circle 1", circle1, Quantity(15, UNITS.mm))

    circle2 = Sketch()
    circle2.circle(Point2D([-40, 50], UNITS.mm), Quantity(12.5, UNITS.mm))
    body2 = design.extrude_sketch("Circle 2", circle2, Quantity(15, UNITS.mm))

    body.unite(body1)
    body.unite(body2)
    assert len(body.faces) == 8
    assert len(body.edges) == 18

    # corner inner circle
    inner_circle_one = Sketch()
    inner_circle_two = Sketch()
    inner_circle_one.circle(Point2D([-40, 50], UNITS.mm), Quantity(8.5, UNITS.mm))
    inner_circle_two.circle(Point2D([40, 50], UNITS.mm), Quantity(8.5, UNITS.mm))

    inner_circle_extrude_one = design.extrude_sketch(
        "First Cut Circle", inner_circle_one, Quantity(15, UNITS.mm)
    )
    inner_circle_extrude_two = design.extrude_sketch(
        "Second Cut Circle", inner_circle_two, Quantity(15, UNITS.mm)
    )

    body.subtract(inner_circle_extrude_one)
    body.subtract(inner_circle_extrude_two)

    assert len(body.faces) == 10
    assert len(body.edges) == 22

    sketch_box = Sketch()
    sketch_box.segment(Point2D([40, 15], UNITS.mm), Point2D([35, 15], UNITS.mm))
    sketch_box.segment(Point2D([35, 15], UNITS.mm), Point2D([35, 0], UNITS.mm))
    sketch_box.segment(Point2D([35, 0], UNITS.mm), Point2D([40, 0], UNITS.mm))
    sketch_box.segment(Point2D([40, 0], UNITS.mm), Point2D([40, 15], UNITS.mm))

    sketch_another_box = Sketch()
    sketch_another_box.segment(Point2D([-40, 15], UNITS.mm), Point2D([-35, 15], UNITS.mm))
    sketch_another_box.segment(Point2D([-35, 15], UNITS.mm), Point2D([-35, 0], UNITS.mm))
    sketch_another_box.segment(Point2D([-35, 0], UNITS.mm), Point2D([-40, 0], UNITS.mm))
    sketch_another_box.segment(Point2D([-40, 0], UNITS.mm), Point2D([-40, 15], UNITS.mm))

    left_box = design.extrude_sketch("Left cut", sketch_box, Quantity(15, UNITS.mm))
    right_box = design.extrude_sketch("Right Cut", sketch_another_box, Quantity(15, UNITS.mm))

    body.subtract(left_box)
    body.subtract(right_box)

    assert len(body.faces) == 14
    assert len(body.edges) == 34

    sketch_3 = Sketch()
    sketch_4 = Sketch()

    sketch_3.circle(Point2D([-17, 30], UNITS.mm), Quantity(6, UNITS.mm))  # -40+23, 50-20
    sketch_4.circle(Point2D([17, 30], UNITS.mm), Quantity(6, UNITS.mm))  # 40-23, 50-20

    sketch_3_extrude = design.extrude_sketch("First Eye", sketch_3, Quantity(15, UNITS.mm))
    sketch_4_extrude = design.extrude_sketch("Second Eye", sketch_4, Quantity(15, UNITS.mm))

    body.subtract(sketch_3_extrude)
    body.subtract(sketch_4_extrude)

    assert len(body.faces) == 16
    assert len(body.edges) == 38

    x_offset = (14 / np.tan(np.radians(60))) + 8

    sketch_trapezoid = Sketch()
    sketch_trapezoid.segment(Point2D([-x_offset, 0], UNITS.mm), Point2D([-8, 14], UNITS.mm))
    sketch_trapezoid.segment(Point2D([-8, 14], UNITS.mm), Point2D([-8, 19], UNITS.mm))
    sketch_trapezoid.segment(Point2D([-8, 19], UNITS.mm), Point2D([8, 19], UNITS.mm))

    sketch_trapezoid.segment(Point2D([8, 19], UNITS.mm), Point2D([8, 14], UNITS.mm))
    sketch_trapezoid.segment(Point2D([8, 14], UNITS.mm), Point2D([x_offset, 0], UNITS.mm))

    sketch_trapezoid.segment(Point2D([x_offset, 0], UNITS.mm), Point2D([-x_offset, 0], UNITS.mm))

    body_trapezoid = design.extrude_sketch("Trapezoid", sketch_trapezoid, Quantity(15, UNITS.mm))

    body.subtract(body_trapezoid)

    assert len(body.faces) == 22
    assert len(body.edges) == 56

    origin = Point3D([0, 0, 0])
    p1 = Point3D([1, 0, 0])
    p2 = Point3D([0, 0, 1])
    plane = Plane(origin=origin, direction_x=p1, direction_y=p2)

    sketch_inside_circle = Sketch(plane)
    sketch_inside_circle.circle(Point2D([0, 15 / 2], UNITS.mm), Quantity(3, UNITS.mm))

    inside_circle = design.extrude_sketch(
        "Inside Circle", sketch_inside_circle, Quantity(-50, UNITS.mm)
    )
    body.subtract(inside_circle)

    assert len(body.faces) == 23
    assert len(body.edges) == 58

    plane_new = Plane(
        origin=Point3D([0, 0, 0]), direction_x=Point3D([0, 0, 1]), direction_y=Point3D([0, 1, 0])
    )
    sketch_cut_box = Sketch(plane_new)

    sketch_cut_box.segment(Point2D([4.5, 0], UNITS.mm), Point2D([10.5, 0], UNITS.mm))
    sketch_cut_box.segment(Point2D([10.5, 0], UNITS.mm), Point2D([10.5, 19], UNITS.mm))
    sketch_cut_box.segment(Point2D([10.5, 19], UNITS.mm), Point2D([4.5, 19], UNITS.mm))
    sketch_cut_box.segment(Point2D([4.5, 19], UNITS.mm), Point2D([4.5, 0], UNITS.mm))

    cut_box_one = design.extrude_sketch("Cutter Box", sketch_cut_box, Quantity(40, UNITS.mm))
    cut_box_two = design.extrude_sketch("other side", sketch_cut_box, Quantity(-40, UNITS.mm))

    body.subtract(cut_box_one)
    body.subtract(cut_box_two)

    assert len(body.faces) == 37
    assert len(body.edges) == 100

    edge_ids = [
        12,
        2,
        8,
        0,
        18,
        19,
        23,
        22,
        1,
        30,
        31,
        32,
        36,
        37,
        39,
        43,
        21,
        38,
        42,
        24,
        25,
        4,
        13,
        5,
        9,
        3,
        20,
        35,
        40,
        33,
        34,
        41,
        44,
        28,
        26,
        14,
        16,
        27,
        15,
        29,
        17,
    ]

    body = design.bodies[0]

    for eid in edge_ids:
        modeler.geometry_commands.fillet(body.edges[eid], 0.001)

    assert len(design.bodies[0].faces) == 88
    assert len(design.bodies[0].edges) == 219


def test_combine_example(modeler: Modeler):
    """Test creating combine example from Sp1ceClaim trainings"""

    scfile = Path(FILES_DIR, "Basic_Combine_2014.0.scdocx")
    design = modeler.open_file(file_path=scfile)

    part_one = design.components[0].bodies[0]

    bottom_plate = design.components[1].bodies[0]

    cut_cylin = design.components[2].bodies[0]

    ring = design.components[2].bodies[1]

    stand_plate = design.components[3].bodies[0]

    sleep_plate = design.components[3].bodies[1]

    screws_1 = design.components[4].components[0].bodies[0]

    screws_2 = design.components[4].components[1].bodies[0]

    screws_3 = design.components[4].components[2].bodies[0]

    screws_4 = design.components[4].components[3].bodies[0]

    screws_5 = design.components[4].components[4].bodies[0]

    screws_6 = design.components[4].components[5].bodies[0]

    screws_7 = design.components[4].components[6].bodies[0]

    screws_8 = design.components[4].components[7].bodies[0]

    screws_9 = design.components[4].components[8].bodies[0]

    screws = [
        screws_1,
        screws_2,
        screws_3,
        screws_4,
        screws_5,
        screws_6,
        screws_7,
        screws_8,
        screws_9,
    ]
    for screw in screws:
        bottom_plate.unite(screw)

    design._update_design_inplace()

    assert len(bottom_plate.faces) == 220
    assert len(bottom_plate.edges) == 453
    assert bottom_plate.volume.m == pytest.approx(
        Quantity(1.3864476820718344e-3, UNITS.m**3).m,
        rel=1e-6,
        abs=1e-8,
    )

    bottom_plate.unite(sleep_plate)
    design._update_design_inplace()
    assert len(bottom_plate.faces) == 215
    assert len(bottom_plate.edges) == 443
    assert bottom_plate.volume.m == pytest.approx(
        Quantity(1.4269747187154044e-3, UNITS.m**3).m,
        rel=1e-6,
        abs=1e-8,
    )

    bottom_plate.unite(ring)
    design._update_design_inplace()

    assert len(bottom_plate.faces) == 185
    assert len(bottom_plate.edges) == 378
    assert bottom_plate.volume.m == pytest.approx(
        Quantity(1.5706619652928885e-3, UNITS.m**3).m,
        rel=1e-6,
        abs=1e-8,
    )

    bottom_plate.unite(cut_cylin)
    design._update_design_inplace()

    assert len(bottom_plate.faces) == 187
    assert len(bottom_plate.edges) == 384
    assert bottom_plate.volume.m == pytest.approx(
        Quantity(2.180802392322327e-3, UNITS.m**3).m,
        rel=1e-6,
        abs=1e-8,
    )

    bottom_plate.unite(stand_plate)
    design._update_design_inplace()

    assert len(bottom_plate.faces) == 189
    assert len(bottom_plate.edges) == 390
    assert bottom_plate.volume.m == pytest.approx(
        Quantity(2.2504771923223263e-3, UNITS.m**3).m,
        rel=1e-6,
        abs=1e-8,
    )

    bottom_plate.subtract(part_one)
    design._update_design_inplace()

    assert len(bottom_plate.faces) == 32
    assert len(bottom_plate.edges) == 81

    design.delete_body(part_one)
    design._update_design_inplace()

    assert len(bottom_plate.faces) == 32
    assert len(bottom_plate.edges) == 81
    assert bottom_plate.volume.m == pytest.approx(
        Quantity(1.3915717201112474e-4, UNITS.m**3).m,
        rel=1e-6,
        abs=1e-8,
    )

    solid_one = design.components[1].bodies[0]
    design.delete_body(solid_one)
    design._update_design_inplace()

    assert len(design.components[1].bodies[0].faces) == 7
    assert len(design.components[1].bodies[0].edges) == 15
    assert design.components[1].bodies[0].volume.m == pytest.approx(
        Quantity(2.1881226057527826e-5, UNITS.m**3).m,
        rel=1e-6,
        abs=1e-8,
    )

    solid_two = design.components[1].bodies[0]
    design.delete_body(solid_two)
    design._update_design_inplace()

    assert len(design.components[1].bodies[0].faces) == 222
    assert len(design.components[1].bodies[0].edges) == 478
    assert design.components[1].bodies[0].volume.m == pytest.approx(
        Quantity(1.9648422680842302e-3, UNITS.m**3).m,
        rel=1e-6,
        abs=1e-8,
    )


def test_pull_example(modeler: Modeler):
    """Test pullin edges and faces example from Sp1ceClaim trainings"""
    scfile = Path(FILES_DIR, "1_Pull_Toolguides.scdocx")
    design = modeler.open_file(file_path=scfile)

    plane = Plane(
        origin=Point3D([0, 0, 0]), direction_x=Point3D([1, 0, 0]), direction_y=Point3D([0, 1, 0])
    )

    sketch1 = Sketch(plane)
    corner = Point2D([28.25, 84.3], UNITS.mm)
    width = 35.55 - 28.25
    height = 91.6 - 84.3

    sketch1.box(corner, width, height)

    body = design.bodies[0]

    path = [body.edges[32].shape, body.edges[31].shape, body.edges[33].shape]
    sweep_body = design.sweep_sketch("Sweep1longEdge", sketch1, path)

    body.unite(sweep_body)

    assert len(body.faces) == 56

    assert len(body.edges) == 136

    assert len(design.bodies) == 1

    assert body.volume.m == pytest.approx(
        0.000873495019735637,
        rel=1e-6,
        abs=1e-8,
    )

    plane_new = Plane(
        origin=Point3D([0, 0, 0]), direction_x=Point3D([0, 1, 0]), direction_y=Point3D([0, 0, 1])
    )

    sk2 = Sketch(plane_new)
    corner2 = Point2D([27.0, 0.0], UNITS.mm)
    sk2.box(corner2, 17.0, 13.0)
    design.extrude_sketch("HelixProfileExtrude", sk2, 0.00001)

    profile_face = design.bodies[1].faces[1]
    axis_line = Line(Point3D([0.0, 0.0, 0.0], UNITS.mm), Point3D([0.0, 0.0, 1.0], UNITS.mm))

    modeler.geometry_commands.revolve_faces_by_helix(
        selection=profile_face,
        axis=axis_line,
        direction=UNITVECTOR3D_Z,
        height=66.864 / 1000,
        pitch=0.02,
        taper_angle=0.0,
        right_handed=True,
        both_sides=False,
    )

    assert len(body.faces) == 64

    assert len(body.edges) == 157

    assert len(design.bodies) == 1

    assert body.volume.m == pytest.approx(
        0.000995727877391032,
        rel=1e-6,
        abs=1e-8,
    )


def test_intersect_example(modeler: Modeler):
    """Test intersect example from Sp1ceClaim trainings"""

    scfile = Path(FILES_DIR, "Intersect.scdocx")
    design = modeler.open_file(file_path=scfile)
    plane = Plane(
        origin=Point3D([0, 0, 0]), direction_x=Point3D([1, 0, 0]), direction_y=Point3D([0, 0, 1])
    )

    sketch = Sketch(plane)

    p1 = Point2D([22.59, 9], UNITS.mm)
    p2 = Point2D([26.338, 0], UNITS.mm)
    p3 = Point2D([34.59, 0], UNITS.mm)
    p4 = Point2D([44.59, 10], UNITS.mm)

    sketch.segment(p1, p2)
    sketch.segment(p2, p3)
    sketch.segment(p3, p4)
    sketch.segment(p4, p1)

    surface = design.create_surface("surface", sketch)
    face = surface.faces[0]
    modeler.geometry_commands.extrude_faces(faces=face, distance=0.01, pull_symmetric=True)

    face_count = 0
    edge_count = 0
    volume_total = 0

    for body in design.get_all_bodies():
        face_count += len(body.faces)
        edge_count += len(body.edges)
        volume_total += body.volume.m

    assert face_count == 738
    assert edge_count == 1703
    assert volume_total == pytest.approx(
        1.3535628774220348e-05,
        rel=1e-6,
        abs=1e-8,
    )

    assert len(design.get_all_bodies()) == 23
    assert len(design.components) == 8

    assert len(design.components[0].components) == 2
    assert len(design.components[1].components) == 5
    assert len(design.components[2].components) == 0
    assert len(design.components[3].components) == 0
    assert len(design.components[4].components) == 0
    assert len(design.components[5].components) == 3
    assert len(design.components[6].components) == 0
    assert len(design.components[7].components) == 8

    assert len(design.components[0].bodies) == 0
    assert len(design.components[0].components[0].bodies) == 1
    assert len(design.components[0].components[1].bodies) == 1

    assert len(design.components[1].components[0].bodies) == 1
    assert len(design.components[1].components[1].bodies) == 1
    assert len(design.components[1].components[2].bodies) == 1
    assert len(design.components[1].components[3].bodies) == 1
    assert len(design.components[1].components[4].bodies) == 1

    assert len(design.components[2].bodies) == 1
    assert len(design.components[3].bodies) == 1
    assert len(design.components[4].bodies) == 1

    assert len(design.components[5].components[0].bodies) == 1
    assert len(design.components[5].components[1].bodies) == 1
    assert len(design.components[5].components[2].bodies) == 1

    assert len(design.components[6].bodies) == 1

    assert len(design.components[7].components[0].bodies) == 1
    assert len(design.components[7].components[1].bodies) == 1
    assert len(design.components[7].components[2].bodies) == 1
    assert len(design.components[7].components[3].bodies) == 1
    assert len(design.components[7].components[4].bodies) == 1
    assert len(design.components[7].components[5].bodies) == 1
    assert len(design.components[7].components[6].bodies) == 1
    assert len(design.components[7].components[7].bodies) == 1

    body_to_split = design.components[7].components[3].bodies[0]

    faces_to_split_with = [
        design.bodies[0].faces[1],
        design.bodies[0].faces[2],
        design.bodies[0].faces[4],
    ]
    modeler.geometry_commands.split_body(
        bodies=[body_to_split],
        plane=None,
        slicers=None,
        faces=faces_to_split_with,
        extendfaces=False,
    )
    design._update_design_inplace()

    design.delete_body(design.bodies[0])
    design._update_design_inplace()

    face_count_two = 0
    edge_count_two = 0
    volume_total_two = 0

    for body_new in design.get_all_bodies():
        face_count_two += len(body_new.faces)
        edge_count_two += len(body_new.edges)
        volume_total_two += body_new.volume.m

    assert face_count_two == 749
    assert edge_count_two == 1753
    assert volume_total_two == pytest.approx(1.0693189709830897e-05, rel=1e-6, abs=1e-8)
    assert len(design.bodies) == 0
    assert len(design.components) == 8

    assert len(design.components[0].components) == 2
    assert len(design.components[1].components) == 5
    assert len(design.components[2].components) == 0
    assert len(design.components[3].components) == 0
    assert len(design.components[4].components) == 0
    assert len(design.components[5].components) == 3
    assert len(design.components[6].components) == 0
    assert len(design.components[7].components) == 8

    assert len(design.components[0].bodies) == 0
    assert len(design.components[0].components[0].bodies) == 1
    assert len(design.components[0].components[1].bodies) == 1

    assert len(design.components[1].components[0].bodies) == 1
    assert len(design.components[1].components[1].bodies) == 1
    assert len(design.components[1].components[2].bodies) == 1
    assert len(design.components[1].components[3].bodies) == 1
    assert len(design.components[1].components[4].bodies) == 1

    assert len(design.components[2].bodies) == 1
    assert len(design.components[3].bodies) == 1
    assert len(design.components[4].bodies) == 1

    assert len(design.components[5].components[0].bodies) == 1
    assert len(design.components[5].components[1].bodies) == 1
    assert len(design.components[5].components[2].bodies) == 1

    assert len(design.components[6].bodies) == 1

    assert len(design.components[7].components[0].bodies) == 1
    assert len(design.components[7].components[1].bodies) == 1
    assert len(design.components[7].components[2].bodies) == 1
    assert len(design.components[7].components[3].bodies) == 2
    assert len(design.components[7].components[4].bodies) == 1
    assert len(design.components[7].components[5].bodies) == 1
    assert len(design.components[7].components[6].bodies) == 1
    assert len(design.components[7].components[7].bodies) == 1

    design.delete_body(design.components[7].components[3].bodies[1])
    design._update_design_inplace()

    face_count_three = 0
    edge_count_three = 0
    volume_count_three = 0
    for body in design.get_all_bodies():
        face_count_three += len(body.faces)
        edge_count_three += len(body.edges)
        volume_count_three += body.volume.magnitude

    assert face_count_three == 736
    assert edge_count_three == 1720
    assert volume_count_three == pytest.approx(1.009880569525018e-05, rel=1e-5, abs=1e-7)

    assert len(design.bodies) == 0
    assert len(design.components) == 8

    assert len(design.components[0].components) == 2
    assert len(design.components[1].components) == 5
    assert len(design.components[2].components) == 0
    assert len(design.components[3].components) == 0
    assert len(design.components[4].components) == 0
    assert len(design.components[5].components) == 3
    assert len(design.components[6].components) == 0
    assert len(design.components[7].components) == 8

    assert len(design.components[0].bodies) == 0
    assert len(design.components[0].components[0].bodies) == 1
    assert len(design.components[0].components[1].bodies) == 1

    assert len(design.components[1].components[0].bodies) == 1
    assert len(design.components[1].components[1].bodies) == 1
    assert len(design.components[1].components[2].bodies) == 1
    assert len(design.components[1].components[3].bodies) == 1
    assert len(design.components[1].components[4].bodies) == 1

    assert len(design.components[2].bodies) == 1
    assert len(design.components[3].bodies) == 1
    assert len(design.components[4].bodies) == 1

    assert len(design.components[5].components[0].bodies) == 1
    assert len(design.components[5].components[1].bodies) == 1
    assert len(design.components[5].components[2].bodies) == 1

    assert len(design.components[6].bodies) == 1

    assert len(design.components[7].components[0].bodies) == 1
    assert len(design.components[7].components[1].bodies) == 1
    assert len(design.components[7].components[2].bodies) == 1
    assert len(design.components[7].components[3].bodies) == 1
    assert len(design.components[7].components[4].bodies) == 1

    bodies_to_split = [
        design.components[0].components[0].bodies[0],
        design.components[0].components[1].bodies[0],
        design.components[1].components[0].bodies[0],
        design.components[1].components[1].bodies[0],
        design.components[1].components[2].bodies[0],
        design.components[1].components[3].bodies[0],
        design.components[1].components[4].bodies[0],
        design.components[2].bodies[0],
        design.components[3].bodies[0],
        design.components[4].bodies[0],
        design.components[5].components[0].bodies[0],
        design.components[5].components[1].bodies[0],
        design.components[5].components[2].bodies[0],
        design.components[6].bodies[0],
        design.components[7].components[0].bodies[0],
        design.components[7].components[1].bodies[0],
        design.components[7].components[2].bodies[0],
        design.components[7].components[3].bodies[0],
        design.components[7].components[4].bodies[0],
        design.components[7].components[5].bodies[0],
        design.components[7].components[6].bodies[0],
        design.components[7].components[7].bodies[0],
    ]

    modeler.geometry_commands.split_body(
        bodies=bodies_to_split, plane=plane, slicers=None, faces=None, extendfaces=False
    )
    design._update_design_inplace()
    face_count_four = 0
    edge_count_four = 0
    volume_count_four = 0
    for body in design.get_all_bodies():
        face_count_four += len(body.faces)
        edge_count_four += len(body.edges)
        volume_count_four += body.volume.magnitude

    assert face_count_four == 1233
    assert edge_count_four == 3353
    assert volume_count_four == pytest.approx(1.0097482219846058e-05, rel=1e-6, abs=1e-8)
    assert len(design.bodies) == 0
    assert len(design.components) == 8

    assert len(design.components[0].components) == 2
    assert len(design.components[1].components) == 5
    assert len(design.components[2].components) == 0
    assert len(design.components[3].components) == 0
    assert len(design.components[4].components) == 0
    assert len(design.components[5].components) == 3
    assert len(design.components[6].components) == 0
    assert len(design.components[7].components) == 8

    assert len(design.components[0].bodies) == 0
    assert len(design.components[0].components[0].bodies) == 2
    assert len(design.components[0].components[1].bodies) == 2

    assert len(design.components[1].components[0].bodies) == 2
    assert len(design.components[1].components[1].bodies) == 2
    assert len(design.components[1].components[2].bodies) == 2
    assert len(design.components[1].components[3].bodies) == 2
    assert len(design.components[1].components[4].bodies) == 2

    assert len(design.components[2].bodies) == 2
    assert len(design.components[3].bodies) == 2
    assert len(design.components[4].bodies) == 2

    assert len(design.components[5].components[0].bodies) == 2
    assert len(design.components[5].components[1].bodies) == 2
    assert len(design.components[5].components[2].bodies) == 2

    assert len(design.components[6].bodies) == 2

    assert len(design.components[7].components[0].bodies) == 2
    assert len(design.components[7].components[1].bodies) == 2
    assert len(design.components[7].components[2].bodies) == 2
    assert len(design.components[7].components[3].bodies) == 2
    assert len(design.components[7].components[4].bodies) == 2
    assert len(design.components[7].components[5].bodies) == 2
    assert len(design.components[7].components[6].bodies) == 2
    assert len(design.components[7].components[7].bodies) == 2

    for body in bodies_to_split:
        design.delete_body(body)
        design._update_design_inplace()

    face_count_five = 0
    edge_count_five = 0
    volume_count_five = 0

    for body in design.get_all_bodies():
        face_count_five += len(body.faces)
        edge_count_five += len(body.edges)
        volume_count_five += body.volume.magnitude

    assert face_count_five == 617
    assert edge_count_five == 1670
    assert volume_count_five == pytest.approx(5.050554634143179e-06, rel=1e-6, abs=1e-8)

    assert len(design.bodies) == 0
    assert len(design.components) == 8

    assert len(design.components[0].components) == 2
    assert len(design.components[1].components) == 5
    assert len(design.components[2].components) == 0
    assert len(design.components[3].components) == 0
    assert len(design.components[4].components) == 0
    assert len(design.components[5].components) == 3
    assert len(design.components[6].components) == 0
    assert len(design.components[7].components) == 8

    assert len(design.components[0].bodies) == 0
    assert len(design.components[0].components[0].bodies) == 1
    assert len(design.components[0].components[1].bodies) == 1

    assert len(design.components[1].components[0].bodies) == 1
    assert len(design.components[1].components[1].bodies) == 1
    assert len(design.components[1].components[2].bodies) == 1
    assert len(design.components[1].components[3].bodies) == 1
    assert len(design.components[1].components[4].bodies) == 1

    assert len(design.components[2].bodies) == 1
    assert len(design.components[3].bodies) == 1
    assert len(design.components[4].bodies) == 1

    assert len(design.components[5].components[0].bodies) == 1
    assert len(design.components[5].components[1].bodies) == 1
    assert len(design.components[5].components[2].bodies) == 1

    assert len(design.components[6].bodies) == 1

    assert len(design.components[7].components[0].bodies) == 1
    assert len(design.components[7].components[1].bodies) == 1
    assert len(design.components[7].components[2].bodies) == 1
    assert len(design.components[7].components[3].bodies) == 1
    assert len(design.components[7].components[4].bodies) == 1
    assert len(design.components[7].components[5].bodies) == 1
    assert len(design.components[7].components[6].bodies) == 1
    assert len(design.components[7].components[7].bodies) == 1
