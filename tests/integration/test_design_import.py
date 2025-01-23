# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Test design import."""

from pathlib import Path

import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.designer import Component, Design
from ansys.geometry.core.designer.design import DesignFileFormat
from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.misc.unsupported import PersistentIdType
from ansys.geometry.core.sketch import Sketch

from .conftest import FILES_DIR, IMPORT_FILES_DIR, skip_if_linux


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
    assert len(new_client.designs) == 1

    # Check the design
    _checker_method(read_design, design)


def test_open_file(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test creation of a component, saving it to a file, and loading it again
    to a second component and make sure they have the same properties.
    """
    design_name = "two_cars"
    design = modeler.create_design(design_name)

    # Create a car
    car1 = design.add_component("Car1")
    comp1 = car1.add_component("A")
    comp2 = car1.add_component("B")
    wheel1 = comp2.add_component("Wheel1")

    # Create car base frame
    sketch = Sketch().box(Point2D([5, 10]), 10, 20)
    base_body = comp2.add_component("Base").extrude_sketch("BaseBody", sketch, 5)

    # Create first wheel
    sketch = Sketch(Plane(direction_x=Vector3D([0, 1, 0]), direction_y=Vector3D([0, 0, 1])))
    sketch.circle(Point2D([0, 0]), 5)
    wheel_body = wheel1.extrude_sketch("Wheel", sketch, -5)

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

    modeler.unsupported.set_export_id(base_body.id, PersistentIdType.PRIME_ID, "1")
    modeler.unsupported.set_export_id(wheel_body.id, PersistentIdType.PRIME_ID, "2")

    modeler.unsupported.set_export_id(base_body.faces[0].id, PersistentIdType.PRIME_ID, "3")
    modeler.unsupported.set_export_id(base_body.edges[0].id, PersistentIdType.PRIME_ID, "4")

    bodies1 = modeler.unsupported.get_body_occurrences_from_import_id(
        "1", PersistentIdType.PRIME_ID
    )
    bodies2 = modeler.unsupported.get_body_occurrences_from_import_id(
        "2", PersistentIdType.PRIME_ID
    )

    # requires a change to core service, uncomment on next core service update
    # assert base_body.id in [b.id for b in bodies1]
    # assert wheel_body.id in [b.id for b in bodies2]
    assert base_body.id not in [b.id for b in bodies1]
    assert wheel_body.id not in [b.id for b in bodies2]

    faces = modeler.unsupported.get_face_occurrences_from_import_id("3", PersistentIdType.PRIME_ID)
    edges = modeler.unsupported.get_edge_occurrences_from_import_id("4", PersistentIdType.PRIME_ID)

    # requires a change to core service, uncomment on next core service update
    # assert base_body.faces[0].id in [f.id for f in faces]
    # assert base_body.edges[0].id in [e.id for e in edges]
    assert base_body.faces[0].id not in [f.id for f in faces]
    assert base_body.edges[0].id not in [e.id for e in edges]

    file = tmp_path_factory.mktemp("test_design_import") / "two_cars.scdocx"
    design.download(str(file))

    design2 = modeler.open_file(file)

    # assert the two cars are the same, excepted for the ID, which should be different
    _checker_method(design, design2, True)

    # Test HOOPS formats (Windows only)
    if modeler.client.backend_type not in (
        BackendType.LINUX_SERVICE,
        BackendType.CORE_LINUX,
        BackendType.CORE_WINDOWS,
    ):
        # IGES
        #
        # TODO: Something has gone wrong with IGES
        # https://github.com/ansys/pyansys-geometry/issues/801

        # file = tmp_path_factory.mktemp("test_design_import") / "two_cars.igs"
        # design.download(file, DesignFileFormat.IGES)
        # design2 = modeler.open_file(file)
        # design3 = modeler.open_file(Path(IMPORT_FILES_DIR, "twoCars.igs")
        # _checker_method(design2, design3, False)

        # STEP
        file = tmp_path_factory.mktemp("test_design_import") / "two_cars.step"
        design.download(file, DesignFileFormat.STEP)
        design2 = modeler.open_file(file)
        design3 = modeler.open_file(Path(IMPORT_FILES_DIR, "twoCars.stp"))
        _checker_method(design2, design3, False)

        # Catia
        design2 = modeler.open_file(Path(IMPORT_FILES_DIR, "catia_car/car.CATProduct"))
        _checker_method(design, design2, False)

        # Rhino
        design2 = modeler.open_file(Path(IMPORT_FILES_DIR, "box.3dm"))
        assert len(design2.components) == 1
        assert len(design2.components[0].bodies) == 1

        # Stride
        design2 = modeler.open_file(Path(IMPORT_FILES_DIR, "sample_box.project"))
        assert len(design2.bodies) == 1

        # SolidWorks
        design2 = modeler.open_file(Path(IMPORT_FILES_DIR, "partColor.SLDPRT"))
        assert len(design2.components[0].bodies) == 1

        # .par
        design2 = modeler.open_file(Path(IMPORT_FILES_DIR, "Tank_Bottom.par"))
        assert len(design2.bodies) == 1

        # .prt
        design2 = modeler.open_file(Path(IMPORT_FILES_DIR, "disk1.prt"))
        assert len(design2.bodies) == 1


def test_design_insert(modeler: Modeler):
    """Test inserting a file into the design."""
    # Skip for Linux service
    skip_if_linux(modeler, test_design_insert.__name__, "insert_file")

    # Create a design and sketch a circle
    design = modeler.create_design("Insert")
    sketch = Sketch()
    sketch.circle(Point2D([0, 0]), 10)
    comp = design.add_component("Component_Cylinder")
    comp.extrude_sketch("Body_Cylinder", sketch, 5)

    # Insert a different file
    design.insert_file(Path(FILES_DIR, "DuplicateFacesDesignBefore.scdocx"))

    # Check that there are two components
    assert len(design.components) == 2
    assert design.components[0].name == "Component_Cylinder"
    assert design.components[1].name == "DuplicatesDesign"


def test_design_insert_with_import(modeler: Modeler):
    """Test inserting a file into the design through the external format import
    process.
    """
    # Skip for Linux service
    skip_if_linux(modeler, test_design_insert_with_import.__name__, "insert_file")

    # Create a design and sketch a circle
    design = modeler.create_design("Insert")
    sketch = Sketch()
    sketch.circle(Point2D([0, 0]), 10)
    comp = design.add_component("Component_Cylinder")
    comp.extrude_sketch("Body_Cylinder", sketch, 5)

    # Import and insert a different file
    design.insert_file(Path(IMPORT_FILES_DIR, "catia_car/Wheel1.CATPart"))

    # Check that there are two components
    assert len(design.components) == 2
    assert design.components[0].name == "Component_Cylinder"
    assert design.components[1].name == "Wheel1"
