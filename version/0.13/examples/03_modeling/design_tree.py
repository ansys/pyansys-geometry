# ---
# jupyter:
#   jupytext:
#     default_lexer: ipython3
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Modeling: Visualization of the design tree on terminal
#
# A user can visualize its model object tree easily by using the ``tree_print()`` method
# available on the ``Design`` and ``Component`` objects. This method prints the tree
# structure of the model in the terminal.
#
# ## Perform required imports
#
# For the following example, you need to import these modules:

# %%
from pint import Quantity

from ansys.geometry.core import launch_modeler
from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Y
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.sketch.sketch import Sketch

# %% [markdown]
# ## Create a design
#
# The following code creates a simple design for demonstration purposes. The design consists of
# several cylinders extruded. The interesting part is visualizing the corresponding design tree.

# %%
# Create a modeler object
modeler = launch_modeler()

# Create your design on the server side
design = modeler.create_design("TreePrintComponent")

# Create a Sketch object and draw a circle (all client side)
sketch = Sketch()
sketch.circle(Point2D([-30, -30]), 10 * UNITS.m)
distance = 30 * UNITS.m

#  The following component hierarchy is made
#
#           |---> comp_1 ---|---> nested_1_comp_1 ---> nested_1_nested_1_comp_1
#           |               |
#           |               |---> nested_2_comp_1
#           |
# DESIGN ---|---> comp_2 -------> nested_1_comp_2
#           |
#           |
#           |---> comp_3
#
#
# Now, only "comp_3", "nested_2_comp_1" and "nested_1_nested_1_comp_1"
# has a body associated.
#

# Create the components
comp_1 = design.add_component("Component_1")
comp_2 = design.add_component("Component_2")
comp_3 = design.add_component("Component_3")
nested_1_comp_1 = comp_1.add_component("Nested_1_Component_1")
nested_1_nested_1_comp_1 = nested_1_comp_1.add_component("Nested_1_Nested_1_Component_1")
nested_2_comp_1 = comp_1.add_component("Nested_2_Component_1")
nested_1_comp_2 = comp_2.add_component("Nested_1_Component_2")

# Create the bodies
b1 = comp_3.extrude_sketch(name="comp_3_circle", sketch=sketch, distance=distance)
b2 = nested_2_comp_1.extrude_sketch(
    name="nested_2_comp_1_circle", sketch=sketch, distance=distance
)
b2.translate(UNITVECTOR3D_X, 50)
b3 = nested_1_nested_1_comp_1.extrude_sketch(
    name="nested_1_nested_1_comp_1_circle", sketch=sketch, distance=distance
)
b3.translate(UNITVECTOR3D_Y, 50)

# %% [markdown]
# ```python
# # Create beams (in design)
# circle_profile_1 = design.add_beam_circular_profile(
#     "CircleProfile1", Quantity(10, UNITS.mm), Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_Y
# )
# beam_1 = nested_1_comp_2.create_beam(
#     Point3D([9, 99, 999], UNITS.mm), Point3D([8, 88, 888], UNITS.mm), circle_profile_1
# )
# ```

# %%
# Visualize the design (optional)
design.plot()

# %% [markdown]
# ## Visualize the design tree
#
# Now, let's visualize the design tree using the ``tree_print()`` method. Let's start by
# printing the tree structure of the design object with no extra arguments.

# %%
design.tree_print()

# %% [markdown]
# ### Controlling the depth of the tree
#
# The ``tree_print()`` method accepts an optional argument ``depth`` to control the depth of the
# tree to be printed. The default value is ``None``, which means the entire tree is printed.

# %%
design.tree_print(depth=1)

# %% [markdown]
# In this case, only the first level of the tree is printed - that is, the three main
# components.
#
# ### Excluding bodies, components, or beams
#
# By default, the ``tree_print()`` method prints all the bodies, components, and beams in the
# design tree. However, you can exclude any of these by setting the corresponding argument to
# ``False``.

# %%
design.tree_print(consider_bodies=False, consider_beams=False)

# %% [markdown]
# In this case, the bodies and beams are not be printed in the tree structure.

# %%
design.tree_print(consider_comps=False)

# %% [markdown]
# In this case, the components are not be printed in the tree structure - leaving only the
# design object represented.
#
# ### Sorting the tree
#
# By default, the tree structure is sorted by the way the components, bodies, and beams were
# created. However, you can sort the tree structure by setting the ``sort_keys`` argument to ``True``.
# In that case, the tree is sorted alphabetically.
#
# Let's add a new component to the design and print the tree structure by default.

# %%
comp_4 = design.add_component("A_Component")
design.tree_print(depth=1)

# %% [markdown]
# Now, let's print the tree structure with the components sorted alphabetically.

# %%
design.tree_print(depth=1, sort_keys=True)

# %% [markdown]
# ### Indenting the tree
#
# By default, the tree structure is printed with an indentation level of 4. However, you
# can indent the tree structure by setting the ``indent`` argument to the desired value.

# %%
design.tree_print(depth=1, indent=8)

# %% [markdown]
# In this case, the tree structure is printed with an indentation level of 8.
#
# ### Printing the tree from a specific component
#
# You can print the tree structure from a specific component by calling the ``tree_print()``
# method on the component object.

# %%
nested_1_comp_1.tree_print()

# %% [markdown]
# ### Closing the modeler
#
# Finally, close the modeler.

# %%
modeler.close()
