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
Modeling: Single body with material assignment
==============================================

In PyAnsys Geometry, a *body* represents solids or surfaces organized
within the ``Design`` assembly. The current state of sketch, which is a
client-side execution, can be used for the operations of the geometric
design assembly.

The Geometry service provides data structures to create individual
materials and their properties. These data structures are exposed
through PyAnsys Geometry.

This example shows how to create a single body from a sketch by
requesting its extrusion. It then shows how to assign a material to this
body.

Perform required imports
------------------------

Perform the required imports.
"""

from pint import Quantity

from ansys.geometry.core import launch_modeler
from ansys.geometry.core.materials import Material, MaterialProperty, MaterialPropertyType
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.sketch import Sketch

###############################################################################
# Create sketch
# -------------
#
# Create a ``Sketch`` instance and insert a circle with a radius of 10
# millimeters in the default plane.

sketch = Sketch()
sketch.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))

###############################################################################
# Initiate design on server
# -------------------------
#
# Launch a modeling service session and initiate a design on the server.

# Start a modeler session
modeler = launch_modeler()
print(modeler)

design_name = "ExtrudeProfile"
design = modeler.create_design(design_name)

###############################################################################
# Add materials to design
# -----------------------
#
# Add materials and their properties to the design. Material properties
# can be added when creating the ``Material`` object or after its
# creation. This code adds material properties after creating the
# ``Material`` object.

density = Quantity(125, 10 * UNITS.kg / (UNITS.m * UNITS.m * UNITS.m))
poisson_ratio = Quantity(0.33, UNITS.dimensionless)
tensile_strength = Quantity(45)
material = Material(
    "steel",
    density,
    [MaterialProperty(MaterialPropertyType.POISSON_RATIO, "PoissonRatio", poisson_ratio)],
)
material.add_property(MaterialPropertyType.TENSILE_STRENGTH, "TensileProp", Quantity(45))
design.add_material(material)

###############################################################################
# Extrude sketch to create body
# -----------------------------
#
# Extrude the sketch to create the body and then assign a material to it.

# Extrude the sketch to create the body
body = design.extrude_sketch("SingleBody", sketch, Quantity(10, UNITS.mm))

# Assign a material to the body
body.assign_material(material)

body.plot()

###############################################################################
# Close session
# -------------
#
# When you finish interacting with your modeling service, you should close
# the active server session. This frees resources wherever the service is
# running.
#
# Close the server session.

modeler.close()

# sphinx_gallery_thumbnail_path = '_static/thumbnails/add_design_material.png'
