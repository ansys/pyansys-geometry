# Copilot Instructions for PyAnsys Geometry

## Project Purpose & Structure
- PyAnsys Geometry provides a Pythonic gRPC interface to the Ansys GeometryService as well as Discovery and SpaceClaim.
- Core source: src/ansys/geometry/core/
- Tests: tests/ (unit and integration tests)
- Examples: doc/source/examples/
- Documentation: doc/source/

## Installation
- **Install (user)**:
  - pip: `pip install ansys-geometry-core`
  - uv: `uv add ansys-geometry-core`
- **Install (developer)**:
  - pip: `python -m venv .venv && .venv\Scripts\Activate.ps1` then `pip install -e . --group dev`
  - uv (preferred): `uv sync`

## Project Conventions
- **Style:** Follows [PyAnsys Developer's Guide](https://dev.docs.pyansys.com/coding-style/index.html#coding-style); use pre-commit (configuration available on repository), to validate the style
- **Tests:** Use `pytest` style; integration tests in `tests/integration/`
- **Docs:** Sphinx, sources in `doc/source/`
- **Editable install:** `pip install -e . --group dev` or `uv sync`

## Examples & References
- See `doc/source/contributing.rst` for detailed contribution guidelines.
- Notebooks: `doc/source/examples/`
- API reference: https://geometry.docs.pyansys.com/version/stable/api/index.html

## Skills
- For specific coding tasks, please read all files in .github/skills/*** to see if there are any relevant skills that can be applied to the task. If there are, apply them as needed. If not, proceed with the task as normal.