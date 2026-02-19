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
# # Miscellaneous: Example template
#
# This example serves as a template for creating new examples in the documentation.
# It shows developers how to structure their code and comments for clarity and consistency.
# It also provides a basic outline for importing necessary modules, initializing the modeler,
# performing operations, and closing the modeler.
#
# It is important to follow the conventions and formatting used in this example to ensure that
# the documentation is easy to read and understandable.
#
# ## Example imports
#
# Perform the required imports for this example.
# This section should include all necessary imports for the example to run correctly.

# %%
# Imports
from ansys.geometry.core import launch_modeler
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.sketch import Sketch

# %% [markdown]
# ## Initialize the modeler

# %%
# Initialize the modeler for this example notebook
m = launch_modeler()
print(m)

# %% [markdown]
# ## Body of your example
#
# Developers can add their code here to perform the desired operations.
# This section should include comments and explanations to explain what the code is doing.
#
# ### Example section: Initialize a design
#
# Create a design named ``example-design``.

# %%
# Initialize the example design
design = m.create_design("example-design")

# %% [markdown]
# ### Example section: Include images
#
# This section demonstrates how to include static images in the documentation.
# You should place these images in the ``doc/source/_static/`` directory.
#
# You can then reference images in the documentation using the following syntax:
#
# ![image](../../_static/thumbnails/101_getting_started.png){align=center}
#
#
# ### Example section: Create a sketch and plot it
#
# This section demonstrates how to create a sketch and plot it.

# %%
sketch = Sketch()
sketch.box(Point2D([0, 0]), 10, 10)
sketch.plot()

# %% [markdown]
# ### Example section: Extrude the sketch and create a body
# This section demonstrates how to extrude the sketch and create a body.

# %%
design.extrude_sketch(f"BoxBody", sketch, distance=10)
design.plot()

# %% [markdown]
# ## Close the modeler

# %%
# Close the modeler
m.close()
