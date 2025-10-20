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
"""Test tessellation and plotting."""

import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.math import Plane, Point2D, UnitVector3D, Vector3D
from ansys.geometry.core.misc.units import UNITS, Quantity
from ansys.geometry.core.sketch import Sketch

from ..conftest import are_graphics_available


@pytest.mark.skipif(
    not are_graphics_available(), reason="Skipping due to graphics requirements missing"
)
def test_body_tessellate(modeler: Modeler):
    """Test the body tessellation."""
    sketch_1 = Sketch()
    sketch_1.box(Point2D([2, 0], UNITS.m), Quantity(4, UNITS.m), Quantity(4, UNITS.m))
    design = modeler.create_design("Design")
    comp_1 = design.add_component("Component_1")
    body_1 = comp_1.extrude_sketch("Sketch_1", sketch_1, Quantity(1, UNITS.m))

    # Tessellate the body without merging the individual faces
    blocks_1 = body_1.tessellate()
    assert "MultiBlock" in str(blocks_1)
    # Number of blocks will be the number of faces
    assert blocks_1.n_blocks == 6
    # Test the center of the bounding box
    assert blocks_1.center == pytest.approx([2, 0, 0.5])
    # Test the values of blocks which are the length 6 tuple of floats
    # containing min/max along each axis
    assert blocks_1.bounds == pytest.approx([0.0, 4.0, -2.0, 2.0, 0.0, 1.0])

    # Tessellate the body merging the individual faces
    mesh_1 = body_1.tessellate(merge=True)
    assert "PolyData" in str(mesh_1)
    # Test number of cells, points and arrays in dataset
    assert mesh_1.n_cells == 12
    assert mesh_1.n_points == 24
    assert blocks_1.bounds == pytest.approx([0.0, 4.0, -2.0, 2.0, 0.0, 1.0])
    assert mesh_1.n_arrays == 0

    sketch_2 = Sketch()
    sketch_2.circle(Point2D([30, 30], UNITS.mm), Quantity(10, UNITS.mm))

    # Create a component
    comp_2 = design.add_component("Component_2")
    body_2 = comp_2.extrude_sketch(name="Body_2", sketch=sketch_2, distance=Quantity(30, UNITS.mm))

    # Tessellate the body without merging the individual faces
    blocks_2 = body_2.tessellate()
    assert "MultiBlock" in str(blocks_2)
    assert blocks_2.n_blocks == 3
    if not BackendType.is_core_service(modeler.client.backend_type):
        assert blocks_2.bounds == pytest.approx(
            [0.019999999999999997, 0.04, 0.020151922469877917, 0.03984807753012208, 0.0, 0.03],
            rel=1e-6,
            abs=1e-8,
        )
    else:
        assert blocks_2.bounds == pytest.approx(
            [0.019999999999999997, 0.04, 0.020151922469877917, 0.03984807753012208, 0.0, 0.03],
            rel=1e-6,
            abs=1e-8,
        )

    assert blocks_2.center == pytest.approx([0.03, 0.03, 0.015], rel=1e-6, abs=1e-8)

    # Tessellate the body merging the individual faces
    mesh_2 = body_2.tessellate(merge=True)
    if not BackendType.is_core_service(modeler.client.backend_type):
        assert "PolyData" in str(mesh_2)
        assert mesh_2.n_cells == 72
        assert mesh_2.n_points == 76
        assert mesh_2.n_arrays == 0
    else:
        assert "PolyData" in str(mesh_2)
        assert mesh_2.n_cells == 72
        assert mesh_2.n_points == 76
        assert mesh_2.n_arrays == 0

    # Make sure instance body tessellation is the same as original
    comp_1_instance = design.add_component("Component_1_Instance", comp_1)
    assert comp_1_instance.bodies[0].tessellate() == comp_1.bodies[0].tessellate()

    # After modifying placement, they should be different
    comp_1_instance.modify_placement(Vector3D([1, 2, 3]))
    assert comp_1_instance.bodies[0].tessellate() != comp_1.bodies[0].tessellate()

    assert comp_1.bodies[0]._template._tessellation is not None

    comp_1.bodies[0].translate(UnitVector3D([1, 0, 0]), 1)

    assert comp_1.bodies[0]._template._tessellation is None


@pytest.mark.skipif(
    not are_graphics_available(), reason="Skipping due to graphics requirements missing"
)
def test_body_tessellate_with_edges(modeler: Modeler):
    """Test the body tessellation including edges."""
    design = modeler.create_design("Design")
    sketch_1 = Sketch().box(Point2D([2, 0], UNITS.m), Quantity(4, UNITS.m), Quantity(4, UNITS.m))
    body_1 = design.extrude_sketch("Body_1", sketch_1, Quantity(4, UNITS.m))

    # Tessellate the body without merging the individual faces
    blocks_1 = body_1.tessellate()
    assert "MultiBlock" in str(blocks_1)
    # Number of blocks will be the number of faces
    assert blocks_1.n_blocks == 6
    # Test the center of the bounding box
    assert blocks_1.center == pytest.approx([2, 0, 2])
    # Test the values of blocks which are the length 6 tuple of floats
    # containing min/max along each axis
    assert blocks_1.bounds == pytest.approx([0.0, 4.0, -2.0, 2.0, 0.0, 4.0])

    # Tessellate the body with edges
    blocks_1_with_edges = body_1.tessellate(reset_cache=True, include_edges=True)
    assert "MultiBlock" in str(blocks_1_with_edges)
    # Number of blocks will be the number of faces + edges
    assert blocks_1_with_edges.n_blocks == 18
    # Test the center of the bounding box
    assert blocks_1_with_edges.center == pytest.approx([2, 0, 2])
    # Test the values of blocks which are the length 6 tuple of floats
    # containing min/max along each axis
    assert blocks_1_with_edges.bounds == pytest.approx([0.0, 4.0, -2.0, 2.0, 0.0, 4.0])

    # Tessellate the body merging the individual faces + include edges
    mesh_1 = body_1.tessellate(merge=True, reset_cache=True, include_edges=True)
    assert "PolyData" in str(mesh_1)
    # Test number of cells, points and arrays in dataset
    assert mesh_1.n_cells == 24
    assert mesh_1.n_points == 48
    assert blocks_1.bounds == pytest.approx([0.0, 4.0, -2.0, 2.0, 0.0, 4.0])
    assert mesh_1.n_arrays == 0

    # Tessellate the body not including faces, only edges
    mesh_1 = body_1.tessellate(
        merge=True, reset_cache=True, include_faces=False, include_edges=True
    )
    assert "PolyData" in str(mesh_1)
    # Test number of cells, points and arrays in dataset
    assert mesh_1.n_cells == 12
    assert mesh_1.n_points == 24
    assert blocks_1.bounds == pytest.approx([0.0, 4.0, -2.0, 2.0, 0.0, 4.0])
    assert mesh_1.n_arrays == 0

    # Check cache with edges
    assert body_1._template._tessellation is not None


@pytest.mark.skipif(
    not are_graphics_available(), reason="Skipping due to graphics requirements missing"
)
def test_component_tessellate(modeler: Modeler):
    """Test the component tessellation."""
    # Create a sketch
    sketch_1 = Sketch()
    sketch_1.box(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(5, UNITS.m))
    sketch_1.circle(Point2D([0, 0], UNITS.m), Quantity(25, UNITS.m))

    # Create the design on the server side
    design = modeler.create_design("Design")
    comp = design.add_component("Component")
    distance = Quantity(10, UNITS.m)
    comp.extrude_sketch("Body", sketch=sketch_1, distance=distance)

    # Create another sketch in a different plane
    sketch_2 = Sketch(Plane([0, 0, 10]))
    sketch_2.box(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(5, UNITS.m))
    sketch_2.circle(Point2D([0, 0], UNITS.m), Quantity(25, UNITS.m))
    comp.extrude_sketch("Body", sketch=sketch_2, distance=distance)

    # Tessellate the component - always a single dataset
    mesh = comp.tessellate()
    comp.plot()
    assert "PolyData" in str(mesh)
    if not BackendType.is_core_service(modeler.client.backend_type):
        assert mesh.n_cells == 3280
        assert mesh.n_arrays == 0
        assert mesh.n_points == 3300
        assert mesh.bounds == pytest.approx(
            [-25.0, 25.0, -24.999251562526105, 24.999251562526105, 0.0, 20.0],
            rel=1e-6,
            abs=1e-8,
        )
    else:
        assert mesh.n_cells == 3280
        assert mesh.n_arrays == 0
        assert mesh.n_points == 3300
        assert mesh.bounds == pytest.approx(
            [-25.0, 25.0, -24.999251562526105, 24.999251562526105, 0.0, 20.0],
            rel=1e-6,
            abs=1e-8,
        )


def test_get_design_tessellation(modeler: Modeler):
    """Test getting the entire design tessellation."""
    # Create a design with two bodies
    design = modeler.create_design("revolve_edges")
    box = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)
    cyl = design.extrude_sketch("cylinder", Sketch().circle(Point2D([1, 0]), 0.5), 2)

    design_tess = design.get_raw_tessellation()
    assert isinstance(design_tess, dict)
    assert len(design_tess) == 2  # Two bodies in the design

    box_tess = design_tess[box.id]
    assert isinstance(box_tess, dict)
    assert len(box_tess) == 6  # Six faces on the box

    for face_id, face_tess in box_tess.items():
        assert isinstance(face_id, str)
        assert isinstance(face_tess, dict)

    cyl_tess = design_tess[cyl.id]
    assert isinstance(cyl_tess, dict)
    assert len(cyl_tess) == 3  # Three faces on the cylinder

    for face_id, face_tess in cyl_tess.items():
        assert isinstance(face_id, str)
        assert isinstance(face_tess, dict)

    # Get the design tessellation including edges
    design_tess = design.get_raw_tessellation(reset_cache=True, include_edges=True)
    assert isinstance(design_tess, dict)
    assert len(design_tess) == 2  # Two bodies in the design

    box_tess = design_tess[box.id]
    assert isinstance(box_tess, dict)
    assert len(box_tess) == 18  # Six faces + Twelve edges on the box

    for face_id, face_tess in box_tess.items():
        assert isinstance(face_id, str)
        assert isinstance(face_tess, dict)

    cyl_tess = design_tess[cyl.id]
    assert isinstance(cyl_tess, dict)
    assert len(cyl_tess) == 5  # Three faces + Two edges on the cylinder

    # Check design cache
    assert design._design_tess == design_tess


def test_get_body_raw_tessellation(modeler: Modeler):
    """Test getting the raw tessellation from a body."""

    design = modeler.create_design("revolve_edges")
    box = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 2, 2), 2)
    cylinder = design.extrude_sketch("cylinder", Sketch().circle(Point2D([1, 0]), 0.5), 2)

    # Get the raw tessellation from the box body
    box_tess = box.get_raw_tessellation()
    assert isinstance(box_tess, dict)
    assert len(box_tess) == 6  # Six faces + Twelve edge on the box

    for id, tess in box_tess.items():
        assert isinstance(id, str)
        assert isinstance(tess, dict)

    # Get the raw tessellation from the box body including edges
    box_tess = box.get_raw_tessellation(reset_cache=True, include_edges=True)
    assert isinstance(box_tess, dict)
    assert len(box_tess) == 18  # Six faces + Twelve edge on the box

    # Get the raw tessellation from the cylinder body only including edges
    cyl_tess = cylinder.get_raw_tessellation(include_faces=False, include_edges=True)
    assert isinstance(cyl_tess, dict)
    assert len(cyl_tess) == 2  # Three faces + Two edges on the cylinder

    for id, tess in cyl_tess.items():
        assert isinstance(id, str)
        assert isinstance(tess, dict)

    # Check raw tessellation cache
    assert box._template._raw_tessellation == box_tess
    assert cylinder._template._raw_tessellation == cyl_tess
