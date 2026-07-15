Added ``Design.export_to_usd()`` to export design tessellation to a USD file
(Universal Scene Description). The export preserves the full component/body
hierarchy, triangulated mesh geometry, and per-body color as a
``UsdPreviewSurface`` material. Supports ``.usda`` (ASCII), ``.usdc`` (binary),
``.usdz`` (zip archive), and ``.usd`` (auto) formats.
Requires the new optional dependency: ``pip install ansys-geometry-core[usd]``.
