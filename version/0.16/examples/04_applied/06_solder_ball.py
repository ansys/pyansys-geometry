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
# # Applied: Solder ball modeling for morphing
#
# Solder balls are the small spherical joints used in ball grid array (BGA)
# packages to electrically and mechanically connect a chip to a printed circuit
# board (PCB). Accurately representing their geometry is critical for thermal,
# structural, and drop-test simulations.
#
# A common meshing challenge is that cylindrical solder columns are easy to
# mesh but physically inaccurate, while spherical solder balls are realistic but
# harder to mesh. Morphing workflows solve this by:
#
# 1. Meshing a **source** model that uses idealised cylindrical solder columns
#    (easy to mesh).
# 2. Defining a **target** model with realistic spherical solder balls.
# 3. Morphing the source mesh so that the solder nodes move from the cylinder
#    shape to the spherical shape, producing a high-quality, physically
#    accurate mesh.
#
# This example builds both models using PyAnsys Geometry:
#
# - **Source model**: A six-layer PCB laminate stack with a 3 × 3 array of
#   cylindrical solder columns and copper pads.  A ``solder_cyl`` named
#   selection marks the solder surfaces that is to be morphed.
# - **Target model**: The same 3 × 3 footprint with spherical solder balls
#   created by revolving a 2D profile.  A ``solder_sph`` named selection marks
#   the spherical surfaces that define the target shape.
#
# ## Required imports
#
# Import the PyAnsys Geometry modules needed throughout the example.

# %%
from ansys.geometry.core import launch_modeler
from ansys.geometry.core.designer import SurfaceType
from ansys.geometry.core.math import (
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    UNITVECTOR3D_Z,
    Plane,
    Point2D,
    Point3D,
)
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Angle, Distance
from ansys.geometry.core.plotting import GeometryPlotter
from ansys.geometry.core.sketch import Sketch

# %% [markdown]
# ## Source model: PCB stack with cylindrical solder columns
#
# ### Launch the modeler and set units
#
# All dimensions in the source model are in millimetres.

# %%
modeler = launch_modeler()
DEFAULT_UNITS.LENGTH = UNITS.mm

# %% [markdown]
# ### Sketch the PCB laminate layers
#
# A realistic PCB stack has alternating copper and dielectric (core/prepreg)
# layers. The following table lists each layer, its start elevation (Z), and its
# thickness.
#
# | Layer | Z start (mm) | Thickness (mm) | Role |
# |-------|-------------|----------------|------|
# | Layer 1 | 0.00 | 0.24 | Bottom copper / dielectric |
# | Layer 2 | 0.24 | 0.26 | Prepreg |
# | Layer 3 | 0.50 | 0.47 | Core |
# | Infill  | 0.97 | 0.67 | PCB infill / underfill region |
# | Layer 4 | 1.64 | 0.24 | Core |
# | Layer 5 | 1.88 | 0.26 | Prepreg |
# | Layer 6 | 2.14 | 0.47 | Top copper / dielectric |
#
# All layers share a 4.0035 × 4.0035 mm² footprint centred at the origin.

# %%
BOARD_SIZE = 4.0035  # mm

layer_1_sketch = Sketch()
layer_1_sketch.box(center=Point2D([0, 0]), width=BOARD_SIZE, height=BOARD_SIZE)

layer_2_sketch = Sketch(Plane(origin=Point3D([0, 0, 0.24])))
layer_2_sketch.box(center=Point2D([0, 0]), width=BOARD_SIZE, height=BOARD_SIZE)

layer_3_sketch = Sketch(Plane(origin=Point3D([0, 0, 0.50])))
layer_3_sketch.box(center=Point2D([0, 0]), width=BOARD_SIZE, height=BOARD_SIZE)

infill_sketch = Sketch(Plane(origin=Point3D([0, 0, 0.97])))
infill_sketch.box(center=Point2D([0, 0]), width=BOARD_SIZE, height=BOARD_SIZE)

layer_4_sketch = Sketch(Plane(origin=Point3D([0, 0, 1.64])))
layer_4_sketch.box(center=Point2D([0, 0]), width=BOARD_SIZE, height=BOARD_SIZE)

layer_5_sketch = Sketch(Plane(origin=Point3D([0, 0, 1.88])))
layer_5_sketch.box(center=Point2D([0, 0]), width=BOARD_SIZE, height=BOARD_SIZE)

layer_6_sketch = Sketch(Plane(origin=Point3D([0, 0, 2.14])))
layer_6_sketch.box(center=Point2D([0, 0]), width=BOARD_SIZE, height=BOARD_SIZE)

# %% [markdown]
# ### Sketch the solder features
#
# Each solder joint consists of three features sharing a 0.25-millimeter radius:
#
# - **Bottom copper pad** — at Z = 0.97 mm, thickness 0.0382 mm
# - **Solder cylinder** — at Z = 1.0082 mm, height 0.5835 mm
# - **Top copper pad** — at Z = 1.5918 mm, thickness 0.0482 mm

# %%
SOLDER_RADIUS = 0.25  # mm

# Bottom copper pad
copper_pad_bottom_sketch = Sketch(Plane(origin=Point3D([0, 0, 0.97])))
copper_pad_bottom_sketch.circle(center=Point2D([0, 0]), radius=Distance(SOLDER_RADIUS))

# Solder cylinder
solder_cylinder_sketch = Sketch(Plane(origin=Point3D([0, 0, 1.0082])))
solder_cylinder_sketch.circle(center=Point2D([0, 0]), radius=Distance(SOLDER_RADIUS))

# Top copper pad
copper_pad_top_sketch = Sketch(Plane(origin=Point3D([0, 0, 1.5918])))
copper_pad_top_sketch.circle(center=Point2D([0, 0]), radius=Distance(SOLDER_RADIUS))

# %% [markdown]
# ### Build the PCB design
#
# Create the design and extrude all sketched profiles into solid bodies.

# %%
design = modeler.create_design("pcb_solder_cylinders")
component = design.add_component("pcb_model")

# PCB laminate layers
layer_1 = component.extrude_sketch("layer_1", layer_1_sketch, distance=Distance(0.24))
layer_2 = component.extrude_sketch("layer_2", layer_2_sketch, distance=Distance(0.26))
layer_3 = component.extrude_sketch("layer_3", layer_3_sketch, distance=Distance(0.47))
layer_4 = component.extrude_sketch("layer_4", layer_4_sketch, distance=Distance(0.24))
layer_5 = component.extrude_sketch("layer_5", layer_5_sketch, distance=Distance(0.26))
layer_6 = component.extrude_sketch("layer_6", layer_6_sketch, distance=Distance(0.47))
infill = component.extrude_sketch("infill", infill_sketch, distance=Distance(0.67))

# Solder features for the centre position (i=0, j=0)
copper_pad_bottom = component.extrude_sketch(
    "copper_pad", copper_pad_bottom_sketch, distance=Distance(0.0382)
)
solder_cylinder = component.extrude_sketch(
    "solder", solder_cylinder_sketch, distance=Distance(0.5835)
)
copper_pad_top = component.extrude_sketch(
    "copper_pad", copper_pad_top_sketch, distance=Distance(0.0482)
)

# %% [markdown]
# ### Replicate solder joints in a 3 × 3 array
#
# The solder balls are arranged on a 1-millimeter pitch in a 3 × 3 grid centered at the
# origin (offsets: −1, 0, +1 mm in X and Y).  The infill body is Boolean-subtracted
# so that the solder columns protrude through the PCB as expected.

# %%
for i in range(-1, 2):
    for j in range(-1, 2):
        if i == 0 and j == 0:
            # Center position — subtract the already-created solder bodies
            # from the infill, keeping the solder bodies themselves.
            infill.subtract(
                [copper_pad_bottom, copper_pad_top, solder_cylinder],
                keep_other=True,
            )
        else:
            # Off-center positions — copy and translate the solder bodies,
            # then subtract each copy from the infill.
            for body, owner in [
                (copper_pad_bottom, component),
                (copper_pad_top, component),
                (solder_cylinder, component),
            ]:
                new_body = body.copy(owner)
                new_body.translate(direction=UNITVECTOR3D_X, distance=i)
                new_body.translate(direction=UNITVECTOR3D_Y, distance=j)
                infill.subtract(new_body, keep_other=True)

# %% [markdown]
# ### Create the ``solder_cyl`` named selection
#
# Collect all ``solder`` bodies and their lateral (non-end-cap) cylindrical
# faces.  This named selection identifies the solder surfaces to be morphed.

# %%
solder_bodies = []
solder_source_faces = []

for body in component.bodies:
    if body.name == "solder":
        solder_bodies.append(body)
        for face in body.faces:
            # Exclude top and bottom end-cap faces (unit normal purely in Z)
            if face.normal().z not in (1, -1):
                solder_source_faces.append(face)

design.create_named_selection(
    "solder_cyl", bodies=solder_bodies, faces=solder_source_faces
)
print(
    f"'solder_cyl' named selection: "
    f"{len(solder_bodies)} bodies, {len(solder_source_faces)} lateral faces"
)

# %% [markdown]
# ### Visualize the source model
#
# The ``GeometryPlotter``, which is the visualization object leveraged throughout PyAnsys Geometry,
# displays each body type in a distinct color and opacity,
# making it easy to see the internal PCB layers through the semi-transparent
# laminate stack:
#
# - **PCB layers**: Green, semi-transparent (opacity 0.3)
# - **Infill / underfill**: Khaki, semi-transparent (opacity 0.2)
# - **Copper pads**: Orange, opaque
# - **Solder cylinders**: Silver, opaque

# %%
pcb_layers = [layer_1, layer_2, layer_3, layer_4, layer_5, layer_6]
copper_pads = [b for b in component.bodies if b.name == "copper_pad"]

plotter = GeometryPlotter()
for layer in pcb_layers:
    plotter.plot(layer, color="green", opacity=0.3, merge_bodies=True)
plotter.plot(infill, color="tan", opacity=0.2, merge_bodies=True)
for pad in copper_pads:
    plotter.plot(pad, color="orange", merge_bodies=True)
for solder in solder_bodies:
    plotter.plot(solder, color="silver", merge_bodies=True)
plotter.show()

# %% [markdown]
# ### Export the source model

# %%
source_file = design.export_to_scdocx()
print(f"Source model exported to: {source_file}")

# %%
modeler.close()

# %% [markdown]
# ## Target model: Spherical solder balls
#
# The target model replaces the cylinders with physically accurate solder ball
# shapes. Each ball is generated by revolving a 2D profile (an arc that
# approximates the meniscus of a reflowed solder joint) 360° around the Z-axis.
#
# ### Solder ball profile
#
# The profile is a circular arc with a 0.3821-millimeter radius that spans 98.82°, connecting
# the bottom pad face to the top pad face. The arc is closed with a straight
# segment to form a closed 2D region suitable for revolving.

# %%
modeler = launch_modeler()
DEFAULT_UNITS.LENGTH = UNITS.mm

# The sketch plane is offset from the Z-axis so the arc profile sits at the
# correct radial distance from the rotation axis.
solder_ball_plane = Plane(
    origin=Point3D([SOLDER_RADIUS, 0, 1.0082]),
    direction_x=UNITVECTOR3D_X,
    direction_y=UNITVECTOR3D_Z,
)

solder_ball_sketch = Sketch(solder_ball_plane)

# Draw the arc profile and close it with a line segment back to the start.
solder_ball_sketch.arc_from_start_center_and_angle(
    start=Point2D([0, 0]),
    center=Point2D([-SOLDER_RADIUS, 0.2918]),
    angle=Angle(98.82, unit=UNITS.degrees),
    clockwise=False,
).segment_to_point(Point2D([0, 0]))

solder_ball_sketch.plot()

# %% [markdown]
# ### Revolve the profile to create a single solder ball

# %%
design_target = modeler.create_design("pcb_solder_spheres")
component_target = design_target.add_component("spherical_balls")

# Revolve 360° around the global Z-axis through the origin.
solder_ball = component_target.revolve_sketch(
    "solder_ball",
    solder_ball_sketch,
    UNITVECTOR3D_Z,
    Angle(360, unit=UNITS.degrees),
    Point3D([0, 0, 1.0082]),
)

# %% [markdown]
# ### Replicate in a 3 × 3 array

# %%
for i in range(-1, 2):
    for j in range(-1, 2):
        if i == 0 and j == 0:
            continue  # Original body is already at the centre
        new_ball = solder_ball.copy(component_target)
        new_ball.translate(direction=UNITVECTOR3D_X, distance=i)
        new_ball.translate(direction=UNITVECTOR3D_Y, distance=j)

# %% [markdown]
# ### Create the ``solder_sph`` named selection
#
# Collect all ``solder_ball`` bodies and their spherical faces. These define
# the target shape for the morphing step.

# %%
solder_ball_bodies = []
solder_target_faces = []

for body in component_target.bodies:
    if body.name == "solder_ball":
        solder_ball_bodies.append(body)
        for face in body.faces:
            if face.surface_type == SurfaceType.SURFACETYPE_SPHERE:
                solder_target_faces.append(face)

design_target.create_named_selection(
    "solder_sph", bodies=solder_ball_bodies, faces=solder_target_faces
)
print(
    f"'solder_sph' named selection: "
    f"{len(solder_ball_bodies)} bodies, {len(solder_target_faces)} spherical faces"
)

# %% [markdown]
# ### Visualize the target model
#
# The solder balls are plotted in silver to convey a metallic solder appearance.

# %%
plotter = GeometryPlotter()
for ball in solder_ball_bodies:
    plotter.plot(ball, color="silver", merge_bodies=True)
plotter.show()

# %% [markdown]
# ### Export the target model

# %%
target_file = design_target.export_to_scdocx()
print(f"Target model exported to: {target_file}")

# %%
modeler.close()

# %% [markdown]
# ## Summary
#
# This example produced two geometry files ready for a mesh-morphing workflow:
#
# | File | Named selection | Purpose |
# |------|-----------------|---------|
# | `pcb_solder_cylinders.scdocx` | `solder_cyl` | Source: Easy-to-mesh cylindrical solder columns |
# | `pcb_solder_spheres.scdocx` | `solder_sph` | Target: Realistic spherical solder balls |
#
# In a downstream morphing tool (for example, Ansys Mechanical with morphing
# technology), the ``solder_cyl`` faces are mapped to the ``solder_sph`` faces so
# that the cylindrical mesh deforms smoothly into the spherical shape while the
# rest of the PCB mesh remains undisturbed.
#
# ### References
#
# - [PyAnsys Geometry API reference](https://geometry.docs.pyansys.com/version/stable/api/index.html)
# - [Sketch.arc_from_start_center_and_angle](https://geometry.docs.pyansys.com/version/stable/api/ansys/geometry/core/sketch/sketch/Sketch.html#Sketch.arc_from_start_center_and_angle)
# - [Component.revolve_sketch](https://geometry.docs.pyansys.com/version/stable/api/ansys/geometry/core/designer/component/Component.html#Component.revolve_sketch)
# - [Design.create_named_selection](https://geometry.docs.pyansys.com/version/stable/api/ansys/geometry/core/designer/design/Design.html#Design.create_named_selection)
