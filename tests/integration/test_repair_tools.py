""""Testing of repair tools."""

import pytest

from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.modeler import Modeler


# TODO: re-enable when Linux service is able to use repair tools
def skip_if_linux(modeler: Modeler):
    """Skip test if running on Linux."""
    if modeler.client.backend_type == BackendType.LINUX_SERVICE:
        pytest.skip("Repair tools not available on Linux service.")


def test_find_split_edges(modeler: Modeler):
    """Test if split edge problem areas are detectable."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/SplitEdgeDesignTest.scdocx")
    problem_areas = modeler.repair_tools.find_split_edges(["0:39"], 25, 150)
    assert len(problem_areas) == 3


def test_find_split_edge_id(modeler: Modeler):
    """Test whether problem area has the id."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/SplitEdgeDesignTest.scdocx")
    problem_areas = modeler.repair_tools.find_split_edges(["0:39"], 25, 150)
    assert problem_areas[0].id > 0


def test_find_split_edge_edges(modeler: Modeler):
    """Test to find split edge problem areas with the connected edges."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/SplitEdgeDesignTest.scdocx")
    problem_areas = modeler.repair_tools.find_split_edges(["0:39"], 25, 150)
    assert len(problem_areas[0].edges) > 0


def test_fix_split_edge(modeler: Modeler):
    """Test to find and fix split edge problem areas."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/SplitEdgeDesignTest.scdocx")
    problem_areas = modeler.repair_tools.find_split_edges(["0:39"], 25, 150)
    assert problem_areas[0].fix().success


def test_find_extra_edges(modeler: Modeler):
    """Test to read geometry and find it's extra edge problem areas."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/ExtraEdgesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_extra_edges(["0:22"])
    assert len(problem_areas) == 1


def test_find_extra_edge_id(modeler: Modeler):
    """Test whether problem area has the id."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/ExtraEdgesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_extra_edges(["0:22"])
    assert problem_areas[0].id > 0


def test_find_extra_edge_edges(modeler: Modeler):
    """Test to read geometry and find it's extra edge problem area with connected
    edges."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/ExtraEdgesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_extra_edges(["0:22"])
    assert len(problem_areas[0].edges) > 0


def test_find_inexact_edges(modeler: Modeler):
    """Test to read geometry and find it's inexact edge problem areas."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/InExactEdgesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_inexact_edges(["0:38"])
    assert len(problem_areas) == 12


def test_find_inexact_edge_id(modeler: Modeler):
    """Test whether problem area has the id."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/InExactEdgesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_inexact_edges(["0:38"])
    assert problem_areas[0].id > 0


def test_find_inexact_edge_edges(modeler: Modeler):
    """Test to read geometry and find it's inexact edge problem areas with connected
    edges."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/InExactEdgesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_inexact_edges(["0:38"])
    assert len(problem_areas[0].edges) > 0


def test_fix_inexact_edge(modeler: Modeler):
    """Test to read geometry and find and fix it's inexact edge problem areas."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/InExactEdgesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_inexact_edges(["0:38"])
    assert problem_areas[0].fix().success


def test_find_missing_faces(modeler: Modeler):
    """Test to read geometry and find it's missing face problem areas."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/MissingFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_missing_faces(["1:40"])
    assert len(problem_areas) == 1


def test_find_missing_face_id(modeler: Modeler):
    """Test whether problem area has the id."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/MissingFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_missing_faces(["1:40"])
    assert problem_areas[0].id > 0


def test_find_missing_face_faces(modeler: Modeler):
    """Test to read geometry and find it's missing face problem area with connected
    edges."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/MissingFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_missing_faces(["1:40"])
    assert len(problem_areas[0].edges) > 0


def test_fix_missing_face(modeler: Modeler):
    """Test to read geometry and find and fix it's missing face problem areas."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/MissingFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_missing_faces(["1:40"])
    assert problem_areas[0].fix().success


def test_find_duplicate_faces(modeler: Modeler):
    """Test to read geometry and find it's duplicate face problem areas."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/DuplicateFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_duplicate_faces(["0:22", "0:85"])
    assert len(problem_areas) == 1


def test_duplicate_face_id(modeler: Modeler):
    """Test whether duplicate face problem area has the id."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/DuplicateFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_duplicate_faces(["0:22", "0:85"])
    assert problem_areas[0].id > 0


def test_duplicate_face_faces(modeler: Modeler):
    """Test to read geometry and find it's duplicate face problem area and its connected
    faces."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/DuplicateFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_duplicate_faces(["0:22", "0:85"])
    assert len(problem_areas[0].faces) > 0


def test_fix_duplicate_face(modeler: Modeler):
    """Test to read geometry and find and fix it's duplicate face problem areas."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/DuplicateFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_duplicate_faces(["0:22", "0:85"])
    assert problem_areas[0].fix().success


def test_find_small_faces(modeler: Modeler):
    """Test to read geometry and find it's small face problem areas."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/SmallFacesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_small_faces(["0:38"])
    assert len(problem_areas) == 4


def test_find_small_face_id(modeler: Modeler):
    """Test whether problem area has the id."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/SmallFacesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_small_faces(["0:38"])
    assert problem_areas[0].id > 0


def test_find_small_face_faces(modeler: Modeler):
    """Test to read geometry, find it's small face problem area and return connected
    faces."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/SmallFacesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_small_faces(["0:38"])
    assert len(problem_areas[0].faces) > 0


def test_fix_small_face(modeler: Modeler):
    """Test to read geometry and find and fix it's small face problem areas."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/SmallFacesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_small_faces(["0:38"])
    assert problem_areas[0].fix().success > 0


def test_find_stitch_faces(modeler: Modeler):
    """Test to read geometry and find it's stitch face problem areas."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/stitch_before.scdocx")
    design = modeler.read_existing_design()
    face_ids = []
    for body in design.bodies:
        face_ids.append(body.id)
    problem_areas = modeler.repair_tools.find_stitch_faces(face_ids)
    assert len(problem_areas) == 1


def test_find_stitch_face_id(modeler: Modeler):
    """Test whether problem area has the id."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/stitch_before.scdocx")
    design = modeler.read_existing_design()
    face_ids = []
    for body in design.bodies:
        face_ids.append(body.id)
    problem_areas = modeler.repair_tools.find_stitch_faces(face_ids)
    assert problem_areas[0].id > 0


def test_find_stitch_face_faces(modeler: Modeler):
    """Test to read geometry and find it's stitch face problem area and return the
    connected faces."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/stitch_before.scdocx")
    design = modeler.read_existing_design()
    face_ids = []
    for body in design.bodies:
        face_ids.append(body.id)
    problem_areas = modeler.repair_tools.find_stitch_faces(face_ids)
    assert len(problem_areas[0].faces) > 0


def test_fix_stitch_face(modeler: Modeler):
    """Test to read geometry, find the split edge problem areas and to fix them."""
    skip_if_linux(modeler)  # Skip test on Linux
    modeler.open_file("./tests/integration/files/stitch_before.scdocx")
    design = modeler.read_existing_design()
    face_ids = []
    for body in design.bodies:
        face_ids.append(body.id)
    problem_areas = modeler.repair_tools.find_stitch_faces(face_ids)
    message = problem_areas[0].fix()
    assert message.success == True
    assert len(message.created_bodies) == 0
    assert len(message.modified_bodies) > 0
