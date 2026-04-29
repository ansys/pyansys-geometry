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
"""Testing of unsupported commands."""

from pathlib import Path

import pytest

from ansys.geometry.core.math import Point2D, Point3D
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.sketch import Sketch

from .conftest import FILES_DIR


def _build_manifest(tmp_path: Path) -> Path:
    """Write a manifest XML with the DLL path resolved to its absolute location.

    Because integration tests run against a local server, the absolute path to
    the DLL (inside the repo's test-files directory) is valid on both the client
    and the server, making this approach machine-agnostic.
    """
    dll_path = (FILES_DIR / "TestRemotePlugin.dll").resolve()
    content = (
        '<?xml version="1.0" encoding="utf-8" ?>\n'
        "<AddIns>\n"
        '\t<AddIn name="TestRemotePlugin"\n'
        '\t       description="TestRemotePlugin for ApiServer Runtime Addins"\n'
        f'\t       assembly="{dll_path}"\n'
        '\t       typename="TestRemotePlugin.RemotePluginAddin"\n'
        '\t       host="SameAppDomain"\n'
        '\t       allowEmbedded="false"/>\n'
        "</AddIns>\n"
    )
    manifest_path = tmp_path / "TestRemotePlugin.xml"
    manifest_path.write_text(content, encoding="utf-8")
    return manifest_path


def test_load_addin_and_run_methods(modeler: Modeler, tmp_path: Path):
    """Test loading an add-in via XML manifest and invoking its methods.

    On the v1 protocol the test:
      1. Generates a manifest with the DLL resolved to its absolute path so the
         test is machine-agnostic (no hardcoded env-var paths).
      2. Loads the add-in from the generated manifest (``load_addin``).
      3. Invokes the no-argument "Health" method and checks the response dict.
      4. Invokes "TestCallingWithArgs" passing a body, a face, and a Point3D.
      5. Invokes "TestCallingWithReturnType" and asserts the returned face count
         equals the number of faces on the extruded box body (6).
    """
    addin_path = "TestRemotePlugin.RemotePluginAddin"

    manifest_path = _build_manifest(tmp_path)
    # 1. Load the add-in from the dynamically generated manifest
    modeler.unsupported.load_addin(manifest_path=manifest_path)

    # 2. Health check - no arguments, no meaningful return value
    health_result = modeler.unsupported.run_addin_method(addin_path, "Health")
    assert isinstance(health_result, dict)
    assert health_result.get("return_value") is None

    # 3. TestCallingWithArgs - body, face, and point arguments; no return value
    design = modeler.create_design("TestAddinMethods")
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 10, 10), 10)
    face = body.faces[0]
    point = Point3D([1, 2, 3])
    args_result = modeler.unsupported.run_addin_method(
        addin_path, "TestCallingWithArgs", arguments=[body, face, point]
    )
    assert isinstance(args_result, dict)
    assert args_result.get("return_value") is None

    # 4. TestCallingWithReturnType - returns the face count of the body
    ret_result = modeler.unsupported.run_addin_method(
        addin_path, "TestCallingWithReturnType", arguments=[body]
    )
    assert isinstance(ret_result, dict)
    assert ret_result.get("return_value") == 6