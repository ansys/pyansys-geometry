"""``Design`` class module."""

from ansys.geometry.core.design_assembly.assembly import Assembly


class Design:
    """
    Provides Design class for organizing 3D geometry design projects.

    Synchronizes to a server.

    Parameters
    ----------
    id : str
        An identifier defined by the source geometry service.

    """

    def __init__(self, id: str):
        """Constructor method for ``Design``."""

        self._id = id
        self._assembly = Assembly()
