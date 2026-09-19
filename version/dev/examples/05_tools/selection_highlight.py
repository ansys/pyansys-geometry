# ---
# jupyter:
#   jupytext:
#     default_lexer: ipython3
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Tools: Highlighting a face selection in the plotter
#
# This example demonstrates how to build a ``FaceSelection`` from a real model and
# overlay the selected faces on top of the plotted geometry by using the
# ``highlight`` parameter of ``GeometryPlotter.plot()``.
#
# The workflow mirrors a typical selection-builder pipeline: start from all faces,
# filter the selection by edge count, area, and location, and then highlight only
# the final subset in the plot.

# %% [markdown]
# ## Perform required imports
#
# Perform the required imports.

# %%
from pathlib import Path
import requests

from ansys.geometry.core import launch_modeler
from ansys.geometry.core.misc.options import ImportOptions
from ansys.geometry.core.plotting import GeometryPlotter
from ansys.geometry.core.selection_builder.selection_builder import RangeType

# %% [markdown]
# ## Download the example file
#
# Download the bracket model from the PyAnsys Geometry repository.

# %%
BASE_URL = (
    "https://raw.githubusercontent.com/ansys/pyansys-geometry/main/tests/integration/files/"
)


def download_file(filename):
    """Download an example file from the PyAnsys Geometry repository."""
    url = BASE_URL + filename
    local_path = Path.cwd() / filename
    response = requests.get(url)
    response.raise_for_status()
    local_path.write_bytes(response.content)
    print(f"Downloaded: {filename}")
    return local_path


file_path = download_file("Bracket_Static_Stress.dsco")

# %% [markdown]
# ## Initialize the modeler

# %%
modeler = launch_modeler()
print(modeler)

# %% [markdown]
# ## Import the bracket model
#
# Import the bracket file and preserve entity names.

# %%
options = ImportOptions()
options.import_names = True

design = modeler.open_file(file_path=file_path, import_options=options)

# %% [markdown]
# ## Build the face selection to highlight
#
# Create a face selection and progressively narrow it down by using the same
# filtering workflow as the local plotting script.

# %%
sb = modeler.create_selection_builder()

all_faces = sb.faces.get_all_faces()
print("All faces:", len(all_faces.items))

faces_3_4_edges = all_faces.filter_faces_by_edge_count(3, 4)
print("Faces with 3-4 edges:", len(faces_3_4_edges.items))

faces_by_area = faces_3_4_edges.filter_faces_by_area(0.00000247858, 0.0002564094)
print("Faces with area range:", len(faces_by_area.items))

faces_by_x = faces_by_area & faces_by_area.get_faces_with_x_location(
    range_type=RangeType.RANGETYPE_CONTAIN, min=0, max=0.010
)
print("Faces with x location 0-0.010:", len(faces_by_x.items))

remove_face = faces_by_x.get_faces_with_y_location(
    range_type=RangeType.RANGETYPE_INTERSECT, min=0.11753, max=0.122
)
print("Faces to remove:", len(remove_face.items))

final_faces = faces_by_x - remove_face
print("Final faces:", len(final_faces.items))

# %% [markdown]
# ## Highlight the selected faces in the plotter
#
# Pass the final ``FaceSelection`` to ``GeometryPlotter.plot()`` by using the
# ``highlight`` parameter. The base design is plotted first, and then the selected
# faces are overlaid on top of it.

# %%
plotter = GeometryPlotter()
plotter.plot(design, highlight=final_faces)
plotter.show()

# %% [markdown]
# ## Close the modeler
#
# Close the modeler to free up resources and release the connection.

# %%
modeler.close()
