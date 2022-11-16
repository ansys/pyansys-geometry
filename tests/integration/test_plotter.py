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
def test_plot_design(modeler: Modeler):
    # Create a Sketch
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design_name = "BoxExtrusions"
    design = modeler.create_design(design_name)

    # Extrude the sketch to create a Body
    box_body = design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.mm))
    design.plot()
    box_body.plot()


@skip_no_xserver
def test_plot_sketch():
    sketch = Sketch()
    sketch.polygon(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), sides=5)
    sketch.plot_selection()
    sketch.segment(Point2D([3, 2]), Point2D([2, 0]), "Segment4")
    sketch.plot_selection()
    sketch.arc(Point2D([10, 10]), Point2D([10, -10]), Point2D([10, 0]), tag="Arc3")
    sketch.plot_selection()
    sketch.triangle(Point2D([10, 10]), Point2D([2, 1]), Point2D([10, -10]), tag="triangle1")
    sketch.plot_selection()
    sketch.trapezoid(10, 8, np.pi / 4, np.pi / 8, Point2D([10, -10]), tag="trapezoid1")
    sketch.plot_selection()
    center, radius = (
        Point2D([10, -10], UNIT_LENGTH),
        (1 * UNIT_LENGTH),
    )
    sketch.circle(center, radius, "Circle")
    sketch.plot_selection()
    semi_major, semi_minor, origin = 2 * UNITS.m, 1 * UNITS.m, Point2D([0, 0], UNITS.m)
    sketch.ellipse(origin, semi_major, semi_minor, tag="Ellipse")
    sketch.plot_selection()
    center = Point2D([2, 3], unit=UNITS.meter)
    width = Distance(4, unit=UNITS.meter)
    height = Distance(2, unit=UNITS.meter)
    sketch.slot(center, width, height)
    sketch.plot_selection()
    center = Point2D([3, 1], unit=UNITS.meter)
    width = Distance(4, unit=UNITS.meter)
    height = Distance(2, unit=UNITS.meter)
    sketch.box(center, width, height)
    sketch.plot_selection()
    sketch.plot()


@skip_no_xserver
def test_plot_sketch_scene():
    sketch = Sketch()
    sketch.polygon(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), sides=5)
    sketch.segment(Point2D([3, 2]), Point2D([2, 0]), "Segment4")
    pl = Plotter()
    pl.plot_sketch(sketch=sketch, show_frame=True, show_plane=True)
    pl.scene.show()
