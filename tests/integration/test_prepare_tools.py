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
"""Testing of prepare tools."""

import numpy as np
from pint import Quantity

from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.measurements import UNITS
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.sketch import Sketch
from ansys.geometry.core.tools.prepare_tools import EnclosureOptions

from .conftest import FILES_DIR


def test_volume_extract_from_faces(modeler: Modeler):
    """Test a volume is created from the provided faces."""
    design = modeler.open_file(FILES_DIR / "hollowCylinder.scdocx")

    body = design.bodies[0]
    inside_faces = [body.faces[0]]
    sealing_faces = [body.faces[1], body.faces[2]]
    created_bodies = modeler.prepare_tools.extract_volume_from_faces(sealing_faces, inside_faces)

    assert len(created_bodies) == 1


def test_volume_extract_from_edge_loops(modeler: Modeler):
    """Test a volume is created from the provided edges."""
    design = modeler.open_file(FILES_DIR / "hollowCylinder.scdocx")

    body = design.bodies[0]
    sealing_edges = [body.edges[2], body.edges[3]]
    created_bodies = modeler.prepare_tools.extract_volume_from_edge_loops(
        sealing_edges,
    )

    assert len(created_bodies) == 1


def test_remove_rounds(modeler: Modeler):
    """Test a round is removed from the geometry."""
    from ansys.geometry.core.designer import SurfaceType

    design = modeler.open_file(FILES_DIR / "BoxWithRound.scdocx")
    assert len(design.bodies[0].faces) == 7
    roundfaces = [
        face
        for face in design.bodies[0].faces
        if face.surface_type == SurfaceType.SURFACETYPE_CYLINDER
    ]
    result = modeler.prepare_tools.remove_rounds(roundfaces)
    assert len(design.bodies[0].faces) == 6
    assert result is True
    result = modeler.prepare_tools.remove_rounds([design.bodies[0].faces[0]])
    # test removing a face that is not a round
    assert result is True  # remove round always returns True for success
    result = modeler.prepare_tools.remove_rounds(None)
    assert result == []


def test_share_topology(modeler: Modeler):
    """Test share topology operation is between two bodies."""
    design = Modeler.create_design(modeler, "ShareTopoDoc")
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(10, UNITS.mm))
    design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.mm))
    sketch = Sketch()
    sketch.box(Point2D([20, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(10, UNITS.mm))
    design.extrude_sketch("JustABox", sketch, Quantity(5, UNITS.mm))
    faces = 0
    edges = 0
    for body in design.bodies:
        faces += len(body.faces)
        edges += len(body.edges)
    assert faces == 12
    assert edges == 24
    modeler.prepare_tools.share_topology(design.bodies)
    faces = 0
    edges = 0
    for body in design.bodies:
        faces += len(body.faces)
        edges += len(body.edges)
    assert faces == 13
    assert edges == 27
    result = modeler.prepare_tools.share_topology(None)
    assert result is False


def test_enhanced_share_topology(modeler: Modeler):
    """Test enhanced share topology operation is between two bodies."""
    design = modeler.open_file(FILES_DIR / "MixingTank.scdocx")
    face_count = (
        len(design.bodies[0].faces) + len(design.bodies[1].faces) + len(design.bodies[2].faces)
    )
    edge_count = (
        len(design.bodies[0].edges) + len(design.bodies[1].edges) + len(design.bodies[2].edges)
    )
    assert face_count == 127
    assert edge_count == 284
    result = modeler.prepare_tools.enhanced_share_topology(design.bodies, 0.000554167, True)
    assert result.found == 14
    assert result.repaired == 14
    result = modeler.prepare_tools.enhanced_share_topology(None, 0, False)
    assert result.found == 0


def test_detect_logos(modeler: Modeler):
    """Test logos are detected and deleted."""
    design = modeler.open_file(FILES_DIR / "partWithLogos.scdocx")
    component = [c for c in design.components if c.name == "Default"][0]
    body = [b for b in component.bodies if b.name == "Solid3"][0]
    assert len(body.faces) == 189
    result = modeler.prepare_tools.find_logos()
    # no logos should be found if max height is not given
    assert len(result.face_ids) == 0
    result = modeler.prepare_tools.find_logos(max_height=0.005)
    assert len(result.face_ids) == 147
    success = modeler.prepare_tools.find_and_remove_logos(max_height=0.005)
    assert success is True
    assert len(body.faces) == 42
    result = modeler.prepare_tools.find_and_remove_logos(None, min_height=0.001, max_height=0.005)
    assert result is False
    result = modeler.prepare_tools.find_and_remove_logos(
        design.components[0].bodies, min_height=0.001, max_height=0.005
    )
    assert result is False


def test_detect_and_fix_logo_as_problem_area(modeler: Modeler):
    """Test logos are detected and deleted as problem area"""
    design = modeler.open_file(FILES_DIR / "partWithLogos.scdocx")
    component = [c for c in design.components if c.name == "Default"][0]
    body = [b for b in component.bodies if b.name == "Solid3"][0]
    # Initial face count
    assert len(body.faces) == 189
    # Test finding logos without max height
    result_no_max_height = modeler.prepare_tools.find_logos()
    assert len(result_no_max_height.face_ids) == 0
    # Test finding logos with max height
    result_with_max_height = modeler.prepare_tools.find_logos(max_height=0.005)
    assert len(result_with_max_height.face_ids) == 147
    # Test removing logos with max height
    success_remove_logos = modeler.prepare_tools.find_and_remove_logos(max_height=0.005)
    assert success_remove_logos is True
    assert len(body.faces) == 42
    # Test removing logos with min and max height (no logos should be removed)
    result_min_max_height = modeler.prepare_tools.find_and_remove_logos(
        None, min_height=0.001, max_height=0.005
    )
    assert result_min_max_height is False
    # Test removing logos from specific bodies (no logos should be removed)
    result_specific_bodies = modeler.prepare_tools.find_and_remove_logos(
        design.components[0].bodies, min_height=0.001, max_height=0.005
    )
    assert result_specific_bodies is False


def test_volume_extract_bad_faces(modeler: Modeler):
    """Test a volume extract with bad faces."""
    design = modeler.open_file(FILES_DIR / "BoxWithRound_noedits.scdocx")

    body = design.bodies[0]
    inside_faces = []
    sealing_faces = [body.faces[1], body.faces[4]]
    created_bodies = modeler.prepare_tools.extract_volume_from_faces(sealing_faces, inside_faces)
    assert len(created_bodies) == 0
    inside_faces = [body.faces[6]]
    sealing_faces = []
    created_bodies = modeler.prepare_tools.extract_volume_from_faces(sealing_faces, inside_faces)
    assert len(created_bodies) == 0
    inside_faces = [body.faces[0]]
    sealing_faces = [body.faces[1]]
    created_bodies = modeler.prepare_tools.extract_volume_from_faces(sealing_faces, inside_faces)
    assert len(created_bodies) == 0


def test_volume_extract_bad_edges(modeler: Modeler):
    """Test a volume extract with bad edges."""
    design = modeler.open_file(FILES_DIR / "BoxWithRound_noedits.scdocx")
    body = design.bodies[0]
    sealing_edges = []
    created_bodies = modeler.prepare_tools.extract_volume_from_edge_loops(
        sealing_edges,
    )
    assert len(created_bodies) == 0
    sealing_edges = [body.edges[0], body.edges[1]]
    created_bodies = modeler.prepare_tools.extract_volume_from_edge_loops(
        sealing_edges,
    )
    assert len(created_bodies) == 0


def test_helix_detection(modeler: Modeler):
    """Test helix detection."""
    design = modeler.open_file(FILES_DIR / "bolt.scdocx")

    bodies = design.bodies
    assert len(bodies) == 2

    search_bodies = [bodies[0]]
    assert len(search_bodies) == 1

    # Test default parameters
    result = modeler.prepare_tools.detect_helixes(search_bodies)
    assert len(result["helixes"]) == 1

    # Test with non-default parameters
    result = modeler.prepare_tools.detect_helixes(search_bodies, 0, 10, 100)
    assert len(result["helixes"]) == 1

    # Test parameters that should yield no results
    result = modeler.prepare_tools.detect_helixes(search_bodies, 5.0, 10.0, 0.01)
    assert len(result["helixes"]) == 0

    # Test with multiple bodies
    result = modeler.prepare_tools.detect_helixes(bodies)
    assert len(result["helixes"]) == 2

    # Test with multiple bodies
    result = modeler.prepare_tools.detect_helixes(bodies)
    assert len(result["helixes"]) == 2


def test_box_enclosure(modeler):
    """Tests creation of a box enclosure. """
    design = modeler.open_file(FILES_DIR / "BoxWithRound.scdocx")
    bodies = [design.bodies[0]]
    enclosure_options = EnclosureOptions()
    modeler.prepare_tools.create_box_enclosure(
        bodies, 0.005, 0.01, 0.01, 0.005, 0.10, 0.10, enclosure_options
    )
    assert len(design.components) == 1
    assert len(design.components[0].bodies) == 1
    # verify that a body is created in a new component
    volume_when_subtracting = design.components[0].bodies[0].volume
    enclosure_options = EnclosureOptions(subtract_bodies=False)
    modeler.prepare_tools.create_box_enclosure(
        bodies, 0.005, 0.01, 0.01, 0.005, 0.10, 0.10, enclosure_options
    )
    assert len(design.components) == 2
    assert len(design.components[1].bodies) == 1
    volume_without_subtracting = design.components[1].bodies[0].volume
    # verify that the volume without subtracting is greater than the one with subtraction
    assert volume_without_subtracting > volume_when_subtracting
    # verify that an enclosure can be created with zero cushion
    modeler.prepare_tools.create_box_enclosure(
        bodies, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, enclosure_options
    )
    assert len(design.components) == 3
    assert len(design.components[2].bodies) == 1


def test_cylinder_enclosure(modeler):
    """Tests creation of a cylinder enclosure. """
    design = modeler.open_file(FILES_DIR / "BoxWithRound.scdocx")
    bodies = [design.bodies[0]]
    origin = Vector3D([0.0, 0.0, 0.0])
    direction_x = UnitVector3D([0, 1, 0])
    direction_y = UnitVector3D([0, 0, 1])
    frame = Frame(origin, direction_x, direction_y)
    enclosure_options = EnclosureOptions(frame=frame)
    modeler.prepare_tools.create_cylinder_enclosure(bodies, 0.1, 0.1, 0.1, enclosure_options)
    assert len(design.components) == 1
    assert len(design.components[0].bodies) == 1
    bounding_box = design.components[0].bodies[0].bounding_box
    # check that the cylinder has been placed in the appropriate position based upon the frame
    assert np.allclose(bounding_box.center, Point3D([0.0, 0.0, 0.01]))


def test_sphere_enclosure(modeler):
    """Tests creation of a sphere enclosure. """
    design = modeler.open_file(FILES_DIR / "BoxWithRound.scdocx")
    bodies = [design.bodies[0]]
    enclosure_options = EnclosureOptions()
    modeler.prepare_tools.create_sphere_enclosure(bodies, 0.1, enclosure_options)
    assert len(design.components) == 1
    assert len(design.components[0].bodies) == 1
