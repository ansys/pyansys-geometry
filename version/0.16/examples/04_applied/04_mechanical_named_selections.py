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
# # Applied: Import a STEP file, add named selections, and export to Mechanical
#
# This example demonstrates a complete geometry-to-simulation workflow:
#
# 1. Open a STEP file using the Geometry Core Service.
# 2. Programmatically create named selections on the geometry using PyAnsys Geometry.
# 3. Export the annotated geometry to a PMDB file — the recommended cross-platform format
#    for transferring geometry with named selections to Ansys Mechanical.
# 4. Import the PMDB file into an embedded Mechanical session and verify that
#    the named selections are preserved.
#
# The geometry used in this example is a two-car assembly (`twoCars.stp`)
# available in the PyAnsys Geometry integration-tests folder. It is downloaded
# at runtime rather than shipped alongside this notebook.
#
# ## Download the STEP file
#
# The STEP file lives in the integration-tests folder of the PyAnsys Geometry
# repository. The following code downloads it at runtime so that no binary asset
# needs to ship alongside the notebook.

# %%
from pathlib import Path
import requests

STEP_URL = (
    "https://raw.githubusercontent.com/ansys/pyansys-geometry/main"
    "/tests/integration/files/import/twoCars.stp"
)

step_file = Path.cwd() / "twoCars.stp"
response = requests.get(STEP_URL)
response.raise_for_status()
step_file.write_bytes(response.content)
print(f"Downloaded STEP file to: {step_file}")

# %% [markdown]
# ## Launch the Geometry service and open the STEP file
#
# The following code starts the Geometry service and opens the STEP file.

# %%
from ansys.geometry.core import launch_modeler

# Launch the Geometry service
modeler = launch_modeler()

# Open the STEP file
design = modeler.open_file(step_file)

# %% [markdown]
# ## Explore the imported design
#
# After opening the file, inspect the design hierarchy. In an imported STEP
# assembly the bodies are owned by *sub-components*, not by the root design
# object directly. Use the built-in ``tree_print()`` method to visualise the
# full component/body tree, then ``get_all_bodies()`` to collect every body
# regardless of nesting depth.

# %%
# Print the component/body tree of the imported design
design.tree_print()

# %%
# Retrieve every body in the assembly (traverses all nested components)
all_bodies = design.get_all_bodies()
print(f"Total bodies found: {len(all_bodies)}")
for body in all_bodies:
    print(f"  {body.name}")

# %%
# Plot the design
design.plot()

# %% [markdown]
# ## Create named selections
#
# Named selections are labels that group bodies, faces, edges, or vertices.
# They pass through the PMDB format into Mechanical as *Named Selections*, where
# they can be used directly as scoping targets for boundary conditions, contacts,
# mesh controls, and result probes.

# %%
# Create one named selection per body so that each part can be
# addressed individually inside Mechanical.
for i, body in enumerate(all_bodies):
    ns_name = f"Part_{i + 1}"
    design.create_named_selection(ns_name, bodies=[body])
    print(f"Created named selection '{ns_name}' containing body '{body.name}'")

# %%
# Create a combined named selection that covers the entire assembly.
# This is useful for applying global mesh settings or result scoping.
design.create_named_selection("All_Parts", bodies=all_bodies)
print("Created named selection 'All_Parts' containing all bodies")

# %%
# Filter to only the named selections we created
filtered_ns = [ns for ns in design.named_selections if ns.name == "All_Parts" or ns.name.startswith("Part_")]
print(f"\nNamed selections in design {len(filtered_ns)}:")
for ns in filtered_ns:
    n_bodies = len(ns.bodies)
    print(f"  '{ns.name}' — {n_bodies} body/bodies")

# %% [markdown]
# ## Export to PMDB
#
# PMDB (Persistent Model Database) is the recommended format for transferring
# geometry **with named selections** from the Geometry service to Ansys Mechanical
# on both Windows and Linux.

# %%
# Export the annotated design to a PMDB file in the current working directory.
pmdb_path = design.export_to_pmdb()
print(f"Design exported to: {pmdb_path}")

# %% [markdown]
# ## Close the Geometry service

# %%
modeler.close()

# %% [markdown]
# ## Import the PMDB into Mechanical
#
# The PMDB file can now be imported into an embedded Mechanical session.
# The named selections created above will be preserved and appear in
# the Mechanical tree under **Named Selections**.
#
# The following code requires [PyMechanical](https://mechanical.docs.pyansys.com)
# and an Ansys Mechanical installation (2024 R1 or later).
#
# ```python
# import ansys.mechanical.core as mech
#
# # Launch an embedded Mechanical session
# app = mech.App(version=261)
#
# # ---- geometry import ----
# geometry_import = app.Model.GeometryImportGroup.AddGeometryImport()
#
# # Enable named-selection transfer
# geometry_import.GeometryImportPreferences.ProcessNamedSelections = True
# geometry_import.GeometryImportPreferences.NameSelectionKey = ""
#
# # Import the PMDB produced in the previous step
# geometry_import.Import(str(pmdb_path))
#
# # ---- verify named selections ----
# ns_group = app.Model.NamedSelections
# print(f"Named selections imported ({ns_group.Children.Count} total):")
# for child in ns_group.Children:
#     print(f"  {child.Name}")
#
# # ---- clean up ----
# app.close()
# ```
#
# The named selections (`Part_1`, `Part_2`, …, `All_Parts`) are now available
# inside Mechanical and can be used for mesh controls, boundary conditions,
# contacts, and result evaluation.
#
# ### References
#
# - [PyMechanical documentation](https://mechanical.docs.pyansys.com)
# - [PMDB export API reference](https://geometry.docs.pyansys.com/version/stable/api/ansys/geometry/core/designer/design/Design.html#Design.export_to_pmdb)
