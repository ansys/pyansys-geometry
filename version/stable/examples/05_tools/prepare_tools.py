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
# # Tools: Using PrepareTools to prepare geometry for simulation
#
# This example demonstrates how to use the ``PrepareTools`` class to prepare geometry
# for simulation. The ``PrepareTools`` class provides methods for extracting flow volumes,
# removing rounds, sharing topology between bodies, detecting helixes, creating enclosures,
# and identifying sweepable bodies.
#
# The ``PrepareTools`` instance is accessible through ``modeler.prepare_tools``.
# It should not be instantiated directly by the user.

# %% [markdown]
# ## Perform required imports
#
# Perform the required imports.

# %%
from pathlib import Path
import requests

from ansys.geometry.core import launch_modeler
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc.measurements import UNITS
from ansys.geometry.core.sketch import Sketch
from ansys.geometry.core.tools.prepare_tools import EnclosureOptions

# %% [markdown]
# ## Download example files
#
# Download example geometry files from the PyAnsys Geometry repository.
# These files are used to demonstrate how the ``PrepareTools`` methods work
# with real geometry.

# %%
BASE_URL = (
    "https://raw.githubusercontent.com/ansys/pyansys-geometry/main/tests/integration/files/"
)

FILES = {
    "hollow_cylinder": "hollowCylinder.scdocx",
    "box_with_round": "BoxWithRound.scdocx",
    "mixing_tank": "MixingTank.scdocx",
    "bolt": "bolt.scdocx",
    "different_shapes": "DifferentShapes.scdocx",
}


def download_file(filename):
    """Download a file from the PyAnsys Geometry repository."""
    url = BASE_URL + filename
    local_path = Path.cwd() / filename
    response = requests.get(url)
    response.raise_for_status()
    local_path.write_bytes(response.content)
    print(f"Downloaded: {filename}")
    return local_path


file_paths = {key: download_file(name) for key, name in FILES.items()}

# %% [markdown]
# ## Initialize the modeler

# %%
modeler = launch_modeler()
print(modeler)

# %% [markdown]
# ## Extract a flow volume from faces
#
# ``extract_volume_from_faces()`` creates a new body representing the interior volume
# of a part. You provide sealing faces (which close off the volume) and inside faces
# (which define the wetted interior surface).
#
# This is commonly used to extract a fluid domain from a solid CAD model.

# %%
design = modeler.open_file(file_paths["hollow_cylinder"])
design.plot()

body = design.bodies[0]
print(f"Body name: {body.name}")
print(f"Number of faces: {len(body.faces)}")

# Use two end faces as sealing faces and the inner cylindrical face as the inside face
sealing_faces = [body.faces[1], body.faces[2]]
inside_faces = [body.faces[0]]

created_bodies = modeler.prepare_tools.extract_volume_from_faces(sealing_faces, inside_faces)
print(f"Number of bodies created: {len(created_bodies)}")
design.plot()

# %% [markdown]
# ## Extract a flow volume from edge loops
#
# ``extract_volume_from_edge_loops()`` creates a volume from a set of edges that
# define a closed loop. This is an alternative to face-based extraction when
# working with open-shell or surface models.

# %%
design = modeler.open_file(file_paths["hollow_cylinder"])

body = design.bodies[0]
print(f"Number of edges: {len(body.edges)}")

# Use two circular edges at either end of the hollow cylinder to define the sealing loop
sealing_edges = [body.edges[2], body.edges[3]]

created_bodies = modeler.prepare_tools.extract_volume_from_edge_loops(sealing_edges)
print(f"Number of bodies created: {len(created_bodies)}")
design.plot()

# %% [markdown]
# ## Remove rounds from geometry
#
# ``remove_rounds()`` removes fillet or round faces from a solid body.
# This is useful for simplifying geometry before meshing or simulation.
#
# The ``auto_shrink`` parameter controls whether the surrounding faces are extended
# to fill the gap left by the removed rounds.

# %%
from ansys.geometry.core.designer import SurfaceType

design = modeler.open_file(file_paths["box_with_round"])
design.plot()

body = design.bodies[0]
print(f"Number of faces before removing rounds: {len(body.faces)}")

# Identify and remove the cylindrical (round) faces
round_faces = [
    face for face in body.faces if face.surface_type == SurfaceType.SURFACETYPE_CYLINDER
]
print(f"Number of round faces found: {len(round_faces)}")

result = modeler.prepare_tools.remove_rounds(round_faces)
print(f"Remove rounds successful: {result}")
print(f"Number of faces after removing rounds: {len(body.faces)}")
design.plot()

# %% [markdown]
# ## Share topology between bodies
#
# ``share_topology()`` merges the topology of touching or intersecting bodies
# so that they share edges and faces at their boundaries. This is required for
# conformal meshing in simulation workflows.

# %%
design = modeler.create_design("ShareTopologyExample")

# Create two adjacent boxes that share a face
sketch1 = Sketch()
sketch1.box(Point2D([10, 10], UNITS.mm), 10 * UNITS.mm, 10 * UNITS.mm)
design.extrude_sketch("Box1", sketch1, 10 * UNITS.mm)

sketch2 = Sketch()
sketch2.box(Point2D([20, 10], UNITS.mm), 10 * UNITS.mm, 10 * UNITS.mm)
design.extrude_sketch("Box2", sketch2, 5 * UNITS.mm)

# Count faces and edges before sharing topology
faces_before = sum(len(body.faces) for body in design.bodies)
edges_before = sum(len(body.edges) for body in design.bodies)
print(f"Faces before share topology:  {faces_before}")
print(f"Edges before share topology:  {edges_before}")

design.plot()

result = modeler.prepare_tools.share_topology(design.bodies)
print(f"Share topology successful: {result}")

# Count faces and edges after sharing topology
faces_after = sum(len(body.faces) for body in design.bodies)
edges_after = sum(len(body.edges) for body in design.bodies)
print(f"Faces after share topology:   {faces_after}")
print(f"Edges after share topology:   {edges_after}")

design.plot()

# %% [markdown]
# ## Detect helixes in geometry
#
# ``detect_helixes()`` identifies helical edges in a body, such as screw threads.
# The method accepts optional ``min_radius``, ``max_radius``, and ``fit_radius_error``
# parameters to control which helixes are detected.

# %%
design = modeler.open_file(file_paths["bolt"])
design.plot()

bodies = design.bodies
print(f"Number of bodies: {len(bodies)}")

# Detect helixes using default parameters
result = modeler.prepare_tools.detect_helixes([bodies[0]])
print(f"Number of helixes detected: {len(result['helixes'])}")

for i, helix in enumerate(result["helixes"]):
    print(f"  Helix {i + 1}: {len(helix['edges'])} edge(s)")

# %% [markdown]
# ## Create a box enclosure around bodies
#
# ``create_box_enclosure()`` generates a rectangular box that surrounds the specified bodies.
# The distance parameters control the clearance between each body face and the enclosure wall.
#
# ``EnclosureOptions`` controls whether the enclosed bodies are subtracted from the enclosure
# and whether shared topology is applied automatically.

# %%
design = modeler.open_file(file_paths["box_with_round"])
bodies = [design.bodies[0]]

# Create an enclosure with the enclosed body subtracted (default behavior)
enclosure_options = EnclosureOptions(subtract_bodies=True)
enclosure_bodies = modeler.prepare_tools.create_box_enclosure(
    bodies, 0.005, 0.01, 0.01, 0.005, 0.10, 0.10, enclosure_options
)
print(f"Number of enclosure bodies created: {len(enclosure_bodies)}")

design.plot()

# %% [markdown]
# ## Create a sphere enclosure around bodies
#
# ``create_sphere_enclosure()`` generates a spherical enclosure around the given bodies.
# The ``radial_distance`` parameter sets the clearance between the bodies and the sphere surface.

# %%
design = modeler.open_file(file_paths["box_with_round"])
bodies = [design.bodies[0]]

enclosure_options = EnclosureOptions()
enclosure_bodies = modeler.prepare_tools.create_sphere_enclosure(bodies, 0.1, enclosure_options)
print(f"Number of enclosure bodies created: {len(enclosure_bodies)}")

design.plot()

# %% [markdown]
# ## Detect sweepable bodies
#
# ``detect_sweepable_bodies()`` checks whether each body in a list can be swept
# (that is, whether it has a consistent cross-section that can be extruded along a path).
# Set ``get_source_target_faces=True`` to also retrieve the source and target faces
# used for the sweep.

# %%
design = modeler.open_file(file_paths["different_shapes"])
bodies = design.bodies
print(f"Number of bodies: {len(bodies)}")

# Check sweepability without retrieving source/target faces
results = modeler.prepare_tools.detect_sweepable_bodies(bodies)
for i, (is_sweepable, faces) in enumerate(results):
    print(f"  Body '{bodies[i].name}': sweepable={is_sweepable}")

# %%
# Check sweepability and retrieve source/target faces for sweepable bodies
results_with_faces = modeler.prepare_tools.detect_sweepable_bodies(
    bodies, get_source_target_faces=True
)
for i, (is_sweepable, faces) in enumerate(results_with_faces):
    face_info = f", source/target faces={len(faces)}" if is_sweepable else ""
    print(f"  Body '{bodies[i].name}': sweepable={is_sweepable}{face_info}")

# %% [markdown]
# ## Close the modeler
#
# Close the modeler to free up resources and release the connection.

# %%
modeler.close()
