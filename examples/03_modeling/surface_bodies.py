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
Modeling: Surface bodies and trimmed surfaces
=============================================

This example shows how to trim different surfaces, and how to use those
surfaces to create surface bodies.

Create a surface
----------------

Create a sphere surface. This can be done without launching the modeler.
"""

from ansys.geometry.core.math import Point3D
from ansys.geometry.core.shapes.surfaces import Sphere

surface = Sphere(origin=Point3D([0, 0, 0]), radius=1)

###############################################################################
# Now get information on how the surface is defined and parameterized.

surface.parameterization()

###############################################################################
# Trim the surface
# ----------------
#
# For a sphere, its parametization is (``u: [0, 2*pi]``,
# ``v:[-pi/2, pi/2]``), where u corresponds to longitude and v corresponds
# to latitude. You can **trim** a surface by providing new parameters.

import math

from ansys.geometry.core.shapes.box_uv import BoxUV
from ansys.geometry.core.shapes.parameterization import Interval

trimmed_surface = surface.trim(
    BoxUV(range_u=Interval(0, math.pi), range_v=Interval(0, math.pi / 2))
)

###############################################################################
# From a ``TrimmedSurface``, you can always refer back to the underlying
# ``Surface`` if needed.

trimmed_surface.geometry

###############################################################################
# Create a surface body
# ---------------------
#
# Now create a surface body by launching the modeler session and providing
# the trimmed surface. Then plot the body to see how you created a quarter
# of a sphere as a surface body.

from ansys.geometry.core import launch_modeler

modeler = launch_modeler()
print(modeler)

design = modeler.create_design("SurfaceBodyExample")
body = design.create_body_from_surface("trimmed_sphere", trimmed_surface)
design.plot()

###############################################################################
# If the sphere was left untrimmed, it would create a solid body since the
# surface is fully closed. In this case, since the surface was open, it
# created a surface body.
#
# This same process can be used with other surfaces including: - ``Cone``
# - ``Cylinder`` - ``Plane`` - ``Torus``
#
# Each surface has its own unique parameterization, which must be
# understood before trying to trim it.

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

# sphinx_gallery_thumbnail_path = '_static/thumbnails/quarter_sphere.png'
