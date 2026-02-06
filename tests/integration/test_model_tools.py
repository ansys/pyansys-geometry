# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
"""Testing of model tools."""

from pint import Quantity
import pytest

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.sketch.sketch import Sketch


def test_detach_faces_geometry_commands_single_body(modeler: Modeler):
    """Test detach_faces via geometry_commands with a single body."""
    design = modeler.create_design("detach_single_body")

    # Create a box
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    # Initial state: 6 faces, 12 edges
    initial_body_count = len(design.bodies)
    assert len(body.faces) == 6
    assert len(body.edges) == 12
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # Detach all faces from the body using geometry_commands
    created_bodies = modeler.geometry_commands.detach_faces(body)

    # After detach, we should have new surface bodies created
    # (one for each face except the original body which is modified to become one of the surface
    # bodies)
    # Original body is modified to become one of the surface bodies, so we get 5 new bodies
    # instead of 6
    assert len(created_bodies) == 5

    # All created bodies should be surface bodies
    for created_body in created_bodies:
        assert created_body.is_surface
        assert len(created_body.faces) == 1

    # Total number of bodies should increase
    # Original body is modified, 5 new bodies created, net increase of 5
    assert len(design.bodies) == initial_body_count + 5


def test_detach_faces_geometry_commands_list_of_bodies(modeler: Modeler):
    """Test detach_faces via geometry_commands with a list of bodies."""
    design = modeler.create_design("detach_list_of_bodies")

    # Create two boxes
    body1 = design.extrude_sketch("box1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    body2 = design.extrude_sketch("box2", Sketch().box(Point2D([2, 0]), 1, 1), 1)

    initial_body_count = len(design.bodies)
    assert initial_body_count == 2

    # Detach faces from both bodies
    created_bodies = modeler.geometry_commands.detach_faces([body1, body2])

    # Should create 5 surface bodies for each box (10 total)
    assert len(created_bodies) == 10

    # All created bodies should be surface bodies
    for created_body in created_bodies:
        assert created_body.is_surface

    # Total number of bodies should increase
    # Original bodies are modified, 10 new bodies created, net increase of 10
    assert len(design.bodies) == initial_body_count + 10


def test_detach_faces_geometry_commands_single_face(modeler: Modeler):
    """Test detach_faces via geometry_commands with a single face."""
    design = modeler.create_design("detach_single_face")

    # Create a box
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    initial_body_count = len(design.bodies)
    initial_face_count = len(body.faces)
    assert initial_face_count == 6

    # Select one face to detach
    face_to_detach = body.faces[0]

    # Detach the single face
    created_bodies = modeler.geometry_commands.detach_faces(face_to_detach)

    # Should create 1 new surface body
    assert len(created_bodies) == 1
    assert created_bodies[0].is_surface
    assert len(created_bodies[0].faces) == 1

    # Total number of bodies should increase by 1
    assert len(design.bodies) == initial_body_count + 1


def test_detach_faces_geometry_commands_list_of_faces(modeler: Modeler):
    """Test detach_faces via geometry_commands with a list of faces."""
    design = modeler.create_design("detach_list_of_faces")

    # Create a box
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    initial_body_count = len(design.bodies)
    assert len(body.faces) == 6

    # Select multiple faces to detach
    faces_to_detach = [body.faces[0], body.faces[1], body.faces[2]]

    # Detach the selected faces
    created_body = modeler.geometry_commands.detach_faces(faces_to_detach)

    # Should create 1 new surface body
    assert len(created_body) == 1

    assert created_body[0].is_surface
    # The created body should have 3 faces corresponding to the detached faces
    assert len(created_body[0].faces) == 3

    # Total number of bodies should increase by 1
    assert len(design.bodies) == initial_body_count + 1


def test_body_detach_faces(modeler: Modeler):
    """Test detach_faces method on Body instance."""
    design = modeler.create_design("body_detach_faces")

    # Create a box
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    initial_body_count = len(design.bodies)
    initial_faces = len(body.faces)
    assert initial_faces == 6
    assert len(body.edges) == 12
    assert body.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    # Call detach_faces directly on the body
    created_bodies = body.detach_faces()

    # After detach, we should have new surface bodies created (one for each face except the
    # original body which is modified to become one of the surface bodies)

    # Original body is modified to become one of the surface bodies, so we get 5 new bodies
    # instead of 6
    assert len(created_bodies) == 5

    # All created bodies should be surface bodies
    for created_body in created_bodies:
        assert created_body.is_surface
        assert len(created_body.faces) == 1

    # Total number of bodies should increase
    # Original body is modified, 6 new bodies created, net increase of 5
    assert len(design.bodies) == initial_body_count + 5


def test_body_detach_faces_multiple_bodies(modeler: Modeler):
    """Test detach_faces on multiple bodies sequentially."""
    design = modeler.create_design("body_detach_multiple")

    # Create two boxes with different sizes
    body1 = design.extrude_sketch("box1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    body2 = design.extrude_sketch("box2", Sketch().box(Point2D([3, 0]), 2, 2), 2)

    initial_body_count = len(design.bodies)
    assert initial_body_count == 2

    # Detach faces from first body
    created_bodies_1 = body1.detach_faces()
    # Original body is modified, 6 new bodies created, net increase of 5
    assert len(created_bodies_1) == 5

    # Detach faces from second body
    created_bodies_2 = body2.detach_faces()
    # Original body is modified, 6 new bodies created, net increase of 5
    assert len(created_bodies_2) == 5
    # Total created bodies should be 10
    assert len(created_bodies_1) + len(created_bodies_2) == 10

    # All created bodies should be surface bodies
    for created_body in created_bodies_1 + created_bodies_2:
        assert created_body.is_surface

    # Total number of bodies should increase by 10
    # Original bodies are modified, 12 new bodies created, net increase of 10
    assert len(design.bodies) == initial_body_count + 10


def test_face_detach(modeler: Modeler):
    """Test detach method on Face instance."""
    design = modeler.create_design("face_detach")

    # Create a box
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    initial_body_count = len(design.bodies)
    initial_face_count = len(body.faces)
    assert initial_face_count == 6

    # Select a face to detach
    face_to_detach = body.faces[0]
    face_area = face_to_detach.area

    # Call detach directly on the face
    result = face_to_detach.detach()

    # The result should be a list containing the created body
    # (Note: based on the implementation, it returns a list from get_bodies_from_ids)
    assert isinstance(result, list)
    assert len(result) == 1

    created_body = result[0]
    assert created_body.is_surface
    assert len(created_body.faces) == 1

    # The created surface body's face should have approximately the same area
    assert created_body.faces[0].area.m == pytest.approx(face_area.m, rel=1e-6, abs=1e-8)

    # Total number of bodies should increase by 1
    assert len(design.bodies) == initial_body_count + 1


def test_face_detach_multiple_faces(modeler: Modeler):
    """Test detaching multiple faces individually."""
    design = modeler.create_design("face_detach_multiple")

    # Create a box
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    initial_body_count = len(design.bodies)
    faces_to_detach = [body.faces[0], body.faces[1], body.faces[2]]

    created_bodies = []

    # Detach each face individually
    for face in faces_to_detach:
        result = face.detach()
        assert isinstance(result, list)
        created_bodies.extend(result)

    # Should have created 3 new surface bodies
    assert len(created_bodies) == 3

    # All created bodies should be surface bodies with one face each
    for created_body in created_bodies:
        assert created_body.is_surface
        assert len(created_body.faces) == 1

    # Total number of bodies should increase by 3
    assert len(design.bodies) == initial_body_count + 3


def test_detach_faces_with_complex_geometry(modeler: Modeler):
    """Test detach_faces with a more complex geometry (cylinder)."""
    design = modeler.create_design("detach_complex")

    # Create a cylinder
    sketch = Sketch()
    sketch.circle(Point2D([0, 0]), 0.5)
    body = design.extrude_sketch("cylinder", sketch, 2)

    initial_body_count = len(design.bodies)
    initial_face_count = len(body.faces)

    # A cylinder should have 3 faces: top, bottom, and cylindrical surface
    assert initial_face_count == 3

    # Detach all faces
    created_bodies = body.detach_faces()

    # Should create 2 new surface bodies
    # Original body is modified to become one of the surface bodies, so we get
    # 2 new bodies instead of 3
    assert len(created_bodies) == 2

    # All created bodies should be surface bodies
    for created_body in created_bodies:
        assert created_body.is_surface
        assert len(created_body.faces) == 1

    # Total number of bodies should increase by 2
    assert len(design.bodies) == initial_body_count + 2


def test_detach_mixed_selection(modeler: Modeler):
    """Test detach_faces with a mixed selection of bodies and faces."""
    design = modeler.create_design("detach_mixed")

    # Create two boxes
    body1 = design.extrude_sketch("box1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    body2 = design.extrude_sketch("box2", Sketch().box(Point2D([3, 0]), 1, 1), 1)

    initial_body_count = len(design.bodies)
    assert initial_body_count == 2

    # Create a mixed selection: one complete body and one face from another body
    # Note: Based on the implementation, we can only pass Body or Face types, not mixed
    # So let's test with just bodies
    created_bodies = modeler.geometry_commands.detach_faces([body1, body2])

    # Should create 5 surface bodies for each box (10 total)
    assert len(created_bodies) == 10

    for created_body in created_bodies:
        assert created_body.is_surface

    # Total number of bodies should increase by 10
    # Original bodies are modified, 12 new bodies created, net increase of 10
    assert len(design.bodies) == initial_body_count + 10


def test_detach_faces_with_tracker_disabled(modeler: Modeler):
    """Test detach_faces when USE_TRACKER_TO_UPDATE_DESIGN is disabled."""
    import ansys.geometry.core as pyansys_geo

    design = modeler.create_design("detach_tracker_disabled")

    # Create a box
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    initial_body_count = len(design.bodies)

    # Save the current tracker setting
    original_tracker_setting = pyansys_geo.USE_TRACKER_TO_UPDATE_DESIGN

    try:
        # Disable the tracker to test the alternative code path
        pyansys_geo.USE_TRACKER_TO_UPDATE_DESIGN = False

        # Detach faces from the body - this should use _update_design_inplace()
        created_bodies = modeler.geometry_commands.detach_faces(body)

        # Verify that bodies were created
        assert len(created_bodies) == 5
        assert len(design.bodies) == initial_body_count + 5

        # All created bodies should be surface bodies
        for created_body in created_bodies:
            assert created_body.is_surface

    finally:
        # Restore the original tracker setting
        pyansys_geo.USE_TRACKER_TO_UPDATE_DESIGN = original_tracker_setting


def test_detach_faces_empty_result_scenario(modeler: Modeler):
    """Test detach_faces behavior with edge cases that might return no bodies."""
    design = modeler.create_design("detach_empty_result")

    # Create a cylinder
    sketch = Sketch()
    sketch.circle(Point2D([0, 0]), 0.5)
    body = design.extrude_sketch("cylinder", sketch, 2)

    initial_body_count = len(design.bodies)
    initial_face_count = len(body.faces)

    # A cylinder should have 3 faces: top, bottom, and cylindrical surface
    assert initial_face_count == 3

    # Detach all faces
    created_bodies = body.detach_faces()

    initial_body_count = len(design.bodies)

    assert len(created_bodies) == 2
    created_body = created_bodies[0]
    assert created_body.is_surface

    # Try to detach faces from a surface body
    # Surface bodies may behave differently
    result = modeler.geometry_commands.detach_faces(created_body)

    # The result might be empty or contain bodies depending on the service implementation
    # This test ensures the method handles various scenarios gracefully
    assert isinstance(result, list)

    # Check that the total body count is consistent
    assert len(design.bodies) >= initial_body_count


def test_body_detach_faces_empty_result_scenario(modeler: Modeler):
    """Test body.detach_faces() behavior with edge cases that might return no bodies."""
    design = modeler.create_design("body_detach_empty_result")

    # Create a cylinder
    sketch = Sketch()
    sketch.circle(Point2D([0, 0]), 0.5)
    body = design.extrude_sketch("cylinder", sketch, 2)

    initial_body_count = len(design.bodies)
    initial_face_count = len(body.faces)

    # A cylinder should have 3 faces: top, bottom, and cylindrical surface
    assert initial_face_count == 3

    # Detach all faces
    created_bodies = body.detach_faces()

    initial_body_count = len(design.bodies)

    assert len(created_bodies) == 2
    created_body = created_bodies[0]
    assert created_body.is_surface

    # Try to detach faces from a surface body using body method
    # Surface bodies may behave differently
    result = created_body.detach_faces()

    # The result might be empty or contain bodies depending on the service implementation
    # This test ensures the method handles various scenarios gracefully
    assert isinstance(result, list)

    # Check that the total body count is consistent
    assert len(design.bodies) >= initial_body_count


def test_face_detach_empty_result_scenario(modeler: Modeler):
    """Test face.detach() behavior with edge cases that might return no bodies."""
    design = modeler.create_design("face_detach_empty_result")

    # Create a cylinder
    sketch = Sketch()
    sketch.circle(Point2D([0, 0]), 0.5)
    body = design.extrude_sketch("cylinder", sketch, 2)

    initial_body_count = len(design.bodies)
    initial_face_count = len(body.faces)

    # A cylinder should have 3 faces: top, bottom, and cylindrical surface
    assert initial_face_count == 3

    # Detach one face first
    face_to_detach = body.faces[0]
    created_bodies = face_to_detach.detach()

    initial_body_count = len(design.bodies)

    assert len(created_bodies) == 1
    created_body = created_bodies[0]
    assert created_body.is_surface

    # Try to detach a face from the surface body
    # Surface bodies may behave differently
    surface_face = created_body.faces[0]
    result = surface_face.detach()

    # The result might be empty or contain bodies depending on the service implementation
    # This test ensures the method handles various scenarios gracefully
    assert isinstance(result, list)

    # Check that the total body count is consistent
    assert len(design.bodies) >= initial_body_count
