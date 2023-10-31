# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.

"""Test design import."""

import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.designer import Component, Design
from ansys.geometry.core.designer.design import DesignFileFormat
from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.sketch import Sketch


def _checker_method(comp: Component, comp_ref: Component, precise_check: bool = True) -> None:
    # Check component features
    if precise_check:
        assert comp.id == comp_ref.id
        assert comp.name == comp_ref.name
    assert len(comp.bodies) == len(comp_ref.bodies)
    assert len(comp.components) == len(comp_ref.components)
    assert len(comp.coordinate_systems) == len(comp_ref.coordinate_systems)
    assert comp.shared_topology == comp_ref.shared_topology

    # Check design features
    if isinstance(comp, Design) and isinstance(comp_ref, Design):
        assert len(comp.materials) == len(comp_ref.materials)
        assert len(comp.named_selections) == len(comp_ref.named_selections)

    if precise_check:
        # Check bodies (if any)
        for body, body_ref in zip(
            sorted(comp.bodies, key=lambda b: b.name), sorted(comp_ref.bodies, key=lambda b: b.name)
        ):
            assert body.id == body_ref.id
            assert body.name == body_ref.name

    # Check subcomponents
    for subcomp, subcomp_ref in zip(
        sorted(comp.components, key=lambda c: c.name),
        sorted(comp_ref.components, key=lambda c: c.name),
    ):
        _checker_method(subcomp, subcomp_ref, precise_check)


def test_design_import_simple_case(modeler: Modeler):
    # With the given session let's create a the following Design
    #
    # Create your design on the server side
    design = modeler.create_design("ReadDesign")

    # Create a Sketch object and draw a circle (all client side)
    sketch = Sketch()
    sketch.circle(Point2D([-30, -30], UNITS.mm), Quantity(10, UNITS.mm))
    distance = Quantity(30, UNITS.mm)

    #  The following component hierarchy is made
    #
    #           |---> comp_1 ---|---> nested_1_comp_1 ---> nested_1_nested_1_comp_1 X
    #           |               |                              X BODY X
    #           |               |---> nested_2_comp_1
    #           |                         X BODY X
    #           |
    # DESIGN ---|---> comp_2 -------> nested_1_comp_2
    #           |
    #           |
    #           |---> comp_3
    #                X BODY X
    #
    #
    # Now, only "comp_3", "nested_2_comp_1" and "nested_1_nested_1_comp_1"
    # will have a body associated...
    #
    #

    # Create the components
    comp_1 = design.add_component("Component_1")
    comp_2 = design.add_component("Component_2")
    comp_3 = design.add_component("Component_3")
    nested_1_comp_1 = comp_1.add_component("Nested_1_Component_1")
    nested_1_nested_1_comp_1 = nested_1_comp_1.add_component("Nested_1_Nested_1_Component_1")
    nested_2_comp_1 = comp_1.add_component("Nested_2_Component_1")
    comp_2.add_component("Nested_1_Component_2")

    # Create the bodies
    comp_3.extrude_sketch(name="comp_3_circle", sketch=sketch, distance=distance)
    nested_2_comp_1.extrude_sketch(name="nested_2_comp_1_circle", sketch=sketch, distance=distance)
    nested_1_nested_1_comp_1.extrude_sketch(
        name="nested_1_nested_1_comp_1_circle", sketch=sketch, distance=distance
    )

    # Now, let's create a new client session
    new_client = Modeler()
    read_design = new_client.read_existing_design()

    # And now assert all its elements
    assert read_design is not None
    assert len(new_client._designs) == 1

    # Check the design
    _checker_method(read_design, design)


def test_open_file(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test creation of a component, saving it to a file, and loading it again to a
    second component and make sure they have the same properties."""

    design_name = "two_cars"
    design = modeler.create_design(design_name)

    # Create a car
    car1 = design.add_component("Car1")
    comp1 = car1.add_component("A")
    comp2 = car1.add_component("B")
    wheel1 = comp2.add_component("Wheel1")

    # Create car base frame
    sketch = Sketch().box(Point2D([5, 10]), 10, 20)
    comp2.add_component("Base").extrude_sketch("BaseBody", sketch, 5)

    # Create first wheel
    sketch = Sketch(Plane(direction_x=Vector3D([0, 1, 0]), direction_y=Vector3D([0, 0, 1])))
    sketch.circle(Point2D([0, 0]), 5)
    wheel1.extrude_sketch("Wheel", sketch, -5)

    # Create 3 other wheels and move them into position
    rotation_origin = Point3D([0, 0, 0])
    rotation_direction = UnitVector3D([0, 0, 1])

    wheel2 = comp2.add_component("Wheel2", wheel1)
    wheel2.modify_placement(Vector3D([0, 20, 0]))

    wheel3 = comp2.add_component("Wheel3", wheel1)
    wheel3.modify_placement(Vector3D([10, 0, 0]), rotation_origin, rotation_direction, np.pi)

    wheel4 = comp2.add_component("Wheel4", wheel1)
    wheel4.modify_placement(Vector3D([10, 20, 0]), rotation_origin, rotation_direction, np.pi)

    # Create 2nd car
    car2 = design.add_component("Car2", car1)
    car2.modify_placement(Vector3D([30, 0, 0]))

    # Create top of car - applies to BOTH cars
    sketch = Sketch(Plane(Point3D([0, 5, 5]))).box(Point2D([5, 2.5]), 10, 5)
    comp1.extrude_sketch("Top", sketch, 5)

    file = tmp_path_factory.mktemp("test_design_import") / "two_cars.scdocx"
    design.download(file)

    # TODO: to be reactivated by https://github.com/ansys/pyansys-geometry/issues/799
    if modeler.client.backend_type != BackendType.LINUX_SERVICE:
        design2 = modeler.open_file(file)

        # assert the two cars are the same, excepted for the ID, which should be different
        _checker_method(design, design2, True)

    # Test HOOPS formats (Windows only)
    if modeler.client.backend_type != BackendType.LINUX_SERVICE:
        # STEP
        file = tmp_path_factory.mktemp("test_design_import") / "two_cars.step"
        design.download(file, DesignFileFormat.STEP)
        design2 = modeler.open_file(file)
        _checker_method(design, design2, False)

        # IGES
        #
        # TODO: Something has gone wrong with IGES
        # TODO: Issue https://github.com/ansys/pyansys-geometry/issues/801
        #
        # file = tmp_path_factory.mktemp("test_design_import") / "two_cars.igs"
        # design.download(file, DesignFileFormat.IGES)
        # design2 = modeler.open_file(file)
        # _checker_method(design, design2, False)

        # Catia
        design2 = modeler.open_file("./tests/integration/files/import/catia_car/car.CATProduct")
        _checker_method(design, design2, False)

        # Rhino
        design2 = modeler.open_file("./tests/integration/files/import/box.3dm")
        assert len(design2.components) == 1
        assert len(design2.components[0].bodies) == 1

        # Stride
        design2 = modeler.open_file("./tests/integration/files/import/sample_box.project")
        assert len(design2.bodies) == 1

        # SolidWorks
        design2 = modeler.open_file("./tests/integration/files/import/partColor.SLDPRT")
        assert len(design2.components[0].bodies) == 1

        # .par
        design2 = modeler.open_file("./tests/integration/files/import/Tank_Bottom.par")
        assert len(design2.bodies) == 1

        # .prt
        design2 = modeler.open_file("./tests/integration/files/import/disk1.prt")
        assert len(design2.bodies) == 1
