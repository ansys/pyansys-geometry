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

import re

import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core._grpc._version import GeometryApiProtos
from ansys.geometry.core.connection.backend import ApiVersions, BackendType
from ansys.geometry.core.errors import GeometryRuntimeError
from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.sketch import Sketch

from .conftest import DSCOSCRIPTS_FILES_DIR


# Python (.py)
@pytest.mark.skip(reason="New failure to be investigated.")
def test_python_simple_script(modeler: Modeler):
    result, _ = modeler.run_discovery_script_file(DSCOSCRIPTS_FILES_DIR / "simple_script.py")
    pattern_db = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.DesignBody", re.IGNORECASE)
    pattern_doc = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.Document", re.IGNORECASE)
    assert len(result) == 2
    assert pattern_db.match(result["design_body"])
    assert pattern_doc.match(result["design"])


@pytest.mark.skip(reason="New failure to be investigated.")
def test_python_simple_script_ignore_api_version(
    modeler: Modeler, caplog: pytest.LogCaptureFixture
):
    result, _ = modeler.run_discovery_script_file(
        DSCOSCRIPTS_FILES_DIR / "simple_script.py",
        api_version=ApiVersions.LATEST,
    )
    pattern_db = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.DesignBody", re.IGNORECASE)
    pattern_doc = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.Document", re.IGNORECASE)
    assert len(result) == 2
    assert pattern_db.match(result["design_body"])
    assert pattern_doc.match(result["design"])

    # Check the logger to see the warning
    assert (
        "The Ansys Geometry Service only supports scripts that are of its same API version."
        in caplog.messages[0]
    )
    assert "Ignoring specified API version." in caplog.messages[1]


def test_python_failing_script(modeler: Modeler):
    if modeler.client.backend_type == BackendType.CORE_LINUX:
        pytest.skip(reason="Skipping test_python_failing_script. Operation fails on github.")
    if modeler.client.services.version != GeometryApiProtos.V0:
        modeler.create_design("test_design")
    with pytest.raises(GeometryRuntimeError):
        modeler.run_discovery_script_file(DSCOSCRIPTS_FILES_DIR / "failing_script.py")


def test_python_integrated_script(modeler: Modeler):
    # Tests the workflow of creating a design in PyAnsys Geometry, modifying it with a script,
    # and continuing to use it in PyAnsys Geometry

    # Waiting for some more well thought system to tag tests against a backend, we skip this one
    # when the backend is Discovery
    if modeler.client.backend_type in (BackendType.DISCOVERY, BackendType.WINDOWS_SERVICE):
        return

    design = modeler.create_design("Integrated_Example")
    design.extrude_sketch("Box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    values, design = modeler.run_discovery_script_file(
        DSCOSCRIPTS_FILES_DIR / "integrated_script.py", {"radius": "1"}, True
    )
    # Script creates a 2nd body
    assert len(design.bodies) == 2
    assert int(values["numBodies"]) == 2


# SpaceClaim (.scscript)
def test_scscript_simple_script(modeler: Modeler):
    # Testing running a simple scscript file
    result, _ = modeler.run_discovery_script_file(DSCOSCRIPTS_FILES_DIR / "simple_script.scscript")
    assert len(result) == 2
    pattern_db = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.DesignBody", re.IGNORECASE)
    pattern_doc = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.Document", re.IGNORECASE)
    assert len(result) == 2
    assert pattern_db.match(result["design_body"])
    assert pattern_doc.match(result["design"])


# Discovery (.dscript)
def test_dscript_simple_script(modeler: Modeler):
    # Testing running a simple dscript file
    result, _ = modeler.run_discovery_script_file(DSCOSCRIPTS_FILES_DIR / "simple_script.dscript")
    assert len(result) == 2
    pattern_db = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.DesignBody", re.IGNORECASE)
    pattern_doc = re.compile(r"SpaceClaim\.Api\.[A-Za-z0-9]+\.Document", re.IGNORECASE)
    assert len(result) == 2
    assert pattern_db.match(result["design_body"])
    assert pattern_doc.match(result["design"])
