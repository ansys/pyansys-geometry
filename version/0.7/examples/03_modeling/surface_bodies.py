# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Modeling: Surface bodies and trimmed surfaces
#
# This example shows how to trim different surfaces, and how to use those surfaces
# to create surface bodies.
#
# ## Create a surface
#
# Create a sphere surface. This can be done without launching the modeler.

# +
from ansys.geometry.core.shapes.surfaces import Sphere
from ansys.geometry.core.math import Point3D

surface = Sphere(origin=Point3D([0, 0, 0]), radius=1)
# -

# Now get information on how the surface is defined and parameterized.

surface.parameterization()

# ## Trim the surface
#
# For a sphere, its parametization is (`u: [0, 2*pi]`, `v:[-pi/2, pi/2]`),
# where u corresponds to longitude and v corresponds to latitude. You
# can **trim** a surface by providing new parameters.

# +
from ansys.geometry.core.shapes.box_uv import BoxUV
from ansys.geometry.core.shapes.parameterization import Interval
import math

trimmed_surface = surface.trim(BoxUV(range_u=Interval(0, math.pi), range_v=Interval(0, math.pi/2)))
# -

# From a ``TrimmedSurface``, you can always refer back to the underlying ``Surface`` if needed.

trimmed_surface.geometry

# ## Create a surface body
#
# Now create a surface body by launching the modeler session and providing the trimmed surface.
# Then plot the body to see how you created a quarter of a sphere as a surface body.

# +
from ansys.geometry.core import launch_modeler

modeler = launch_modeler()
print(modeler)
# -

design = modeler.create_design("SurfaceBodyExample")
body = design.create_body_from_surface("trimmed_sphere", trimmed_surface)
design.plot()

# If the sphere was left untrimmed, it would create a solid body since the surface is fully
# closed. In this case, since the surface was open, it created a surface body.
#
# This same process can be used with other surfaces including:
# - ``Cone``
# - ``Cylinder``
# - ``Plane``
# - ``Torus``
#
# Each surface has its own unique parameterization, which must be understood before trying to trim it.

# ## Close session
#
# When you finish interacting with your modeling service, you should close the active server
# session. This frees resources wherever the service is running.
#
# Close the server session.

modeler.close()
