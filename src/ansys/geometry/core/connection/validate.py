"""
Perform a connection validation check. This method is only used for testing the
default docker service on GitHub.
"""
import os

from ..modeler import Modeler


def validate():
    """Create the modeler using the default settings and print the modeler."""
    modeler = Modeler(
        host=os.environ.get("ANSYS_GEO_HOST", "127.0.0.1"),
        port=os.environ.get("ANSYS_GEO_PORT", 50051),
    )
    print(modeler)
