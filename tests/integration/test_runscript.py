# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
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

import re

import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.errors import GeometryRuntimeError
from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.sketch import Sketch


# Python (.py)
def test_python_simple_script(modeler: Modeler, skip_not_on_linux_service):
    result = modeler.run_discovery_script_file(
        "./tests/integration/files/disco_scripts/simple_script.py"
    )
    pattern_db = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.DesignBody", re.IGNORECASE)
    pattern_doc = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.Document", re.IGNORECASE)
    assert len(result) == 2
    assert pattern_db.match(result["design_body"])
    assert pattern_doc.match(result["design"])


def test_python_failing_script(modeler: Modeler, skip_not_on_linux_service):
    with pytest.raises(GeometryRuntimeError):
        modeler.run_discovery_script_file(
            "./tests/integration/files/disco_scripts/failing_script.py"
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
    result = modeler.run_discovery_script_file(
        "./tests/integration/files/disco_scripts/simple_script.scscript"
    )
    assert len(result) == 2
    pattern_db = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.DesignBody", re.IGNORECASE)
    pattern_doc = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.Document", re.IGNORECASE)
    assert len(result) == 2
    assert pattern_db.match(result["design_body"])
    assert pattern_doc.match(result["design"])


# Discovery (.dscript)
def test_dscript_simple_script(modeler: Modeler, skip_not_on_linux_service):
    result = modeler.run_discovery_script_file(
        "./tests/integration/files/disco_scripts/simple_script.dscript"
    )
    assert len(result) == 2
    pattern_db = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.DesignBody", re.IGNORECASE)
    pattern_doc = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.Document", re.IGNORECASE)
    assert len(result) == 2
    assert pattern_db.match(result["design_body"])
    assert pattern_doc.match(result["design"])
