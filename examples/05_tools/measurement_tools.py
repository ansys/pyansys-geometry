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
Tools: Using MeasurementTools to measure distances
==================================================

This example demonstrates how to use the ``MeasurementTools`` class to
measure the minimum distance between geometric objects such as bodies,
faces, and edges.

The ``MeasurementTools`` instance is accessible through
``modeler.measurement_tools``. It should not be instantiated directly by
the user.
"""

###############################################################################
# Perform required imports
# ------------------------
#
# Perform the required imports.

from ansys.geometry.core import launch_modeler
from ansys.geometry.core.math import UNITVECTOR3D_X, Point2D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.sketch import Sketch

###############################################################################
# Initialize the modeler
# ----------------------

modeler = launch_modeler()
print(modeler)

###############################################################################
# Create a design with two separate bodies
# ----------------------------------------
#
# Create a design and extrude two box sketches into separate bodies. The
# bodies are placed apart from each other so that a measurable gap exists
# between them.

design = modeler.create_design("MeasurementToolsDemo")

# Create the first box body
sketch1 = Sketch()
sketch1.box(Point2D([0, 0], unit=UNITS.m), width=1 * UNITS.m, height=1 * UNITS.m)
box1 = design.extrude_sketch("Box1", sketch1, 1 * UNITS.m)

# Create the second box body and translate it away from the first
sketch2 = Sketch()
sketch2.box(Point2D([0, 0], unit=UNITS.m), width=1 * UNITS.m, height=1 * UNITS.m)
box2 = design.extrude_sketch("Box2", sketch2, 1 * UNITS.m)
box2.translate(UNITVECTOR3D_X, 3)

design.plot()

###############################################################################
# Measure the minimum distance between two bodies
# -----------------------------------------------
#
# Use ``modeler.measurement_tools.min_distance_between_objects()`` to find
# the minimum distance between the two box bodies. The method returns a
# ``Gap`` object whose ``distance`` attribute contains the measured value.

gap = modeler.measurement_tools.min_distance_between_objects(box1, box2)
print(f"Minimum distance between Box1 and Box2: {gap.distance}")

###############################################################################
# Measure the minimum distance between two faces
# ----------------------------------------------
#
# The same method accepts ``Face`` objects as inputs (requires Ansys
# release 25R2 or later). This allows measuring the gap between specific
# faces of the bodies.

# Select a face from each body to measure between
face1 = box1.faces[0]
face2 = box2.faces[0]

gap_faces = modeler.measurement_tools.min_distance_between_objects(face1, face2)
print(f"Minimum distance between selected faces: {gap_faces.distance}")

###############################################################################
# Measure the minimum distance between two edges
# ----------------------------------------------
#
# Similarly, ``Edge`` objects can be passed to measure the gap between
# specific edges (requires Ansys release 25R2 or later).

# Select an edge from each body to measure between
edge1 = box1.edges[0]
edge2 = box2.edges[0]

gap_edges = modeler.measurement_tools.min_distance_between_objects(edge1, edge2)
print(f"Minimum distance between selected edges: {gap_edges.distance}")

###############################################################################
# Close the modeler
# -----------------
#
# Close the modeler to free up resources and release the connection.

modeler.close()

# sphinx_gallery_thumbnail_path = '_static/thumbnails/measurement_tools.png'
