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


@skip_no_xserver
def test_body_plot(modeler: Modeler):
    """Test plotting the body."""

    # Create a Sketch
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design_name = "BoxExtrusions"
    design = modeler.create_design(design_name)

    # Extrude the sketch to create a Body
    box_body = design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.mm))
    box_body.plot()


@skip_no_xserver
def test_component_plot(modeler: Modeler):
    """Test plotting the component."""

    # Create a Sketch
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(10, UNITS.mm))
    # Create your design on the server side
    design_name = "Box_Extrusion"
    design = modeler.create_design(design_name)

    # Extrude the sketch to create a Body
    design.extrude_sketch("Box", sketch, Quantity(10, UNITS.mm))
    component_1 = design.add_component("Component")

    sketch_1 = Sketch()
    sketch_1.ellipse(Point2D([50, 50], UNITS.mm), Quantity(30, UNITS.mm), Quantity(10, UNITS.mm))
    component_1.create_surface("Component_Surface", sketch_1)

    # Test the plotting of the component
    design.plot()


@skip_no_xserver
def test_plot_sketches():

    # Create a Sketch instance
    sketch = Sketch()

    # Create a polygon and plot
    sketch.polygon(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), sides=5, tag="Polygon")
    sketch.select("Polygon")
    sketch.plot_selection()

    # Create a segment and plot
    sketch.segment(Point2D([3, 2]), Point2D([2, 0]), "Segment")
    sketch.select("Segment")
    sketch.plot_selection()

    # Create a arc and plot
    sketch.arc(Point2D([10, 10]), Point2D([10, -10]), Point2D([10, 0]), tag="Arc")
    sketch.select("Arc")
    sketch.plot_selection()

    # Create a triangle and plot
    sketch.triangle(Point2D([10, 10]), Point2D([2, 1]), Point2D([10, -10]), tag="Triangle")
    sketch.select("Triangle")
    sketch.plot_selection()

    # Create a trapezoid and plot
    sketch.trapezoid(10, 8, np.pi / 4, np.pi / 8, Point2D([10, -10]), tag="Trapezoid")
    sketch.select("Trapezoid")
    sketch.plot_selection()

    # Create a circle and plot
    sketch.circle(Point2D([10, -10], UNIT_LENGTH), Quantity(1, UNIT_LENGTH), "Circle")
    sketch.plot_selection()
    sketch.select("Circle")

    # Create a ellipse and plot
    sketch.ellipse(
        Point2D([0, 0], UNITS.m), Quantity(2, UNITS.m), Quantity(1, UNITS.m), tag="Ellipse"
    )
    sketch.plot_selection()
    sketch.select("Ellipse")

    # Create a slot and plot
    sketch.slot(
        Point2D([2, 3], unit=UNITS.meter),
        Distance(4, unit=UNITS.meter),
        Distance(2, unit=UNITS.meter),
        tag="Slot",
    )
    sketch.plot_selection()
    sketch.select("Slot")

    # Create a box and plot
    sketch.box(
        Point2D([3, 1], unit=UNITS.meter),
        Distance(4, unit=UNITS.meter),
        Distance(2, unit=UNITS.meter),
        tag="Box",
    )
    sketch.select("Box")
    sketch.plot_selection()

    # Plot the entire sketch instance
    sketch.plot()


@skip_no_xserver
def test_plot_sketch_scene():
    """Test plotting a sketch in the scene."""

    # Create a sketch
    sketch = Sketch()
    sketch.polygon(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), sides=5)
    sketch.segment(Point2D([3, 2]), Point2D([2, 0]), "Segment")

    # initialize the ``Plotter`` class
    pl = Plotter()

    # showing the plane of the sketch and its frame.
    pl.plot_sketch(sketch=sketch, show_frame=True, show_plane=True)
    pl.scene.show()


def test_visualization_polydata():
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
    assert slot.visualization_polydata.n_faces == 6
    assert slot.visualization_polydata.n_cells == 6
    assert slot.visualization_polydata.n_points == 402
    assert slot.visualization_polydata.n_open_edges == 0

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

    trapezoid = Trapezoid(10, 8, np.pi / 4, np.pi / 8, Point2D([10, -10]))
    assert trapezoid.visualization_polydata.center == ([5.34314575050762, -10.0, 0.0])
    assert trapezoid.visualization_polydata.bounds == pytest.approx(
        [-4.313708498984759, 15.0, -14.0, -6.0, 0.0, 0.0],
        rel=1e-6,
        abs=1e-8,
    )
    assert trapezoid.visualization_polydata.n_faces == 1
    assert trapezoid.visualization_polydata.n_cells == 1
    assert trapezoid.visualization_polydata.n_points == 4
    assert trapezoid.visualization_polydata.n_open_edges == 4

    circle = Circle(Point2D([10, -10], UNIT_LENGTH), Quantity(1, UNIT_LENGTH))
    assert circle.visualization_polydata.center == ([10.000251728808408, -10.0, 0.0])
    assert circle.visualization_polydata.bounds == pytest.approx(
        [9.000503457616816, 11.0, -10.999874127673875, -9.000125872326125, 0.0, 0.0],
        rel=1e-6,
        abs=1e-8,
    )
    assert circle.visualization_polydata.n_faces == 1
    assert circle.visualization_polydata.n_cells == 1
    assert circle.visualization_polydata.n_points == 100
    assert circle.visualization_polydata.n_open_edges == 100

    ellipse = Ellipse(Point2D([0, 0], UNITS.m), Quantity(1, UNITS.m), Quantity(1, UNITS.m))
    assert ellipse.visualization_polydata.center == ([0.0002517288084074587, 0.0, 0.0])
    assert ellipse.visualization_polydata.bounds == pytest.approx(
        [-0.9994965423831851, 1.0, -0.9998741276738751, 0.9998741276738751, 0.0, 0.0],
        rel=1e-6,
        abs=1e-8,
    )
    assert ellipse.visualization_polydata.n_faces == 1
    assert ellipse.visualization_polydata.n_cells == 1
    assert ellipse.visualization_polydata.n_points == 100
    assert ellipse.visualization_polydata.n_open_edges == 100

    box = Box(
        Point2D([3, 1], unit=UNITS.meter),
        Distance(4, unit=UNITS.meter),
        Distance(2, unit=UNITS.meter),
    )
    assert box.visualization_polydata.center == ([3.0, 1.0, 0.0])
    assert box.visualization_polydata.bounds == pytest.approx(
        [0.0, 10.0, -10.0, 10.0, 0.0, 0.0],
        rel=1e-6,
        abs=1e-8,
    )
    assert box.visualization_polydata.n_faces == 1
    assert box.visualization_polydata.n_cells == 1
    assert box.visualization_polydata.n_points == 4
    assert box.visualization_polydata.n_open_edges == 4
