""""Testing of repair tools."""

from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.tools.repair_tools import RepairTools


def test_find_split_edges():
    modeler = Modeler(host="localhost", port=50051)
    design = modeler.open_file(r"C:\\Users\\usoysal\\Downloads\\ExtraEdgesDesignBefore.scdoc")
    rep = RepairTools()
    problem_areas = rep.FindExtraEdges(["0:22"])
    assert len(problem_areas) == 3


def test_find_extra_edges():
    modeler = Modeler(host="localhost", port=50051)
    design = modeler.open_file(r"C:\\Users\\usoysal\\Downloads\\ExtraEdgesDesignBefore.scdoc")
    rep = RepairTools()
    problem_areas = rep.FindExtraEdges(["0:22"])
    assert len(problem_areas) == 1
