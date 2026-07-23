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

from unittest.mock import MagicMock, PropertyMock, patch

try:
    from ansys.geometry.core.misc.checks import run_if_graphics_required

    run_if_graphics_required()

    from ansys.geometry.core.errors import GeometryRuntimeError
    from ansys.geometry.core.plotting.usd_export import (
        _validate_usd_format,
        export_design_to_usd,
        raw_tess_to_usd_mesh_data,
        sanitize_usd_name,
        unique_name,
    )

except ImportError:
    import pytest

    pytest.skip(
        "Skipping test_usd_export module due to graphics requirements missing.",
        allow_module_level=True,
    )

import pytest

pxr = pytest.importorskip("pxr", reason="usd-core not installed")
from pxr import Usd, UsdGeom, UsdShade  # noqa: E402


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

# --- Helpers ---


def _make_body(name: str, color: str = "#D6F7D1FF", raw_tess: dict | None = None):
    body = MagicMock()
    body.name = name
    type(body).color = PropertyMock(return_value=color)
    type(body).opacity = PropertyMock(return_value=1.0)
    body.is_alive = True
    body.get_raw_tessellation.return_value = (
        raw_tess
        if raw_tess is not None
        else {
            "face_1": {
                "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
                "faces": [3, 0, 1, 2],
                "is_edge": False,
            }
        }
    )
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


# ============================================================
# Task 5: Design.export_to_usd() method tests
# ============================================================


def test_design_export_to_usd_method_invalid_format():
    """Design.export_to_usd raises GeometryRuntimeError for unknown file_format.

    We test this by calling _validate_usd_format directly (same code path),
    since instantiating a real Design requires a live server.
    """
    from ansys.geometry.core.plotting.usd_export import _validate_usd_format

    with pytest.raises(GeometryRuntimeError, match="xyz"):
        _validate_usd_format("xyz")


def test_design_has_export_to_usd_method():
    """Design class exposes an export_to_usd method."""
    from ansys.geometry.core.designer.design import Design

    assert hasattr(Design, "export_to_usd")
    assert callable(Design.export_to_usd)


def test_export_creates_parent_directory(tmp_path):
    """export_design_to_usd creates missing parent directories automatically."""
    design = _make_design("D")
    out = tmp_path / "nonexistent" / "subdir" / "out.usda"
    export_design_to_usd(design, out)
    assert out.exists()


def test_export_empty_body_does_not_consume_name_slot(tmp_path):
    """A body with empty tessellation does not consume its prim name slot."""
    empty_body = _make_body("Body", raw_tess={})
    real_body = _make_body("Body")  # same name, has real tessellation
    comp = _make_component("C", bodies=[empty_body, real_body])
    design = _make_design("D", components=[comp])
    out = tmp_path / "out.usda"
    export_design_to_usd(design, out)
    stage = Usd.Stage.Open(str(out))
    # real_body should be at /D/C/Body (not /D/C/Body_1) since empty_body was skipped
    assert stage.GetPrimAtPath("/D/C/Body").IsValid()
    assert not stage.GetPrimAtPath("/D/C/Body_1").IsValid()


# ============================================================
# USDZ export tests
# ============================================================


def test_export_creates_usdz(tmp_path):
    """export_design_to_usd with a .usdz path creates a valid usdz archive."""
    design = _make_design("D", bodies=[_make_body("Box")])
    out = tmp_path / "out.usdz"
    export_design_to_usd(design, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_export_usdz_cleans_up_temp_file(tmp_path):
    """Temporary .usdc staging file is removed after successful .usdz packaging."""
    known_tmp = tmp_path / "staging.usdc"
    known_tmp.touch()
    mock_ntf = MagicMock()
    mock_ntf.name = str(known_tmp)

    with (
        patch("tempfile.NamedTemporaryFile", return_value=mock_ntf),
        patch("ansys.geometry.core.plotting.usd_export._write_stage"),
        patch("pxr.UsdUtils.CreateNewUsdzPackage"),
    ):
        export_design_to_usd(_make_design("D"), tmp_path / "out.usdz")

    assert not known_tmp.exists()


def test_export_usdz_cleans_up_on_write_failure(tmp_path):
    """Temporary .usdc staging file is removed even when _write_stage raises."""
    known_tmp = tmp_path / "staging.usdc"
    known_tmp.touch()
    mock_ntf = MagicMock()
    mock_ntf.name = str(known_tmp)

    with (
        patch("tempfile.NamedTemporaryFile", return_value=mock_ntf),
        patch(
            "ansys.geometry.core.plotting.usd_export._write_stage",
            side_effect=RuntimeError("write failed"),
        ),
    ):
        with pytest.raises(RuntimeError, match="write failed"):
            export_design_to_usd(_make_design("D"), tmp_path / "out.usdz")

    assert not known_tmp.exists()


# ============================================================
# Design.export_to_usd() method tests (via __wrapped__ to bypass decorator)
# ============================================================


def test_export_to_usd_method_returns_path(tmp_path):
    """Design.export_to_usd returns the path produced by __build_export_file_location."""
    from ansys.geometry.core.designer.design import Design

    expected = tmp_path / "MyDesign.usda"
    design = _make_design("MyDesign")
    design._Design__build_export_file_location = MagicMock(return_value=expected)

    with patch("ansys.geometry.core.plotting.usd_export.export_design_to_usd"):
        result = Design.export_to_usd.__wrapped__(design, location=tmp_path)

    assert result == expected


def test_export_to_usd_method_delegates_to_impl(tmp_path):
    """Design.export_to_usd calls export_design_to_usd with the correct arguments."""
    from ansys.geometry.core.designer.design import Design

    expected = tmp_path / "D.usda"
    design = _make_design("D")
    design._Design__build_export_file_location = MagicMock(return_value=expected)
    mock_opts = MagicMock()

    with patch("ansys.geometry.core.plotting.usd_export.export_design_to_usd") as mock_impl:
        Design.export_to_usd.__wrapped__(design, location=tmp_path, tess_options=mock_opts)

    mock_impl.assert_called_once_with(design, expected, mock_opts)


def test_export_to_usd_method_invalid_format_raises():
    """Design.export_to_usd raises GeometryRuntimeError for an unsupported format."""
    from ansys.geometry.core.designer.design import Design

    with pytest.raises(GeometryRuntimeError, match="Invalid USD file format"):
        Design.export_to_usd.__wrapped__(_make_design("D"), file_format="obj")


def test_export_to_usd_method_missing_usd_core():
    """Design.export_to_usd raises ImportError when usd-core is not installed."""
    from ansys.geometry.core.designer.design import Design
    import ansys.geometry.core.plotting.usd_export as usd_mod

    original = usd_mod._USD_AVAILABLE
    usd_mod._USD_AVAILABLE = False
    try:
        with pytest.raises(ImportError, match="usd-core"):
            Design.export_to_usd.__wrapped__(_make_design("D"))
    finally:
        usd_mod._USD_AVAILABLE = original


# ============================================================
# Design.export_to_html() method tests (via __wrapped__ to bypass decorator)
# ============================================================


def test_export_to_html_method_calls_export_usd_to_html(tmp_path):
    """Design.export_to_html calls export_usd_to_html with the default wireframe settings."""
    from ansys.geometry.core.designer.design import Design

    expected = tmp_path / "D.html"
    design = _make_design("D")
    design._Design__build_export_file_location = MagicMock(return_value=expected)
    mock_stage = MagicMock()
    mock_viz = MagicMock()
    mock_viz.export_usd_to_html.return_value = expected

    with (
        patch("ansys.geometry.core.plotting.usd_export.run_if_usd_required"),
        patch("ansys.geometry.core.plotting.usd_export._build_stage", return_value=mock_stage),
        patch.dict("sys.modules", {"ansys.tools.visualization_interface": mock_viz}),
    ):
        result = Design.export_to_html.__wrapped__(design, location=tmp_path)

    mock_viz.export_usd_to_html.assert_called_once_with(
        mock_stage,
        expected,
        show_mesh_lines=True,
        line_color="#ffffff",
        line_opacity=0.9,
    )
    assert result == expected


def test_export_to_html_method_custom_kwargs(tmp_path):
    """Design.export_to_html forwards custom wireframe settings to export_usd_to_html."""
    from ansys.geometry.core.designer.design import Design

    expected = tmp_path / "D.html"
    design = _make_design("D")
    design._Design__build_export_file_location = MagicMock(return_value=expected)
    mock_stage = MagicMock()
    mock_viz = MagicMock()

    with (
        patch("ansys.geometry.core.plotting.usd_export.run_if_usd_required"),
        patch("ansys.geometry.core.plotting.usd_export._build_stage", return_value=mock_stage),
        patch.dict("sys.modules", {"ansys.tools.visualization_interface": mock_viz}),
    ):
        Design.export_to_html.__wrapped__(
            design,
            location=tmp_path,
            show_mesh_lines=False,
            line_color="#000000",
            line_opacity=0.5,
        )

    mock_viz.export_usd_to_html.assert_called_once_with(
        mock_stage,
        expected,
        show_mesh_lines=False,
        line_color="#000000",
        line_opacity=0.5,
    )


def test_export_to_html_method_missing_viz_interface():
    """Design.export_to_html raises ImportError with the [html] install hint
    when viz-interface is absent."""
    from ansys.geometry.core.designer.design import Design

    design = _make_design("D")
    mock_stage = MagicMock()

    with (
        patch("ansys.geometry.core.plotting.usd_export.run_if_usd_required"),
        patch("ansys.geometry.core.plotting.usd_export._build_stage", return_value=mock_stage),
        patch.dict("sys.modules", {"ansys.tools.visualization_interface": None}),
    ):
        with pytest.raises(ImportError, match=r"ansys-geometry-core\[html\]"):
            Design.export_to_html.__wrapped__(design)


def test_export_to_html_method_missing_usd_core():
    """Design.export_to_html raises ImportError when usd-core is not installed."""
    from ansys.geometry.core.designer.design import Design
    import ansys.geometry.core.plotting.usd_export as usd_mod

    original = usd_mod._USD_AVAILABLE
    usd_mod._USD_AVAILABLE = False
    try:
        with pytest.raises(ImportError, match="usd-core"):
            Design.export_to_html.__wrapped__(_make_design("D"))
    finally:
        usd_mod._USD_AVAILABLE = original
