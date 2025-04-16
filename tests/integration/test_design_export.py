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
"""Test design export functionality."""

import numpy as np
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.designer import Component, Design
from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.sketch import Sketch

from .conftest import skip_if_core_service, skip_if_spaceclaim, skip_if_windows


def _create_demo_design(modeler: Modeler) -> Design:
    """Create a demo design for the tests."""
    modeler.create_design("Demo")

    design_name = "DemoDesign"
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

    return design


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


def test_export_to_scdocx(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test exporting a design to scdocx format."""
    # Create a demo design
    design = _create_demo_design(modeler)

    # Define the location and expected file location
    location = tmp_path_factory.mktemp("test_export_to_scdocx")
    file_location = location / f"{design.name}.scdocx"

    # Export to scdocx
    design.export_to_scdocx(location)

    # Check the exported file
    assert file_location.exists()

    # Import the scdocx
    design_read = modeler.open_file(file_location)

    # Check the imported design
    _checker_method(design_read, design, True)


def test_export_to_stride(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test exporting a design to stride format."""
    skip_if_windows(modeler, test_export_to_stride.__name__, "design")  # Skip test on SC/DMS
    # Create a demo design
    design = _create_flat_design(modeler)

    # Define the location and expected file location
    location = tmp_path_factory.mktemp("test_export_to_stride")
    file_location = location / f"{design.name}.stride"

    # Export to stride
    design.export_to_stride(location)

    # Check the exported file
    assert file_location.exists()

    # Import the stride
    design_read = modeler.open_file(file_location)

    # Check the imported design
    _checker_method(design_read, design, False)


def test_export_to_disco(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test exporting a design to dsco format."""
    skip_if_spaceclaim(modeler, test_export_to_disco.__name__, "disco export")
    # Create a demo design
    design = _create_demo_design(modeler)

    # Define the location and expected file location
    location = tmp_path_factory.mktemp("test_export_to_disco")
    file_location = location / f"{design.name}.dsco"

    # Export to dsco
    design.export_to_disco(location)

    # Check the exported file
    assert file_location.exists()

    # Import the dsco
    design_read = modeler.open_file(file_location)

    # Check the imported design
    _checker_method(design_read, design, True)

@pytest.mark.skip("Windows Core service failing")
def test_export_to_parasolid_text(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test exporting a design to parasolid text format."""
    # Create a demo design
    design = _create_demo_design(modeler)

    # Define the location and expected file location
    location = tmp_path_factory.mktemp("test_export_to_parasolid_text")

    if BackendType.is_core_service(modeler.client.backend_type):
        file_location = location / f"{design.name}.x_t"
    else:
        file_location = location / f"{design.name}.xmt_txt"

    # Export to parasolid text
    design.export_to_parasolid_text(location)

    # Check the exported file
    assert file_location.exists()

    # TODO: Check the exported file content
    # https://github.com/ansys/pyansys-geometry/issues/1146

@pytest.mark.skip("Windows Core service failing")
def test_export_to_parasolid_binary(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test exporting a design to parasolid binary format."""
    # Create a demo design
    design = _create_demo_design(modeler)

    # Define the location and expected file location
    location = tmp_path_factory.mktemp("test_export_to_parasolid_binary")

    if BackendType.is_core_service(modeler.client.backend_type):
        file_location = location / f"{design.name}.x_b"
    else:
        file_location = location / f"{design.name}.xmt_bin"

    # Export to parasolid binary
    design.export_to_parasolid_bin(location)

    # Check the exported file
    assert file_location.exists()

    # TODO: Check the exported file content
    # https://github.com/ansys/pyansys-geometry/issues/1146


def test_export_to_step(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test exporting a design to STEP format."""
    skip_if_core_service(modeler, test_export_to_step.__name__, "step_export")
    # Create a demo design
    design = _create_demo_design(modeler)

    # Define the location and expected file location
    location = tmp_path_factory.mktemp("test_export_to_step")
    file_location = location / f"{design.name}.stp"

    # Export to STEP
    design.export_to_step(location)

    # Check the exported file
    assert file_location.exists()

    if not BackendType.is_core_service(modeler.client.backend_type):
        # Import the STEP file
        design_read = modeler.open_file(file_location)

        # Check the imported design
        _checker_method(design_read, design, False)


def test_export_to_iges(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test exporting a design to IGES format."""
    skip_if_core_service(modeler, test_export_to_iges.__name__, "iges_export")

    # Create a demo design
    design = _create_demo_design(modeler)

    # Define the location and expected file location
    location = tmp_path_factory.mktemp("test_export_to_stl")
    file_location = location / f"{design.name}.igs"

    # Export to IGES
    design.export_to_iges(location)

    # Check the exported file
    assert file_location.exists()

    # TODO: Check the exported file content
    # https://github.com/ansys/pyansys-geometry/issues/1146


def test_export_to_fmd(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test exporting a design to FMD format."""
    skip_if_core_service(modeler, test_export_to_fmd.__name__, "fmd_export")

    # Create a demo design
    design = _create_demo_design(modeler)

    # Define the location and expected file location
    location = tmp_path_factory.mktemp("test_export_to_fmd")
    file_location = location / f"{design.name}.fmd"

    # Export to FMD
    design.export_to_fmd(location)

    # Check the exported file
    assert file_location.exists()

    # TODO: Check the exported file content
    # https://github.com/ansys/pyansys-geometry/issues/1146


def test_export_to_pmdb(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test exporting a design to PMDB format."""
    # Create a demo design
    design = _create_demo_design(modeler)

    # Define the location and expected file location
    location = tmp_path_factory.mktemp("test_export_to_pmdb")
    file_location = location / f"{design.name}.pmdb"

    # Export to PMDB
    design.export_to_pmdb(location)

    # Check the exported file
    assert file_location.exists()

    # TODO: Check the exported file content
    # https://github.com/ansys/pyansys-geometry/issues/1146
