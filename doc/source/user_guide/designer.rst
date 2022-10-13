PyGeometry design Subpackage
****************************

Design subpackage provides a ``Design`` for organizing geometry assemblies and synchronizes to
a supporting geometry service instance.*

Defining the model
------------------

.. code:: python

    # Create a Sketch and draw a circle (all client side)
    sketch = Sketch()
    sketch.draw_circle(Point3D([10, 10, 0], UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design_name = "ExtrudeProfile"
    design = modeler.create_design(design_name) 


Add materials to model
-----------------------

You can add the data structure and property for individual materials.

.. code:: python

    density = Quantity(125, 1000 * UNITS.kg / (UNITS.m * UNITS.m * UNITS.m))
    poisson_ratio = Quantity(0.33, UNITS.dimensionless)
    tensile_strength = Quantity(45)
    material = Material(
        "steel",
        density,
        [MaterialProperty(MaterialPropertyType.POISSON_RATIO, "myPoisson", poisson_ratio)],
    )
    material.add_property(MaterialPropertyType.TENSILE_STRENGTH, "myTensile", Quantity(45))
    design.add_material(material)

Create bodies by extruding the sketch
-------------------------------------

Projects all of the specified geometries onto the body. ypou can extrude the sketch from the bodies.

.. code:: python

    body = design.extrude_sketch("JustACircle", sketch, Quantity(10, UNITS.mm))
