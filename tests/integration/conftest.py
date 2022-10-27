"""
This testing module automatically connects to the geometry service running at
localhost:50051.

If you wish to override these defaults, set the following environment variables.

- export ANSRV_GEO_HOST=127.0.0.1
- export ANSRV_GEO_PORT=50051

"""
import logging
import os
from pathlib import Path

import pytest
import pyvista as pv

from ansys.geometry.core import Modeler

pv.OFF_SCREEN = True


@pytest.fixture(scope="session")
def modeler():

    # Log to file - accepts str or Path objects, Path is passed for testing/coverage purposes.
    log_file_path = Path(__file__).absolute().parent / "logs" / "integration_tests_logs.txt"

    try:
        os.remove(log_file_path)
    except OSError:
        pass

    modeler = Modeler(logging_level=logging.DEBUG, logging_file=log_file_path)

    yield modeler

    # TODO: check cleanup on exit
    # modeler.exit()
    # assert modeler._client.closed
