"""
This testing module automatically connects to the geometry service running at
localhost:50051.

If you wish to override these defaults, set the following environment variables.

- export ANSRV_GEO_HOST=127.0.0.1
- export ANSRV_GEO_PORT=50051

"""
import pytest
import pyvista as pv

from ansys.geometry.core import Modeler

pv.OFF_SCREEN = True


@pytest.fixture(scope="session")
def modeler():
    modeler = Modeler()
    yield modeler

    # TODO: check cleanup on exit
    # modeler.exit()
    # assert modeler._client.closed
