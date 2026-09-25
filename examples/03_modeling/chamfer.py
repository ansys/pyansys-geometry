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
Modeling: Chamfer edges and faces
=================================

A chamfer is an angled cut on an edge. Chamfers can be created using the
``Modeler.geometry_commands`` module.
"""

###############################################################################
# Create a block
# --------------
#
# Launch the modeler and create a block.

from ansys.geometry.core import launch_modeler

modeler = launch_modeler()
print(modeler)

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.sketch import Sketch

design = modeler.create_design("chamfer_block")
body = design.extrude_sketch("block", Sketch().box(Point2D([0, 0]), 1, 1), 1)

body.plot()

###############################################################################
# Chamfer edges
# -------------
#
# Create a uniform chamfer on all edges of the block.

modeler.geometry_commands.chamfer(body.edges, distance=0.1)

body.plot()

###############################################################################
# Chamfer faces
# -------------
#
# The chamfer of a face can also be modified. Create a chamfer on a single
# edge and then modify the chamfer distance value by providing the newly
# created face that represents the chamfer.

body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

modeler.geometry_commands.chamfer(body.edges[0], distance=0.1)

body.plot()

modeler.geometry_commands.chamfer(body.faces[-1], distance=0.3)

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

# sphinx_gallery_thumbnail_path = '_static/thumbnails/chamfer.png'
