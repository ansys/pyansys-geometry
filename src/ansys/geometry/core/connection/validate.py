"""
Perform a connection validation check.

This method is only used for testing the default Docker service on
GitHub and can safely be skipped within testing.

This command shows how this method is typically used:

.. code:: bash

   python -c "from ansys.geometry.core.connection import validate; validate()"
"""
from ansys.geometry.core.connection.client import GrpcClient


def validate():  # pragma: no cover
    """Create a client using the default settings and validate it."""
    print(GrpcClient())
    # TODO: consider adding additional server stat reporting
