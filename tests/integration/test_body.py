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

"""Test body interaction."""

from pathlib import Path
from unittest.mock import patch

import matplotlib.colors as mcolors
import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.designer.body import FillStyle
from ansys.geometry.core.materials import Material, MaterialProperty, MaterialPropertyType
from ansys.geometry.core.math import (
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    UNITVECTOR3D_Z,
    Plane,
    Point2D,
    Point3D,
    UnitVector3D,
    Vector3D,
)
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Accuracy, Distance
from ansys.geometry.core.sketch import Sketch

from .conftest import FILES_DIR


def test_body_tracker_update_paths(modeler: Modeler):
    """Test USE_TRACKER_TO_UPDATE_DESIGN=True branches and detach_faces failure path."""
    import ansys.geometry.core as pyansys_geo

    design = modeler.create_design("TrackerPaths")
    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 2, 2)
    body = design.extrude_sketch("box", sketch, 2)
    sketch2 = Sketch()
    sketch2.box(Point2D([10, 0]), 1, 1)
    body2 = design.extrude_sketch("box2", sketch2, 1)

    bodies_svc = body._grpc_client.services.bodies
    original_tracker = pyansys_geo.USE_TRACKER_TO_UPDATE_DESIGN
    try:
        pyansys_geo.USE_TRACKER_TO_UPDATE_DESIGN = True

        with patch.object(bodies_svc, "boolean", return_value={"tracker_response": {}}):
            with patch.object(design, "_update_from_tracker"):
                body.intersect(body2)

        backend_ver = body._grpc_client.backend_version
        if backend_ver >= (25, 2, 0):
            with patch.object(
                bodies_svc,
                "combine_merge",
                return_value={"success": True, "tracker_response": {}},
            ):
                with patch.object(design, "_update_from_tracker"):
                    body._template.combine_merge(body2)

        if backend_ver >= (26, 1, 0):
            with patch.object(bodies_svc, "combine", return_value={"tracker_response": {}}):
                with patch.object(design, "_update_from_tracker"):
                    body._combine_subtract(body2)

        if backend_ver >= (27, 1, 0):
            model_tools_svc = body._grpc_client.services.model_tools
            with patch.object(
                model_tools_svc,
                "detach_faces",
                return_value={"success": True, "tracked_response": {}, "created_bodies": []},
            ):
                with patch.object(design, "_update_from_tracker"):
                    body.detach_faces()

            with patch.object(
                model_tools_svc,
                "detach_faces",
                return_value={"success": False},
            ):
                result = body.detach_faces()
                assert result == []
    finally:
        pyansys_geo.USE_TRACKER_TO_UPDATE_DESIGN = original_tracker


def test_assigning_and_getting_material(modeler: Modeler):
    """Test the assignment and retrieval of materials from a design."""
    # Create a Sketch and draw a circle (all client side)
    sketch = Sketch()
    sketch.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design_name = "ExtrudeProfile"
    design = modeler.create_design(design_name)

    # Add a material to body
    density = Quantity(125, 1000 * UNITS.kg / (UNITS.m**3))
    poisson_ratio = Quantity(0.33, UNITS.dimensionless)
    tensile_strength = Quantity(45.0, UNITS.pascal)
    material = Material(
        "steel",
        density,
        [MaterialProperty(MaterialPropertyType.POISSON_RATIO, "myPoisson", poisson_ratio)],
    )
    material.add_property(MaterialPropertyType.TENSILE_STRENGTH, "myTensile", Quantity(45))
    design.add_material(material)

    # Extrude the sketch to create a Body
    body = design.extrude_sketch("JustACircle", sketch, Quantity(10, UNITS.mm))

    # Assign a material to a Body
    body.material = material
    mat_service = body.material

    # Test material and property retrieval
    assert mat_service.name == "steel"
    assert len(mat_service.properties) == 3
    assert mat_service.properties[MaterialPropertyType.DENSITY].type == MaterialPropertyType.DENSITY
    assert mat_service.properties[MaterialPropertyType.DENSITY].name == "Density"
    assert mat_service.properties[MaterialPropertyType.DENSITY].quantity == density
    assert (
        mat_service.properties[MaterialPropertyType.POISSON_RATIO].type
        == MaterialPropertyType.POISSON_RATIO
    )
    assert mat_service.properties[MaterialPropertyType.POISSON_RATIO].name == "myPoisson"
    assert mat_service.properties[MaterialPropertyType.POISSON_RATIO].quantity == poisson_ratio
    assert (
        mat_service.properties[MaterialPropertyType.TENSILE_STRENGTH].type
        == MaterialPropertyType.TENSILE_STRENGTH
    )
    assert mat_service.properties[MaterialPropertyType.TENSILE_STRENGTH].name == "myTensile"
    assert (
        mat_service.properties[MaterialPropertyType.TENSILE_STRENGTH].quantity == tensile_strength
    )


def test_get_empty_material(modeler: Modeler):
    """Check that the material service returns an empty material."""
    # Create a Sketch and draw a circle (all client side)
    sketch = Sketch()
    sketch.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design_name = "ExtrudeProfile"
    design = modeler.create_design(design_name)

    # Extrude the sketch to create a Body
    body = design.extrude_sketch("JustACircle", sketch, Quantity(10, UNITS.mm))

    # Assign a material to a Body
    mat_service = body.material
    assert mat_service.name == ""
    assert mat_service.properties[MaterialPropertyType.DENSITY].quantity == Quantity(
        0, UNITS.kg / (UNITS.m**3)
    )
    assert len(mat_service.properties) == 1


def test_single_body_translation(modeler: Modeler):
    """Test for verifying the correct translation of a ``Body``.

    Notes
    -----
    Requires storing scdocx file and checking manually (for now).
    """
    # Create your design on the server side
    design = modeler.create_design("SingleBodyTranslation_Test")

    # Create 2 Sketch objects and draw a circle and a polygon (all client side)
    sketch_1 = Sketch()
    sketch_1.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))
    sketch_2 = Sketch()
    sketch_2.polygon(Point2D([-30, -30], UNITS.mm), Quantity(10, UNITS.mm), sides=5)

    # Build 2 independent components and bodies
    circle_comp = design.add_component("CircleComponent")
    body_circle_comp = circle_comp.extrude_sketch("Circle", sketch_1, Quantity(50, UNITS.mm))
    polygon_comp = design.add_component("PolygonComponent")
    body_polygon_comp = polygon_comp.extrude_sketch("Polygon", sketch_2, Quantity(30, UNITS.mm))

    body_circle_comp.translate(UnitVector3D([1, 0, 0]), Distance(50, UNITS.mm))
    body_polygon_comp.translate(UnitVector3D([-1, 1, -1]), Quantity(88, UNITS.mm))
    body_polygon_comp.translate(UnitVector3D([-1, 1, -1]), 101)


def test_boolean_body_operations(modeler: Modeler):
    """
    Test cases:

    1) master/master
        a) intersect
            i) normal
                x) identity
                y) transform
            ii) empty failure
        b) subtract
            i) normal
                x) identity
                y) transform
            ii) empty failure
            iii) disjoint
        c) unite
            i) normal
                x) identity
                y) transform
            ii) disjoint
    2) instance/instance
        a) intersect
            i) normal
                x) identity
                y) transform
            ii) empty failure
        b) subtract
            i) normal
                x) identity
                y) transform
            ii) empty failure
        c) unite
            i) normal
                x) identity
                y) transform
    """
    design = modeler.create_design("TestBooleanOperations")

    comp1 = design.add_component("Comp1")
    comp2 = design.add_component("Comp2")
    comp3 = design.add_component("Comp3")

    body1 = comp1.extrude_sketch("Body1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    body2 = comp2.extrude_sketch("Body2", Sketch().box(Point2D([0.5, 0]), 1, 1), 1)
    body3 = comp3.extrude_sketch("Body3", Sketch().box(Point2D([5, 0]), 1, 1), 1)

    # 1.a.i.x
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy1.intersect(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

    # 1.a.i.y
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.intersect(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.25)

    # 1.a.ii
    copy1 = body1.copy(comp1, "Copy1")
    copy3 = body3.copy(comp3, "Copy3")
    with pytest.raises(ValueError, match="bodies do not intersect"):
        copy1.intersect(copy3)

    assert copy1.is_alive
    assert copy3.is_alive

    # 1.b.i.x
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy1.subtract(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

    # 1.b.i.y
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.subtract(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.75)

    # 1.b.ii
    copy1 = body1.copy(comp1, "Copy1")
    copy1a = body1.copy(comp1, "Copy1a")
    with pytest.raises(ValueError):
        copy1.subtract(copy1a)

    assert copy1.is_alive
    assert copy1a.is_alive

    # 1.b.iii
    copy1 = body1.copy(comp1, "Copy1")
    copy3 = body3.copy(comp3, "Copy3")
    copy1.subtract(copy3)

    assert Accuracy.length_is_equal(copy1.volume.m, 1)
    assert copy1.volume
    assert not copy3.is_alive

    # 1.c.i.x
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy1.unite(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1.5)

    # 1.c.i.y
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.unite(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1.75)

    # 1.c.ii
    copy1 = body1.copy(comp1, "Copy1")
    copy3 = body3.copy(comp3, "Copy3")
    copy1.unite(copy3)

    assert not copy3.is_alive
    assert body3.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1)

    # Test instance/instance
    comp1_i = design.add_component("Comp1_i", comp1)
    comp2_i = design.add_component("Comp2_i", comp2)
    comp3_i = design.add_component("Comp3_i", comp3)

    comp1_i.modify_placement(
        Vector3D([52, 61, -43]), Point3D([-4, 26, 66]), UnitVector3D([-21, 20, 87]), np.pi / 4
    )
    comp2_i.modify_placement(
        Vector3D([52, 61, -43]), Point3D([-4, 26, 66]), UnitVector3D([-21, 20, 87]), np.pi / 4
    )
    comp3_i.modify_placement(
        Vector3D([52, 61, -43]), Point3D([-4, 26, 66]), UnitVector3D([-21, 20, 87]), np.pi / 4
    )

    body1 = comp1_i.bodies[0]
    body2 = comp2_i.bodies[0]
    body3 = comp3_i.bodies[0]

    # 2.a.i.x
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy1.intersect(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

    # 2.a.i.y
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.intersect(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.25)

    # 2.a.ii
    copy1 = body1.copy(comp1_i, "Copy1")
    copy3 = body3.copy(comp3_i, "Copy3")
    with pytest.raises(ValueError, match="bodies do not intersect"):
        copy1.intersect(copy3)

    assert copy1.is_alive
    assert copy3.is_alive

    # 2.b.i.x
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy1.subtract(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

    # 2.b.i.y
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.subtract(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.75)

    # 2.b.ii
    copy1 = body1.copy(comp1_i, "Copy1")
    copy1a = body1.copy(comp1_i, "Copy1a")
    with pytest.raises(ValueError):
        copy1.subtract(copy1a)

    assert copy1.is_alive
    assert copy1a.is_alive

    # 2.b.iii
    copy1 = body1.copy(comp1_i, "Copy1")
    copy3 = body3.copy(comp3_i, "Copy3")
    copy1.subtract(copy3)

    assert Accuracy.length_is_equal(copy1.volume.m, 1)
    assert copy1.volume
    assert not copy3.is_alive

    # 2.c.i.x
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy1.unite(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1.5)

    # 2.c.i.y
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.unite(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1.75)

    # 2.c.ii
    copy1 = body1.copy(comp1_i, "Copy1")
    copy3 = body3.copy(comp3_i, "Copy3")
    copy1.unite(copy3)

    assert not copy3.is_alive
    assert body3.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1)


def test_set_body_name(modeler: Modeler):
    """Test the setting the name of a body."""
    design = modeler.create_design("simple_cube")
    unit = DEFAULT_UNITS.LENGTH
    plane = Plane(
        Point3D([1 / 2, 1 / 2, 0.0], unit=unit),
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )
    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0]), width=1 * unit, height=1 * unit)
    box = design.extrude_sketch("first_name", box_plane, 1 * unit)
    assert box.name == "first_name"
    box.set_name("updated_name")
    assert box.name == "updated_name"
    box.name = "updated_name2"
    assert box.name == "updated_name2"


def test_set_fill_style(modeler: Modeler):
    """Test the setting the fill style of a body."""
    design = modeler.create_design("RVE")
    unit = DEFAULT_UNITS.LENGTH

    plane = Plane(
        Point3D([1 / 2, 1 / 2, 0.0], unit=unit),
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )

    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0]), width=1 * unit, height=1 * unit)
    box = design.extrude_sketch("Matrix", box_plane, 1 * unit)

    assert box.fill_style == FillStyle.DEFAULT
    box.set_fill_style(FillStyle.TRANSPARENT)
    assert box.fill_style == FillStyle.TRANSPARENT
    box.fill_style = FillStyle.OPAQUE
    assert box.fill_style == FillStyle.OPAQUE


def test_body_suppression(modeler: Modeler):
    """Test the suppression of a body."""

    design = modeler.create_design("RVE")
    unit = DEFAULT_UNITS.LENGTH

    plane = Plane(
        Point3D([1 / 2, 1 / 2, 0.0], unit=unit),
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )

    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0]), width=1 * unit, height=1 * unit)
    box = design.extrude_sketch("Matrix", box_plane, 1 * unit)

    assert box.is_suppressed is False
    box.set_suppressed(True)
    assert box.is_suppressed is True
    box.is_suppressed = False
    assert box.is_suppressed is False


def test_set_body_color(modeler: Modeler):
    """Test the getting and setting of body color."""

    design = modeler.create_design("RVE2")
    unit = DEFAULT_UNITS.LENGTH

    plane = Plane(
        Point3D([1 / 2, 1 / 2, 0.0], unit=unit),
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )
    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0]), width=1 * unit, height=1 * unit)
    box = design.extrude_sketch("Block", box_plane, 1 * unit)

    # Default body color is if it is not set on server side.
    assert box.color == DEFAULT_COLOR

    # Set the color of the body using hex code.
    box.color = "#0000ff"
    assert box.color[0:7] == "#0000ff"

    box.color = "#ffc000"
    assert box.color[0:7] == "#ffc000"

    # Set the color of the body using color name.
    box.set_color("green")
    box.color[0:7] == "#008000"

    # Set the color of the body using RGB values between (0,1) as floats.
    box.set_color((1.0, 0.0, 0.0))
    box.color[0:7] == "#ff0000"

    # Set the color of the body using RGB values between (0,255) as integers).
    box.set_color((0, 255, 0))
    box.color[0:7] == "#00ff00"

    # Assigning color object directly
    blue_color = mcolors.to_rgba("#0000FF")
    box.color = blue_color
    assert box.color[0:7] == "#0000ff"

    # Test an RGBA color
    box.color = "#ff00003c"
    assert box.color == "#ff00003c"

    # Test setting the opacity separately
    box.opacity = 0.8
    assert box.color == "#ff0000cc"

    # Try setting the opacity to an invalid value
    with pytest.raises(
        ValueError, match="Invalid color value: Opacity value must be between 0 and 1."
    ):
        box.opacity = 255


def test_shell_body(modeler: Modeler):
    """Test shell command."""
    design = modeler.create_design("shell")
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    assert base.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 6

    # shell
    success = base.shell_body(0.1)
    assert success
    assert base.volume.m == pytest.approx(Quantity(0.728, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 12

    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    success = base.shell_body(-0.1)
    assert success
    assert base.volume.m == pytest.approx(Quantity(0.488, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 12


def test_shell_faces(modeler: Modeler):
    """Test shell commands for a single face."""
    design = modeler.create_design("shell")
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    assert base.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 6

    # shell
    success = base.remove_faces(base.faces[0], 0.1)
    assert success
    assert base.volume.m == pytest.approx(Quantity(0.584, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 11


def test_shell_multiple_faces(modeler: Modeler):
    """Test shell commands for multiple faces."""
    design = modeler.create_design("shell")
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    assert base.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 6

    # shell
    success = base.remove_faces([base.faces[0], base.faces[2]], 0.1)
    assert success
    assert base.volume.m == pytest.approx(Quantity(0.452, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 10


def test_combine_merge(modeler: Modeler):
    design = modeler.create_design("combine_merge")
    box1 = design.extrude_sketch("box1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    box2 = design.extrude_sketch("box2", Sketch().box(Point2D([0.5, 0.5]), 1, 1), 1)
    assert len(design.bodies) == 2

    # combine the two boxes and check body count and volume
    box1.combine_merge([box2])
    assert len(design.bodies) == 1
    assert box1.volume.m == pytest.approx(Quantity(1.75, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # create a third box
    box1 = design.bodies[0]
    box3 = design.extrude_sketch("box3", Sketch().box(Point2D([-0.5, -0.5]), 1, 1), 1)
    assert len(design.bodies) == 2

    # combine the two boxes and check body count and volume
    box1.combine_merge([box3])
    assert len(design.bodies) == 1
    assert box1.volume.m == pytest.approx(Quantity(2.5, UNITS.m**3).m, rel=1e-6, abs=1e-8)


def test_combine_subtract_transfer_ns(modeler: Modeler):
    """Testing the transfer of named selection during an intersect"""
    input_file = Path(FILES_DIR, "sub_valid.scdocx")
    design = modeler.open_file(input_file)

    inside = design.bodies[0]
    outside = design.bodies[1]
    # Confirm the number of named selection then subtract
    assert len(design.named_selections) == 4
    outside._combine_subtract(inside)
    # Confirm the subtraction worked
    assert len(design.bodies) == 1
    assert len(design.named_selections) == 4
    # Then confirm the named selections
    assert design.named_selections[0].faces[0].area.m == design.bodies[0].faces[9].area.m
    assert design.named_selections[1].faces[0].area.m == design.bodies[0].faces[11].area.m
    assert design.named_selections[3].faces[0].area.m == design.bodies[0].faces[6].area.m
    assert len(design.named_selections[2].edges) == 4
    assert len(design.named_selections[3].edges) == 2


def test_combine_subtract_transfer_ns_default_options_changed(modeler: Modeler):
    """Testing the transfer of named selection during an
    intersect with default options overridden"""
    input_file = Path(FILES_DIR, "sub_valid.scdocx")
    design = modeler.open_file(input_file)
    # Confirm the number of named selection then subtract
    inside = design.bodies[0]
    outside = design.bodies[1]

    assert len(design.named_selections) == 4
    outside._combine_subtract(inside, keep_other=True, transfer_named_selections=False)
    # Then confirm the named selections
    assert len(design.bodies) == 2
    assert len(design.named_selections) == 4


def test_get_centroid(modeler: Modeler):
    """Test get_centroid() method on body, face, and edge objects.

    This test validates that the centroid calculation works correctly for:
    - Body: Tests a simple box and a cylinder
    - Face: Tests face centroids from various geometries
    - Edge: Tests edge centroids from various geometries
    """
    # Create a design
    design = modeler.create_design("CentroidTest")

    # Test 1: Body centroid - Box centered at origin
    sketch_box = Sketch()
    sketch_box.box(Point2D([0, 0], UNITS.mm), Quantity(20, UNITS.mm), Quantity(10, UNITS.mm))
    box_body = design.extrude_sketch("TestBox", sketch_box, Quantity(5, UNITS.mm))

    # Get centroid of the box body
    # Expected: center of a 20x10x5 mm box, centered at origin
    # The box is drawn from [0,0] with width=20, height=10, so center is at [0, 0] in XY
    # Extruded by 5mm, so center in Z is at 2.5mm
    box_centroid = box_body.centroid
    assert isinstance(box_centroid, Point3D)
    assert box_centroid.x.m == pytest.approx(0, rel=1e-6, abs=1e-8)
    assert box_centroid.y.m == pytest.approx(0, rel=1e-6, abs=1e-8)
    assert box_centroid.z.m == pytest.approx(2.5e-3, rel=1e-6, abs=1e-8)  # 2.5mm in meters

    # Test 2: Body centroid - Cylinder
    sketch_circle = Sketch()
    sketch_circle.circle(Point2D([50, 50], UNITS.mm), Quantity(10, UNITS.mm))
    cylinder_body = design.extrude_sketch("TestCylinder", sketch_circle, Quantity(30, UNITS.mm))

    # Get centroid of the cylinder body
    # Expected: center of cylinder with base at [50, 50, 0] and height 30mm
    # So centroid should be at [50, 50, 15] mm
    cylinder_centroid = cylinder_body.centroid
    assert isinstance(cylinder_centroid, Point3D)
    assert cylinder_centroid.x.m == pytest.approx(50e-3, rel=1e-6, abs=1e-8)  # 50mm in meters
    assert cylinder_centroid.y.m == pytest.approx(50e-3, rel=1e-6, abs=1e-8)  # 50mm in meters
    assert cylinder_centroid.z.m == pytest.approx(15e-3, rel=1e-6, abs=1e-8)  # 15mm in meters

    # Test 3: Face centroid - Top face of the box
    # The box has 6 faces. Let's test the top face (typically the last face after extrusion)
    top_face = next(f for f in box_body.faces if np.allclose(f.normal(0, 0), UNITVECTOR3D_Z))
    top_face_centroid = top_face.centroid
    assert isinstance(top_face_centroid, Point3D)
    assert top_face_centroid.x.m == pytest.approx(0, rel=1e-6, abs=1e-8)
    assert top_face_centroid.y.m == pytest.approx(0, rel=1e-6, abs=1e-8)
    assert top_face_centroid.z.m == pytest.approx(5e-3, rel=1e-6, abs=1e-8)  # Top face at 5mm

    # Test 4: Face centroid - Circular face of cylinder
    top_face = next(f for f in cylinder_body.faces if np.allclose(f.normal(0, 0), UNITVECTOR3D_Z))
    top_face_centroid = top_face.centroid
    assert isinstance(top_face_centroid, Point3D)
    assert top_face_centroid.x.m == pytest.approx(50e-3, rel=1e-6, abs=1e-8)
    assert top_face_centroid.y.m == pytest.approx(50e-3, rel=1e-6, abs=1e-8)
    assert top_face_centroid.z.m == pytest.approx(30e-3, rel=1e-6, abs=1e-8)

    # Test 5: Edge centroid - Edges of the box
    box_edges = box_body.edges
    edge_centroid = box_edges[0].centroid  # Edge at the bottom of the box
    assert isinstance(edge_centroid, Point3D)
    assert edge_centroid.x.m == pytest.approx(0, rel=1e-6, abs=1e-8)
    assert edge_centroid.y.m == pytest.approx(0, rel=1e-6, abs=1e-8)
    assert edge_centroid.z.m == pytest.approx(2.5e-3, rel=1e-6, abs=1e-8)

    # Test 6: Edge centroid - Edges of the cylinder
    cylinder_edges = cylinder_body.edges
    edge_centroid = cylinder_edges[0].centroid
    assert isinstance(edge_centroid, Point3D)
    assert edge_centroid.x.m == pytest.approx(50e-3, rel=1e-6, abs=1e-8)
    assert edge_centroid.y.m == pytest.approx(50e-3, rel=1e-6, abs=1e-8)
    assert edge_centroid.z.m == pytest.approx(15e-3, rel=1e-6, abs=1e-8)
