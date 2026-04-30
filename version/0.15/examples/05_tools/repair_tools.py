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
# # Tools: Using RepairTools to inspect and fix geometry
#
# This example demonstrates how to use the ``RepairTools`` class to inspect
# and repair common geometry issues. The ``RepairTools`` class provides methods
# for finding and fixing problems such as split edges, extra edges, inexact edges,
# short edges, duplicate faces, missing faces, small faces, and stitchable faces.
#
# The ``RepairTools`` instance is accessible through ``modeler.repair_tools``.
# It should not be instantiated directly by the user.

# %% [markdown]
# ## Perform required imports
#
# Perform the required imports.

# %%
from pathlib import Path
import requests

from ansys.geometry.core import launch_modeler

# %% [markdown]
# ## Download example files
#
# Download example geometry files that contain known problem areas from the
# PyAnsys Geometry repository. These files are used to demonstrate how the
# ``RepairTools`` methods detect and fix real geometry issues.

# %%
BASE_URL = (
    "https://raw.githubusercontent.com/ansys/pyansys-geometry/main/tests/integration/files/"
)

FILES = {
    "split_edges": "SplitEdgeDesignTest.scdocx",
    "extra_edges": "ExtraEdgesDesignBefore.scdocx",
    "inexact_edges": "InExactEdgesBefore.scdocx",
    "short_edges": "ShortEdgesBefore.scdocx",
    "duplicate_faces": "DuplicateFacesDesignBefore.scdocx",
    "missing_faces": "MissingFacesDesignBefore.scdocx",
    "small_faces": "SmallFaces.scdocx",
    "stitch_faces": "stitch_before.scdocx",
    "inspect_repair": "InspectAndRepair01.scdocx",
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
# ## Find split edges
#
# Split edges are edges that are unnecessarily divided into multiple segments.
# ``find_split_edges()`` detects them. Optional ``angle`` and ``length`` parameters
# control the detection thresholds.

# %%
design = modeler.open_file(file_paths["split_edges"])
split_edge_problems = modeler.repair_tools.find_split_edges(design.bodies)
print(f"Number of split edge problem areas found: {len(split_edge_problems)}")

# %% [markdown]
# ## Fix split edge problem areas
#
# Each problem area object returned by the ``find_*`` methods exposes a ``fix()``
# method that resolves that specific issue.

# %%
for problem in split_edge_problems:
    result = problem.fix()
    print(f"Split edge fix successful: {result.success}")

# Verify the problem areas are resolved
split_edge_problems_after = modeler.repair_tools.find_split_edges(design.bodies)
print(f"Split edge problem areas remaining: {len(split_edge_problems_after)}")

# %% [markdown]
# ## Find extra edges
#
# Extra edges are edges that exist inside a face but do not contribute to
# defining the face boundary.
# ``find_extra_edges()`` detects them.

# %%
design = modeler.open_file(file_paths["extra_edges"])
extra_edge_problems = modeler.repair_tools.find_extra_edges(design.bodies)
print(f"Number of extra edge problem areas found: {len(extra_edge_problems)}")

# %% [markdown]
# ## Fix extra edge problem areas

# %%
for problem in extra_edge_problems:
    result = problem.fix()
    print(f"Extra edge fix successful: {result.success}")

extra_edge_problems_after = modeler.repair_tools.find_extra_edges(design.bodies)
print(f"Extra edge problem areas remaining: {len(extra_edge_problems_after)}")

# %% [markdown]
# ## Find inexact edges
#
# Inexact edges are edges whose geometry does not precisely match the underlying
# surface geometry.
# ``find_inexact_edges()`` detects them.

# %%
design = modeler.open_file(file_paths["inexact_edges"])
inexact_edge_problems = modeler.repair_tools.find_inexact_edges(design.bodies)
print(f"Number of inexact edge problem areas found: {len(inexact_edge_problems)}")

# %% [markdown]
# ## Fix inexact edge problem areas

# %%
for problem in inexact_edge_problems:
    result = problem.fix()
    print(f"Inexact edge fix successful: {result.success}")

inexact_edge_problems_after = modeler.repair_tools.find_inexact_edges(design.bodies)
print(f"Inexact edge problem areas remaining: {len(inexact_edge_problems_after)}")

# %% [markdown]
# ## Find short edges
#
# Short edges are edges that are shorter than a given threshold length.
# ``find_short_edges()`` detects them. Provide a length threshold to control
# which edges are flagged.

# %%
design = modeler.open_file(file_paths["short_edges"])
short_edge_problems = modeler.repair_tools.find_short_edges(design.bodies, 10)
print(f"Number of short edge problem areas found: {len(short_edge_problems)}")

# %% [markdown]
# ## Fix short edge problem areas

# %%
for problem in short_edge_problems:
    result = problem.fix()
    print(f"Short edge fix successful: {result.success}")

short_edge_problems_after = modeler.repair_tools.find_short_edges(design.bodies, 10)
print(f"Short edge problem areas remaining: {len(short_edge_problems_after)}")

# %% [markdown]
# Even though all of the ``fix()`` calls were successful, some designs are unable to fix all problem areas simultaneously.

# %% [markdown]
# ## Find duplicate faces
#
# Duplicate faces are faces that occupy the same region of space.
# ``find_duplicate_faces()`` detects them.

# %%
design = modeler.open_file(file_paths["duplicate_faces"])
duplicate_face_problems = modeler.repair_tools.find_duplicate_faces(design.bodies)
print(f"Number of duplicate face problem areas found: {len(duplicate_face_problems)}")

# %% [markdown]
# ## Fix duplicate face problem areas

# %%
for problem in duplicate_face_problems:
    result = problem.fix()
    print(f"Duplicate face fix successful: {result.success}")

duplicate_face_problems_after = modeler.repair_tools.find_duplicate_faces(design.bodies)
print(f"Duplicate face problem areas remaining: {len(duplicate_face_problems_after)}")

# %% [markdown]
# ## Find missing faces
#
# Missing faces represent openings in an otherwise closed solid body.
# ``find_missing_faces()`` detects them.

# %%
design = modeler.open_file(file_paths["missing_faces"])
design.plot()
missing_face_problems = modeler.repair_tools.find_missing_faces(design.bodies)
print(f"Number of missing face problem areas found: {len(missing_face_problems)}")

# %% [markdown]
# ## Fix missing face problem areas

# %%
for problem in missing_face_problems:
    result = problem.fix()
    print(f"Missing face fix successful: {result.success}")

missing_face_problems_after = modeler.repair_tools.find_missing_faces(design.bodies)
print(f"Missing face problem areas remaining: {len(missing_face_problems_after)}")
design.plot()

# %% [markdown]
# ## Find small faces
#
# Small faces are faces that fall below a given area or width threshold.
# ``find_small_faces()`` detects them.

# %%
design = modeler.open_file(file_paths["small_faces"])
design.plot()
small_face_problems = modeler.repair_tools.find_small_faces(design.bodies)
print(f"Number of small face problem areas found: {len(small_face_problems)}")

# %% [markdown]
# ## Fix small face problem areas

# %%
for problem in small_face_problems:
    result = problem.fix()
    print(f"Small face fix successful: {result.success}")

small_face_problems_after = modeler.repair_tools.find_small_faces(design.bodies)
print(f"Small face problem areas remaining: {len(small_face_problems_after)}")

# %%
# Fix the remaining issue
small_face_problems_after[0].fix()
small_face_problems_after = modeler.repair_tools.find_small_faces(design.bodies)
print(f"Small face problem areas remaining: {len(small_face_problems_after)}")
design.plot()

# %% [markdown]
# ## Find stitchable faces
#
# Stitchable faces are faces that can be joined together at a shared boundary.
# ``find_stitch_faces()`` detects them. An optional ``max_distance`` parameter
# sets the tolerance for coincident boundaries.

# %%
design = modeler.open_file(file_paths["stitch_faces"])
stitch_face_problems = modeler.repair_tools.find_stitch_faces(design.bodies)
print(f"Number of stitch face problem areas found: {len(stitch_face_problems)}")

# %% [markdown]
# ## Fix stitch face problem areas

# %%
for problem in stitch_face_problems:
    result = problem.fix()
    print(f"Stitch face fix successful: {result.success}")
    print(f"  Bodies modified: {len(result.modified_bodies)}")

stitch_face_problems_after = modeler.repair_tools.find_stitch_faces(design.bodies)
print(f"Stitch face problem areas remaining: {len(stitch_face_problems_after)}")

# %% [markdown]
# ## Find and fix short edges in one step
#
# The ``find_and_fix_*`` convenience methods combine detection and repair into
# a single call and return a ``RepairToolMessage`` summarizing the outcome.

# %%
design = modeler.open_file(file_paths["short_edges"])
result = modeler.repair_tools.find_and_fix_short_edges(design.bodies, 10)
print(f"Find-and-fix short edges successful: {result.success}")
print(f"  Problem areas found:    {result.found}")
print(f"  Problem areas repaired: {result.repaired}")

# %% [markdown]
# ## Find and fix extra edges in one step

# %%
design = modeler.open_file(file_paths["extra_edges"])
result = modeler.repair_tools.find_and_fix_extra_edges(design.bodies)
print(f"Find-and-fix extra edges successful: {result.success}")
print(f"  Problem areas found:    {result.found}")
print(f"  Problem areas repaired: {result.repaired}")

# %% [markdown]
# ## Find and fix split edges in one step

# %%
design = modeler.open_file(file_paths["split_edges"])
result = modeler.repair_tools.find_and_fix_split_edges(design.bodies)
print(f"Find-and-fix split edges successful: {result.success}")
print(f"  Problem areas found:    {result.found}")
print(f"  Problem areas repaired: {result.repaired}")

# %% [markdown]
# ## Inspect and repair all geometry issues
#
# The ``inspect_geometry()`` method returns a detailed list of all detected
# issues grouped by body. Each entry in the list exposes a ``repair()``
# method for fixing that specific issue.
#
# The ``repair_geometry()`` method attempts to fix all detected issues
# automatically with a single call.

# %%
design = modeler.open_file(file_paths["inspect_repair"])

# Inspect all geometry issues in the design
inspect_results = modeler.repair_tools.inspect_geometry(design.bodies)
print(f"Number of bodies with issues: {len(inspect_results)}")

for result in inspect_results:
    print(f"  Body: {result.body.name if result.body else 'N/A'}")
    for issue in result.issues:
        print(f"    [{issue.message_type}] {issue.message}")

# %%
# Repair all geometry issues automatically
repair_result = modeler.repair_tools.repair_geometry(design.bodies)
print(f"Repair geometry successful: {repair_result.success}")

# Verify all issues have been resolved
inspect_results_after = modeler.repair_tools.inspect_geometry(design.bodies)
print(f"Bodies with issues remaining: {len(inspect_results_after)}")

# %% [markdown]
# ## Close the modeler
#
# Close the modeler to free up resources and release the connection.

# %%
modeler.close()
