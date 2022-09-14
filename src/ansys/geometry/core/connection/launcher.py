"""Module for connecting to geometry service instances."""

from ansys.geometry.core.modeler import Modeler


def launch_modeler() -> Modeler:
    """Start the PyGeometry modeler.

    Returns
    -------
    ansys.geometry.core.Modeler
        Pythonic interface for geometry modeling.

    Examples
    --------
    Launch the ansys geometry service.

    >>> from ansys.geometry.core import launch_modeler
    >>> modeler = launch_modeler()
    """
    # This needs a local installation of the geometry service or PyPIM to
    # work. Neither is integrated, we can consider adding it later.

    # Another alternative is running docker locally from this method.

    raise NotImplementedError("Not yet implemented")
