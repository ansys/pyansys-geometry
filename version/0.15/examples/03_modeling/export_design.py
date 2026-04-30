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
# # Modeling: Exporting designs
#
# After creating a design, you typically want to bring it into a CAD tool for further
# development. This notebook demonstrates how to export a design to the various supported
# CAD formats.
#
# ## Create a design
#
# The code creates a simple design for demonstration purposes. The design consists of
# a set of rectangular pads with a circular hole in the center.

# %%
from ansys.geometry.core import launch_modeler
from ansys.geometry.core.math import UNITVECTOR3D_X, UNITVECTOR3D_Y, Point2D
from ansys.geometry.core.sketch import Sketch

# Instantiate the modeler
modeler = launch_modeler()

# Create a design
design = modeler.create_design("ExportDesignExample")

# Create a sketch
sketch = Sketch()

# Create a simple rectangle
sketch.box(Point2D([0, 0]), 10, 5)

# Extrude the sketch and displace the resulting body
# to make a plane of rectangles
for x_step in [-60, -45, -30, -15, 0, 15, 30, 45, 60]:
    for y_step in [-40, -30, -20, -10, 0, 10, 20, 30, 40]:
        # Extrude the sketch
        body = design.extrude_sketch(f"Body_X_{x_step}_Y_{y_step}", sketch, 5)

        # Displace the body in the x and y directions
        body.translate(UNITVECTOR3D_X, x_step)
        body.translate(UNITVECTOR3D_Y, y_step)

# Plot the design
design.plot()

# %% [markdown]
# ## Export the design
#
# You can export the design to various CAD formats. For the formats supported
# see the [DesignFileFormat](https://geometry.docs.pyansys.com/version/stable/api/ansys/geometry/core/designer/design/DesignFileFormat.html)
# class, which is part of the the ``design`` module documentation.
#
# Nonetheless, there are a set of convenience methods that you can use to export
# the design to the supported formats. The following code snippets demonstrate how
# to do it. You can decide whether to export the design to a file in
# a certain directory or in the current working directory.
#
# ### Export to a file in the current working directory

# %%
# Export the design to a file in the current working directory
file_location = design.export_to_scdocx()
print(f"Design exported to {file_location}")

# %% [markdown]
# ### Export to a file in a certain directory

# %%
from pathlib import Path

# Define a downloads directory
download_dir = Path.cwd() / "downloads"

# Export the design to a file in a certain directory
file_location = design.export_to_scdocx(download_dir)
print(f"Design exported to {file_location}")

# %% [markdown]
# ### Export to SCDOCX format

# %%
# Export the design to a file in the requested directory
file_location = design.export_to_scdocx(download_dir)

# Print the file location
print(f"Design exported to {file_location}")
print(f"Does the file exist? {Path(file_location).exists()}")

# %% [markdown]
# ### Export to Parasolid text format

# %%
# Export the design to a file in the requested directory
file_location = design.export_to_parasolid_text(download_dir)

# Print the file location
print(f"Design exported to {file_location}")
print(f"Does the file exist? {Path(file_location).exists()}")

# %% [markdown]
# ### Export to Parasolid binary format

# %%
# Export the design to a file in the requested directory
file_location = design.export_to_parasolid_bin(download_dir)

# Print the file location
print(f"Design exported to {file_location}")
print(f"Does the file exist? {Path(file_location).exists()}")

# %% [markdown]
# ### Export to STEP format
#
# ```python
# # Export the design to a file in the requested directory
# file_location = design.export_to_step(download_dir)
#
# # Print the file location
# print(f"Design exported to {file_location}")
# print(f"Does the file exist? {Path(file_location).exists()}")
# ```
#
# ### Export to IGES format
#
# ```python
# # Export the design to a file in the requested directory
# file_location = design.export_to_iges(download_dir)
#
# # Print the file location
# print(f"Design exported to {file_location}")
# print(f"Does the file exist? {Path(file_location).exists()}")
# ```
#
# ### Export to FMD format

# %%
# Export the design to a file in the requested directory
file_location = design.export_to_fmd(download_dir)

# Print the file location
print(f"Design exported to {file_location}")
print(f"Does the file exist? {Path(file_location).exists()}")

# %% [markdown]
# ### Export to PMDB format
#
# ```python
# # Export the design to a file in the requested directory
# file_location = design.export_to_pmdb(download_dir)
# ```
#
# ### Export to Discovery format

# %%
# Export the design to a file in the requested directory
file_location = design.export_to_disco(download_dir)

# Print the file location
print(f"Design exported to {file_location}")
print(f"Does the file exist? {Path(file_location).exists()}")

# %% [markdown]
# ### Close the modeler
#
# Close the modeler after exporting the design.

# %%
# Close the modeler
modeler.close()
