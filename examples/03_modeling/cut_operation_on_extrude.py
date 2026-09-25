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
Modeling: Extruded plate with cut operations
============================================

As seen in the `Rectangular plate with multiple
bodies <./plate_with_hole.html>`__ example, you can create a complex
sketch with holes and extrude it to create a body. However, you can also
perform cut operations on the extruded body to achieve similar results.
"""

###############################################################################
# Perform required imports
# ------------------------
#
# Perform the required imports.

from pint import Quantity

from ansys.geometry.core import launch_modeler
from ansys.geometry.core.math import Plane, Point2D, Point3D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.sketch import Sketch

###############################################################################
# Define sketch profile without holes
# -----------------------------------
#
# Create a sketch profile for the proposed design. The sketch is the same
# as the `Rectangular plate with multiple
# bodies <./plate_with_hole.html>`__ example, but without the holes.
#
# These holes are created by performing cut operations on the extruded
# body in the next steps.

sketch = Sketch()
(
    sketch.segment(Point2D([-4, 5], unit=UNITS.m), Point2D([4, 5], unit=UNITS.m))
    .segment_to_point(Point2D([4, -5], unit=UNITS.m))
    .segment_to_point(Point2D([-4, -5], unit=UNITS.m))
    .segment_to_point(Point2D([-4, 5], unit=UNITS.m))
    .box(Point2D([0, 0], unit=UNITS.m), Quantity(3, UNITS.m), Quantity(3, UNITS.m))
)

modeler = launch_modeler()
design = modeler.create_design("ExtrudedPlateNoHoles")
body = design.extrude_sketch("PlateLayer", sketch, Quantity(2, UNITS.m))

design.plot()

###############################################################################
# Define sketch profile for holes
# -------------------------------
#
# Create a sketch profile for the holes in the proposed design. The holes
# are created by sketching circles at the four corners of the plate. First
# create a reference sketch for all the circles. This sketch is translated
# to the four corners of the plate.

sketch_hole = Sketch()
sketch_hole.circle(Point2D([0, 0], unit=UNITS.m), Quantity(0.5, UNITS.m))

hole_centers = [
    Plane(Point3D([3, 4, 0], unit=UNITS.m)),
    Plane(Point3D([-3, 4, 0], unit=UNITS.m)),
    Plane(Point3D([-3, -4, 0], unit=UNITS.m)),
    Plane(Point3D([3, -4, 0], unit=UNITS.m)),
]

###############################################################################
# Perform cut operations on the extruded body
# -------------------------------------------
#
# Perform cut operations on the extruded body to create holes at the four
# corners of the plate.

for center in hole_centers:
    sketch_hole.plane = center
    design.extrude_sketch(
        name=f"H_{center.origin.x}_{center.origin.y}",
        sketch=sketch_hole,
        distance=Quantity(2, UNITS.m),
        cut=True,
    )

design.plot()

###############################################################################
# Close the modeler
# -----------------
#
# Close the modeler to free up resources and release the connection.

modeler.close()

# sphinx_gallery_thumbnail_path = '_static/thumbnails/cut_operation_on_extrude.png'
