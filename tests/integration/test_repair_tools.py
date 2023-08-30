import os
import sys
import math
from pathlib import Path
from ansys.geometry.core import *
from ansys.geometry.core.connection import *
from ansys.geometry.core.designer import *
from ansys.geometry.core.errors import *
from ansys.geometry.core.materials import *
from ansys.geometry.core.math import *
from ansys.geometry.core.misc import *
from ansys.geometry.core.misc.units import *
from ansys.geometry.core.plotting import *
from ansys.geometry.core.primitives import *
from ansys.geometry.core.sketch import *
from ansys.geometry.core.tools.repair_tools import RepairTools



def test_find_split_edges():
    modeler = Modeler(host="localhost", port= 50051)
    design=modeler.open_file(r"C:\\Users\\usoysal\\Downloads\\ExtraEdgesDesignBefore.scdoc")
    rep = RepairTools()
    problem_areas = rep.FindExtraEdges(["0:22"])
    assert len(problem_areas) == 3

def test_find_extra_edges():
    modeler = Modeler(host="localhost", port= 50051)
    design=modeler.open_file(r"C:\\Users\\usoysal\\Downloads\\ExtraEdgesDesignBefore.scdoc")
    rep = RepairTools()
    problem_areas = rep.FindExtraEdges(["0:22"])
    assert len(problem_areas) == 1