# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Applied: Prepare a NACA airfoil for a Fluent simulation
#
# Once a NACA airfoil is designed, it is necessary to prepare the geometry for a CFD simulation. This notebook demonstrates
# how to prepare a NACA 6412 airfoil for a Fluent simulation. The starting point of this example is the previously designed
# NACA 6412 airfoil. The airfoil was saved in an SCDOCX file, which is now imported into the notebook. The geometry is then
# prepared for the simulation.
#
# In case you want to run this notebook, make sure that you have run the previous notebook to design the NACA 6412 airfoil.
#
# ## Import the NACA 6412 airfoil
#
# The following code starts up the Geometry Service and imports the NACA 6412 airfoil. The airfoil is then displayed in the
# notebook.

# +
import os

from ansys.geometry.core import launch_modeler

# Launch the modeler
modeler = launch_modeler()

# Import the NACA 6412 airfoil
design = modeler.open_file(os.path.join(os.getcwd(), f"NACA_Airfoil_6412.scdocx"))

# Retrieve the airfoil body
airfoil = design.bodies[0]

# Display the airfoil
design.plot()
# -

# ## Prepare the geometry for the simulation
#
# The current design is only composed of the airfoil. To prepare the geometry for the simulation,
# you must define the domain around the airfoil. The following code creates a rectangular
# fluid domain around the airfoil.
#
# The airfoil has the following dimensions:
#
# * Chord length: 1 (X-axis)
# * Thickness: Depends on NACA value (Y-axis)
#
# Define the fluid domain as a large box with these dimensions:
#
# * Length (X-axis) - 10 times the chord length
# * Width (Z-axis) - 5 times the chord length
# * Height (Y-axis) - 4 times the chord length
#
# Place the airfoil at the center of the fluid domain.

# +
from ansys.geometry.core.math import Point2D, Plane, Point3D
from ansys.geometry.core.sketch import Sketch

BOX_LENGTH = 10  # X-Axis
BOX_WIDTH = 5  # Z-Axis
BOX_HEIGHT = 4  # Y-Axis

# Create the sketch
fluid_sketch = Sketch(
    plane=Plane(origin=Point3D([0, 0, 0.5 - (BOX_WIDTH / 2)]))
)
fluid_sketch.box(
    center=Point2D([0.5, 0]),
    height=BOX_HEIGHT,
    width=BOX_LENGTH,
)

# Extrude the fluid domain
fluid = design.extrude_sketch("Fluid", fluid_sketch, BOX_WIDTH)
# -

# ## Create named selections
#
# Named selections are used to define boundary conditions in Fluent. The following code creates named selections for the
# inlet, outlet, and walls of the fluid domain. The airfoil is also assigned a named selection.
#
# The airfoil is aligned with the X axis. The inlet is located at the left side of the airfoil, the outlet is located at the
# right side of the airfoil, and the walls are located at the top and bottom of the airfoil. The inlet face has therefore
# a negative X-axis normal vector, and the outlet face has a positive X-axis normal vector. The rest of the faces, therefore,
# constitute the walls.

# +
# Create named selections in the fluid domain (inlet, outlet, and surrounding faces)
# Add also the airfoil as a named selection
fluid_faces = fluid.faces
surrounding_faces = []
inlet_faces = []
outlet_faces = []
for face in fluid_faces:
    if face.normal().x == 1:
        outlet_faces.append(face)
    elif face.normal().x == -1:
        inlet_faces.append(face)
    else:
        surrounding_faces.append(face)

design.create_named_selection("Outlet Fluid", faces=outlet_faces)
design.create_named_selection("Inlet Fluid", faces=inlet_faces)
design.create_named_selection("Surrounding Faces", faces=surrounding_faces)
design.create_named_selection("Airfoil Faces", faces=airfoil.faces)
# -

# ## Display the geometry
#
# The geometry is now ready for the simulation. The following code displays the geometry in the notebook.
# This example uses the ``PlotterHelper`` class to display the geometry for
# the airfoil and fluid domain in different colors with a specified opacity level.
#
# The airfoil is displayed in green, and the fluid domain is displayed in blue with an opacity of 0.25.

# +
from ansys.geometry.core.plotting import PlotterHelper

plotter_helper = PlotterHelper()
plotter_helper.add(airfoil, color="green")
plotter_helper.add(fluid, color="blue", opacity=0.15)
plotter_helper.show_plotter()
# -

# ## Export the geometry
#
# Export the geometry into a Fluent-compatible format. The following code exports the geometry
# into a PMDB file, which retains the named selections.

# Save the design
file = design.export_to_pmdb()
print(f"Design saved to {file}.")

# You can import the exported PMDB file into Fluent to set up the mesh and perform the simulation.
# For an example of how to set up the mesh and boundary conditions in Fluent, see the [Modeling External Compressible Flow](https://fluent.docs.pyansys.com/version/stable/examples/00-fluent/external_compressible_flow.html) example in the Fluent documentation.
#
# The main difference between the Fluent example and this geometry is the coordinate system. The Fluent example
# defines the airfoil in the XY plane, while this geometry defines the airfoil in the XZ plane.
