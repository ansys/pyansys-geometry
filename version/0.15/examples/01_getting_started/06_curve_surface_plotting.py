# ---
# jupyter:
#   jupytext:
#     default_lexer: ipython3
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # PyAnsys Geometry 101: Curve and Surface Plotting
#
# This example provides an overview of how to visualize PyAnsys Geometry's Curve and Surface objects. After constructing some of the Curve and Surface objects, it shows how to plot them.
#
# ## Perform required imports
#
# Perform the required imports.

# %%
from ansys.geometry.core.math import Point3D
from ansys.geometry.core.plotting import GeometryPlotter

# %% [markdown]
# ## Create curve shapes
#
# PyAnsys Geometry provides several curve types. Let's create instances of each.

# %% [markdown]
# ### Create a ``Circle`` curve

# %%
from ansys.geometry.core.shapes.curves.circle import Circle

circle = Circle(origin=Point3D([0, 0, 0]), radius=1)

# %% [markdown]
# ### Create a ``Line`` curve

# %%
from ansys.geometry.core.shapes.curves.line import Line
from ansys.geometry.core.math import UnitVector3D

line = Line(origin=Point3D([5, 0, 0]), direction=UnitVector3D([1, 1, 0]))

# %% [markdown]
# ### Create an ``Ellipse`` curve

# %%
from ansys.geometry.core.shapes.curves.ellipse import Ellipse

ellipse = Ellipse(origin=Point3D([10, 0, 0]), major_radius=1.5, minor_radius=0.8)

# %% [markdown]
# ### Create a ``NURBSCurve``

# %%
from ansys.geometry.core.shapes.curves.nurbs import NURBSCurve
import numpy as np

# Create a simple NURBS curve with 4 control points
points = [
    Point3D([0, 5, 0]),
    Point3D([1, 6, 0]),
    Point3D([2, 5, 0]),
    Point3D([3, 6, 0])
]
nurbs = NURBSCurve.fit_curve_from_points(points=points, degree=3)

# %% [markdown]
# ## Plot individual curves with colors
#
# Now let's plot each curve individually with different colors.

# %% [markdown]
# ### Plot the circle in blue

# %%
plotter = GeometryPlotter()
plotter.plot(circle, color="blue", opacity=1)
plotter.show()

# %% [markdown]
# ### Plot the line in red

# %%
plotter = GeometryPlotter()
plotter.plot(line, color="red", opacity=1)
plotter.show()

# %% [markdown]
# ### Plot the ellipse in green

# %%
plotter = GeometryPlotter()
plotter.plot(ellipse, color="green", opacity=1)
plotter.show()

# %% [markdown]
# ### Plot the NURBS curve in magenta

# %%
plotter = GeometryPlotter()
plotter.plot(nurbs, color="magenta")
plotter.show()

# %% [markdown]
# ## Plot multiple curves together
#
# You can also plot multiple curves together in a single scene with different colors.

# %%
plotter = GeometryPlotter()

# Add all curves with different colors
plotter.plot(circle, color="blue", opacity=1)
plotter.plot(line, color="red", opacity=1)
plotter.plot(ellipse, color="green", opacity=1)
plotter.plot(nurbs, color="magenta", opacity=1)

# Show all curves together
plotter.show()

# %% [markdown]
# You can also plot multiple curves with the same settings using a list.

# %%
plotter = GeometryPlotter()

# Add all curves with the same color
plotter.plot([circle, line, ellipse], color="magenta", opacity=1)

# Show all curves together
plotter.show()

# %% [markdown]
# ## Create surface shapes
#
# PyAnsys Geometry provides several surface types. Let's create instances of each.

# %% [markdown]
# ### Create a ``Sphere`` shape

# %%
from ansys.geometry.core.shapes.surfaces.sphere import Sphere

sphere = Sphere(origin=Point3D([0, 10, 0]), radius=1)

# %% [markdown]
# ### Create a ``Cylinder`` shape

# %%
from ansys.geometry.core.shapes.surfaces.cylinder import Cylinder

cylinder = Cylinder(origin=Point3D([5, 10, 0]), radius=0.8)

# %% [markdown]
# ### Create a ``Cone`` shape

# %%
from ansys.geometry.core.shapes.surfaces.cone import Cone
import numpy as np

cone = Cone(origin=Point3D([10, 10, 0]), radius=1, half_angle=np.pi / 6)

# %% [markdown]
# ### Create a ``Torus`` shape

# %%
from ansys.geometry.core.shapes.surfaces.torus import Torus

torus = Torus(origin=Point3D([0, 15, 0]), major_radius=1.5, minor_radius=0.5)

# %% [markdown]
# ### Create a ``PlaneSurface`` shape

# %%
from ansys.geometry.core.shapes.surfaces.plane import PlaneSurface

plane = PlaneSurface(origin=Point3D([5, 15, 0]))

# %% [markdown]
# ## Plot individual surfaces with colors
#
# Now let's plot each surface individually with different colors.

# %% [markdown]
# ### Plot the sphere in blue

# %%
plotter = GeometryPlotter()
plotter.plot(sphere, color="blue", opacity=1)
plotter.show()

# %% [markdown]
# ### Plot the cylinder in red

# %%
plotter = GeometryPlotter()
plotter.plot(cylinder, color="red", opacity=1)
plotter.show()

# %% [markdown]
# ### Plot the cone in green

# %%
plotter = GeometryPlotter()
plotter.plot(cone, color="green", opacity=1)
plotter.show()

# %% [markdown]
# ### Plot the torus in yellow

# %%
plotter = GeometryPlotter()
plotter.plot(torus, color="yellow", opacity=1)
plotter.show()

# %% [markdown]
# ### Plot the plane in cyan

# %%
plotter = GeometryPlotter()
plotter.plot(plane, color="cyan", opacity=1)
plotter.show()

# %% [markdown]
# ## Plot multiple surfaces together
#
# You can also plot multiple surfaces together in a single scene with different colors.

# %%
plotter = GeometryPlotter()

# Add all surfaces with different colors
plotter.plot(sphere, color="blue", opacity=1)
plotter.plot(cylinder, color="red", opacity=1)
plotter.plot(cone, color="green", opacity=1)
plotter.plot(torus, color="yellow", opacity=1)
plotter.plot(plane, color="cyan", opacity=1)

# Show all surfaces together
plotter.show()

# %% [markdown]
# You can also plot multiple surfaces with the same settings using a list

# %%
plotter = GeometryPlotter()

# Add all surfaces with different colors
plotter.plot([sphere, cylinder, cone], color="orange", opacity=1)

# Show all surfaces together
plotter.show()
