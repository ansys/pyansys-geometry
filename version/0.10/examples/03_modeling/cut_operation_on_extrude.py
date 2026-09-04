# ---
# jupyter:
#   jupytext:
#     default_lexer: ipython3
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Modeling: Extruded plate with cut operations
#
# As seen in the [Rectangular plate with multiple bodies](./plate_with_hole.mystnb) example,
# you can create a complex sketch with holes and extrude it to create a body. However, you can also
# perform cut operations on the extruded body to achieve similar results.

# %% [markdown]
# ## Perform required imports
#
# Perform the required imports.

# %%
from pint import Quantity

from ansys.geometry.core import launch_modeler
from ansys.geometry.core.math import Plane, Point3D, Point2D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.sketch import Sketch

# %% [markdown]
# ## Define sketch profile without holes
#
# Create a sketch profile for the proposed design. The sketch is the same as the
# [Rectangular plate with multiple bodies](./plate_with_hole.mystnb) example, but without the holes.
#
# These holes are created by performing cut operations on the extruded body in the next steps.

# %%
sketch = Sketch()
(sketch.segment(Point2D([-4, 5], unit=UNITS.m), Point2D([4, 5], unit=UNITS.m))
    .segment_to_point(Point2D([4, -5], unit=UNITS.m))
    .segment_to_point(Point2D([-4, -5], unit=UNITS.m))
    .segment_to_point(Point2D([-4, 5], unit=UNITS.m))
    .box(Point2D([0,0], unit=UNITS.m), Quantity(3, UNITS.m), Quantity(3, UNITS.m))
)

modeler = launch_modeler()
design = modeler.create_design("ExtrudedPlateNoHoles")
body = design.extrude_sketch(f"PlateLayer", sketch, Quantity(2, UNITS.m))

design.plot()

# %% [markdown]
# ## Define sketch profile for holes
#
# Create a sketch profile for the holes in the proposed design. The holes are created by
# sketching circles at the four corners of the plate. First create a reference sketch
# for all the circles. This sketch is translated to the four corners of the plate.

# %%
sketch_hole = Sketch()
sketch_hole.circle(Point2D([0, 0], unit=UNITS.m), Quantity(0.5, UNITS.m))

hole_centers = [
    Plane(Point3D([3, 4, 0], unit=UNITS.m)),
    Plane(Point3D([-3, 4, 0], unit=UNITS.m)),
    Plane(Point3D([-3, -4, 0], unit=UNITS.m)),
    Plane(Point3D([3, -4, 0], unit=UNITS.m)),
]

# %% [markdown]
# ## Perform cut operations on the extruded body
#
# Perform cut operations on the extruded body to create holes at the four corners of the plate.

# %%
for center in hole_centers:
    sketch_hole.plane = center
    design.extrude_sketch(
        name= f"H_{center.origin.x}_{center.origin.y}",
        sketch=sketch_hole,
        distance=Quantity(2, UNITS.m),
        cut=True,
    )

design.plot()

# %% [markdown]
# ## Close the modeler
#
# Close the modeler to free up resources and release the connection.

# %%
modeler.close()
