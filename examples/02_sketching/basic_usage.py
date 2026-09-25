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

"""
Sketching: Basic usage
======================

This example shows how to use basic PyAnsys Geometry sketching
capabilities.
"""

###############################################################################
# Perform required imports
# ------------------------
#
# Perform the required imports.

###############################################################################
# Create a sketch
# ---------------
#
# Sketches are fundamental objects for drawing basic shapes like lines,
# segments, circles, ellipses, arcs, and polygons.
#
# You create a ``Sketch`` instance by defining a drawing plane. To define
# a plane, you declare a point and two fundamental orthogonal directions.
from ansys.geometry.core.math import Plane, Point2D, Point3D
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.sketch import Sketch

###############################################################################
# Define a plane for creating a sketch.

# Define the origin point of the plane
origin = Point3D([1, 1, 1])

# Create a plane located in previous point with desired fundamental directions
plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, -1, 1])

# Instantiate a new sketch object from previous plane
sketch = Sketch(plane)

###############################################################################
# Draw shapes
# -----------
#
# To draw different shapes in the sketch, you use ``draw`` methods.

###############################################################################
# Draw a circle
# ~~~~~~~~~~~~~
#
# You draw a circle in a sketch by specifying the center and radius.

sketch.circle(Point2D([2, 1]), radius=30 * UNITS.cm, tag="Circle")
sketch.select("Circle")
sketch.plot_selection()

###############################################################################
# Draw an ellipse
# ~~~~~~~~~~~~~~~
#
# You draw an ellipse in a sketch by specifying the center, major radius,
# and minor radius.

sketch.ellipse(Point2D([1, 1]), major_radius=2 * UNITS.m, minor_radius=1 * UNITS.m, tag="Ellipse")
sketch.select("Ellipse")
sketch.plot_selection()

###############################################################################
# Draw a polygon
# ~~~~~~~~~~~~~~
#
# You draw a regular polygon by specifying the center, radius, and desired
# number of sides.

sketch.polygon(Point2D([1, 1]), inner_radius=3 * UNITS.m, sides=5, tag="Polygon")
sketch.select("Polygon")
sketch.plot_selection()

###############################################################################
# Draw an arc
# ~~~~~~~~~~~
#
# You draw an arc of circumference by specifying the center, starting
# point, and ending point.

start_point, end_point = Point2D([2, 1], unit=UNITS.m), Point2D([0, 1], unit=UNITS.meter)
sketch.arc(start_point, end_point, Point2D([1, 1]), tag="Arc")
sketch.select("Arc")
sketch.plot_selection()

###############################################################################
# There are also additional ways to draw arcs, such as by specifying the
# start, center point, and angle.

start_point = Point2D([2, 1], unit=UNITS.m)
center_point = Point2D([1, 1], unit=UNITS.m)
angle = 90
sketch.arc_from_start_center_and_angle(
    start_point, center_point, angle=90, tag="Arc_from_start_center_angle"
)
sketch.select("Arc_from_start_center_angle")
sketch.plot_selection()

###############################################################################
# Or by specifying the start, end point, and radius.

start_point, end_point = Point2D([2, 1], unit=UNITS.m), Point2D([0, 1], unit=UNITS.meter)
radius = 1 * UNITS.m
sketch.arc_from_start_end_and_radius(
    start_point, end_point, radius, tag="Arc_from_start_end_radius"
)
sketch.select("Arc_from_start_end_radius")
sketch.plot_selection()

###############################################################################
# Draw a slot
# ~~~~~~~~~~~
#
# You draw a slot by specifying the center, width, and height.

sketch.slot(Point2D([2, 0]), 4, 3, tag="Slot")
sketch.select("Slot")
sketch.plot_selection()

###############################################################################
# Draw a box
# ~~~~~~~~~~
#
# You draw a box by specifying the center, width, and height.

sketch.box(Point2D([2, 0]), 4, 5, tag="Box")
sketch.select("Box")
sketch.plot_selection()

###############################################################################
# Draw a segment
# ~~~~~~~~~~~~~~
#
# You draw a segment by specifying the starting point and ending point.

start_point, end_point = Point2D([2, 1], unit=UNITS.m), Point2D([0, 1], unit=UNITS.meter)
sketch.segment(start_point, end_point, "Segment")
sketch.select("Segment")
sketch.plot_selection()

###############################################################################
# Plot the sketch
# ---------------
#
# The ``Plotter`` class provides capabilities for plotting different
# PyAnsys Geometry objects. PyAnsys Geometry uses PyVista as the
# visualization backend.
#
# You use the ``plot_sketch`` method to plot a sketch. This method accepts
# a ``Sketch`` instance and some extra arguments to further customize the
# visualization of the sketch. These arguments include showing the plane
# of the sketch and its frame.

# Plot the sketch in the whole scene
from ansys.geometry.core.plotting import GeometryPlotter

pl = GeometryPlotter()
pl.add_sketch(sketch, show_plane=True, show_frame=True)
pl.show()

# sphinx_gallery_thumbnail_path = '_static/thumbnails/basic_usage.png'
