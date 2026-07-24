# ---
# jupyter:
#   jupytext:
#     default_lexer: ipython3
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.4
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
# ### Export to USD format
#
# The design tessellation can be exported to a
# [Universal Scene Description (USD)](https://openusd.org/release/index.html) file.
# USD is a widely adopted open format for 3D scenes used in visual effects, gaming,
# and engineering workflows (e.g. NVIDIA Omniverse, Apple RealityKit).
#
# The export tessellates all bodies in the design, preserves the full component/body
# hierarchy as USD prims, and writes per-body color as a ``UsdPreviewSurface`` material.
#
# This feature requires the optional ``usd-core`` package:
#
# ```text
# pip install ansys-geometry-core[usd]
# ```
#
# Once installed, call ``export_to_usd()`` on any active design. The default format is
# USD ASCII (``usda``), which is human-readable and useful for debugging:
#
# ```python
# from pathlib import Path
#
# download_dir = Path.cwd() / "downloads"
#
# # Export to USD ASCII format (default)
# file_location = design.export_to_usd(download_dir)
# print(f"Design exported to {file_location}")
# ```
#
# You can choose the USD format via the ``file_format`` parameter:
#
# ```python
# # USD binary crate format (compact, faster to load)
# file_location = design.export_to_usd(download_dir, file_format="usdc")
#
# # USD zip archive (self-contained, ideal for sharing)
# file_location = design.export_to_usd(download_dir, file_format="usdz")
# ```
#
# To control tessellation quality, pass a ``TessellationOptions`` object:
#
# ```python
# from ansys.geometry.core.misc.options import TessellationOptions
# from ansys.geometry.core.misc.measurements import Distance, Angle
# from pint import Quantity
#
# # Fine tessellation: small surface deviation, tight angle tolerance
# tess_options = TessellationOptions(
#     surface_deviation=Distance(Quantity(0.001, "m")),
#     angle_deviation=Angle(Quantity(0.1, "rad")),
# )
#
# file_location = design.export_to_usd(download_dir, tess_options=tess_options)
# print(f"Design exported to {file_location}")
# ```
#
# The resulting USD file preserves the full component/body hierarchy. For a design
# named ``MyDesign`` with one component and two bodies it looks like:
#
# ```text
# /MyDesign                         # root Xform (default prim)
#   /MyComponent                    # Xform per component
#     /Body1                        # Mesh prim (triangulated geometry)
#     /Body2                        # Mesh prim (triangulated geometry)
#     /Looks
#       /Body1_mat                  # UsdPreviewSurface material (body color)
#       /Body2_mat                  # UsdPreviewSurface material (body color)
# ```
#
# ### Export to HTML format
#
# The design can be exported directly to a self-contained HTML viewer using
# [ansys-tools-visualization-interface](https://visualization-interface.tools.docs.pyansys.com).
# The resulting HTML page embeds all geometry as a GLB file and renders it with
# [Three.js](https://threejs.org) — only a CDN connection is required to view it
# in any modern browser. No intermediate USD file is written to disk.
#
# This feature requires the ``usd`` optional extra, which bundles
# ``ansys-tools-visualization-interface[usd]``:
#
# ```text
# pip install ansys-geometry-core[html]
# ```
#
# Once installed, call ``export_to_html()`` on any active design:
#
# ```python
# from pathlib import Path
#
# download_dir = Path.cwd() / "downloads"
#
# html_path = design.export_to_html(download_dir)
# print(f"HTML viewer written to: {html_path}")
# ```
#
# The generated HTML file is fully self-contained — copy it anywhere and open
# it without a server:
#
# ```python
# import webbrowser
#
# webbrowser.open(html_path.as_uri())
# ```
#
# ### Close the modeler
#
# Close the modeler after exporting the design.

# %%
# Close the modeler
modeler.close()
