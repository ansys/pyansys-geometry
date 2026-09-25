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
Miscellaneous: Example template
===============================

This example serves as a template for creating new examples in the
documentation. It shows developers how to structure their code and
comments for clarity and consistency. It also provides a basic outline
for importing necessary modules, initializing the modeler, performing
operations, and closing the modeler.

It is important to follow the conventions and formatting used in this
example to ensure that the documentation is easy to read and
understandable.

Example imports
---------------

Perform the required imports for this example. This section should
include all necessary imports for the example to run correctly.
"""

# Imports
from ansys.geometry.core import launch_modeler
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.sketch import Sketch

###############################################################################
# Initialize the modeler
# ----------------------

# Initialize the modeler for this example notebook
m = launch_modeler()
print(m)

###############################################################################
# Body of your example
# --------------------
#
# Developers can add their code here to perform the desired operations.
# This section should include comments and explanations to explain what
# the code is doing.
#
# Example section: Initialize a design
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Create a design named ``example-design``.

# Initialize the example design
design = m.create_design("example-design")

###############################################################################
# Example section: Include images
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# This section demonstrates how to include static images in the
# documentation. You should place these images in the
# ``doc/source/_static/`` directory.
#
# You can then reference images in the documentation using the following
# syntax:
#
# .. figure:: ../../_static/thumbnails/101_getting_started.png
#    :align: center
#    :alt: image
#
#    image
#
# Example section: Create a sketch and plot it
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# This section demonstrates how to create a sketch and plot it.

sketch = Sketch()
sketch.box(Point2D([0, 0]), 10, 10)
sketch.plot()

###############################################################################
# Example section: Extrude the sketch and create a body
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# This section demonstrates how to extrude the sketch and create a body.

design.extrude_sketch("BoxBody", sketch, distance=10)
design.plot()

###############################################################################
# Close the modeler
# -----------------

# Close the modeler
m.close()

# sphinx_gallery_thumbnail_path = '_static/thumbnails/101_getting_started.png'
