# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
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

"""Integration tests for USD and HTML export."""

import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.sketch import Sketch

pytest.importorskip("pxr", reason="usd-core not installed")


def _box_design(modeler: Modeler, name: str):
    """Create a simple design with one extruded box body."""
    design = modeler.create_design(name)
    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 10, 10)
    body = design.extrude_sketch("Box", sketch, 10)
    body.color = "red"
    return design


def test_export_to_usd_creates_file(modeler: Modeler, tmp_path):
    """export_to_usd writes a .usda file that exists and is non-empty."""
    design = _box_design(modeler, "UsdExport")
    path = design.export_to_usd(tmp_path)
    assert path.exists()
    assert path.stat().st_size > 0
    assert path.suffix == ".usda"


def test_export_to_usd_binary_format(modeler: Modeler, tmp_path):
    """export_to_usd with file_format='usdc' writes a binary USD file."""
    design = _box_design(modeler, "UsdExportBinary")
    path = design.export_to_usd(tmp_path, file_format="usdc")
    assert path.exists()
    assert path.stat().st_size > 0
    assert path.suffix == ".usdc"



def test_export_to_html_creates_file(modeler: Modeler, tmp_path):
    """export_to_html writes a .html file that exists and is non-empty."""
    pytest.importorskip(
        "ansys.tools.visualization_interface",
        reason="ansys-tools-visualization-interface not installed",
    )
    design = _box_design(modeler, "HtmlExport")
    path = design.export_to_html(tmp_path)
    assert path.exists()
    assert path.stat().st_size > 0
    assert path.suffix == ".html"
