# ---
# jupyter:
#   jupytext:
#     default_lexer: ipython3
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Modeling: Body color assignment and usage
#
# In PyAnsys Geometry, a *body* represents solids or surfaces organized within the ``Design`` assembly.
# As users might be already familiar with, Ansys CAD products (like SpaceClaim, Ansys Discovery and the
# Geometry Service), allow to assign colors to bodies. This example shows how to assign colors to a body,
# retrieve their value and how to use them in the client-side visualization.
#
# ## Perform required imports
#
# Perform the required imports.

# %%
import ansys.geometry.core as pyansys_geometry

from ansys.geometry.core import launch_modeler
from ansys.geometry.core.math import Point2D, UNITVECTOR3D_X, UNITVECTOR3D_Y
from ansys.geometry.core.sketch import Sketch

# %% [markdown]
# ## Create a box sketch
#
# Create a ``Sketch`` instance and insert a box sketch with a width and height of 10
# in the default plane.

# %%
sketch = Sketch()
sketch.box(Point2D([0, 0]), 10, 10)

# %% [markdown]
# ## Initiate design on server
#
# Establish a server connection and initiate a design on the server.

# %%
modeler = launch_modeler()
design = modeler.create_design("ServiceColors")

# %% [markdown]
# ## Extrude the box sketch to create the matrix style design
#
# Given the initial sketch, you can extrude it to create a matrix style design.
# In this example, you can create a 2x3 matrix of bodies. Each body is separated by 30 units
# in the X direction and 30 units in the Y direction. You have a total of 6 bodies.

# %%
translate = [[0, 30, 60], [0, 30, 60]]

for r_idx, row in enumerate(translate):
    comp = design.add_component(f"Component{r_idx}")

    for b_idx, dist in enumerate(row):
        body = comp.extrude_sketch(f"Component{r_idx}_Body{b_idx}", sketch, distance=10)
        body.translate(UNITVECTOR3D_Y, r_idx*30)
        body.translate(UNITVECTOR3D_X, dist)

design.plot()

# %% [markdown]
# ## Assign colors to the bodies
#
# Given the previous design, you can assign a color to each body. You could have done
# this assignment while creating the bodies, but for the sake of encapsulating the
# color assignment logic, it is done in its own code cell.

# %%
colors = [["red", "blue", "yellow"], ["orange", "green", "purple"]]

for c_idx, comp in enumerate(design.components):
    for b_idx, body in enumerate(comp.bodies):
        body.color = colors[c_idx][b_idx]
        print(f"Body {body.name} has color {body.color}")

# %% [markdown]
# ## Plotting the design with colors
#
# By default, the plot method does **not** use the colors assigned to the bodies.
# To plot the design with the assigned colors, you need to specifically request it.
#
# Users have two options for plotting with the assigned colors:
#
# * Pass the parameter ``use_service_colors=True`` to the plot method.
# * Set the global parameter ``USE_SERVICE_COLORS`` to ``True``.
#
# It is important to note that the usage of colors when plotting might slow down the
# plotting process, as it requires additional information to be sent from the server
# to the client and processed in the client side.
#
# If you just request the plot without setting the global parameter, the plot will
# be displayed without the colors, as shown below.

# %%
design.plot()

# %% [markdown]
# As stated previously, if you pass the parameter ``use_service_colors=True`` to the plot
# method, the plot is displayed with the assigned colors.

# %%
design.plot(use_service_colors=True)

# %% [markdown]
# However, if you set the global parameter to ``True``, the plot is displayed
# with the assigned colors without the need to pass the parameter to the plot method.

# %%
import ansys.geometry.core as pyansys_geometry

pyansys_geometry.USE_SERVICE_COLORS = True

design.plot()

# Reverting the global parameter to its default value
pyansys_geometry.USE_SERVICE_COLORS = False

# %% [markdown]
# This last method is useful when the user wants to plot all the designs with the
# assigned colors without the need to pass the parameter to the plot method in
# every call.
#
#
# ## Plotting specific bodies or components with colors
#
# If the user wants to plot specific bodies with the assigned colors, the user can
# follow the same approach as before. The user can pass the parameter ``use_service_colors=True``
# to the plot method or set the global parameter ``USE_SERVICE_COLORS`` to ``True``.
#
# In the following examples, you are shown how to do this using the
# ``use_service_colors=True`` parameter.
#
# Let's plot the first body of the first component with the assigned colors.

# %%
body = design.components[0].bodies[0]

body.plot(use_service_colors=True)

# %% [markdown]
# Now, let's plot the second component with the assigned colors.

# %%
comp = design.components[1]

comp.plot(use_service_colors=True)
