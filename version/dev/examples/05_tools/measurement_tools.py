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
# # Tools: Using MeasurementTools to measure distances
#
# This example demonstrates how to use the ``MeasurementTools`` class to measure
# the minimum distance between geometric objects such as bodies, faces, and edges.
#
# The ``MeasurementTools`` instance is accessible through ``modeler.measurement_tools``.
# It should not be instantiated directly by the user.

# %% [markdown]
# ## Perform required imports
#
# Perform the required imports.

# %%
from ansys.geometry.core import launch_modeler
from ansys.geometry.core.math import UNITVECTOR3D_X, UNITVECTOR3D_Y, Point2D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.sketch import Sketch

# %% [markdown]
# ## Initialize the modeler

# %%
modeler = launch_modeler()
print(modeler)

# %% [markdown]
# ## Create a design with two separate bodies
#
# Create a design and extrude two box sketches into separate bodies. The bodies are
# placed apart from each other so that a measurable gap exists between them.

# %%
design = modeler.create_design("MeasurementToolsDemo")

# Create the first box body
sketch1 = Sketch()
sketch1.box(Point2D([0, 0], unit=UNITS.m), width=1 * UNITS.m, height=1 * UNITS.m)
box1 = design.extrude_sketch("Box1", sketch1, 1 * UNITS.m)

# Create the second box body and translate it away from the first
sketch2 = Sketch()
sketch2.box(Point2D([0, 0], unit=UNITS.m), width=1 * UNITS.m, height=1 * UNITS.m)
box2 = design.extrude_sketch("Box2", sketch2, 1 * UNITS.m)
box2.translate(UNITVECTOR3D_X, 3)

design.plot()

# %% [markdown]
# ## Measure the minimum distance between two bodies
#
# Use ``modeler.measurement_tools.min_distance_between_objects()`` to find the
# minimum distance between the two box bodies. The method returns a ``Gap`` object
# whose ``distance`` attribute contains the measured value.

# %%
gap = modeler.measurement_tools.min_distance_between_objects(box1, box2)
print(f"Minimum distance between Box1 and Box2: {gap.distance}")

# %% [markdown]
# ## Measure the minimum distance between two faces
#
# The same method accepts ``Face`` objects as inputs (requires Ansys release 25R2
# or later). This allows measuring the gap between specific faces of the bodies.

# %%
# Select a face from each body to measure between
face1 = box1.faces[0]
face2 = box2.faces[0]

gap_faces = modeler.measurement_tools.min_distance_between_objects(face1, face2)
print(f"Minimum distance between selected faces: {gap_faces.distance}")

# %% [markdown]
# ## Measure the minimum distance between two edges
#
# Similarly, ``Edge`` objects can be passed to measure the gap between specific
# edges (requires Ansys release 25R2 or later).

# %%
# Select an edge from each body to measure between
edge1 = box1.edges[0]
edge2 = box2.edges[0]

gap_edges = modeler.measurement_tools.min_distance_between_objects(edge1, edge2)
print(f"Minimum distance between selected edges: {gap_edges.distance}")

# %% [markdown]
# ## Close the modeler
#
# Close the modeler to free up resources and release the connection.

# %%
modeler.close()
