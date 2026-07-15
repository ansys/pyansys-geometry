# Tessellation → USD Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `Design.export_to_usd()` that tessellates all bodies in a design and writes them to a USD file with the full component/body hierarchy, triangulated mesh geometry, and per-body `UsdPreviewSurface` color/material.

**Architecture:** A new `plotting/usd_export.py` module contains all USD logic — the `usd_required` decorator, name sanitization helpers, tessellation-to-mesh conversion, and the main `export_design_to_usd()` function. `Design.export_to_usd()` in `design.py` is a thin wrapper that validates inputs, builds the output path via the existing `__build_export_file_location()` helper, and delegates to `export_design_to_usd()`. `usd-core` is a new optional dependency group `[usd]`; all pxr imports are lazy (inside functions) so the module loads without `usd-core` installed.

**Tech Stack:** Python 3.12+, `usd-core>=24.0` (OpenUSD/Pixar), `matplotlib` (already a dependency — used for hex-color parsing), `numpy` (already a dependency — used for vertex reshape).

## Global Constraints

- Python `>=3.12,<4`
- `usd-core>=24.0` — optional dep only; users install with `pip install ansys-geometry-core[usd]`
- All `pxr.*` imports must be **lazy** (inside function bodies), never at module top-level
- MIT license header required on every new source file (copy from any existing file)
- NumPy docstring convention (ruff `D` rules, `pydocstyle.convention = "numpy"`)
- Line length: 100 characters (ruff config)
- Test files: pytest style, skip USD tests with `pytest.importorskip("pxr")` if `usd-core` not installed
- `body.get_raw_tessellation()` returns `dict[str, dict]`; each value has `"vertices"` (flat `list[float]`), `"faces"` (VTK connectivity `[3, i, j, k, ...]`), `"is_edge"` (bool)
- `body.color` returns a hex string `#RRGGBBAA`; `body.opacity` returns `float` 0–1
- `Design.__build_export_file_location(location, ext)` returns `Path(location) / f"{self.name}.{ext}"`, or `Path.cwd() / f"{self.name}.{ext}"` if location is `None`; `location` should be a directory or `None`

---

### Task 1: `usd-core` optional dependency and `usd_required` decorator

**Files:**
- Modify: `pyproject.toml`
- Create: `src/ansys/geometry/core/plotting/usd_export.py`
- Create: `tests/test_usd_export.py`

**Interfaces:**
- Produces:
  - `_USD_AVAILABLE: bool | None` — module-level cache flag
  - `run_if_usd_required() -> None` — raises `ImportError` if `usd-core` not installed
  - `usd_required(method) -> Callable` — decorator calling `run_if_usd_required()`

---

- [ ] **Step 1: Write the failing tests**

Create `tests/test_usd_export.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/test_usd_export.py -v
```
Expected: `ModuleNotFoundError` or `ImportError` — `usd_export` module does not exist yet.

- [ ] **Step 3: Add `usd-core` to `pyproject.toml`**

In `pyproject.toml`, add after `optional-dependencies.graphics`:

```toml
optional-dependencies.usd = [
  "usd-core>=24.0",
]
```

Also add `"usd-core>=24.0"` to `optional-dependencies.all`.

- [ ] **Step 4: Create `src/ansys/geometry/core/plotting/usd_export.py`**

```python
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

"""Provides USD export utilities for PyAnsys Geometry."""

import functools
import re
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.colors as mcolors

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.component import Component
    from ansys.geometry.core.designer.design import Design
    from ansys.geometry.core.misc.options import TessellationOptions

_USD_AVAILABLE: bool | None = None
"""Cached availability flag for usd-core. ``None`` means not yet checked."""

_ERROR_USD_REQUIRED = (
    "The 'usd-core' package is required for USD export. "
    "Install it with: pip install ansys-geometry-core[usd]"
)

_VALID_USD_FORMATS = ("usda", "usdc", "usdz", "usd")


def run_if_usd_required() -> None:
    """Check that usd-core is installed, raising ImportError if not."""
    global _USD_AVAILABLE
    if _USD_AVAILABLE is None:
        try:
            from pxr import Usd  # noqa: F401

            _USD_AVAILABLE = True
        except (ModuleNotFoundError, ImportError):
            _USD_AVAILABLE = False

    if _USD_AVAILABLE is False:
        raise ImportError(_ERROR_USD_REQUIRED)


def usd_required(method):
    """Decorate a method as requiring usd-core.

    Parameters
    ----------
    method : callable
        Method to decorate.

    Returns
    -------
    callable
        Decorated method that raises ``ImportError`` if ``usd-core`` is not installed.
    """

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        run_if_usd_required()
        return method(*args, **kwargs)

    return wrapper
```

- [ ] **Step 5: Run tests to verify they pass**

```
pytest tests/test_usd_export.py -v
```
Expected: All 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/ansys/geometry/core/plotting/usd_export.py tests/test_usd_export.py
git commit -m "feat: add usd-core optional dependency and usd_required decorator

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: USD prim name sanitization utilities

**Files:**
- Modify: `src/ansys/geometry/core/plotting/usd_export.py`
- Modify: `tests/test_usd_export.py`

**Interfaces:**
- Produces:
  - `sanitize_usd_name(name: str) -> str` — valid USD prim name from any string
  - `unique_name(name: str, existing: set[str]) -> str` — de-duplicated name

---

- [ ] **Step 1: Write failing tests**

Append to `tests/test_usd_export.py`:

```python
from ansys.geometry.core.plotting.usd_export import sanitize_usd_name, unique_name


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
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_usd_export.py::test_sanitize_spaces -v
```
Expected: `ImportError` — `sanitize_usd_name` not yet defined.

- [ ] **Step 3: Add sanitization functions to `usd_export.py`**

Add after the `_VALID_USD_FORMATS` line in `usd_export.py`:

```python
def sanitize_usd_name(name: str) -> str:
    """Convert an arbitrary string to a valid USD prim name.

    USD prim names must match ``[A-Za-z_][A-Za-z0-9_]*``.

    Parameters
    ----------
    name : str
        Input name (e.g. body or component name from the service).

    Returns
    -------
    str
        A valid USD prim name.
    """
    if not name:
        return "_unnamed"
    sanitized = re.sub(r"[^A-Za-z0-9_]", "_", name)
    if sanitized[0].isdigit():
        sanitized = "_" + sanitized
    return sanitized


def unique_name(name: str, existing: set) -> str:
    """Return ``name`` or a de-duplicated variant if it already exists in ``existing``.

    Parameters
    ----------
    name : str
        Desired prim name.
    existing : set[str]
        Names already in use within the current USD prim scope.

    Returns
    -------
    str
        ``name`` if no collision, otherwise ``name_1``, ``name_2``, etc.
    """
    if name not in existing:
        return name
    counter = 1
    while f"{name}_{counter}" in existing:
        counter += 1
    return f"{name}_{counter}"
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_usd_export.py -v
```
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/ansys/geometry/core/plotting/usd_export.py tests/test_usd_export.py
git commit -m "feat: add USD prim name sanitization utilities

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 3: Raw tessellation → USD mesh data conversion

**Files:**
- Modify: `src/ansys/geometry/core/plotting/usd_export.py`
- Modify: `tests/test_usd_export.py`

**Interfaces:**
- Consumes: raw tessellation dict shape:
  ```python
  {
      "face_id": {
          "vertices": [x0, y0, z0, x1, y1, z1, ...],  # flat float list
          "faces": [3, i, j, k, 3, i, j, k, ...],      # VTK connectivity (all triangles)
          "is_edge": False,
      }
  }
  ```
- Produces:
  - `raw_tess_to_usd_mesh_data(raw_tess: dict) -> tuple[list[tuple[float,float,float]], list[int], list[int]]`
    Returns `(points, face_vertex_counts, face_vertex_indices)` ready for `UsdGeom.Mesh`.

---

- [ ] **Step 1: Write failing tests**

Append to `tests/test_usd_export.py`:

```python
from ansys.geometry.core.plotting.usd_export import raw_tess_to_usd_mesh_data


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
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_usd_export.py::test_raw_tess_single_triangle -v
```
Expected: `ImportError` — `raw_tess_to_usd_mesh_data` not yet defined.

- [ ] **Step 3: Implement `raw_tess_to_usd_mesh_data` in `usd_export.py`**

Add after `unique_name` in `usd_export.py`:

```python
def raw_tess_to_usd_mesh_data(
    raw_tess: dict,
) -> tuple[list[tuple[float, float, float]], list[int], list[int]]:
    """Convert raw tessellation data to USD mesh arrays.

    Parameters
    ----------
    raw_tess : dict
        Raw tessellation as returned by ``Body.get_raw_tessellation()``.
        Keys are face/edge IDs; values are dicts with ``"vertices"`` (flat float list),
        ``"faces"`` (VTK connectivity ``[3, i, j, k, ...]``), and ``"is_edge"`` (bool).

    Returns
    -------
    tuple
        A 3-tuple of ``(points, face_vertex_counts, face_vertex_indices)``:

        - ``points``: list of ``(x, y, z)`` float tuples.
        - ``face_vertex_counts``: list of ints (all 3 for triangulated meshes).
        - ``face_vertex_indices``: flat list of vertex indices.
    """
    all_points: list[tuple[float, float, float]] = []
    all_counts: list[int] = []
    all_indices: list[int] = []

    for entry in raw_tess.values():
        if entry.get("is_edge", False):
            continue

        verts_flat: list[float] = entry.get("vertices") or []
        faces_vtk: list[int] = entry.get("faces") or []

        if not verts_flat or not faces_vtk:
            continue

        vertex_offset = len(all_points)
        pts = [
            (verts_flat[i], verts_flat[i + 1], verts_flat[i + 2])
            for i in range(0, len(verts_flat), 3)
        ]
        all_points.extend(pts)

        # Parse VTK connectivity format: [n_pts, i0, i1, ..., n_pts, i0, i1, ...]
        idx = 0
        while idx < len(faces_vtk):
            n = faces_vtk[idx]
            idx += 1
            face_indices = [faces_vtk[idx + k] + vertex_offset for k in range(n)]
            idx += n
            all_counts.append(n)
            all_indices.extend(face_indices)

    return all_points, all_counts, all_indices
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_usd_export.py -v
```
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/ansys/geometry/core/plotting/usd_export.py tests/test_usd_export.py
git commit -m "feat: add raw tessellation to USD mesh data conversion

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 4: `export_design_to_usd()` and helpers

**Files:**
- Modify: `src/ansys/geometry/core/plotting/usd_export.py`
- Modify: `tests/test_usd_export.py`

**Interfaces:**
- Consumes:
  - `sanitize_usd_name(name: str) -> str`
  - `unique_name(name: str, existing: set[str]) -> str`
  - `raw_tess_to_usd_mesh_data(raw_tess: dict) -> tuple[list, list, list]`
  - `body.get_raw_tessellation(tess_options=None) -> dict`
  - `body.name -> str`, `body.color -> str` (`#RRGGBBAA`), `body.opacity -> float`
  - `component.bodies -> list[Body]`, `component.components -> list[Component]`, `component.name -> str`
  - `component.is_alive -> bool` (skip dead components; bodies are already filtered in `component.bodies`)
  - `design.name -> str`, `design.bodies -> list[Body]`, `design.components -> list[Component]`
- Produces:
  - `_validate_usd_format(file_format: str) -> None` — raises `GeometryRuntimeError` for unknown formats
  - `export_design_to_usd(design, path: Path, tess_options=None) -> None`

---

- [ ] **Step 1: Write failing tests**

Append to `tests/test_usd_export.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_usd_export.py::test_validate_format_invalid -v
```
Expected: `ImportError` — `_validate_usd_format` and `export_design_to_usd` not yet defined.

- [ ] **Step 3: Add `_validate_usd_format` to `usd_export.py`**

Add after `_VALID_USD_FORMATS` definition in `usd_export.py`:

```python
def _validate_usd_format(file_format: str) -> None:
    """Raise ``GeometryRuntimeError`` if ``file_format`` is not a valid USD extension.

    Parameters
    ----------
    file_format : str
        Extension to validate (without the leading dot).
    """
    from ansys.geometry.core.errors import GeometryRuntimeError

    if file_format not in _VALID_USD_FORMATS:
        raise GeometryRuntimeError(
            f"Invalid USD file format '{file_format}'. "
            f"Valid formats: {', '.join(_VALID_USD_FORMATS)}."
        )
```

- [ ] **Step 4: Add `export_design_to_usd`, `_export_component`, and `_export_body` to `usd_export.py`**

Append to the end of `usd_export.py`:

```python
def export_design_to_usd(
    design: "Design",
    path: Path,
    tess_options: "TessellationOptions | None" = None,
) -> None:
    """Export a design's tessellation to a USD stage file.

    Parameters
    ----------
    design : Design
        The design to export.
    path : ~pathlib.Path
        Output file path. Must end with ``.usda``, ``.usdc``, ``.usdz``, or ``.usd``.
    tess_options : TessellationOptions | None, default: None
        Tessellation quality options. ``None`` uses the server default.
    """
    from pxr import Usd, UsdGeom

    stage = Usd.Stage.CreateNew(str(path))
    root_name = sanitize_usd_name(design.name)
    root_prim = UsdGeom.Xform.Define(stage, f"/{root_name}")
    stage.SetDefaultPrim(root_prim.GetPrim())
    root_path = f"/{root_name}"

    # Export bodies directly on the design (root level)
    used_root_names: set[str] = {"Looks"}
    for body in design.bodies:
        body_prim_name = unique_name(sanitize_usd_name(body.name), used_root_names)
        used_root_names.add(body_prim_name)
        _export_body(stage, root_path, body, tess_options, body_prim_name)

    # Export sub-components
    for component in design.components:
        if not component.is_alive:
            continue
        comp_prim_name = unique_name(sanitize_usd_name(component.name), used_root_names)
        used_root_names.add(comp_prim_name)
        _export_component(stage, root_path, component, tess_options, comp_prim_name)

    stage.GetRootLayer().Save()


def _export_component(
    stage,
    parent_path: str,
    component: "Component",
    tess_options: "TessellationOptions | None",
    prim_name: str,
) -> None:
    """Recursively export a component and all its children to the USD stage.

    Parameters
    ----------
    stage : Usd.Stage
        The USD stage to write to.
    parent_path : str
        Absolute USD prim path of the parent.
    component : Component
        The component to export.
    tess_options : TessellationOptions | None
        Tessellation quality options.
    prim_name : str
        Pre-computed sanitized and de-duplicated prim name for this component.
    """
    from pxr import UsdGeom

    comp_path = f"{parent_path}/{prim_name}"
    UsdGeom.Xform.Define(stage, comp_path)

    # Reserve "Looks" so body/sub-component names cannot collide with it
    used_child_names: set[str] = {"Looks"}

    for body in component.bodies:
        body_prim_name = unique_name(sanitize_usd_name(body.name), used_child_names)
        used_child_names.add(body_prim_name)
        _export_body(stage, comp_path, body, tess_options, body_prim_name)

    for sub_comp in component.components:
        if not sub_comp.is_alive:
            continue
        sub_prim_name = unique_name(sanitize_usd_name(sub_comp.name), used_child_names)
        used_child_names.add(sub_prim_name)
        _export_component(stage, comp_path, sub_comp, tess_options, sub_prim_name)


def _export_body(
    stage,
    parent_path: str,
    body: "Body",
    tess_options: "TessellationOptions | None",
    body_prim_name: str,
) -> None:
    """Export a single body as a ``UsdGeom.Mesh`` prim with a ``UsdPreviewSurface`` material.

    Parameters
    ----------
    stage : Usd.Stage
        The USD stage to write to.
    parent_path : str
        Absolute USD prim path of the parent component.
    body : Body
        The body to export.
    tess_options : TessellationOptions | None
        Tessellation quality options.
    body_prim_name : str
        Pre-computed sanitized and de-duplicated prim name for this body.
    """
    from pxr import Gf, Sdf, UsdGeom, UsdShade, Vt

    raw_tess = body.get_raw_tessellation(tess_options=tess_options)
    if not raw_tess:
        return

    points, counts, indices = raw_tess_to_usd_mesh_data(raw_tess)
    if not points:
        return

    mesh_path = f"{parent_path}/{body_prim_name}"
    mesh = UsdGeom.Mesh.Define(stage, mesh_path)
    mesh.GetPointsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*p) for p in points]))
    mesh.GetFaceVertexCountsAttr().Set(counts)
    mesh.GetFaceVertexIndicesAttr().Set(indices)

    # Build UsdPreviewSurface material under a sibling Looks/ scope
    mat_path = f"{parent_path}/Looks/{body_prim_name}_mat"
    material = UsdShade.Material.Define(stage, mat_path)

    shader_path = f"{mat_path}/PBRShader"
    shader = UsdShade.Shader.Define(stage, shader_path)
    shader.CreateIdAttr("UsdPreviewSurface")

    hex_rgb = body.color[:7]  # strip alpha channel
    r, g, b = mcolors.to_rgb(hex_rgb)
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(r, g, b))
    shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(float(body.opacity))

    material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    UsdShade.MaterialBindingAPI(mesh.GetPrim()).Bind(material)
```

- [ ] **Step 5: Run tests to verify they pass**

```
pytest tests/test_usd_export.py -v
```
Expected: All tests PASS (USD-dependent tests are skipped if `usd-core` is not installed).

- [ ] **Step 6: Commit**

```bash
git add src/ansys/geometry/core/plotting/usd_export.py tests/test_usd_export.py
git commit -m "feat: implement export_design_to_usd with hierarchy, geometry, and materials

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 5: `Design.export_to_usd()` public method

**Files:**
- Modify: `src/ansys/geometry/core/designer/design.py`
- Modify: `tests/test_usd_export.py`

**Interfaces:**
- Consumes:
  - `_validate_usd_format(file_format: str) -> None` (from Task 4)
  - `export_design_to_usd(design, path: Path, tess_options=None) -> None` (from Task 4)
  - `usd_required` decorator (from Task 1)
  - `design.__build_export_file_location(location, ext) -> Path` (private — call as `self.__build_export_file_location(location, file_format)` from inside `Design`)
  - `TessellationOptions` (already imported in `design.py` from `ansys.geometry.core.misc.options`)
  - `ensure_design_is_active` (already imported in `design.py`)
- Produces:
  - `Design.export_to_usd(location=None, tess_options=None, file_format="usda") -> Path`

---

- [ ] **Step 1: Write failing test**

Append to `tests/test_usd_export.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_usd_export.py::test_design_has_export_to_usd_method -v
```
Expected: `AssertionError` — `Design` does not yet have `export_to_usd`.

- [ ] **Step 3: Add imports to `design.py`**

In `src/ansys/geometry/core/designer/design.py`, add to the existing import block (after the `misc.checks` imports):

```python
from ansys.geometry.core.plotting.usd_export import (
    _validate_usd_format as _usd_validate_format,
    export_design_to_usd as _export_to_usd_impl,
    usd_required,
)
```

- [ ] **Step 4: Add `export_to_usd` method to the `Design` class in `design.py`**

Add after `export_to_pmdb()` method (search for `def export_to_pmdb` to find the insertion point):

```python
@usd_required
@ensure_design_is_active
def export_to_usd(
    self,
    location: Path | str | None = None,
    tess_options: TessellationOptions | None = None,
    file_format: str = "usda",
) -> Path:
    """Export the design tessellation to a USD file.

    Tessellates all bodies in the design and writes them to a Universal Scene
    Description (USD) file. The export preserves the full component/body hierarchy,
    mesh geometry, and per-body color as a ``UsdPreviewSurface`` material.

    Parameters
    ----------
    location : ~pathlib.Path | str | None, default: None
        Output directory. If ``None``, the file is saved in the current working
        directory using the design name as the filename.
    tess_options : TessellationOptions | None, default: None
        Tessellation quality options. If ``None``, the server default is used.
    file_format : str, default: ``"usda"``
        USD file format. One of:

        - ``"usda"`` — USD ASCII (human-readable)
        - ``"usdc"`` — USD binary crate (compact)
        - ``"usdz"`` — USD zip archive (self-contained)
        - ``"usd"`` — auto-detect (usd-core chooses binary or ASCII)

    Returns
    -------
    ~pathlib.Path
        Path to the saved USD file.

    Raises
    ------
    ImportError
        If ``usd-core`` is not installed.
        Install with: ``pip install ansys-geometry-core[usd]``.
    ~ansys.geometry.core.errors.GeometryRuntimeError
        If ``file_format`` is not one of the valid values.

    Examples
    --------
    Export to USD ASCII in the current directory:

    >>> path = design.export_to_usd()

    Export to binary USD in a specific directory:

    >>> path = design.export_to_usd("output/", file_format="usdc")
    """
    _usd_validate_format(file_format)
    file_location = self.__build_export_file_location(location, file_format)
    _export_to_usd_impl(self, file_location, tess_options)
    return file_location
```

- [ ] **Step 5: Run tests to verify they pass**

```
pytest tests/test_usd_export.py -v
```
Expected: All tests PASS.

- [ ] **Step 6: Run the full unit test suite to confirm no regressions**

```
pytest tests/ -v --ignore=tests/integration -x
```
Expected: All tests PASS. (Note: if `usd-core` is not installed, USD-specific tests will be skipped with `pytest.importorskip`.)

- [ ] **Step 7: Commit**

```bash
git add src/ansys/geometry/core/designer/design.py tests/test_usd_export.py
git commit -m "feat: add Design.export_to_usd() public method

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 6: Linting, changelog, and final verification

**Files:**
- Create: `doc/changelog.d/usd-export.added.md`

---

- [ ] **Step 1: Run pre-commit linting on all changed files**

```
pre-commit run --files src/ansys/geometry/core/plotting/usd_export.py src/ansys/geometry/core/designer/design.py tests/test_usd_export.py pyproject.toml
```
Expected: All checks pass. If ruff reports issues, fix them (typically import ordering or line-length violations) and re-run until clean.

- [ ] **Step 2: Create changelog entry**

Create `doc/changelog.d/usd-export.added.md`:

```markdown
Added ``Design.export_to_usd()`` to export design tessellation to a USD file
(Universal Scene Description). The export preserves the full component/body
hierarchy, triangulated mesh geometry, and per-body color as a
``UsdPreviewSurface`` material. Supports ``.usda`` (ASCII), ``.usdc`` (binary),
``.usdz`` (zip archive), and ``.usd`` (auto) formats.
Requires the new optional dependency: ``pip install ansys-geometry-core[usd]``.
```

- [ ] **Step 3: Run full unit test suite one final time**

```
pytest tests/ -v --ignore=tests/integration
```
Expected: All tests PASS (USD tests skipped if `usd-core` not installed).

- [ ] **Step 4: Commit**

```bash
git add doc/changelog.d/usd-export.added.md
git commit -m "docs: add changelog entry for USD tessellation export feature

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```
