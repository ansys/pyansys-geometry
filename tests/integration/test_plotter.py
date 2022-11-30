from pathlib import Path

import numpy as np
from pint import Quantity
import pytest
from pyvista.plotting import system_supports_plotting

from ansys.geometry.core import Modeler
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import UNIT_LENGTH, UNITS, Distance
from ansys.geometry.core.plotting import Plotter
from ansys.geometry.core.sketch import (
    Arc,
    Box,
    Circle,
    Ellipse,
    Polygon,
    Segment,
    Sketch,
    Slot,
    Trapezoid,
    Triangle,
)

skip_no_xserver = pytest.mark.skipif(
    not system_supports_plotting(), reason="Requires active X Server"
)

IMAGE_RESULTS_DIR = Path(Path(__file__).parent, "image_cache", "results")


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
    sketch.trapezoid(10, 8, np.pi / 4, np.pi / 8, Point2D([10, -10]), tag="Trapezoid")
    sketch.select("Trapezoid")
    sketch.plot_selection(view_2d=True, screenshot=Path(IMAGE_RESULTS_DIR, "plot_trapezoid.png"))


@skip_no_xserver
def test_plot_circle(verify_image_cache):
    """Test plotting of a circle."""

    # Create a sketch instance
    sketch = Sketch()

    # Create a circle and plot
    sketch.circle(Point2D([0, 1], UNIT_LENGTH), Quantity(2, UNIT_LENGTH), "Circle")
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
def test_plot_sketch_scene(verify_image_cache):
    """Test plotting a sketch in the scene."""

    # Create a sketch
    sketch = Sketch()
    sketch.polygon(Point2D([0, 0], UNITS.m), Quantity(2, UNITS.m), sides=5)
    sketch.segment(Point2D([0, 2]), Point2D([2, 0]), "Segment")

    # Initialize the ``Plotter`` class
    pl = Plotter()

    # Showing the plane of the sketch and its frame.
    pl.plot_sketch(sketch=sketch, show_frame=True, show_plane=True)
    pl.scene.show(screenshot=Path(IMAGE_RESULTS_DIR, "plot_sketch_scene.png"))


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
    assert polygon.visualization_polydata.n_faces == 2
    assert polygon.visualization_polydata.n_cells == 2
    assert polygon.visualization_polydata.n_points == 5
    assert polygon.visualization_polydata.n_open_edges == 5

    # Test for arc visualization polydata
    arc = Arc(Point2D([10, 0]), Point2D([10, 10]), Point2D([10, -10]))
    assert arc.visualization_polydata.center == ([5.0, 0.0, 0.0])
    assert arc.visualization_polydata.bounds == pytest.approx(
        [0.0, 10.0, -10.0, 10.0, 0.0, 0.0],
        rel=1e-6,
        abs=1e-8,
    )
    assert arc.visualization_polydata.n_faces == 2
    assert arc.visualization_polydata.n_cells == 2
    assert arc.visualization_polydata.n_points == 202
    assert arc.visualization_polydata.n_open_edges == 0

    # Test for segment visualization polydata
    segment = Segment(Point2D([3, 2]), Point2D([2, 0]))
    assert segment.visualization_polydata.center == ([2.5, 1.0, 0.0])
    assert segment.visualization_polydata.bounds == pytest.approx(
        [2.0, 3.0, 0.0, 2.0, 0.0, 0.0],
        rel=1e-6,
        abs=1e-8,
    )
    assert segment.visualization_polydata.n_faces == 1
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
    assert slot.visualization_polydata.bounds == pytest.approx(
        [0.0, 4.0, 2.0, 4.0, 0.0, 0.0],
        rel=1e-6,
        abs=1e-8,
    )
    assert slot.visualization_polydata.center == ([2.0, 3.0, 0.0])
    # Two arcs and segments creates the slot, thus it should have 6 faces
    assert slot.visualization_polydata.n_faces == 6
    assert slot.visualization_polydata.n_cells == 6
    assert slot.visualization_polydata.n_points == 402
    assert slot.visualization_polydata.n_open_edges == 0

    # Test for triangle visualization polydata
    triangle = Triangle(Point2D([10, 10]), Point2D([2, 1]), Point2D([10, -10]))
    assert triangle.visualization_polydata.center == ([6.0, 0.0, 0.0])
    assert triangle.visualization_polydata.bounds == pytest.approx(
        [2.0, 10.0, -10.0, 10.0, 0.0, 0.0],
        rel=1e-6,
        abs=1e-8,
    )
    assert triangle.visualization_polydata.n_faces == 1
    assert triangle.visualization_polydata.n_cells == 1
    assert triangle.visualization_polydata.n_points == 3
    assert triangle.visualization_polydata.n_open_edges == 3

    # Test for trapezoid visualization polydata
    trapezoid = Trapezoid(10, 8, np.pi / 4, np.pi / 8, Point2D([10, -10]))
    assert trapezoid.visualization_polydata.center == pytest.approx(
        ([5.34314575050762, -10.0, 0.0]),
        rel=1e-6,
        abs=1e-8,
    )
    assert trapezoid.visualization_polydata.bounds == pytest.approx(
        [-4.313708498984759, 15.0, -14.0, -6.0, 0.0, 0.0],
        rel=1e-6,
        abs=1e-8,
    )
    assert trapezoid.visualization_polydata.n_faces == 1
    assert trapezoid.visualization_polydata.n_cells == 1
    assert trapezoid.visualization_polydata.n_points == 4
    assert trapezoid.visualization_polydata.n_open_edges == 4

    # Test for circle visualization polydata
    circle = Circle(Point2D([10, -10], UNIT_LENGTH), Quantity(1, UNIT_LENGTH))
    assert circle.visualization_polydata.center == pytest.approx(
        ([10.000251728808408, -10.0, 0.0]),
        rel=1e-6,
        abs=1e-8,
    )
    assert circle.visualization_polydata.bounds == pytest.approx(
        [9.000503457616816, 11.0, -10.999874127673875, -9.000125872326125, 0.0, 0.0],
        rel=1e-6,
        abs=1e-8,
    )
    assert circle.visualization_polydata.n_faces == 1
    assert circle.visualization_polydata.n_cells == 1
    assert circle.visualization_polydata.n_points == 100
    assert circle.visualization_polydata.n_open_edges == 100

    # Test for ellipse visualization polydata
    ellipse = Ellipse(Point2D([0, 0], UNITS.m), Quantity(1, UNITS.m), Quantity(1, UNITS.m))
    assert ellipse.visualization_polydata.center == pytest.approx(
        ([0.0002517288084074587, 0.0, 0.0]),
        rel=1e-6,
        abs=1e-8,
    )
    assert ellipse.visualization_polydata.bounds == pytest.approx(
        [-0.9994965423831851, 1.0, -0.9998741276738751, 0.9998741276738751, 0.0, 0.0],
        rel=1e-6,
        abs=1e-8,
    )
    assert ellipse.visualization_polydata.n_faces == 1
    assert ellipse.visualization_polydata.n_cells == 1
    assert ellipse.visualization_polydata.n_points == 100
    assert ellipse.visualization_polydata.n_open_edges == 100

    # Test for box visualization polydata
    box = Box(
        Point2D([3, 1], unit=UNITS.meter),
        Distance(4, unit=UNITS.meter),
        Distance(2, unit=UNITS.meter),
    )
    assert box.visualization_polydata.center == ([3.0, 1.0, 0.0])
    assert box.visualization_polydata.bounds == pytest.approx(
        [1.0, 5.0, 0.0, 2.0, 0.0, 0.0],
        rel=1e-6,
        abs=1e-8,
    )
    assert box.visualization_polydata.n_faces == 1
    assert box.visualization_polydata.n_cells == 1
    assert box.visualization_polydata.n_points == 4
    assert box.visualization_polydata.n_open_edges == 4
