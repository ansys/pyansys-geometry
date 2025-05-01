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
""" "Testing of repair tools."""

from ansys.geometry.core.modeler import Modeler

from .conftest import FILES_DIR, skip_if_core_service


def test_find_split_edges(modeler: Modeler):
    """Test if split edge problem areas are detectable."""
    design = modeler.open_file(FILES_DIR / "SplitEdgeDesignTest.scdocx")
    problem_areas = modeler.repair_tools.find_split_edges(design.bodies, 25, 150)
    assert len(problem_areas) == 3


def test_find_split_edge_id(modeler: Modeler):
    """Test whether problem area has the id."""
    design = modeler.open_file(FILES_DIR / "SplitEdgeDesignTest.scdocx")
    problem_areas = modeler.repair_tools.find_split_edges(design.bodies, 25, 150)
    assert problem_areas[0].id != "0"


def test_find_split_edge_edges(modeler: Modeler):
    """Test to find split edge problem areas with the connected edges."""
    design = modeler.open_file(FILES_DIR / "SplitEdgeDesignTest.scdocx")
    problem_areas = modeler.repair_tools.find_split_edges(design.bodies, 25, 150)
    assert len(problem_areas[0].edges) > 0


def test_fix_split_edge(modeler: Modeler):
    """Test to find and fix split edge problem areas."""
    design = modeler.open_file(FILES_DIR / "SplitEdgeDesignTest.scdocx")
    problem_areas = modeler.repair_tools.find_split_edges(design.bodies, 25, 150)
    assert problem_areas[0].fix().success is True


def test_find_extra_edges(modeler: Modeler):
    """Test to read geometry and find it's extra edge problem areas."""
    design = modeler.open_file(FILES_DIR / "ExtraEdgesDesignBefore.scdocx")

    problem_areas = modeler.repair_tools.find_extra_edges(design.bodies)
    assert len(problem_areas) == 1


def test_find_extra_edge_id(modeler: Modeler):
    """Test whether problem area has the id."""
    design = modeler.open_file(FILES_DIR / "ExtraEdgesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_extra_edges(design.bodies)
    assert problem_areas[0].id != "0"


def test_find_extra_edge_edges(modeler: Modeler):
    """Test to read geometry and find it's extra edge problem area with
    connected edges.
    """
    design = modeler.open_file(FILES_DIR / "ExtraEdgesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_extra_edges(design.bodies)
    assert len(problem_areas[0].edges) > 0


def test_fix_extra_edge(modeler: Modeler):
    """Test to find and fix extra edge problem areas."""
    design = modeler.open_file(FILES_DIR / "ExtraEdgesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_extra_edges(design.bodies)
    assert problem_areas[0].fix().success is True


def test_find_inexact_edges(modeler: Modeler):
    """Test to read geometry and find it's inexact edge problem areas."""
    design = modeler.open_file(FILES_DIR / "InExactEdgesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_inexact_edges(design.bodies)
    assert len(problem_areas) == 12


def test_find_inexact_edge_id(modeler: Modeler):
    """Test whether problem area has the id."""
    design = modeler.open_file(FILES_DIR / "InExactEdgesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_inexact_edges(design.bodies)
    assert problem_areas[0].id != "0"


def test_find_inexact_edge_edges(modeler: Modeler):
    """Test to read geometry and find it's inexact edge problem areas with
    connected edges.
    """
    design = modeler.open_file(FILES_DIR / "InExactEdgesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_inexact_edges(design.bodies)
    assert len(problem_areas[0].edges) > 0


def test_fix_inexact_edge(modeler: Modeler):
    """Test to read geometry and find and fix it's inexact edge problem
    areas.
    """
    design = modeler.open_file(FILES_DIR / "InExactEdgesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_inexact_edges(design.bodies)
    assert problem_areas[0].fix().success is True


def test_find_missing_faces(modeler: Modeler):
    """Test to read geometry and find it's missing face problem areas."""
    design = modeler.open_file(FILES_DIR / "MissingFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_missing_faces(design.bodies)
    assert len(problem_areas) == 1


def test_find_missing_face_id(modeler: Modeler):
    """Test whether problem area has the id."""
    design = modeler.open_file(FILES_DIR / "MissingFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_missing_faces(design.bodies)
    assert problem_areas[0].id != "0"


def test_find_missing_face_faces(modeler: Modeler):
    """Test to read geometry and find it's missing face problem area with
    connected edges.
    """
    design = modeler.open_file(FILES_DIR / "MissingFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_missing_faces(design.bodies)
    assert len(problem_areas[0].edges) > 0


def test_fix_missing_face(modeler: Modeler):
    """Test to read geometry and find and fix it's missing face problem
    areas.
    """
    design = modeler.open_file(FILES_DIR / "MissingFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_missing_faces(design.bodies)
    assert problem_areas[0].fix().success is True


def test_find_duplicate_faces(modeler: Modeler):
    """Test to read geometry and find it's duplicate face problem areas."""
    design = modeler.open_file(FILES_DIR / "DuplicateFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_duplicate_faces(design.bodies)
    assert len(problem_areas) == 1


def test_duplicate_face_id(modeler: Modeler):
    """Test whether duplicate face problem area has the id."""
    design = modeler.open_file(FILES_DIR / "DuplicateFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_duplicate_faces(design.bodies)
    assert problem_areas[0].id != "0"


def test_duplicate_face_faces(modeler: Modeler):
    """Test to read geometry and find it's duplicate face problem area and its
    connected faces.
    """
    design = modeler.open_file(FILES_DIR / "DuplicateFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_duplicate_faces(design.bodies)
    assert len(problem_areas[0].faces) > 0


def test_fix_duplicate_face(modeler: Modeler):
    """Test to read geometry and find and fix it's duplicate face problem
    areas.
    """
    design = modeler.open_file(FILES_DIR / "DuplicateFacesDesignBefore.scdocx")
    problem_areas = modeler.repair_tools.find_duplicate_faces(design.bodies)
    assert problem_areas[0].fix().success is True


def test_find_small_faces(modeler: Modeler):
    """Test to read geometry and find it's small face problem areas."""
    # Skip test on CoreService
    skip_if_core_service(modeler, test_find_small_faces.__name__, "repair_tools")
    design = modeler.open_file(FILES_DIR / "SmallFacesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_small_faces(design.bodies)
    assert len(problem_areas) == 4


def test_find_small_face_id(modeler: Modeler):
    """Test whether problem area has the id."""
    # Skip test on CoreService
    skip_if_core_service(modeler, test_find_small_face_id.__name__, "repair_tools")
    design = modeler.open_file(FILES_DIR / "SmallFacesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_small_faces(design.bodies)
    assert problem_areas[0].id != "0"


def test_find_small_face_faces(modeler: Modeler):
    """Test to read geometry, find it's small face problem area and return
    connected faces.
    """
    skip_if_core_service(
        modeler, test_find_small_face_faces.__name__, "repair_tools"
    )  # Skip test on CoreService
    design = modeler.open_file(FILES_DIR / "SmallFacesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_small_faces(design.bodies)
    assert len(problem_areas[0].faces) > 0


def test_fix_small_face(modeler: Modeler):
    """Test to read geometry and find and fix it's small face problem areas."""
    # Skip test on CoreService
    skip_if_core_service(modeler, test_fix_small_face.__name__, "repair_tools")
    design = modeler.open_file(FILES_DIR / "SmallFacesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_small_faces(design.bodies)
    assert problem_areas[0].fix().success is True


def test_find_stitch_faces(modeler: Modeler):
    """Test to read geometry and find it's stitch face problem areas."""
    design = modeler.open_file(FILES_DIR / "stitch_before.scdocx")
    problem_areas = modeler.repair_tools.find_stitch_faces(design.bodies)
    assert len(problem_areas) == 1


def test_find_stitch_face_id(modeler: Modeler):
    """Test whether problem area has the id."""
    design = modeler.open_file(FILES_DIR / "stitch_before.scdocx")
    problem_areas = modeler.repair_tools.find_stitch_faces(design.bodies)
    assert problem_areas[0].id != "0"


def test_find_stitch_face_bodies(modeler: Modeler):
    """Test to read geometry and find it's stitch face problem area and return
    the connected faces.
    """
    design = modeler.open_file(FILES_DIR / "stitch_before.scdocx")
    problem_areas = modeler.repair_tools.find_stitch_faces(design.bodies)
    assert len(problem_areas[0].bodies) > 0


def test_fix_stitch_face(modeler: Modeler):
    """Test to read geometry, find the split edge problem areas and to fix
    them.
    """
    design = modeler.open_file(FILES_DIR / "stitch_before.scdocx")
    problem_areas = modeler.repair_tools.find_stitch_faces(design.bodies)
    message = problem_areas[0].fix()
    assert message.success is True
    assert len(message.created_bodies) == 0
    assert len(message.modified_bodies) > 0


def test_find_short_edges(modeler: Modeler):
    """Test to read geometry and find it's short edge problem areas."""
    design = modeler.open_file(FILES_DIR / "ShortEdgesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_short_edges(design.bodies, 10)
    assert len(problem_areas) == 12


def test_fix_short_edges(modeler: Modeler):
    """Test to read geometry and find and fix it's short edge problem areas."""
    design = modeler.open_file(FILES_DIR / "ShortEdgesBefore.scdocx")
    problem_areas = modeler.repair_tools.find_short_edges(design.bodies, 10)
    assert problem_areas[0].fix().success is True


def test_find_interference(modeler: Modeler):
    """Test to read geometry and find the interference problem areas."""
    design = modeler.open_file(FILES_DIR / "SimpleInterference.scdocx")
    problem_areas = modeler.repair_tools.find_interferences(design.bodies, False)
    assert len(problem_areas) == 1
    assert len(problem_areas[0].bodies) == 2


def test_fix_interference(modeler: Modeler):
    """Test to read geometry and fix ind the interference problem areas."""
    design = modeler.open_file(FILES_DIR / "SimpleInterference.scdocx")
    problem_areas = modeler.repair_tools.find_interferences(design.bodies, False)
    result = problem_areas[0].fix()
    assert result.success is True


def test_find_and_fix_duplicate_faces(modeler: Modeler):
    """Test to read geometry, find and fix duplicate faces and validate they are removed."""
    design = modeler.open_file(FILES_DIR / "DuplicateFaces.scdocx")
    assert len(design.bodies) == 7
    areas = modeler.repair_tools.find_duplicate_faces(design.bodies)
    assert len(areas) == 6
    for area in areas:
        area.fix()
    assert len(design.bodies) == 1


def test_find_and_fix_extra_edges_problem_areas(modeler: Modeler):
    """Test to read geometry, find and fix extra edges and validate they are removed."""
    design = modeler.open_file(FILES_DIR / "ExtraEdges_NoComponents.scdocx")
    assert len(design.bodies) == 3
    starting_edge_count = 0
    for body in design.bodies:
        starting_edge_count += len(body.edges)
    assert starting_edge_count == 69
    extra_edges = modeler.repair_tools.find_extra_edges(design.bodies)
    assert len(extra_edges) == 6
    for edge in extra_edges:
        edge.fix()
    final_edge_count = 0
    for body in design.bodies:
        final_edge_count += len(body.edges)
    assert final_edge_count == 36


def test_find_and_fix_extra_edges_in_components(modeler: Modeler):
    """
    Test to read geometry, find and fix extra edges in components and validate they are
    removed.
    """
    design = modeler.open_file(FILES_DIR / "ExtraEdges.scdocx")
    len(design.components)
    starting_edge_count = 0
    for components in design.components:
        starting_edge_count += len(components.bodies[0].edges)
    assert starting_edge_count == 69
    for components in design.components:
        extra_edges = modeler.repair_tools.find_extra_edges(components.bodies)
        for edge in extra_edges:
            edge.fix()
    final_edge_count = 0
    for components in design.components:
        final_edge_count += len(components.bodies[0].edges)
    assert final_edge_count == 36


def test_find_and_fix_inexact_edges(modeler: Modeler):
    """Test to read geometry, find and fix inexact edges and validate they are fixed removed."""
    design = modeler.open_file(FILES_DIR / "gear.scdocx")
    assert len(design.bodies[0].edges) == 310
    inexact_edges = modeler.repair_tools.find_inexact_edges(design.bodies)
    assert len(inexact_edges) == 73
    for i in inexact_edges:
        i.fix()
    assert len(design.bodies[0].edges) == 310
    inexact_edges = modeler.repair_tools.find_inexact_edges(design.bodies)
    assert len(inexact_edges) == 0


def test_find_and_fix_missing_faces(modeler: Modeler):
    """Test to read geometry, find and fix missing faces and validate that we now have solids."""
    design = modeler.open_file(FILES_DIR / "MissingFaces.scdocx")
    assert len(design.bodies) == 1
    assert design.bodies[0].is_surface
    assert len(design.components) == 3
    for comp in design.components:
        assert comp.bodies[0].is_surface
    missing_faces = modeler.repair_tools.find_missing_faces(design.bodies)
    for face in missing_faces:
        face.fix()
    for components in design.components:
        missing_faces = modeler.repair_tools.find_missing_faces(components.bodies)
        for face in missing_faces:
            face.fix()
    assert not design.bodies[0].is_surface
    for comp in design.components:
        assert not comp.bodies[0].is_surface


def test_find_and_fix_short_edges_problem_areas(modeler: Modeler):
    """Test to read geometry, find and fix short edges and validate they are fixed removed."""
    design = modeler.open_file(FILES_DIR / "ShortEdges.scdocx")
    assert len(design.bodies[0].edges) == 685
    short_edges = modeler.repair_tools.find_short_edges(design.bodies, 0.000127)
    assert len(short_edges) == 8
    for i in short_edges:
        i.fix()
    assert len(design.bodies[0].edges) == 675  ##We get 673 edges if we repair all in one go


def test_find_and_fix_split_edges_problem_areas(modeler: Modeler):
    """Test to read geometry, find and fix split edges and validate they are fixed removed."""
    design = modeler.open_file(FILES_DIR / "bracket-with-split-edges.scdocx")
    assert len(design.bodies[0].edges) == 158
    split_edges = modeler.repair_tools.find_split_edges(design.bodies, 2.61799, 0.01)
    assert len(split_edges) == 86
    for i in split_edges:
        try:  # Try/Except is a workaround. Having .alive would be better
            i.fix()
        except Exception:
            pass
    assert len(design.bodies[0].edges) == 99


def test_find_and_stitch_and_missing_faces(modeler: Modeler):
    """Test to read geometry,fix stitch faces and fix missing faces, verify that we get a solid."""
    design = modeler.open_file(FILES_DIR / "Stitch_And_MissingFaces.scdocx")
    assert len(design.bodies) == 132
    stitch_faces = modeler.repair_tools.find_stitch_faces(design.bodies)
    assert len(stitch_faces) == 1
    for i in stitch_faces:
        i.fix()
    assert len(design.bodies) == 1
    assert design.bodies[0].is_surface
    missing_faces = modeler.repair_tools.find_missing_faces(design.bodies)
    for face in missing_faces:
        face.fix()
    assert len(design.bodies) == 1
    assert not design.bodies[0].is_surface


def test_find_and_fix_stitch_faces(modeler: Modeler):
    """Test to find and fix stitch faces and validate that we get a solid."""
    design = modeler.open_file(FILES_DIR / "stitch_1200_bodies.dsco")
    assert len(design.bodies) == 3600

    stitch_faces = modeler.repair_tools.find_and_fix_stitch_faces(design.bodies)
    assert stitch_faces.found == 1
    assert stitch_faces.repaired == 1

    assert len(design.bodies) == 1200


def test_find_and_fix_stitch_faces_comprehensive(modeler: Modeler):
    """Test to find and fix stitch faces and validate that we get a solid."""
    design = modeler.open_file(FILES_DIR / "stitch_1200_bodies.dsco")
    assert len(design.bodies) == 3600

    stitch_faces = modeler.repair_tools.find_and_fix_stitch_faces(
        design.bodies, 
        comprehensive_result=True
    )
    assert stitch_faces.found == 1200
    assert stitch_faces.repaired == 1200

    assert len(design.bodies) == 1200


def test_find_simplify(modeler: Modeler):
    """Test to read geometry and find it's unsimplified face problem areas."""
    design = modeler.open_file(FILES_DIR / "SOBracket2_HalfModel.scdocx")
    problem_areas = modeler.repair_tools.find_simplify(design.bodies)
    assert len(problem_areas) == 23


def test_fix_simplify(modeler: Modeler):
    """Test to read geometry and find and fix it's unsimplified face problem areas."""
    design = modeler.open_file(FILES_DIR / "SOBracket2_HalfModel.scdocx")
    problem_areas = modeler.repair_tools.find_simplify(design.bodies)
    assert problem_areas[0].fix().success is True


def test_find_and_fix_short_edges(modeler: Modeler):
    """Test to read geometry, find and fix short edges and validate they are fixed removed."""
    design = modeler.open_file(FILES_DIR / "ShortEdges.scdocx")
    assert len(design.bodies[0].edges) == 685
    modeler.repair_tools.find_and_fix_short_edges(design.bodies, 0.000127)
    assert len(design.bodies[0].edges) == 673  ##We get 673 edges if we repair all in one go


def test_find_and_fix_split_edges(modeler: Modeler):
    """Test to read geometry, find and fix split edges and validate they are fixed removed."""
    design = modeler.open_file(FILES_DIR / "bracket-with-split-edges.scdocx")
    assert len(design.bodies[0].edges) == 158
    modeler.repair_tools.find_and_fix_split_edges(design.bodies, 2.61799, 0.01)
    assert len(design.bodies[0].edges) == 72


def test_find_and_fix_extra_edges(modeler: Modeler):
    """Test to read geometry, find and fix extra edges and validate they are removed."""
    design = modeler.open_file(FILES_DIR / "ExtraEdges_NoComponents.scdocx")
    assert len(design.bodies) == 3
    starting_edge_count = 0
    for body in design.bodies:
        starting_edge_count += len(body.edges)
    assert starting_edge_count == 69
    modeler.repair_tools.find_and_fix_extra_edges(design.bodies)
    final_edge_count = 0
    for body in design.bodies:
        final_edge_count += len(body.edges)
    assert final_edge_count == 36


def test_inspect_geometry(modeler: Modeler):
    """Test the result of the inspect geometry query and the ability to repair one issue"""
    modeler.open_file(FILES_DIR / "InspectAndRepair01.scdocx")
    inspect_results = modeler.repair_tools.inspect_geometry()
    assert len(inspect_results) == 1
    issues = len(inspect_results[0].issues)
    assert issues == 7
    result_to_repair = inspect_results[0]
    result_to_repair.repair()
    # Reinspect the geometry
    inspect_results = modeler.repair_tools.inspect_geometry()
    # All issues should have been fixed
    assert len(inspect_results) == 0


def test_repair_geometry(modeler: Modeler):
    """Test the ability to repair a geometry. Inspect geometry is called behind the scenes"""
    modeler.open_file(FILES_DIR / "InspectAndRepair01.scdocx")
    modeler.repair_tools.repair_geometry()
    # Reinspect the geometry
    inspect_results = modeler.repair_tools.inspect_geometry()
    # All issues should have been fixed
    assert len(inspect_results) == 0


def test_find_and_fix_short_edges_comprehensive(modeler: Modeler):
    """Test to read geometry, find and fix short edges and validate they are fixed removed."""
    design = modeler.open_file(FILES_DIR / "ShortEdges.scdocx")
    assert len(design.bodies[0].edges) == 685
    result = modeler.repair_tools.find_and_fix_short_edges(design.bodies, 0.000127, True)
    assert len(design.bodies[0].edges) == 675  ##We get 673 edges if we repair all in one go
    assert result.found == 8
    assert result.repaired == 8


def test_find_and_fix_split_edges_comprehensive(modeler: Modeler):
    """Test to read geometry, find and fix split edges and validate they are fixed removed."""
    design = modeler.open_file(FILES_DIR / "bracket-with-split-edges.scdocx")
    assert len(design.bodies[0].edges) == 158
    result = modeler.repair_tools.find_and_fix_split_edges(design.bodies, 2.61799, 0.01, True)
    assert len(design.bodies[0].edges) == 99
    assert result.found == 59
    assert result.repaired == 59


def test_find_and_fix_extra_edges_comprehensive(modeler: Modeler):
    """Test to read geometry, find and fix extra edges and validate they are removed."""
    design = modeler.open_file(FILES_DIR / "ExtraEdges_NoComponents.scdocx")
    assert len(design.bodies) == 3
    starting_edge_count = 0
    for body in design.bodies:
        starting_edge_count += len(body.edges)
    assert starting_edge_count == 69
    result = modeler.repair_tools.find_and_fix_extra_edges(design.bodies, True)
    assert result.found == 6
    assert result.repaired == 6
    final_edge_count = 0
    for body in design.bodies:
        final_edge_count += len(body.edges)
    assert final_edge_count == 36
    assert len(result.modified_bodies) == 3


def test_find_and_fix_simplify(modeler: Modeler):
    """Test to read geometry and find and fix spline faces"""
    design = modeler.open_file(FILES_DIR / "SOBracket2_HalfModel.scdocx")
    result = modeler.repair_tools.find_and_fix_simplify(design.bodies, True)
    assert result
    assert result.found == 23
    assert result.repaired == 23  # There is a SC bug where success is always true
