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

"""Tests for the USD export module."""

import pytest

from ansys.geometry.core.plotting.usd_export import (
    raw_tess_to_usd_mesh_data,
    sanitize_usd_name,
    unique_name,
)


def test_usd_required_raises_when_unavailable():
    """run_if_usd_required raises ImportError when usd-core is not available."""
    import ansys.geometry.core.plotting.usd_export as usd_mod

    original = usd_mod._USD_AVAILABLE
    usd_mod._USD_AVAILABLE = False
    try:
        with pytest.raises(ImportError, match="usd-core"):
            usd_mod.run_if_usd_required()
    finally:
        usd_mod._USD_AVAILABLE = original


def test_usd_required_decorator_raises_when_unavailable():
    """@usd_required propagates ImportError when usd-core is not available."""
    import ansys.geometry.core.plotting.usd_export as usd_mod

    @usd_mod.usd_required
    def _dummy():
        return "ok"

    original = usd_mod._USD_AVAILABLE
    usd_mod._USD_AVAILABLE = False
    try:
        with pytest.raises(ImportError, match="usd-core"):
            _dummy()
    finally:
        usd_mod._USD_AVAILABLE = original


def test_usd_required_passes_when_available():
    """run_if_usd_required does not raise when _USD_AVAILABLE is True."""
    import ansys.geometry.core.plotting.usd_export as usd_mod

    original = usd_mod._USD_AVAILABLE
    usd_mod._USD_AVAILABLE = True
    try:
        usd_mod.run_if_usd_required()  # must not raise
    finally:
        usd_mod._USD_AVAILABLE = original


def test_sanitize_spaces():
    assert sanitize_usd_name("my body") == "my_body"


def test_sanitize_special_chars():
    assert sanitize_usd_name("body-1 (main)") == "body_1__main_"


def test_sanitize_digit_prefix():
    assert sanitize_usd_name("1body") == "_1body"


def test_sanitize_empty():
    assert sanitize_usd_name("") == "_unnamed"


def test_sanitize_already_valid():
    assert sanitize_usd_name("ValidName_123") == "ValidName_123"


def test_unique_name_no_collision():
    assert unique_name("body", set()) == "body"


def test_unique_name_single_collision():
    assert unique_name("body", {"body"}) == "body_1"


def test_unique_name_multiple_collisions():
    assert unique_name("body", {"body", "body_1", "body_2"}) == "body_3"


def test_raw_tess_single_triangle():
    """Single face tessellation with one triangle."""
    raw_tess = {
        "face_1": {
            "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            "faces": [3, 0, 1, 2],
            "is_edge": False,
        }
    }
    points, counts, indices = raw_tess_to_usd_mesh_data(raw_tess)
    assert points == [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
    assert counts == [3]
    assert indices == [0, 1, 2]


def test_raw_tess_two_faces_index_offset():
    """Two face tessellations are merged with correct vertex index offsets."""
    raw_tess = {
        "face_1": {
            "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            "faces": [3, 0, 1, 2],
            "is_edge": False,
        },
        "face_2": {
            "vertices": [2.0, 0.0, 0.0, 3.0, 0.0, 0.0, 2.0, 1.0, 0.0],
            "faces": [3, 0, 1, 2],
            "is_edge": False,
        },
    }
    points, counts, indices = raw_tess_to_usd_mesh_data(raw_tess)
    assert len(points) == 6
    assert counts == [3, 3]
    assert indices == [0, 1, 2, 3, 4, 5]  # face_2 indices offset by 3


def test_raw_tess_empty_dict():
    """Empty raw tessellation returns empty lists."""
    points, counts, indices = raw_tess_to_usd_mesh_data({})
    assert points == []
    assert counts == []
    assert indices == []


def test_raw_tess_skips_edges():
    """Edge entries (is_edge=True) are ignored."""
    raw_tess = {
        "edge_1": {
            "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            "faces": [],
            "is_edge": True,
        },
        "face_1": {
            "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            "faces": [3, 0, 1, 2],
            "is_edge": False,
        },
    }
    points, counts, indices = raw_tess_to_usd_mesh_data(raw_tess)
    assert len(points) == 3
    assert counts == [3]
    assert indices == [0, 1, 2]


def test_raw_tess_skips_empty_entry():
    """Face entries with no vertices/faces are skipped."""
    raw_tess = {
        "face_1": {"vertices": [], "faces": [], "is_edge": False},
        "face_2": {
            "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            "faces": [3, 0, 1, 2],
            "is_edge": False,
        },
    }
    points, counts, indices = raw_tess_to_usd_mesh_data(raw_tess)
    assert len(points) == 3


# ============================================================
# Task 4: _validate_usd_format and export_design_to_usd tests
# ============================================================

from pathlib import Path
from unittest.mock import MagicMock, PropertyMock

from ansys.geometry.core.errors import GeometryRuntimeError

pxr = pytest.importorskip("pxr", reason="usd-core not installed")
from pxr import Usd, UsdGeom, UsdShade  # noqa: E402

from ansys.geometry.core.plotting.usd_export import (  # noqa: E402
    _validate_usd_format,
    export_design_to_usd,
)


# --- Helpers ---


def _make_body(name: str, color: str = "#D6F7D1FF", raw_tess: dict | None = None):
    body = MagicMock()
    body.name = name
    type(body).color = PropertyMock(return_value=color)
    type(body).opacity = PropertyMock(return_value=1.0)
    body.is_alive = True
    body.get_raw_tessellation.return_value = raw_tess if raw_tess is not None else {
        "face_1": {
            "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            "faces": [3, 0, 1, 2],
            "is_edge": False,
        }
    }
    return body


def _make_component(name: str, bodies=None, sub_components=None):
    comp = MagicMock()
    comp.name = name
    comp.bodies = bodies or []
    comp.components = sub_components or []
    comp.is_alive = True
    return comp


def _make_design(name: str, bodies=None, components=None):
    design = MagicMock()
    design.name = name
    design.bodies = bodies or []
    design.components = components or []
    return design


# --- _validate_usd_format ---


def test_validate_format_invalid():
    with pytest.raises(GeometryRuntimeError, match="xyz"):
        _validate_usd_format("xyz")


def test_validate_format_all_valid():
    for fmt in ("usda", "usdc", "usdz", "usd"):
        _validate_usd_format(fmt)  # must not raise


# --- export_design_to_usd ---


def test_export_creates_file(tmp_path):
    design = _make_design("TestDesign")
    out = tmp_path / "out.usda"
    export_design_to_usd(design, out)
    assert out.exists()


def test_export_root_prim_name(tmp_path):
    design = _make_design("My Design")
    out = tmp_path / "out.usda"
    export_design_to_usd(design, out)
    stage = Usd.Stage.Open(str(out))
    assert stage.GetDefaultPrim().GetName() == "My_Design"


def test_export_body_creates_mesh_prim(tmp_path):
    body = _make_body("Cube")
    comp = _make_component("CompA", bodies=[body])
    design = _make_design("D", components=[comp])
    out = tmp_path / "out.usda"
    export_design_to_usd(design, out)
    stage = Usd.Stage.Open(str(out))
    prim = stage.GetPrimAtPath("/D/CompA/Cube")
    assert prim.IsValid()
    assert UsdGeom.Mesh(prim)


def test_export_body_mesh_geometry(tmp_path):
    """Mesh prim has correct points, face counts, and indices."""
    body = _make_body("Tri")
    comp = _make_component("C", bodies=[body])
    design = _make_design("D", components=[comp])
    out = tmp_path / "out.usda"
    export_design_to_usd(design, out)
    stage = Usd.Stage.Open(str(out))
    mesh = UsdGeom.Mesh(stage.GetPrimAtPath("/D/C/Tri"))
    assert len(mesh.GetPointsAttr().Get()) == 3
    assert list(mesh.GetFaceVertexCountsAttr().Get()) == [3]
    assert list(mesh.GetFaceVertexIndicesAttr().Get()) == [0, 1, 2]


def test_export_body_material_diffuse_color(tmp_path):
    """Material diffuseColor matches the body's color (without alpha)."""
    body = _make_body("Box", color="#FF8000FF")  # orange
    comp = _make_component("C", bodies=[body])
    design = _make_design("D", components=[comp])
    out = tmp_path / "out.usda"
    export_design_to_usd(design, out)
    stage = Usd.Stage.Open(str(out))
    shader_prim = stage.GetPrimAtPath("/D/C/Looks/Box_mat/PBRShader")
    assert shader_prim.IsValid()
    shader = UsdShade.Shader(shader_prim)
    diffuse = shader.GetInput("diffuseColor").Get()
    import matplotlib.colors as mcolors
    expected = mcolors.to_rgb("#FF8000")
    assert abs(diffuse[0] - expected[0]) < 0.01
    assert abs(diffuse[1] - expected[1]) < 0.01
    assert abs(diffuse[2] - expected[2]) < 0.01


def test_export_mesh_bound_to_material(tmp_path):
    """UsdGeom.Mesh prim is bound to its material."""
    body = _make_body("Box")
    comp = _make_component("C", bodies=[body])
    design = _make_design("D", components=[comp])
    out = tmp_path / "out.usda"
    export_design_to_usd(design, out)
    stage = Usd.Stage.Open(str(out))
    mesh_prim = stage.GetPrimAtPath("/D/C/Box")
    binding_api = UsdShade.MaterialBindingAPI(mesh_prim)
    bound_mat, _ = binding_api.ComputeBoundMaterial()
    assert bound_mat.GetPrim().IsValid()


def test_export_nested_hierarchy(tmp_path):
    """Nested components produce nested Xform prims."""
    inner_body = _make_body("Inner")
    inner_comp = _make_component("InnerComp", bodies=[inner_body])
    outer_comp = _make_component("OuterComp", sub_components=[inner_comp])
    design = _make_design("D", components=[outer_comp])
    out = tmp_path / "out.usda"
    export_design_to_usd(design, out)
    stage = Usd.Stage.Open(str(out))
    assert stage.GetPrimAtPath("/D/OuterComp").IsValid()
    assert stage.GetPrimAtPath("/D/OuterComp/InnerComp").IsValid()
    assert stage.GetPrimAtPath("/D/OuterComp/InnerComp/Inner").IsValid()


def test_export_empty_tessellation_body_skipped(tmp_path):
    """Body with empty tessellation dict is skipped silently."""
    body = _make_body("Empty", raw_tess={})
    comp = _make_component("C", bodies=[body])
    design = _make_design("D", components=[comp])
    out = tmp_path / "out.usda"
    export_design_to_usd(design, out)
    stage = Usd.Stage.Open(str(out))
    assert not stage.GetPrimAtPath("/D/C/Empty").IsValid()


def test_export_empty_design(tmp_path):
    """Design with no bodies or components creates file with only the root Xform."""
    design = _make_design("Empty")
    out = tmp_path / "out.usda"
    export_design_to_usd(design, out)
    assert out.exists()
    stage = Usd.Stage.Open(str(out))
    assert stage.GetDefaultPrim().GetName() == "Empty"


def test_export_body_name_collision(tmp_path):
    """Two bodies with the same name in one component get de-duplicated prim names."""
    body1 = _make_body("Body")
    body2 = _make_body("Body")
    comp = _make_component("C", bodies=[body1, body2])
    design = _make_design("D", components=[comp])
    out = tmp_path / "out.usda"
    export_design_to_usd(design, out)
    stage = Usd.Stage.Open(str(out))
    assert stage.GetPrimAtPath("/D/C/Body").IsValid()
    assert stage.GetPrimAtPath("/D/C/Body_1").IsValid()


def test_export_design_level_bodies(tmp_path):
    """Bodies directly on the design (root level) are also exported."""
    body = _make_body("RootBody")
    design = _make_design("D", bodies=[body])
    out = tmp_path / "out.usda"
    export_design_to_usd(design, out)
    stage = Usd.Stage.Open(str(out))
    assert stage.GetPrimAtPath("/D/RootBody").IsValid()

