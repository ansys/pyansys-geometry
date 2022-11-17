import numpy as np
from pint import Quantity
import pytest
from pyvista.plotting import system_supports_plotting

from ansys.geometry.core import Modeler
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import UNIT_LENGTH, UNITS, Distance
from ansys.geometry.core.plotting import Plotter
from ansys.geometry.core.sketch import Sketch

skip_no_xserver = pytest.mark.skipif(
    not system_supports_plotting(), reason="Requires active X Server"
)


@skip_no_xserver
def test_component_plot(modeler: Modeler):
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
def test_body_plot(modeler: Modeler):
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
        Point2D([0, 0]), UNITS.m, Quantity(2, UNITS.m), Quantity(1, UNITS.m), tag="Ellipse"
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
    sketch = Sketch()
    sketch.polygon(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), sides=5)
    sketch.segment(Point2D([3, 2]), Point2D([2, 0]), "Segment4")
    pl = Plotter()
    pl.plot_sketch(sketch=sketch, show_frame=True, show_plane=True)
    pl.scene.show()
