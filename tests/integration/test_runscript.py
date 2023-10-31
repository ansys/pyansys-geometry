# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.

import re

import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.errors import GeometryRuntimeError
from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.sketch import Sketch


# Python (.py)
def test_python_simple_script(modeler: Modeler, skip_not_on_linux_service):
    args = {}
    result = modeler.run_discovery_script_file(
        "./tests/integration/files/disco_scripts/simple_script.py", args
    )
    pattern_db = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.DesignBody", re.IGNORECASE)
    pattern_doc = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.Document", re.IGNORECASE)
    assert len(result) == 2
    assert pattern_db.match(result["design_body"])
    assert pattern_doc.match(result["design"])


def test_python_failing_script(modeler: Modeler, skip_not_on_linux_service):
    args = {}
    with pytest.raises(GeometryRuntimeError):
        modeler.run_discovery_script_file(
            "./tests/integration/files/disco_scripts/failing_script.py", args
        )


def test_python_integrated_script(modeler: Modeler, skip_not_on_linux_service):
    # Tests the workflow of creating a design in PyAnsys Geometry, modifying it with a script,
    # and continuing to use it in PyAnsys Geometry

    # Waiting for some more well thought system to tag tests against a backend, we skip this one
    # when the backend is Discovery
    if modeler.client.backend_type == BackendType.DISCOVERY:
        return

    design = modeler.create_design("Integrated_Example")
    design.extrude_sketch("Box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    values, design = modeler.run_discovery_script_file(
        "./tests/integration/files/disco_scripts/integrated_script.py", {"radius": "1"}, True
    )
    # Script creates a 2nd body
    assert len(design.bodies) == 2
    assert int(values["numBodies"]) == 2


# SpaceClaim (.scscript)
def test_scscript_simple_script(modeler: Modeler, skip_not_on_linux_service):
    args = {}
    result = modeler.run_discovery_script_file(
        "./tests/integration/files/disco_scripts/simple_script.scscript", args
    )
    assert len(result) == 2
    pattern_db = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.DesignBody", re.IGNORECASE)
    pattern_doc = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.Document", re.IGNORECASE)
    assert len(result) == 2
    assert pattern_db.match(result["design_body"])
    assert pattern_doc.match(result["design"])


# Discovery (.dscript)
def test_dscript_simple_script(modeler: Modeler, skip_not_on_linux_service):
    args = {}
    result = modeler.run_discovery_script_file(
        "./tests/integration/files/disco_scripts/simple_script.dscript", args
    )
    assert len(result) == 2
    pattern_db = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.DesignBody", re.IGNORECASE)
    pattern_doc = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.Document", re.IGNORECASE)
    assert len(result) == 2
    assert pattern_db.match(result["design_body"])
    assert pattern_doc.match(result["design"])
