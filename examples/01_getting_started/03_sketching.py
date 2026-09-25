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
PyAnsys Geometry 101: Sketching
===============================

With PyAnsys Geometry, you can build powerful dynamic sketches without
communicating with the Geometry service. This example shows how to build
some simple sketches.
"""

###############################################################################
# Perform required imports
# ------------------------
#
# Perform the required imports.

from pint import Quantity

from ansys.geometry.core.math import Plane, Point2D, Point3D, Vector3D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.sketch import Sketch

###############################################################################
# Add a box to sketch
# -------------------
#
# The ``Sketch`` object is the starting point. Once it is created, you can
# dynamically add various curves to the sketch. Here are some of the
# curves that are available:
#
# - ``arc``
# - ``box``
# - ``circle``
# - ``ellipse``
# - ``gear``
# - ``polygon``
# - ``segment``
# - ``slot``
# - ``trapezoid``
# - ``triangle``
#
# Add a box to the sketch.

sketch = Sketch()

sketch.segment(Point2D([0, 0]), Point2D([0, 1]))
sketch.segment(Point2D([0, 1]), Point2D([1, 1]))
sketch.segment(Point2D([1, 1]), Point2D([1, 0]))
sketch.segment(Point2D([1, 0]), Point2D([0, 0]))

sketch.plot()

###############################################################################
# A *functional-style sketching API* is also implemented. It allows you to
# append curves to the sketch with the idea of *never picking up your
# pen*.
#
# Use the functional-style sketching API to add a box.

sketch = Sketch()

(
    sketch.segment(Point2D([0, 0]), Point2D([0, 1]))
    .segment_to_point(Point2D([1, 1]))
    .segment_to_point(Point2D([1, 0]))
    .segment_to_point(Point2D([0, 0]))
)

sketch.plot()

###############################################################################
# A ``Sketch`` object uses the XY plane by default. You can define your
# own custom plane using three parameters: ``origin``, ``direction_x``,
# and ``direction_y``.
#
# Add a box on a custom plane.

plane = Plane(
    origin=Point3D([0, 0, 0]), direction_x=Vector3D([1, 2, -1]), direction_y=Vector3D([1, 0, 1])
)

sketch = Sketch(plane)

sketch.box(Point2D([0, 0]), 1, 1)

sketch.plot()

###############################################################################
# Combine concepts to create powerful sketches
# --------------------------------------------
#
# Combine these simple concepts to create powerful sketches.

# Complex Fluent API Sketch - PCB

sketch = Sketch()

(
    sketch.segment(Point2D([0, 0], unit=UNITS.mm), Point2D([40, 1], unit=UNITS.mm), "LowerEdge")
    .arc_to_point(
        Point2D([41.5, 2.5], unit=UNITS.mm),
        Point2D([40, 2.5], unit=UNITS.mm),
        tag="SupportedCorner",
    )
    .segment_to_point(Point2D([41.5, 5], unit=UNITS.mm))
    .arc_to_point(Point2D([43, 6.5], unit=UNITS.mm), Point2D([43, 5], unit=UNITS.mm), True)
    .segment_to_point(Point2D([55, 6.5], unit=UNITS.mm))
    .arc_to_point(Point2D([56.5, 8], unit=UNITS.mm), Point2D([55, 8], unit=UNITS.mm))
    .segment_to_point(Point2D([56.5, 35], unit=UNITS.mm))
    .arc_to_point(Point2D([55, 36.5], unit=UNITS.mm), Point2D([55, 35], unit=UNITS.mm))
    .segment_to_point(Point2D([0, 36.5], unit=UNITS.mm))
    .segment_to_point(Point2D([0, 0], unit=UNITS.mm))
    .circle(Point2D([4, 4], UNITS.mm), Quantity(1.5, UNITS.mm), "Anchor1")
    .circle(Point2D([51, 34.5], UNITS.mm), Quantity(1.5, UNITS.mm), "Anchor2")
)

sketch.plot()

# sphinx_gallery_thumbnail_path = '_static/thumbnails/101_getting_started.png'
