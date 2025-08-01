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
from ansys.geometry.core.math import UNITVECTOR3D_Z, Plane, Point2D, Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import UNITS, Distance
from ansys.geometry.core.sketch import Sketch
from ansys.geometry.core.tools.unsupported import PersistentIdType

from .conftest import FILES_DIR, IMPORT_FILES_DIR


def _create_flat_design(modeler: Modeler) -> Design:
    """Create a demo design for the tests."""
    modeler.create_design("Demo")

    design_name = "DemoFlatDesign"
    design = modeler.create_design(design_name)

    # Create a car
    comp1 = design.add_component("A")
    wheel1 = design.add_component("Wheel1")

    # Create car base frame
    sketch = Sketch().box(Point2D([5, 10]), 10, 20)
    design.add_component("Base").extrude_sketch("BaseBody", sketch, 5)

    # Create first wheel
    sketch = Sketch(Plane(direction_x=Vector3D([0, 1, 0]), direction_y=Vector3D([0, 0, 1])))
    sketch.circle(Point2D([0, 0]), 5)
    wheel1.extrude_sketch("Wheel", sketch, -5)

    # Create 3 other wheels and move them into position
    rotation_origin = Point3D([0, 0, 0])
    rotation_direction = UnitVector3D([0, 0, 1])

    wheel2 = design.add_component("Wheel2", wheel1)
    wheel2.modify_placement(Vector3D([0, 20, 0]))

    wheel3 = design.add_component("Wheel3", wheel1)
    wheel3.modify_placement(Vector3D([10, 0, 0]), rotation_origin, rotation_direction, np.pi)

    wheel4 = design.add_component("Wheel4", wheel1)
    wheel4.modify_placement(Vector3D([10, 20, 0]), rotation_origin, rotation_direction, np.pi)

    # Create top of car - applies to BOTH cars
    sketch = Sketch(Plane(Point3D([0, 5, 5]))).box(Point2D([5, 2.5]), 10, 5)
    comp1.extrude_sketch("Top", sketch, 5)

    return design


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

    if BackendType.is_core_service(modeler.client.backend_type):
        # Set single export ids and verify
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

        assert base_body.id in [b.id for b in bodies1]
        assert wheel_body.id in [b.id for b in bodies2]

        faces = modeler.unsupported.get_face_occurrences_from_import_id(
            "3", PersistentIdType.PRIME_ID
        )
        edges = modeler.unsupported.get_edge_occurrences_from_import_id(
            "4", PersistentIdType.PRIME_ID
        )

        assert base_body.faces[0].id in [f.id for f in faces]
        assert base_body.edges[0].id in [e.id for e in edges]

        # Set multiple export ids at once and verify
        modeler.unsupported.set_multiple_export_ids(
            [base_body.faces[1].id, base_body.edges[1].id],
            [PersistentIdType.PRIME_ID, PersistentIdType.PRIME_ID],
            ["5", "6"]
        )

        faces2 = modeler.unsupported.get_face_occurrences_from_import_id(
            "5", PersistentIdType.PRIME_ID
        )
        edges2 = modeler.unsupported.get_edge_occurrences_from_import_id(
            "6", PersistentIdType.PRIME_ID
        )

        assert base_body.faces[1].id in [b.id for b in faces2]
        assert base_body.edges[1].id in [b.id for b in edges2]

    file = tmp_path_factory.mktemp("test_design_import") / "two_cars.scdocx"
    design.download(str(file))

    # Pre-download the STEP file for comparison... once the design is closed, the
    # file is no longer available for download from the original design
    if not BackendType.is_core_service(modeler.client.backend_type):
        file_step = tmp_path_factory.mktemp("test_design_import") / "two_cars.step"
        design.download(file_step, DesignFileFormat.STEP)
        #
        # file_iges = tmp_path_factory.mktemp("test_design_import") / "two_cars.igs"
        # design.download(file_iges, DesignFileFormat.IGES)

    design2 = modeler.open_file(file)

    # assert the two cars are the same, excepted for the ID, which should be different
    _checker_method(design, design2, True)

    # Test Reader formats (Windows only)
    if not BackendType.is_core_service(modeler.client.backend_type):
        # IGES
        #
        # TODO: Something has gone wrong with IGES
        # https://github.com/ansys/pyansys-geometry/issues/1146
        # design2 = modeler.open_file(file_iges)
        # design3 = modeler.open_file(Path(IMPORT_FILES_DIR, "twoCars.igs")
        # _checker_method(design2, design3, False)

        # STEP
        design2 = modeler.open_file(file_step)
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

    if modeler.client.backend_type not in (
        BackendType.SPACECLAIM,
        BackendType.WINDOWS_SERVICE,
        BackendType.DISCOVERY,
    ):
        design_stride = _create_flat_design(modeler)
        file = tmp_path_factory.mktemp("test_design_import") / "two_cars.stride"
        design_stride.download(file, DesignFileFormat.STRIDE)
        design2 = modeler.open_file(file)
        design3 = modeler.open_file(Path(IMPORT_FILES_DIR, "twoCars.stride"))
        _checker_method(design2, design3, False)


def test_design_insert(modeler: Modeler):
    """Test inserting a file into the design."""
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
    assert design.is_active is True
    assert design.components[0].name == "Component_Cylinder"
    assert design.components[1].name == "DuplicateFacesDesignBefore"


def test_design_insert_with_import(modeler: Modeler):
    """Test inserting a file into the design through the external format import
    process.
    """
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
    assert design.is_active is True
    assert design.components[0].name == "Component_Cylinder"
    assert design.components[1].name == "Wheel1"


def test_design_import_with_named_selections(modeler: Modeler):
    """Test importing a design with named selections."""
    # Open the design
    design = modeler.open_file(Path(FILES_DIR, "NamedSelectionImport.scdocx"))

    # Check that there are 5 Named Selections
    assert len(design.named_selections) == 6

    # Get full body named selection
    body = design._named_selections["SolidBody"]
    assert len(body.bodies) == 1
    assert len(body.faces) == 0
    assert len(body.beams) == 0

    # Get beam named selection
    beam = design._named_selections["Beam1"]
    assert len(beam.bodies) == 0
    assert len(beam.beams) == 1

    # Get mixed named selection 1
    ns1 = design._named_selections["Group1"]
    assert len(ns1.bodies) == 0
    assert len(ns1.faces) == 2

    # Get mixed named selection 2
    ns2 = design._named_selections["Group2"]
    assert len(ns2.bodies) == 1
    assert len(ns2.beams) == 1
    assert len(ns2.design_points) == 1

    # Get mixed named selection 3
    ns3 = design._named_selections["Group3"]
    assert len(ns3.bodies) == 0
    assert len(ns3.design_points) == 1

    # Get mixed named selection 4
    ns4 = design._named_selections["VertexGroup"]
    assert len(ns4.bodies) == 0
    assert len(ns4.vertices) == 2
    assert len(ns4.faces) == 1


def test_design_import_acad_2024(modeler: Modeler):
    """Test importing a 2024 AutoCAD file."""
    # Open the design
    design = modeler.open_file(Path(IMPORT_FILES_DIR, "ACAD/CylinderBox_2024.dwg"))
    assert len(design.components) == 3
    assert len(design.components[1].bodies[0].faces) == 6


def test_design_import_cat5_2024(modeler: Modeler):
    """Test importing a 2024 CATIA V5 file."""
    # Open the design
    design = modeler.open_file(Path(IMPORT_FILES_DIR, "CAT5/Bracket_Hole_2024.CATPart"))
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 24


def test_design_import_cat6_2023(modeler: Modeler):
    """Test importing a CATIA V6 file."""
    # Open the design
    design = modeler.open_file(Path(IMPORT_FILES_DIR, "CAT6/Skateboard A.1_2023x.3dxml"))
    assert len(design.components) == 4
    assert len(design.components[0].components) == 1
    assert len(design.components[1].components) == 3
    assert len(design.components[2].components) == 3
    assert len(design.components[3].components) == 1
    assert len(design.components[1].components[0].components[0].bodies) == 15
    assert len(design.components[1].components[1].components[0].bodies) == 16
    assert len(design.components[1].components[2].components[0].bodies) == 16


def test_design_import_creo_11(modeler: Modeler):
    """Test importing a Creo 11 file."""
    # Open the design
    design = modeler.open_file(Path(IMPORT_FILES_DIR, "Creo/rearwheel_creo11.prt.2"))
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 32


def test_design_import_jt(modeler: Modeler):
    """Test importing a JT file."""
    # Open the design
    design = modeler.open_file(Path(IMPORT_FILES_DIR, "JT/assly_sub-assly_asso.jt"))
    assert len(design.components) == 2
    assert len(design.components[0].components) == 2
    assert len(design.components[0].components[0].bodies[0].faces) == 6


def test_design_import_rhino(modeler: Modeler):
    """Test importing a Rhino file."""
    # Open the design
    design = modeler.open_file(Path(IMPORT_FILES_DIR, "Rhino/box.3dm"))
    assert len(design.components[0].bodies) == 1
    assert len(design.components[0].bodies[0].faces) == 6


def test_design_import_solid_edge2025(modeler: Modeler):
    """Test importing a 2025 Solid Edge file."""
    # Open the design
    design = modeler.open_file(Path(IMPORT_FILES_DIR, "SolidEdge/L_Solid_2025.par"))
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 8


# def test_design_import_parasolid(modeler: Modeler):
#    """Test importing a Parasolid file."""
#    # Open the design
#    design = modeler.open_file(Path(IMPORT_FILES_DIR, "Parasolid/blockhole_M.x_t"))
#    assert len(design.bodies) == 4


def test_design_import_solidworks(modeler: Modeler):
    """Test importing a SOLIDWORKS file."""
    # Open the design
    design = modeler.open_file(Path(IMPORT_FILES_DIR, "SOLIDWORKS/Base_Plate.SLDPRT"))
    assert len(design.components) == 1
    assert len(design.components[0].bodies[0].faces) == 38


def test_design_import_nx2412(modeler: Modeler):
    """Test importing a NX 2412 file."""
    # Open the design
    design = modeler.open_file(Path(IMPORT_FILES_DIR, "NX/base_plate_2412.prt"))
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 18


def test_design_import_inventor2026(modeler: Modeler):
    """Test importing a 2026 Inventor file."""
    # Open the design
    design = modeler.open_file(Path(IMPORT_FILES_DIR, "Inventor/ai_param_dsdm_part1_2026.ipt"))
    assert len(design.bodies) == 1
    assert len(design.bodies[0].faces) == 9


def test_design_import_stride_with_named_selections(modeler: Modeler):
    """Test importing a .stride file with named selections."""
    # Open stride file
    design = modeler.open_file(Path(FILES_DIR, "WithNamedSelections.stride"))
    assert len(design.named_selections) == 4

    # Expected named selections and their properties
    expected_named_selections = {
        "Edges": {"bodies": 0, "faces": 0, "edges": 3, "vertices": 0},
        "Faces": {"bodies": 0, "faces": 2, "edges": 0, "vertices": 0},
        "Body": {"bodies": 1, "faces": 0, "edges": 0, "vertices": 0},
        "Mixed": {"bodies": 1, "faces": 0, "edges": 2, "vertices": 0},
    }

    # Verify named selections
    for named_selection in design.named_selections:
        assert named_selection.name in expected_named_selections, (
            f"Unexpected named selection: {named_selection.name}"
        )
        expected_properties = expected_named_selections[named_selection.name]
        assert len(named_selection.bodies) == expected_properties["bodies"], (
            f"Mismatch in bodies for {named_selection.name}"
        )
        assert len(named_selection.faces) == expected_properties["faces"], (
            f"Mismatch in faces for {named_selection.name}"
        )
        assert len(named_selection.edges) == expected_properties["edges"], (
            f"Mismatch in edges for {named_selection.name}"
        )
        assert len(named_selection.vertices) == expected_properties["vertices"], (
            f"Mismatch in vertices for {named_selection.name}"
        )


def test_design_insert_id_bug(modeler: Modeler):
    """Test inserting a file into the design with ID bug fix."""
    # This fix is available in version 261 and later
    design1 = modeler.create_design("Test")

    design1.add_component("test")

    design1.insert_file(Path(FILES_DIR, "bottom_mounted_imp.dsco"))
    design1.components[1].bodies[0].copy(design1.components[0], "test")

    ns = design1.create_named_selection("ComponentNS", components=[design1.components[0]])
    modeler.geometry_commands.move_translate(
        ns, direction=UNITVECTOR3D_Z, distance=Distance(1, UNITS.m)
    )

    assert len(design1.components[0].bodies) == 1
    assert len(design1.components[1].bodies) == 1


@pytest.mark.skip(reason="Object reference not set to an instance of an object.")
def test_import_scdocx_with_external_docs(modeler: Modeler):
    """Test importing an SCDOCX file with external documents and verify it is internalized."""
    # Create a new design
    design = modeler.create_design("Insert External Document")

    # Define the path to the external SCDOCX file
    path_to_external_doc = Path(FILES_DIR, "external_file_scdocx", "Design1.scdocx")

    # Import the external SCDOCX file
    design.insert_file(file_location=path_to_external_doc)

    # Verify that the design structure is internalized
    # Check the number of bodies in the design
    assert len(design.bodies) == 0

    # Check the number of components in the design
    assert len(design.components) == 1

    # Check the number of bodies in the first component
    assert len(design.components[0].bodies) == 1

    # Check the number of subcomponents in the first component
    assert len(design.components[0].components) == 5

    for component in design.components[0].components:
        assert len(component.bodies) == 1
