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
Modeling: Tessellation of two bodies
====================================

This example shows how to create two stacked bodies and return the
tessellation as two merged bodies.
"""

###############################################################################
# Perform required imports
# ------------------------
#
# Perform the required imports.

from pint import Quantity

from ansys.geometry.core import launch_modeler
from ansys.geometry.core.math import Plane, Point2D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.sketch import Sketch

###############################################################################
# Create design
# -------------
#
# Create the basic sketches to be tessellated and extrude the sketch in
# the required plane. For more information on creating a component and
# extruding a sketch in the design, see the `Rectangular plate with
# multiple bodies <plate_with_hole.html>`__ example.
#
# Here is a typical situation in which two bodies, with different sketch
# planes, merge each body into a single dataset. This effectively combines
# all the faces of each individual body into a single dataset without
# separating faces.

modeler = launch_modeler()

sketch_1 = Sketch()
box = sketch_1.box(
    Point2D([10, 10], unit=UNITS.m), width=Quantity(10, UNITS.m), height=Quantity(5, UNITS.m)
)
circle = sketch_1.circle(Point2D([0, 0], unit=UNITS.m), radius=Quantity(25, UNITS.m))

design = modeler.create_design("TessellationDesign")
comp = design.add_component("TessellationComponent")
body = comp.extrude_sketch("Body", sketch=sketch_1, distance=10 * UNITS.m)

# Create the second body in a plane with a different origin
sketch_2 = Sketch(Plane([0, 0, 10]))
box = sketch_2.box(
    Point2D([10, 10], unit=UNITS.m), width=Quantity(10, UNITS.m), height=Quantity(5, UNITS.m)
)
circle = sketch_2.circle(Point2D([0, 10], unit=UNITS.m), radius=Quantity(25, UNITS.m))

body = comp.extrude_sketch("Body", sketch=sketch_2, distance=10 * UNITS.m)

###############################################################################
# Tessellate component as two merged bodies
# -----------------------------------------
#
# Tessellate the component and merge each body into a single dataset. This
# effectively combines all the faces of each individual body into a single
# dataset without separating faces.

dataset = comp.tessellate()
dataset

###############################################################################
# Single body tessellation is possible. In that case, users can request
# the body-level tessellation method to tessellate the body and merge all
# the faces into a single dataset.

dataset = comp.bodies[0].tessellate()
dataset

###############################################################################
# Plot design
# -----------
#
# Plot the design.

design.plot()

###############################################################################
# Close the modeler
# -----------------
#
# Close the modeler.

modeler.close()

# sphinx_gallery_thumbnail_path = '_static/thumbnails/tessellation_usage.png'
