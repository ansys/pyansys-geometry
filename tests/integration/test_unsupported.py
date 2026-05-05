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

import os
from pathlib import Path

import pytest

from ansys.geometry.core import logger
from ansys.geometry.core.math import Point2D, Point3D
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.sketch import Sketch

from .conftest import FILES_DIR

SKIP_ADDIN_LOAD_TESTS_CONDITION = (
    os.getenv("IS_WORKFLOW_RUNNING") is None,
    "Load add-in tests only run on workflow.",
)
"""Only run load add-in tests if running on workflow."""


def _build_manifest(tmp_path: Path, dll_path: str | Path) -> Path:
    """Write a manifest XML embedding the given server-side DLL path.

    Parameters
    ----------
    tmp_path : Path
        Temporary directory provided by pytest.
    dll_path : str | Path
        Path to the DLL *as seen by the server process*.  For a local server
        this is the host absolute path; for a Docker container this is the
        container-internal path (e.g. ``/test-files/TestRemotePlugin.dll``).
    """
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


@pytest.mark.skipif(SKIP_ADDIN_LOAD_TESTS_CONDITION[0], reason=SKIP_ADDIN_LOAD_TESTS_CONDITION[1])
def test_load_addin_and_run_methods(modeler: Modeler, tmp_path: Path):
    """Test loading an add-in via XML manifest and invoking its methods.

    The test:
      1. Resolves the DLL path as seen by the server (container-internal path
         when running against Docker in CI via ``ANSYS_GEOMETRY_TEST_FILES``,
         or the host absolute path for a local server).
      2. Generates a manifest embedding that path and loads the add-in
         (``load_addin``).
      3. Invokes the no-argument "Health" method and checks the response dict.
      4. Invokes "TestCallingWithArgs" passing a body, a face, and a Point3D.
      5. Invokes "TestCallingWithReturnType" and asserts the returned face count
         equals the number of faces on the extruded box body (6).
    """
    # In CI the pipeline copies test files into the container with ``docker cp``
    # and sets ANSYS_GEOMETRY_TEST_FILES to the container-internal destination.
    # For a local server the env var is absent and the host path is used instead.
    container_test_files = os.getenv("ANSYS_GEOMETRY_TEST_FILES")
    if container_test_files is not None:
        dll_path = f"{container_test_files}/TestRemotePlugin.dll"
    else:
        dll_path = str((FILES_DIR / "TestRemotePlugin.dll").resolve())

    logger.warn(f"\n[DEBUG] ANSYS_GEOMETRY_TEST_FILES={container_test_files!r}")
    logger.warn(f"[DEBUG] dll_path sent to server: {dll_path!r}")

    addin_path = "TestRemotePlugin.RemotePluginAddin"

    manifest_path = _build_manifest(tmp_path, dll_path)
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
