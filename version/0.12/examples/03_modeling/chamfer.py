# ---
# jupyter:
#   jupytext:
#     default_lexer: ipython3
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Modeling: Chamfer edges and faces
# A chamfer is an angled cut on an edge. Chamfers can be created using the ``Modeler.geometry_commands`` module.

# %% [markdown]
# ## Create a block
# Launch the modeler and create a block.

# %%
from ansys.geometry.core import launch_modeler, Modeler

modeler = launch_modeler()
print(modeler)

# %%
from ansys.geometry.core.sketch import Sketch
from ansys.geometry.core.math import Point2D

design = modeler.create_design("chamfer_block")
body = design.extrude_sketch("block", Sketch().box(Point2D([0, 0]), 1, 1), 1)

body.plot()

# %% [markdown]
# ## Chamfer edges
# Create a uniform chamfer on all edges of the block.

# %%
modeler.geometry_commands.chamfer(body.edges, distance=0.1)

body.plot()

# %% [markdown]
# ## Chamfer faces
# The chamfer of a face can also be modified. Create a chamfer on a single edge and then modify the chamfer distance value by providing the newly created face that represents the chamfer.

# %%
body = design.extrude_sketch("box", Sketch().box(Point2D([0,0]), 1, 1), 1)

modeler.geometry_commands.chamfer(body.edges[0], distance=0.1)

body.plot()

# %%
modeler.geometry_commands.chamfer(body.faces[-1], distance=0.3)

body.plot()

# %% [markdown]
# ## Close session
#
# When you finish interacting with your modeling service, you should close the active
# server session. This frees resources wherever the service is running.
#
# Close the server session.

# %%
modeler.close()
