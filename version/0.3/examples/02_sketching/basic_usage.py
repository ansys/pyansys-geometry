# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Sketching: Basic usage
#
# This example shows how to use basic PyAnsys Geometry sketching capabilities.

# ## Perform required imports
#
# Perform the required imports.

from ansys.geometry.core.misc.units import UNITS as u
from ansys.geometry.core.sketch import Sketch
from ansys.geometry.core.plotting import Plotter

# ## Create a sketch
#
# Sketches are fundamental objects for drawing basic shapes like lines, segments, circles,
# ellipses, arcs, and polygons.
#
# You create a ``Sketch`` instance by defining a drawing plane. To define a plane, you
# declare a point and two fundamental orthogonal directions.

from ansys.geometry.core.math import Plane, Point2D, Point3D

# Define a plane for creating a sketch.

# +
# Define the origin point of the plane
origin = Point3D([1, 1, 1])

# Create a plane located in previous point with desired fundamental directions
plane = Plane(
    origin, direction_x=[1, 0, 0], direction_y=[0, -1, 1]
)

# Instantiate a new sketch object from previous plane
sketch = Sketch(plane)
# -

# ## Draw shapes
#
# To draw different shapes in the sketch, you use ``draw`` methods.

# ### Draw a circle
#
# You draw a circle in a sketch by specifying the center and radius.

sketch.circle(Point2D([2, 1]), radius=30 * u.cm, tag="Circle")
sketch.select("Circle")
sketch.plot_selection()

# ### Draw an ellipse
#
# You draw an ellipse in a sketch by specifying the center, major radius, and minor radius.

sketch.ellipse(
    Point2D([1, 1]), major_radius=2*u.m, minor_radius=1*u.m, tag="Ellipse"
)
sketch.select("Ellipse")
sketch.plot_selection()

# ### Draw a polygon
#
# You draw a regular polygon by specifying the center, radius, and desired number of sides.

sketch.polygon(
    Point2D([1, 1]), inner_radius=3*u.m, sides=5, tag="Polygon"
)
sketch.select("Polygon")
sketch.plot_selection()

# ### Draw an arc
#
# You draw an arc of circumference by specifying the center, starting point, and ending point.

start_point, end_point = Point2D([2, 1], unit=u.m), Point2D([0, 1], unit=u.meter)
sketch.arc(start_point, end_point, Point2D([1,1]), tag="Arc")
sketch.select("Arc")
sketch.plot_selection()

# ### Draw a slot
#
# You draw a slot by specifying the center, width, and height.

sketch.slot(Point2D([2, 0]), 4, 3, tag="Slot")
sketch.select("Slot")
sketch.plot_selection()

# ### Draw a box
#
# You draw a box by specifying the center, width, and height.

sketch.box(Point2D([2, 0]), 4, 5, tag="Box")
sketch.select("Box")
sketch.plot_selection()

# ### Draw a segment
#
# You draw a segment by specifying the starting point and ending point.

start_point, end_point = Point2D([2, 1], unit=u.m), Point2D([0, 1], unit=u.meter)
sketch.segment(start_point, end_point, "Segment")
sketch.select("Segment")
sketch.plot_selection()

# ## Plot the sketch
#
# The ``Plotter`` class provides capabilities for plotting different PyAnsys Geometry objects.
# PyAnsys Geometry uses PyVista as the visualization backend.
#
# You use the ``plot_sketch`` method to plot a sketch. This method accepts a ``Sketch`` instance and
# some extra arguments to further customize the visualization of the sketch. These arguments include
# showing the plane of the sketch and its frame.

# Plot the sketch in the whole scene
pl = Plotter()
pl.plot_sketch(sketch, show_plane=True, show_frame=True)
pl.scene.show(jupyter_backend="panel")
