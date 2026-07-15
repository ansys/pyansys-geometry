# Tessellation → USD Export Feature Design

**Date:** 2026-07-15
**Status:** Approved

---

## 1. Overview

Add `Design.export_to_usd()` to PyAnsys Geometry, allowing users to export the service-provided tessellation of a design to a Universal Scene Description (USD) file. The export preserves the full component/body hierarchy, geometry (triangulated mesh), and per-body color/material.

---

## 2. Scope

- **Level**: `Design` only (matches the existing `export_to_step()`, `export_to_scdocx()`, etc. pattern).
- **USD content**: geometry + body names as prim paths + per-body color/opacity as `UsdPreviewSurface` material.
- **USD library**: `usd-core` (official OpenUSD/Pixar Python bindings) as a new optional dependency.
- **File formats**: `.usda` (default), `.usdc`, `.usdz`, `.usd` — user-selectable via `file_format` parameter.

---

## 3. Architecture

### New Files

| File | Purpose |
|------|---------|
| `src/ansys/geometry/core/plotting/usd_export.py` | All USD conversion logic; `run_if_usd_required()` + `usd_required` decorator |

### Modified Files

| File | Change |
|------|--------|
| `src/ansys/geometry/core/designer/design.py` | Add `export_to_usd()` public method |
| `pyproject.toml` | Add `usd-core>=24.0` to a new `[usd]` optional-dependency group |

---

## 4. Public API

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

    Parameters
    ----------
    location : ~pathlib.Path | str | None, default: None
        Output path. Can be a file path (with or without extension) or a directory.
        If None, the file is saved in the current working directory using the design name.
    tess_options : TessellationOptions | None, default: None
        Tessellation quality options. If None, the server's default quality is used.
    file_format : str, default: "usda"
        USD file format. One of: ``"usda"`` (ASCII), ``"usdc"`` (binary crate),
        ``"usdz"`` (zip archive), ``"usd"`` (auto).

    Returns
    -------
    ~pathlib.Path
        Path to the saved USD file.

    Raises
    ------
    ImportError
        If ``usd-core`` is not installed.
    GeometryRuntimeError
        If ``file_format`` is not one of the valid values.
    """
```

### Usage example

```python
from ansys.geometry.core import Modeler

modeler = Modeler()
design = modeler.open_file("my_model.scdocx")
path = design.export_to_usd("output/my_model.usda")
# or with options:
from ansys.geometry.core.misc.options import TessellationOptions
opts = TessellationOptions(surface_deviation=0.01, angle_deviation=0.5)
path = design.export_to_usd("output/", tess_options=opts, file_format="usdc")
```

---

## 5. Data Flow

```
Design.export_to_usd(location, tess_options, file_format)
  │
  ├─ validate file_format → GeometryRuntimeError if invalid
  ├─ build output path (create parent dirs if missing)
  │
  └─► plotting.usd_export.export_design_to_usd(design, path, tess_options)
        │
        ├─► Usd.Stage.CreateNew(str(path))
        ├─► UsdGeom.Xform.Define(stage, "/<sanitized_design_name>")   # root prim
        ├─► stage.SetDefaultPrim(root_prim)
        │
        ├─► _export_component(stage, parent_prim, component, tess_options)  [recursive]
        │     ├─► UsdGeom.Xform.Define(stage, parent_path + "/" + sanitized_name)
        │     ├─► for body in component.bodies:
        │     │       _export_body(stage, comp_prim, body, tess_options)
        │     └─► for sub_comp in component.components:
        │             _export_component(stage, comp_prim, sub_comp, tess_options)
        │
        ├─► _export_body(stage, parent_prim, body, tess_options)
        │     ├─► body.get_raw_tessellation(tess_options=tess_options)
        │     │     → dict: {face_id: {"vertices": [...], "faces": [...], "is_edge": False}}
        │     ├─► merge all face data → flat points array + faceVertexIndices
        │     ├─► UsdGeom.Mesh.Define(stage, parent_path + "/" + sanitized_name)
        │     ├─► mesh.GetPointsAttr().Set(Vt.Vec3fArray(points))
        │     ├─► mesh.GetFaceVertexCountsAttr().Set([3] * n_faces)
        │     ├─► mesh.GetFaceVertexIndicesAttr().Set(face_indices)
        │     └─► _apply_material(stage, mesh_prim, body.color, body.opacity)
        │
        └─► stage.GetRootLayer().Save()
```

---

## 6. USD Hierarchy

```
/<DesignName>                           # UsdGeom.Xform  (default prim)
  /<ComponentA>                         # UsdGeom.Xform
    /<Body1>                            # UsdGeom.Mesh
    /<Body2>                            # UsdGeom.Mesh
    /<SubComponentB>                    # UsdGeom.Xform
      /<Body3>                          # UsdGeom.Mesh
  /<ComponentC>                         # UsdGeom.Xform
    /<Body4>                            # UsdGeom.Mesh
```

Each `UsdGeom.Mesh` prim has a sibling `Looks/<BodyName>_mat` prim containing the `UsdPreviewSurface` material bound to it.

---

## 7. Material / Color

- Material type: `UsdPreviewSurface` (standard USD preview shader).
- `diffuseColor`: RGB from `body.color` (parsed from hex string via `matplotlib.colors.to_rgb`).
- `opacity`: from `body.opacity` (float 0–1).
- Binding: `UsdShade.MaterialBindingAPI(mesh_prim).Bind(material)`.

---

## 8. Prim Name Sanitization

USD prim names must match `[A-Za-z_][A-Za-z0-9_]*`.

Rules applied in order:
1. Replace any character not in `[A-Za-z0-9_]` with `_`.
2. If the first character is a digit, prepend `_`.
3. If empty after sanitization, use `_unnamed`.
4. Deduplicate within a parent scope by appending `_1`, `_2`, ... on collision.

---

## 9. `usd_required` Decorator

Located in `plotting/usd_export.py`:

```python
_USD_AVAILABLE: bool | None = None

def run_if_usd_required() -> None:
    global _USD_AVAILABLE
    if _USD_AVAILABLE is None:
        try:
            from pxr import Usd  # noqa: F401
            _USD_AVAILABLE = True
        except ImportError:
            _USD_AVAILABLE = False
    if not _USD_AVAILABLE:
        raise ImportError(
            "The 'usd-core' package is required for USD export. "
            "Install it with: pip install usd-core"
        )

def usd_required(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        run_if_usd_required()
        return method(*args, **kwargs)
    return wrapper
```

---

## 10. Error Handling

| Scenario | Behavior |
|----------|----------|
| `usd-core` not installed | `ImportError` with pip install hint |
| Invalid `file_format` | `GeometryRuntimeError` listing valid formats |
| Empty design (no bodies) | USD written with only root Xform prim; no error |
| Body with empty tessellation | Skip body; emit `log.debug` warning |
| Prim name collision | Append `_1`, `_2`, ... suffix |
| Output directory missing | Auto-create (matches existing `export_to_*` behavior) |

---

## 11. Optional Dependency

`pyproject.toml` addition:

```toml
[project.optional-dependencies]
usd = [
  "usd-core>=24.0",
]
```

Users install with:

```bash
pip install ansys-geometry-core[usd]
```

---

## 12. Testing

**File**: `tests/test_usd_export.py`

| Test | Description |
|------|-------------|
| `test_sanitize_name` | Name sanitization rules: spaces, digits, empty, collision |
| `test_export_empty_design` | Design with no bodies → valid USD with root prim only |
| `test_export_single_body` | Verify mesh points, face counts, face indices |
| `test_export_material_color` | Verify `diffuseColor` and `opacity` match body values |
| `test_export_hierarchy` | Component tree → correct prim paths |
| `test_invalid_file_format` | `GeometryRuntimeError` raised for unknown format |
| `test_usd_not_installed` | `ImportError` raised when `usd-core` missing (mock import) |
| `test_all_formats` | `.usda`, `.usdc`, `.usdz`, `.usd` all produce files |

Tests are unit tests using mocked `body.get_raw_tessellation()` data; `usd-core` must be installed in the test environment (or tests are skipped with `pytest.importorskip`).
