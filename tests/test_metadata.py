# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.

from ansys.geometry.core import __version__


def test_pkg_version():
    try:
        import importlib.metadata as importlib_metadata
    except ModuleNotFoundError:  # pragma: no cover
        import importlib_metadata

    # Read from the pyproject.toml
    # major, minor, patch
    read_version = importlib_metadata.version("ansys-geometry-core")

    assert __version__ == read_version
