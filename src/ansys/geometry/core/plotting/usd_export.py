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
from pathlib import Path
import re
from typing import TYPE_CHECKING

import matplotlib.colors as mcolors

if TYPE_CHECKING:
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.component import Component
    from ansys.geometry.core.designer.design import Design

_USD_AVAILABLE: bool | None = None
"""Cached availability flag for usd-core. ``None`` means not yet checked."""

_VALID_USD_FORMATS: frozenset[str] = frozenset({"usda", "usdc", "usdz", "usd"})
"""Valid USD file format extensions (without leading dot)."""

_ERROR_USD_REQUIRED = (
    "The 'usd-core' package is required for USD export. "
    "Install it with: pip install ansys-geometry-core[usd]"
)


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


def unique_name(name: str, existing: set[str]) -> str:
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


def run_if_usd_required() -> None:
    """Check that usd-core is installed, raising ImportError if not.

    Raises
    ------
    ImportError
        If ``usd-core`` is not installed.
    """
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


def export_design_to_usd(
    design: "Design",
    path: Path,
    tess_options=None,
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

    _validate_usd_format(path.suffix.lstrip("."))
    path.parent.mkdir(parents=True, exist_ok=True)
    stage = Usd.Stage.CreateNew(str(path))
    root_name = sanitize_usd_name(design.name)
    root_prim = UsdGeom.Xform.Define(stage, f"/{root_name}")
    stage.SetDefaultPrim(root_prim.GetPrim())
    root_path = f"/{root_name}"

    used_root_names: set[str] = {"Looks"}
    for body in design.bodies:
        body_prim_name = unique_name(sanitize_usd_name(body.name), used_root_names)
        if _export_body(stage, root_path, body, tess_options, body_prim_name):
            used_root_names.add(body_prim_name)

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
    tess_options,
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

    used_child_names: set[str] = {"Looks"}

    for body in component.bodies:
        body_prim_name = unique_name(sanitize_usd_name(body.name), used_child_names)
        if _export_body(stage, comp_path, body, tess_options, body_prim_name):
            used_child_names.add(body_prim_name)

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
    tess_options,
    body_prim_name: str,
) -> bool:
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

    Returns
    -------
    bool
        ``True`` if a prim was created, ``False`` if the body was skipped
        (empty tessellation).
    """
    from pxr import Gf, Sdf, UsdGeom, UsdShade, Vt

    raw_tess = body.get_raw_tessellation(tess_options=tess_options)
    if not raw_tess:
        return False

    points, counts, indices = raw_tess_to_usd_mesh_data(raw_tess)
    if not points:
        return False

    mesh_path = f"{parent_path}/{body_prim_name}"
    mesh = UsdGeom.Mesh.Define(stage, mesh_path)
    mesh.GetPointsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*p) for p in points]))
    mesh.GetFaceVertexCountsAttr().Set(counts)
    mesh.GetFaceVertexIndicesAttr().Set(indices)

    mat_path = f"{parent_path}/Looks/{body_prim_name}_mat"
    material = UsdShade.Material.Define(stage, mat_path)

    shader_path = f"{mat_path}/PBRShader"
    shader = UsdShade.Shader.Define(stage, shader_path)
    shader.CreateIdAttr("UsdPreviewSurface")

    hex_rgb = body.color[:7]
    r, g, b = mcolors.to_rgb(hex_rgb)
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(r, g, b))
    shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(float(body.opacity))

    material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    UsdShade.MaterialBindingAPI(mesh.GetPrim()).Bind(material)
    return True
