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
# # PyAnsys Geometry 101: Plotter
# This example provides an overview of PyAnsys Geometry's plotting capabilities, focusing on
# its plotter features. After reviewing the fundamental concepts of sketching
# and modeling in PyAnsys Geometry, it shows how to leverage these key plotting capabilities:
#
# - **Multi-object plotting**: You can conveniently plot a list of elements, including objects
#   created in both PyAnsys Geometry and PyVista libraries.
# - **Interactive object selection**: You can interactively select PyAnsys Geometry objects within the
#   scene. This enables efficient manipulation of these objects in subsequent scripting.

# %% [markdown]
# ## Perform required imports
#
# Perform the required imports.

# %%
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.plotting import GeometryPlotter
from ansys.geometry.core.sketch import Sketch

# %% [markdown]
# ## Launch modeling service
#
# Launch a modeling service session.

# %%
from ansys.geometry.core import launch_modeler

# Start a modeler session
modeler = launch_modeler()
print(modeler)

# %% [markdown]
# You can also launch your own services and connect to them. For information on
# connecting to an existing service, see the
# [Modeler API](https://geometry.docs.pyansys.com/version/stable/api/ansys/geometry/core/modeler/Modeler.html)
# documentation.

# %% [markdown]
# ## Instantiate design and initialize object list
#
# Instantiate a new design to work on and initialize a list
# of objects for plotting.

# %%
# init modeler
design = modeler.create_design("Multiplot")

plot_list = []

# %% [markdown]
# You are now ready to create some objects and use the
# plotter capabilities.

# %% [markdown]
# ## Create a PyAnsys Geometry body cylinder
#
# Use PyAnsys Geometry to create a body cylinder.

# %%
cylinder = Sketch()
cylinder.circle(Point2D([10, 10], UNITS.m), 1.0)
cylinder_body = design.extrude_sketch("JustACyl", cylinder, Quantity(10, UNITS.m))
plot_list.append(cylinder_body)

# %% [markdown]
# ## Create a PyAnsys Geometry arc sketch
#
# Use PyAnsys Geometry to create an arc sketch.

# %%
sketch = Sketch()
sketch.arc(
    Point2D([20, 20], UNITS.m),
    Point2D([20, -20], UNITS.m),
    Point2D([10, 0], UNITS.m),
    tag="Arc",
)
plot_list.append(sketch)

# %% [markdown]
# ## Create a PyVista cylinder
#
# Use PyVista to create a cylinder.

# %%
cyl = pv.Cylinder(radius=5, height=20, center=(-20, 10, 10))
plot_list.append(cyl)

# %% [markdown]
# ## Create a PyVista multiblock
#
# Use PyVista to create a multiblock with a sphere and a cube.

# %%
blocks = pv.MultiBlock(
    [pv.Sphere(center=(20, 10, -10), radius=10), pv.Cube(x_length=10, y_length=10, z_length=10)]
)
plot_list.append(blocks)

# %% [markdown]
# ## Create a PyAnsys Geometry body box
#
# Use PyAnsys Geometry to create a body box that is a cube.

# %%
box2 = Sketch()
box2.box(Point2D([-10, 20], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))
box_body2 = design.extrude_sketch("JustABox", box2, Quantity(10, UNITS.m))
plot_list.append(box_body2)

# %% [markdown]
# ## Plot objects
#
# When plotting the created objects, you have several options.
#
# You can simply plot one of the created objects.

# %%
plotter = GeometryPlotter()
plotter.show(box_body2)

# %% [markdown]
# You can plot the whole list of objects.

# %%
plotter = GeometryPlotter()
plotter.show(plot_list)

# %% [markdown]
# The Python visualizer is used by default. However, you can also use
# [trame](https://kitware.github.io/trame/index.html) for visualization.
#
# ```python
#
# plotter = GeometryPlotter(use_trame=True)
# plotter.show(plot_list)
# ```
#
# ## Clip objects
#
# You can clip any object represented in the plotter by defining a ``Plane`` object that
# intersects the target object.

# %%
from ansys.geometry.core.math import Plane, Point3D
pl = GeometryPlotter()

# Define PyAnsys Geometry box
box2 = Sketch()
box2.box(Point2D([-10, 20], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))
box_body2 = design.extrude_sketch("JustABox", box2, Quantity(10, UNITS.m))

# Define plane to clip the box
origin = Point3D([-10., 20., 5.], UNITS.m)
plane = Plane(origin=origin, direction_x=[1, 1, 1], direction_y=[-1, 0, 1])

# Add the object with the clipping plane
pl.plot(box_body2, clipping_plane=plane)
pl.show()

# %% [markdown]
# ## Select objects interactively
#
# PyAnsys Geometry's plotter supports interactive object selection within the scene.
# This enables you to pick objects for subsequent script manipulation.

# %%
plotter = GeometryPlotter(allow_picking=True)

# Plotter returns picked bodies
picked_list = plotter.show(plot_list)
print(picked_list)

# %% [markdown]
# It is also possible to enable picking directly for a specific ``design`` or ``component``
# object alone. In the following cell, picking is enabled for the ``design`` object.

# %%
picked_list = design.plot(allow_picking=True)
print(picked_list)

# %% [markdown]
# ## Render in different colors
#
# You can render the objects in different colors automatically using PyVista's default
# color cycler. In order to do this, activate the ``multi_colors=True`` option when calling
# the ``plot()`` method.
#
# In the following cell you can create a new design and plot a prism and a cylinder in different colors.

# %%
design = modeler.create_design("MultiColors")

# Create a sketch of a box
sketch_box = Sketch().box(Point2D([0, 0], unit=UNITS.m), width=30 * UNITS.m, height=40 * UNITS.m)

# Create a sketch of a circle (overlapping the box slightly)
sketch_circle = Sketch().circle(Point2D([20, 0], unit=UNITS.m), radius=3 * UNITS.m)

# Extrude both sketches to get a prism and a cylinder
design.extrude_sketch("Prism", sketch_box, 50 * UNITS.m)
design.extrude_sketch("Cylinder", sketch_circle, 50 * UNITS.m)

# Design plotting
design.plot(multi_colors=True)

# %% [markdown]
# ## Close session
#
# When you finish interacting with your modeling service, you should close the active
# server session. This frees resources wherever the service is running.
#
# Close the server session.

# %%
modeler.close()
