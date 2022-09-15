"""
Perform a connection validation check. This method is only used for testing the
default docker service on GitHub and can safely be skipped within testing.

Typical use:

.. code:: python

   python -c "from ansys.geometry.core.connection import validate; validate()"

"""
from ansys.geometry.core.connection.client import GrpcClient


def validate():  # pragma: no cover
    """Create a client using the default settings and it."""
    print(GrpcClient())
    # TODO: consider adding additional server stat reporting
