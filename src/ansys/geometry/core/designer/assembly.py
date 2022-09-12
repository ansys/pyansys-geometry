"""``Assembly`` class module."""


class Assembly:
    """
    Provides Assembly class for building 3D design elements.

    Synchronizes to a server.
    """

    def __init__(self):
        """Constructor method for ``Assembly``."""
        self._design_geometries = (
            []
        )  # DesignGeometry[] maintaining reference to all geometries within the current assembly
