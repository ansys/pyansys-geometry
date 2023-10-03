""""Testing of repair tools."""

from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.tools import RepairTools


def test_find_split_edges(modeler: Modeler):
    modeler.open_file("./tests/integration/files/SplitEdgeDesignTest.scdocx")
    problem_areas = modeler.repair_tools.find_split_edges(["0:39"], 25, 150)
    assert len(problem_areas) == 3


def test_find_extra_edges(modeler: Modeler):
    """Test to read geometry and find it's extra edge problem areas."""
    modeler.open_file("./tests/integration/files/ExtraEdgesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_extra_edges(["0:22"])
    assert len(problem_areas) == 1


def test_find_inexact_edges(modeler: Modeler):
    """Test to read geometry and find it's inexact edge problem areas."""
    modeler.open_file("./tests/integration/files/InExactEdgesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_inexact_edges(["0:38"])
    assert len(problem_areas) == 6


def test_find_missing_faces(modeler: Modeler):
    """Test to read geometry and find it's missing face problem areas."""
    modeler.open_file("./tests/integration/files/MissingFacesDesignBefore.scdocx")
    repair_tools = RepairTools(modeler.client)
    problem_areas = repair_tools.find_missing_faces(["1:40"])
    assert len(problem_areas) == 1


def test_find_duplicate_faces(modeler: Modeler):
    """Test to read geometry and find it's duplicate face problem areas."""
    modeler.open_file("./tests/integration/files/DuplicateFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_duplicate_faces(["0:22", "0:85"])
    assert len(problem_areas) == 1


def test_find_small_faces(modeler: Modeler):
    """Test to read geometry and find it's small face problem areas."""
    modeler.open_file("./tests/integration/files/SmallFacesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_small_faces(["0:38"])
    assert len(problem_areas) == 4


def test_find_stitch_faces(modeler: Modeler):
    """Test to read geometry and find it's stitch face problem areas."""
    modeler.open_file("./tests/integration/files/stitch_before.scdocx")
    design = modeler.read_existing_design()
    faceIds = []
    for body in design.bodies:
        faceIds.append(body.id)
    problem_areas = modeler.repair_tools.find_stitch_faces(faceIds)
    assert len(problem_areas) == 1
