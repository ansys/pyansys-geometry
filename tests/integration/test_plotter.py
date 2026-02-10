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

try:
    from ansys.geometry.core.misc.checks import run_if_graphics_required

    run_if_graphics_required()

    import pyvista as pv
    from pyvista.plotting import system_supports_plotting

except ImportError:
    import pytest

    pytest.skip(
        "Skipping test_plotter module due to graphics requirements missing.",
        allow_module_level=True,
    )

from pathlib import Path

from ansys.tools.visualization_interface import MeshObjectPlot
import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.math import UNITVECTOR3D_Y, UNITVECTOR3D_Z, Plane, Point2D, Point3D
from ansys.geometry.core.math.constants import UNITVECTOR3D_X
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Distance
from ansys.geometry.core.misc.measurements import Angle
from ansys.geometry.core.plotting import GeometryPlotter
from ansys.geometry.core.sketch import (
    Arc,
    Box,
    Polygon,
    Sketch,
    SketchCircle,
    SketchEllipse,
    SketchSegment,
    Slot,
    Trapezoid,
    Triangle,
)

skip_no_xserver = pytest.mark.skipif(
    not system_supports_plotting(), reason="Requires active X Server"
)

IMAGE_RESULTS_DIR = Path(Path(__file__).parent, "image_cache", "results")


@skip_no_xserver
def test_adding_to_plotter(modeler: Modeler, verify_image_cache):
    """Testing out clipping plane, adding body edges and face,
    and if body is suppressed to an existing plotter"""
    plotter = GeometryPlotter(allow_picking=True)
    plane = Plane(origin=[0, 0, 0], direction_x=[1, 0, 0], direction_y=[0, 1, 0])
    box_plane = Sketch(plane=plane)
    plotting_options = {"clipping_plane": True}
    plotter.add_sketch(box_plane, show_plane=True, show_frame=True, **plotting_options)
    design = modeler.create_design("Box")
    box_plane.box(Point2D([0.0, 0.0]), width=1, height=1)
    box = design.extrude_sketch("Box", box_plane, 1)
    box_plot = MeshObjectPlot(box, mesh=None)
    plotter.add_body_edges(box_plot)
    box.set_suppressed(True)
    plotter.add_body(box)
    box.set_suppressed(False)
    plotter.add_body(box)
    plotter.add_face(box.faces[0])
    plotter.show(screenshot=Path(IMAGE_RESULTS_DIR, "adding_to_plotter.png"))


@skip_no_xserver
def test_different_color_than_default(modeler: Modeler, verify_image_cache):
    """Testing out adding a face to the plotter with a different color than the default."""
    design = modeler.create_design("Box")
    plane = Plane(origin=[0, 0, 0], direction_x=[1, 0, 0], direction_y=[0, 1, 0])
    box_plane = Sketch(plane=plane)
    box_plane.box(Point2D([0.0, 0.0]), width=1, height=1)
    box = design.extrude_sketch("Box", box_plane, 1)
    plotter2 = GeometryPlotter(allow_picking=True, use_service_colors=True)
    box.faces[0].color = "blue"
    plotter2.add_face(box.faces[0])
    plotter2.show(
        plotting_object=box, screenshot=Path(IMAGE_RESULTS_DIR, "different_color_than_default.png")
    )


@skip_no_xserver
def test_plot_body(modeler: Modeler, verify_image_cache):
    """Test plotting of the body."""
    # Create a Sketch
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design = modeler.create_design("BoxExtrusions")

    # Extrude the sketch to create a body
    box_body = design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.mm))

    # Test the plotting of the body
    box_body.plot(screenshot=Path(IMAGE_RESULTS_DIR, "plot_body.png"))


@skip_no_xserver
def test_plot_component(modeler: Modeler, verify_image_cache):
    """Test plotting of the component."""
    # Create a Sketch
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(10, UNITS.mm))
    # Create your design on the server side
    design = modeler.create_design("BoxExtrusion")

    # Extrude the sketch to create a Body
    design.extrude_sketch("Box", sketch, Quantity(10, UNITS.mm))
    component_1 = design.add_component("Component")

    sketch_1 = Sketch()
    sketch_1.ellipse(Point2D([50, 50], UNITS.mm), Quantity(30, UNITS.mm), Quantity(10, UNITS.mm))
    component_1.create_surface("Component_Surface", sketch_1)

    # Test the plotting of the component
    design.plot(screenshot=Path(IMAGE_RESULTS_DIR, "plot_component.png"))


@skip_no_xserver
def test_plot_sketch(verify_image_cache):
    """Test plotting the sketch instance."""
    # Create a sketch instance
    sketch = Sketch()
    sketch.polygon(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), sides=5, tag="Polygon1")
    sketch.segment(Point2D([3, 0], UNITS.m), Point2D([10, 0], UNITS.m), "Segment1")
    sketch.arc(
        Point2D([10, 10], UNITS.m),
        Point2D([10, -10], UNITS.m),
        Point2D([10, 0], UNITS.m),
        tag="Arc1",
    )

    # Plot the entire sketch instance
    sketch.plot(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_sketch.png"))


@skip_no_xserver
def test_plot_nurbs_sketch(verify_image_cache):
    # Create a NURBS sketch instance
    sketch = Sketch()
    sketch.nurbs_from_2d_points(
        [
            Point2D([0, 0]),
            Point2D([2, 2]),
            Point2D([3, 6]),
            Point2D([4, 7]),
        ]
    )

    # Plot the NURBS sketch
    sketch.plot(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_nurbs_sketch.png"))


@skip_no_xserver
def test_plot_geometryplotter_sketch_pyvista(verify_image_cache):
    # define sketch
    sketch = Sketch()
    sketch.polygon(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), sides=5, tag="Polygon1")

    # define pyvista PolyData
    cyl = pv.Cylinder(radius=5, height=20, center=(-20, 10, 10))

    # define PyVista Multiblock
    blocks = pv.MultiBlock([pv.Sphere(center=(20, 10, -10), radius=4), pv.Cube()])

    # plot together
    pl = GeometryPlotter()
    pl.plot([sketch, cyl, blocks])
    pl.show(
        screenshot=Path(IMAGE_RESULTS_DIR, "test_plot_geometryplotter_sketch_pyvista.png"),
    )


@skip_no_xserver
def test_plot_geometryplotter_sketch_body(modeler: Modeler, verify_image_cache):
    # init modeler
    design = modeler.create_design("Multiplot")

    # define sketch
    sketch = Sketch()
    sketch.polygon(Point2D([-10, 10], UNITS.m), Quantity(10, UNITS.m), sides=5, tag="Polygon1")

    # define body
    body_sketch = Sketch()
    body_sketch.box(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))
    box_body = design.extrude_sketch("JustABox", body_sketch, Quantity(10, UNITS.m))

    # plot together
    pl = GeometryPlotter()
    pl.plot([sketch, box_body])
    pl.show(
        screenshot=Path(IMAGE_RESULTS_DIR, "test_plot_geometryplotter_sketch_body.png"),
    )


@skip_no_xserver
def test_plot_geometryplotter_sketch_several_bodies(modeler: Modeler, verify_image_cache):
    # init modeler
    design = modeler.create_design("Multiplot")

    # define sketch
    sketch = Sketch()
    sketch.polygon(Point2D([10, -10], UNITS.m), Quantity(10, UNITS.m), sides=5, tag="Polygon1")

    # define box body
    box_sketch = Sketch()
    box_sketch.box(Point2D([-10, -10], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))
    box_body = design.extrude_sketch("JustABox", box_sketch, Quantity(10, UNITS.m))

    # define box body
    cyl_sketch = Sketch()
    cyl_sketch.circle(Point2D([-20, 5], UNITS.m), Quantity(10, UNITS.m))
    cyl_body = design.extrude_sketch("JustABox", cyl_sketch, Quantity(10, UNITS.m))

    # Create a gear
    sketch_gear = Sketch(plane=Plane(direction_x=UNITVECTOR3D_Y, direction_y=UNITVECTOR3D_Z))
    sketch_gear.dummy_gear(
        Point2D([3, 1], unit=UNITS.meter),
        Distance(4, unit=UNITS.meter),
        Distance(3.8, unit=UNITS.meter),
        30,
        tag="Gear",
    )
    gear_body = design.extrude_sketch("GearExtruded", sketch_gear, Quantity(1, UNITS.m))

    # plot together
    pl = GeometryPlotter()
    pl.plot([sketch, box_body, gear_body, cyl_body])
    pl.show(
        screenshot=Path(IMAGE_RESULTS_DIR, "test_plot_geometryplotter_sketch_several_bodies.png"),
    )


@skip_no_xserver
def test_plot_geometryplotter_sketch_design(modeler: Modeler, verify_image_cache):
    # init modeler
    design = modeler.create_design("Multiplot")

    # define sketch
    sketch = Sketch()
    sketch.polygon(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), sides=5, tag="Polygon1")

    # define box body
    box_sketch = Sketch()
    box_sketch.box(Point2D([-10, -10], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))
    design.extrude_sketch("JustABox", box_sketch, Quantity(10, UNITS.m))

    # plot together
    pl = GeometryPlotter()
    pl.plot([sketch, design])
    pl.show(
        screenshot=Path(IMAGE_RESULTS_DIR, "test_plot_geometryplotter_sketch_design.png"),
    )


@skip_no_xserver
def test_plot_geometryplotter_all_types(modeler: Modeler, verify_image_cache):
    """Test plotting a list of PyAnsys Geometry objects."""
    plot_list = []

    # init modeler
    design = modeler.create_design("Multiplot")

    # Sketch 1 definition
    sketch = Sketch()
    sketch.polygon(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), sides=5, tag="Polygon1")
    sketch.segment(Point2D([3, 0], UNITS.m), Point2D([10, 0], UNITS.m), "Segment1")
    sketch.arc(
        Point2D([10, 10], UNITS.m),
        Point2D([10, -10], UNITS.m),
        Point2D([10, 0], UNITS.m),
        tag="Arc1",
    )
    plot_list.append(sketch)
    # Sketch 2 definition
    sketch2 = Sketch()
    sketch2.arc(
        Point2D([20, 20], UNITS.m),
        Point2D([20, -20], UNITS.m),
        Point2D([10, 0], UNITS.m),
        tag="Arc2",
    )
    plot_list.append(sketch2)

    # PyVista PolyData
    cyl = pv.Cylinder(radius=5, height=20, center=(-20, 10, 10))
    plot_list.append(cyl)

    # PyVista Multiblock
    blocks = pv.MultiBlock(
        [pv.Sphere(center=(20, 10, -10), radius=10), pv.Cube(x_length=10, y_length=10, z_length=10)]
    )
    plot_list.append(blocks)

    # Create a Body cylinder
    cylinder = Sketch()
    cylinder.circle(Point2D([10, 10], UNITS.m), 1.0)
    cylinder_body = design.extrude_sketch("JustACyl", cylinder, Quantity(10, UNITS.m))
    plot_list.append(cylinder_body)

    # Create a Body box
    box2 = Sketch()
    box2.box(Point2D([-10, 20], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))
    box_body2 = design.extrude_sketch("JustABox", box2, Quantity(10, UNITS.m))
    plot_list.append(box_body2)

    pl = GeometryPlotter()
    pl.plot(plot_list)
    pl.show(
        screenshot=Path(IMAGE_RESULTS_DIR, "test_plot_geometryplotter_all_types.png"),
    )


@skip_no_xserver
def test_plot_polygon(verify_image_cache):
    """Test plotting of a polygon."""
    # Create a sketch instance
    sketch = Sketch()

    # Create a polygon and plot
    sketch.polygon(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), sides=5, tag="Polygon")
    sketch.select("Polygon")
    sketch.plot_selection(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_polygon.png"))


@skip_no_xserver
def test_plot_segment(verify_image_cache):
    """Test plotting of a segment."""
    # Create a sketch instance
    sketch = Sketch()

    # Create a segment and plot
    sketch.segment(Point2D([3, 2]), Point2D([2, 0]), "Segment")
    sketch.select("Segment")
    sketch.plot_selection(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_segment.png"))


@skip_no_xserver
def test_plot_arc(verify_image_cache):
    """Test plotting of an arc."""
    # Create a sketch instance
    sketch = Sketch()

    # Create an arc and plot
    sketch.arc(Point2D([10, 10]), Point2D([10, -10]), Point2D([10, 0]), tag="Arc")
    sketch.select("Arc")
    sketch.plot_selection(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_arc.png"))


@skip_no_xserver
def test_plot_arc_from_three_points_clockwise(verify_image_cache):
    """Test plotting of an arc from three points (clockwise)."""
    # Create a sketch instance
    sketch = Sketch()

    # Create start and end points for the arc
    start = Point2D([0, 5])
    end = Point2D([5, 0])

    # Forcing a clockwise arc
    inter = Point2D([2, 4])
    sketch.arc_from_three_points(start, inter, end, tag="Arc_clockwise")
    sketch.select("Arc_clockwise")
    sketch.plot_selection(
        view_2d=True,
        screenshot=Path(IMAGE_RESULTS_DIR, "plot_arc_from_three_points_clockwise.png"),
    )


@skip_no_xserver
def test_plot_arc_from_three_points_counterclockwise(verify_image_cache):
    """Test plotting of an arc from three points (counter-clockwise)."""
    # Create a sketch instance
    sketch = Sketch()

    # Create start and end points for the arc
    start = Point2D([0, 5])
    end = Point2D([5, 0])

    # Forcing a counter-clockwise arc
    inter = Point2D([0, -5])
    sketch.arc_from_three_points(start, inter, end, tag="Arc_counterclockwise")
    sketch.select("Arc_counterclockwise")
    sketch.plot_selection(
        view_2d=True,
        screenshot=Path(IMAGE_RESULTS_DIR, "plot_arc_from_three_points_counterclockwise.png"),
    )


@skip_no_xserver
def test_plot_triangle(verify_image_cache):
    """Test plotting of a triangle."""
    # Create a sketch instance
    sketch = Sketch()

    # Create a triangle and plot
    sketch.triangle(Point2D([10, 10]), Point2D([2, 1]), Point2D([10, -10]), tag="Triangle")
    sketch.select("Triangle")
    sketch.plot_selection(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_triangle.png"))


@skip_no_xserver
def test_plot_trapezoid(verify_image_cache):
    """Test plotting of a trapezoid."""
    # Create a sketch instance
    sketch = Sketch()

    # Create a trapezoid and plot
    sketch.trapezoid(10, 2, np.pi / 4, np.pi / 8, Point2D([10, -10]), tag="Trapezoid")
    sketch.select("Trapezoid")
    sketch.plot_selection(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_trapezoid.png"))


@skip_no_xserver
def test_plot_trapezoid_symmetric(verify_image_cache):
    """Test plotting of a trapezoid which is symmetric."""
    # Create a sketch instance
    sketch = Sketch()

    # Create a trapezoid and plot
    sketch.trapezoid(10, 2, np.pi / 4, tag="Trapezoid-symmetric")
    sketch.select("Trapezoid-symmetric")
    sketch.plot_selection(
        view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_trapezoid_sym.png")
    )


@skip_no_xserver
def test_plot_circle(verify_image_cache):
    """Test plotting of a circle."""
    # Create a sketch instance
    sketch = Sketch()

    # Create a circle and plot
    sketch.circle(
        Point2D([0, 1], DEFAULT_UNITS.LENGTH), Quantity(2, DEFAULT_UNITS.LENGTH), "Circle"
    )
    sketch.select("Circle")
    sketch.plot_selection(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_circle.png"))


@skip_no_xserver
def test_plot_ellipse(verify_image_cache):
    """Test plotting of an ellipse."""
    # Create a sketch instance
    sketch = Sketch()

    # Create a ellipse and plot
    sketch.ellipse(
        Point2D([0, 0], UNITS.m), Quantity(2, UNITS.m), Quantity(1, UNITS.m), tag="Ellipse"
    )
    sketch.select("Ellipse")
    sketch.plot_selection(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_ellipse.png"))


@skip_no_xserver
def test_plot_slot(verify_image_cache):
    """Test plotting of a slot."""
    # Create a sketch instance
    sketch = Sketch()

    # Create a slot and plot
    sketch.slot(
        Point2D([2, 3], unit=UNITS.meter),
        Distance(4, unit=UNITS.meter),
        Distance(2, unit=UNITS.meter),
        tag="Slot",
    )
    sketch.select("Slot")
    sketch.plot_selection(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_slot.png"))


@skip_no_xserver
def test_plot_box(verify_image_cache):
    """Test plotting of a box."""
    # Create a sketch instance
    sketch = Sketch()

    # Create a box and plot
    sketch.box(
        Point2D([3, 1], unit=UNITS.meter),
        Distance(4, unit=UNITS.meter),
        Distance(2, unit=UNITS.meter),
        tag="Box",
    )
    sketch.select("Box")
    sketch.plot_selection(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_box.png"))


@skip_no_xserver
def test_plot_dummy_gear(verify_image_cache):
    """Test plotting of a dummy gear."""
    # Create a sketch instance
    sketch = Sketch()

    # Create a gear
    sketch.dummy_gear(
        Point2D([3, 1], unit=UNITS.meter),
        Distance(4, unit=UNITS.meter),
        Distance(3.8, unit=UNITS.meter),
        30,
        tag="Gear",
    )
    sketch.select("Gear")
    sketch.plot_selection(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_dummy_gear.png"))


@skip_no_xserver
def test_extrude_dummy_gear(modeler: Modeler, verify_image_cache):
    """Test plotting and extrusion of a dummy gear."""
    # Create a sketch instance
    sketch = Sketch()

    # Create a gear
    sketch.dummy_gear(
        Point2D([3, 1], unit=UNITS.meter),
        Distance(4, unit=UNITS.meter),
        Distance(3.8, unit=UNITS.meter),
        30,
        tag="Gear",
    )
    sketch.circle(Point2D([3, 1], unit=UNITS.meter), Distance(1, unit=UNITS.meter), tag="Circle")

    # Create your design on the server side
    design = modeler.create_design("GearExtrusions")

    # Extrude the sketch to create a body
    box_body = design.extrude_sketch("GearExtruded", sketch, Quantity(500, UNITS.mm))

    # Test the plotting of the body
    box_body.plot(screenshot=Path(IMAGE_RESULTS_DIR, "plot_extrude_dummy_gear.png"))


@skip_no_xserver
def test_plot_spur_gear(verify_image_cache):
    """Test plotting of a spur gear."""
    # Create a sketch instance
    sketch = Sketch()

    # Create a spur gear
    center = Point2D([0, 0], unit=UNITS.meter)
    sketch.spur_gear(
        center, module=6, pressure_angle=Quantity(20, UNITS.deg), n_teeth=22, tag="SpurGear"
    )

    # Plot
    sketch.select("SpurGear")
    sketch.plot_selection(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_spur_gear.png"))


@skip_no_xserver
def test_extrude_spur_gear(modeler: Modeler, verify_image_cache):
    """Test plotting and extrusion of a spur gear."""
    # Create a sketch instance
    sketch = Sketch()

    # Create a spur gear
    center = Point2D([0, 0], unit=UNITS.meter)
    sketch.spur_gear(center, module=6, pressure_angle=Quantity(20, UNITS.deg), n_teeth=22)
    sketch.circle(center, Distance(10, unit=UNITS.mm), tag="Circle")

    # Create your design on the server side
    design = modeler.create_design("SpurGearExtrusions")

    # Extrude the sketch to create a body
    box_body = design.extrude_sketch("SpurGearExtruded", sketch, Quantity(50, UNITS.mm))

    # Test the plotting of the body
    box_body.plot(screenshot=Path(IMAGE_RESULTS_DIR, "plot_extrude_spur_gear.png"))


@skip_no_xserver
def test_plot_sketch_scene(verify_image_cache):
    """Test plotting a sketch in the scene."""
    # Create a sketch
    sketch = Sketch()
    sketch.polygon(Point2D([0, 0], UNITS.m), Quantity(2, UNITS.m), sides=5)
    sketch.segment(Point2D([0, 2]), Point2D([2, 0]), "Segment")

    # Initialize the ``Plotter`` class
    pl = GeometryPlotter()

    # Showing the plane of the sketch and its frame.
    pl.add_sketch(sketch=sketch, show_frame=True, show_plane=True)
    pl.show(screenshot=Path(IMAGE_RESULTS_DIR, "plot_sketch_scene.png"))


def test_visualization_polydata():
    """Test the VTK polydata representation for PyVista visualization."""
    # Test for polygon visualization polydata
    polygon = Polygon(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), sides=5)
    assert polygon.visualization_polydata.center == pytest.approx(
        ([0.01095491, 0.0099999998, 0.0]),
        rel=1e-6,
        abs=1e-8,
    )
    assert polygon.visualization_polydata.bounds == pytest.approx(
        [
            0.0019098299089819193,
            0.019999999552965164,
            0.0004894344601780176,
            0.01951056532561779,
            0.0,
            0.0,
        ],
        rel=1e-6,
        abs=1e-8,
    )
    assert polygon.visualization_polydata.n_cells == 2
    assert polygon.visualization_polydata.n_points == 5
    assert polygon.visualization_polydata.n_open_edges == 5

    # Test for arc visualization polydata
    arc = Arc(Point2D([10, 10]), Point2D([10, -10]), Point2D([10, 0]))
    assert arc.visualization_polydata.center == pytest.approx([5.0, 0.0, 0.0])
    assert arc.visualization_polydata.bounds == pytest.approx([0.0, 10.0, -10.0, 10.0, 0.0, 0.0])
    assert arc.visualization_polydata.n_cells == 2
    assert arc.visualization_polydata.n_points == 202
    assert arc.visualization_polydata.n_open_edges == 0

    # Test for segment visualization polydata
    segment = SketchSegment(Point2D([3, 2]), Point2D([2, 0]))
    assert segment.visualization_polydata.center == pytest.approx([2.5, 1.0, 0.0])
    assert segment.visualization_polydata.bounds == pytest.approx([2.0, 3.0, 0.0, 2.0, 0.0, 0.0])
    assert segment.visualization_polydata.n_cells == 1
    assert segment.visualization_polydata.n_points == 2
    assert segment.visualization_polydata.n_open_edges == 0

    # Test for slot visualization polydata
    slot = Slot(
        Point2D([2, 3], unit=UNITS.meter),
        Distance(4, unit=UNITS.meter),
        Distance(2, unit=UNITS.meter),
    )
    assert slot.visualization_polydata
    assert slot.visualization_polydata.bounds == pytest.approx([0.0, 4.0, 2.0, 4.0, 0.0, 0.0])
    assert slot.visualization_polydata.center == pytest.approx([2.0, 3.0, 0.0])
    # Two arcs and segments creates the slot, thus it should have 6 faces
    assert slot.visualization_polydata.n_cells == 6
    assert slot.visualization_polydata.n_points == 402
    assert slot.visualization_polydata.n_open_edges == 0

    # Test for triangle visualization polydata
    triangle = Triangle(Point2D([10, 10]), Point2D([2, 1]), Point2D([10, -10]))
    assert triangle.visualization_polydata.center == pytest.approx([6.0, 0.0, 0.0])
    assert triangle.visualization_polydata.bounds == pytest.approx(
        [2.0, 10.0, -10.0, 10.0, 0.0, 0.0]
    )
    assert triangle.visualization_polydata.n_cells == 1
    assert triangle.visualization_polydata.n_points == 3
    assert triangle.visualization_polydata.n_open_edges == 3

    # Test for trapezoid visualization polydata
    trapezoid = Trapezoid(10, 2, np.pi / 4, np.pi / 8, Point2D([10, -10]))
    assert trapezoid.visualization_polydata.center == pytest.approx(
        ([10.0, -10.0, 0.0]),
        rel=1e-6,
        abs=1e-8,
    )
    assert trapezoid.visualization_polydata.bounds == pytest.approx(
        [5.0, 15.0, -11.0, -9.0, 0.0, 0.0],
        rel=1e-6,
        abs=1e-8,
    )
    assert trapezoid.visualization_polydata.n_cells == 1
    assert trapezoid.visualization_polydata.n_points == 4
    assert trapezoid.visualization_polydata.n_open_edges == 4

    # Test for circle visualization polydata
    circle = SketchCircle(
        Point2D([10, -10], DEFAULT_UNITS.LENGTH), Quantity(1, DEFAULT_UNITS.LENGTH)
    )
    assert circle.visualization_polydata.center == pytest.approx([10.0, -10.0, 0.0])
    assert circle.visualization_polydata.bounds == pytest.approx([9.0, 11.0, -11.0, -9.0, 0.0, 0.0])
    assert circle.visualization_polydata.n_cells == 1
    assert circle.visualization_polydata.n_points == 100
    assert circle.visualization_polydata.n_open_edges == 100

    # Test for ellipse visualization polydata
    ellipse = SketchEllipse(Point2D([0, 0], UNITS.m), Quantity(1, UNITS.m), Quantity(1, UNITS.m))
    assert ellipse.visualization_polydata.center == pytest.approx([0.0, 0.0, 0.0])
    assert ellipse.visualization_polydata.bounds == pytest.approx([-1.0, 1.0, -1.0, 1.0, 0.0, 0.0])
    assert ellipse.visualization_polydata.n_cells == 1
    assert ellipse.visualization_polydata.n_points == 100
    assert ellipse.visualization_polydata.n_open_edges == 100

    # Test for box visualization polydata
    box = Box(
        Point2D([3, 1], unit=UNITS.meter),
        Distance(4, unit=UNITS.meter),
        Distance(2, unit=UNITS.meter),
    )
    assert box.visualization_polydata.center == pytest.approx([3.0, 1.0, 0.0])
    assert box.visualization_polydata.bounds == pytest.approx([1.0, 5.0, 0.0, 2.0, 0.0, 0.0])
    assert box.visualization_polydata.n_cells == 1
    assert box.visualization_polydata.n_points == 4
    assert box.visualization_polydata.n_open_edges == 4


@skip_no_xserver
def test_plot_design_point(modeler: Modeler, verify_image_cache):
    """Test the plotting of DesignPoint objects."""
    design = modeler.create_design("Multiplot")
    plot_list = []

    # add body to check compatibility
    body_sketch = Sketch()
    body_sketch.box(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))
    box_body = design.extrude_sketch("JustABox", body_sketch, Quantity(10, UNITS.m))
    plot_list.append(box_body)

    # add single point
    point_set_2 = [Point3D([10, 10, 10], UNITS.m), Point3D([20, 20, 20], UNITS.m)]

    # add list of points
    design_points_2 = design.add_design_points("SecondPointSet", point_set_2)
    plot_list.extend(design_points_2)

    # plot
    pl = GeometryPlotter()
    pl.plot(plot_list)
    pl.show(
        screenshot=Path(IMAGE_RESULTS_DIR, "test_plot_design_point.png"),
    )


@skip_no_xserver
def test_plot_revolve_sketch_normal(modeler: Modeler, verify_image_cache):
    """Test plotting of a sketch revolved around an axis."""
    # Initialize the donut sketch design
    design = modeler.create_design("quarter-donut")

    # Donut parameters
    path_radius = 5
    profile_radius = 2

    # Create the circular profile on the XZ plane centered at (5, 0, 0)
    # with a radius of 2
    plane_profile = Plane(
        origin=Point3D([path_radius, 0, 0]), direction_x=UNITVECTOR3D_X, direction_y=UNITVECTOR3D_Z
    )
    profile = Sketch(plane=plane_profile)
    profile.circle(Point2D([0, 0]), profile_radius)

    # Revolve the profile around the Z axis and center in the absolute origin
    # for an angle of 90 degrees
    design.revolve_sketch(
        "donut-body",
        sketch=profile,
        axis=UNITVECTOR3D_Z,
        angle=Angle(90, unit=UNITS.degrees),
        rotation_origin=Point3D([0, 0, 0]),
    )

    # plot
    pl = GeometryPlotter()
    pl.plot(design)
    pl.show(
        screenshot=Path(IMAGE_RESULTS_DIR, "test_plot_revolve_sketch_normal.png"),
    )


@skip_no_xserver
def test_plot_revolve_sketch_negative_angle(modeler: Modeler, verify_image_cache):
    """Test plotting of a sketch revolved around an axis with a negative
    angle.
    """
    # Initialize the donut sketch design
    design = modeler.create_design("quarter-donut")

    # Specify donut parameters
    path_radius = 5
    profile_radius = 2

    # Create the circular profile on the XZ plane centered at (5, 0, 0)
    # with a radius of 2
    plane_profile = Plane(
        origin=Point3D([path_radius, 0, 0]), direction_x=UNITVECTOR3D_X, direction_y=UNITVECTOR3D_Z
    )
    profile = Sketch(plane=plane_profile)
    profile.circle(Point2D([0, 0]), profile_radius)

    # Revolve the profile around the Z axis and centered in the absolute origin
    # for an angle of 90 degrees
    design.revolve_sketch(
        "donut-body-negative",
        sketch=profile,
        axis=UNITVECTOR3D_Z,
        angle=Angle(-90, unit=UNITS.degrees),
        rotation_origin=Point3D([0, 0, 0]),
    )

    # plot
    pl = GeometryPlotter()
    pl.plot(design)
    pl.show(
        screenshot=Path(IMAGE_RESULTS_DIR, "test_plot_revolve_sketch_negative_angle.png"),
    )


@skip_no_xserver
def test_plot_server_colors_on_design(
    modeler: Modeler, use_service_colors: None, verify_image_cache
):
    """Test plotting of a design with server colors."""
    # The following design is created:
    #
    #  - From our main design we have a component that contains 3 boxes
    #  - This component has at the same time another subcomponent that contains 3 boxes
    #  - Each box has a different color
    #  - Boxes are 10x10x10 in size (meters by default) and the center of their
    #    lower bases are placed at:
    #      - Component (i.e. Component0): (0, 30, 0), (30, 30, 0) and (60, 30, 0)
    #      - Subcomponent (i.e. Component1): (0, 60, 0), (30, 60, 0) and (60, 60, 0)
    translate = [[0, 30, 60], [0, 30, 60]]
    colors = [["red", "blue", "yellow"], ["orange", "green", "purple"]]

    design = modeler.create_design("ServerColorsDesign")

    # Generic sketch for all boxes to be extruded with
    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 10, 10)

    comp = design
    for r_idx, row in enumerate(translate):
        comp = comp.add_component(f"Component{r_idx}")
        for b_idx, dist in enumerate(row):
            body = comp.extrude_sketch(f"Component{r_idx}_Body{b_idx}", sketch, distance=10)
            body.translate(UNITVECTOR3D_Y, (r_idx + 1) * 30)
            body.translate(UNITVECTOR3D_X, dist)

            # Assign color to the body
            body.color = colors[r_idx][b_idx]

    # Test the plotting of the design
    design.plot(screenshot=Path(IMAGE_RESULTS_DIR, "plot_server_colors_on_design.png"))


@skip_no_xserver
def test_plot_server_color_on_single_body(
    modeler: Modeler, use_service_colors: None, verify_image_cache
):
    """Test plotting of a single body with server colors."""
    design = modeler.create_design("ServerColorsBody")

    # Generic sketch for all boxes to be extruded with
    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 10, 10)
    body = design.extrude_sketch("BodyColored", sketch, distance=10)
    body.color = "red"

    body.plot(screenshot=Path(IMAGE_RESULTS_DIR, "plot_server_color_on_single_body.png"))


@skip_no_xserver
def test_plot_server_colors_on_design_using_input(
    modeler: Modeler, use_service_colors: None, verify_image_cache
):
    """Test plotting of a design with server colors (via argument)."""
    # The following design is created:
    #
    #  - From our main design we have a component that contains 3 boxes
    #  - This component has at the same time another subcomponent that contains 3 boxes
    #  - Each box has a different color
    #  - Boxes are 10x10x10 in size (meters by default) and the center of their
    #    lower bases are placed at:
    #      - Component (i.e. Component0): (0, 30, 0), (30, 30, 0) and (60, 30, 0)
    #      - Subcomponent (i.e. Component1): (0, 60, 0), (30, 60, 0) and (60, 60, 0)
    translate = [[0, 30, 60], [0, 30, 60]]
    colors = [["red", "blue", "yellow"], ["orange", "green", "purple"]]

    design = modeler.create_design("ServerColorsDesignUsingInput")

    # Generic sketch for all boxes to be extruded with
    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 10, 10)

    comp = design
    for r_idx, row in enumerate(translate):
        comp = comp.add_component(f"Component{r_idx}")
        for b_idx, dist in enumerate(row):
            body = comp.extrude_sketch(f"Component{r_idx}_Body{b_idx}", sketch, distance=10)
            body.translate(UNITVECTOR3D_Y, (r_idx + 1) * 30)
            body.translate(UNITVECTOR3D_X, dist)

            # Assign color to the body
            body.color = colors[r_idx][b_idx]

    # Test the plotting of the design
    design.plot(
        screenshot=Path(IMAGE_RESULTS_DIR, "plot_server_colors_on_design_using_input.png"),
        use_service_colors=True,
    )


@skip_no_xserver
def test_plot_server_color_on_single_body_using_input(modeler: Modeler, verify_image_cache):
    """Test plotting of a single body with server colors (via argument)."""
    design = modeler.create_design("ServerColorsBodyUsingInput")

    # Generic sketch for all boxes to be extruded with
    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 10, 10)
    body = design.extrude_sketch("BodyColored", sketch, distance=10)
    body.color = "red"

    body.plot(
        screenshot=Path(IMAGE_RESULTS_DIR, "plot_server_color_on_single_body_using_input.png"),
        use_service_colors=True,
    )


@skip_no_xserver
def test_plot_design_multi_colors(modeler: Modeler, verify_image_cache):
    """Test plotting of design with/without multi_colors."""
    design = modeler.create_design("DesignMultiColors")
    # Create a sketch of a box
    sketch_box = Sketch().box(
        Point2D([0, 0], unit=UNITS.m), width=30 * UNITS.m, height=40 * UNITS.m
    )

    # Create a sketch of a circle (overlapping the box slightly)
    sketch_circle = Sketch().circle(Point2D([20, 0], unit=UNITS.m), radius=3 * UNITS.m)

    # Extrude both sketches to get a prism and a cylinder
    design.extrude_sketch("Prism", sketch_box, 50 * UNITS.m)
    design.extrude_sketch("Cylinder", sketch_circle, 50 * UNITS.m)

    # Design plotting
    design.plot(
        screenshot=Path(IMAGE_RESULTS_DIR, "plot_design_multi_colors.png"),
        multi_colors=True,
    )

    design.plot(
        screenshot=Path(IMAGE_RESULTS_DIR, "plot_design_multi_colors_single_color.png"),
        multi_colors=False,
    )


@skip_no_xserver
def test_plot_design_face_colors(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test plotting of design with/without multi_colors."""
    design = modeler.create_design("DesignFaceColors")
    # Create a sketch of a box
    sketch_box = Sketch().box(
        Point2D([0, 0], unit=UNITS.m), width=10 * UNITS.m, height=10 * UNITS.m
    )

    # Extrude both sketches to get a prism and change face colors
    design.extrude_sketch("Prism", sketch_box, 10 * UNITS.m)
    design.bodies[0].faces[0].set_color((255, 0, 0))
    design.bodies[0].faces[1].set_color((0, 255, 0))
    design.bodies[0].faces[2].set_color((0, 0, 255))

    # Define file name for screenshot
    screenshot_path = (
        tmp_path_factory.mktemp("test_plot_design_face_colors") / "plot_design_face_colors.png"
    )

    # Assert that the file does not exist before plotting
    assert not screenshot_path.exists()

    # Design plotting
    design.bodies[0].plot(
        screenshot=screenshot_path,
        merge=False,
        multi_colors=True,  # Results are random and thus we cannot compare screenshots easily
    )

    # Assert that the file exists after plotting
    assert screenshot_path.exists()


@skip_no_xserver
def test_export_glb(modeler: Modeler):
    """Test exporting a box to glb."""
    # Create a Sketch
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design = modeler.create_design("GLBBox")

    # Extrude the sketch to create a body
    box_body = design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.mm))

    pl = GeometryPlotter()
    pl.plot(box_body)

    output_glb_path = Path(IMAGE_RESULTS_DIR, "plot_box_glb")
    pl.export_glb(filename=output_glb_path)

    tempglb = pl.export_glb(filename=None)
    assert tempglb.exists()

    # Add suffix to the output path
    output_glb_path = output_glb_path.with_suffix(".glb")
    assert output_glb_path.exists(), "GLB file was not created successfully."

    # Delete the temporary GLB file
    tempglb.unlink(missing_ok=True)


@skip_no_xserver
def test_export_glb_with_color(modeler: Modeler):
    """Test exporting a box to glb."""
    # Create a Sketch
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design = modeler.create_design("GLBBoxWithColor")

    # Extrude the sketch to create a body
    box_body = design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.mm))
    box_body.set_color((255, 0, 0))

    pl = GeometryPlotter(use_service_colors=True)
    pl.plot(box_body)

    output_glb_path = Path(IMAGE_RESULTS_DIR, "plot_box_glb_colored.glb")
    pl.export_glb(filename=output_glb_path)

    assert output_glb_path.exists(), "GLB file with color was not created successfully."


@skip_no_xserver
def test_export_glb_with_face_color(modeler: Modeler):
    """Test exporting a box to glb."""
    # Create a Sketch
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))

    # Create your design on the server side
    design = modeler.create_design("GLBBoxWithFaceColors")

    # Extrude the sketch to create a body
    box_body = design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.m))
    box_body.set_color((255, 0, 0))
    box_body.faces[0].set_color((0, 0, 255))
    box_body.faces[1].set_color((0, 255, 0))

    pl = GeometryPlotter(use_service_colors=True)

    output_glb_path = Path(IMAGE_RESULTS_DIR, "plot_box_glb_face_colored.glb")
    pl.export_glb(box_body, filename=output_glb_path)

    assert output_glb_path.exists(), "GLB file with face color was not created successfully."


@skip_no_xserver
def test_export_glb_cylinder_with_face_color(modeler: Modeler):
    """Test exporting a cylinder to glb."""
    # Create your design on the server side
    design = modeler.create_design("GLBCylinderWithFaceColors")

    # Create a sketch of a circle (overlapping the box slightly)
    sketch_circle = Sketch().circle(Point2D([20, 0], unit=UNITS.m), radius=3 * UNITS.m)
    cyl = design.extrude_sketch("Cylinder", sketch_circle, 50 * UNITS.m)

    cyl.set_color((255, 0, 0))
    cyl.faces[0].set_color((0, 0, 255))
    cyl.faces[1].set_color((0, 255, 0))

    pl = GeometryPlotter(use_service_colors=True)

    output_glb_path = Path(IMAGE_RESULTS_DIR, "plot_cylinder_glb_face_colored.glb")
    pl.export_glb(cyl, filename=output_glb_path)

    assert output_glb_path.exists(), "GLB file with face color was not created successfully."


@skip_no_xserver
def test_plot_face_colors_from_service(modeler: Modeler, verify_image_cache):
    """Test exporting a box to glb."""
    # Create a Sketch
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))

    # Create your design on the server side
    design = modeler.create_design("BoxWithColors")

    # Extrude the sketch to create a body
    box_body = design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.m))
    # Box at large - Red
    box_body.set_color((255, 0, 0))

    for face in box_body.faces:
        # A) +Z face - Green
        if face.normal() == UNITVECTOR3D_Z:
            face.set_color((0, 255, 0))
        # B) +X face - Blue
        elif face.normal() == UNITVECTOR3D_X:
            face.set_color((0, 0, 255))

    box_body.plot(
        screenshot=Path(IMAGE_RESULTS_DIR, "test_plot_face_colors_from_service.png"),
        use_service_colors=True,
    )


@skip_no_xserver
def test_plot_single_face(modeler: Modeler, verify_image_cache):
    """Test plotting a single face."""
    # Create your design on the server side
    design = modeler.create_design("SingleFace")

    # Create a sketch of a box
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))

    # Extrude the sketch to create a body
    box_body = design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.m))

    # Test the plotting of the body
    box_body.faces[1].plot(screenshot=Path(IMAGE_RESULTS_DIR, "plot_single_face.png"))


@skip_no_xserver
def test_plot_single_face_with_service_color(
    modeler: Modeler, use_service_colors: None, verify_image_cache
):
    """Test plotting a single face with service colors."""
    # Create your design on the server side
    design = modeler.create_design("SingleFaceWithServiceColor")

    # Create a sketch of a box
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))

    # Extrude the sketch to create a body
    box_body = design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.m))

    # Assign color to the body
    box_body.color = "red"

    # Test the plotting of the body
    box_body.faces[1].plot(
        screenshot=Path(IMAGE_RESULTS_DIR, "plot_single_face_with_service_color.png")
    )


@skip_no_xserver
def test_plot_with_body_opacity(modeler: Modeler, verify_image_cache):
    """Test plotting a body with decreased opacity."""
    # Create your design on the server side
    design = modeler.create_design("BoxWithOpacity")

    # Create a sketch of a box
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))

    # Extrude the sketch to create a body
    box_body = design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.m))

    # Assign color to the body
    box_body.color = (255, 0, 0, 80)

    # Test the plotting of the body
    box_body.plot(
        screenshot=Path(IMAGE_RESULTS_DIR, "plot_box_with_opacity.png"), use_service_colors=True
    )


@skip_no_xserver
def test_plot_with_face_opacity(modeler: Modeler, verify_image_cache):
    """Test plotting a body with decreased opacity."""
    # Create your design on the server side
    design = modeler.create_design("BoxWithOpacity")

    # Create a sketch of a box
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))

    # Extrude the sketch to create a body
    box_body = design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.m))

    # Assign color to the body - On all + X, Y, Z faces
    for face in box_body.faces:
        normal = face.normal()
        if normal == UNITVECTOR3D_X or normal == UNITVECTOR3D_Y or normal == UNITVECTOR3D_Z:
            face.color = (255, 0, 0, 80)

    # Test the plotting of the body
    box_body.plot(
        screenshot=Path(IMAGE_RESULTS_DIR, "plot_face_with_opacity.png"), use_service_colors=True
    )


@skip_no_xserver
def test_plot_datum_plane(modeler: Modeler, verify_image_cache):
    """Test plotting a datum plane."""
    # Create your design on the server side
    design = modeler.create_design("DatumPlane")

    # Create a datum plane with custom orientation
    plane = Plane(
        origin=Point3D([0, 0, 10], UNITS.m),
        direction_x=UnitVector3D([0.6, 0.8, 0]),
        direction_y=UnitVector3D([-0.8, 0.6, 1]),
    )
    datum_plane = design.create_datum_plane("OffsetPlane", plane)

    # Plot the datum plane
    pl = GeometryPlotter()
    pl.plot(datum_plane)
    pl.show(screenshot=Path(IMAGE_RESULTS_DIR, "test_plot_datum_plane.png"))
