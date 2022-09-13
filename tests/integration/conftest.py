"""
This testing module automatically connects to the geometry service running at
localhost:50051.

If you wish to override these defaults, set the following environment variables.

- export ANSYS_GEO_HOST=127.0.0.1
- export ANSYS_GEO_PORT=50051

"""
import os

import pytest

from ansys.geometry.core import Modeler


@pytest.fixture(scope="session")
def modeler():
    yield Modeler(
        host=os.environ.get("ANSYS_GEO_HOST", "127.0.0.1"),
        port=os.environ.get("ANSYS_GEO_PORT", 50051),
    )

    # TODO: check cleanup on exit
