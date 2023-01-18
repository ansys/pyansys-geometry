"""Provides for connecting to Geometry service instances."""
from beartype.typing import TYPE_CHECKING, Optional

from ansys.geometry.core.connection.localinstance import LocalDockerInstance
from ansys.geometry.core.logger import LOG as logger
from ansys.geometry.core.misc import check_type

try:
    import ansys.platform.instancemanagement as pypim

    _HAS_PIM = True
except ModuleNotFoundError:  # pragma: no cover
    _HAS_PIM = False

from ansys.geometry.core.connection.client import MAX_MESSAGE_LENGTH

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.modeler import Modeler


def launch_modeler() -> "Modeler":
    """Start the ``Modeler`` for PyGeometry.

    Returns
    -------
    ansys.geometry.core.Modeler
        Pythonic interface for geometry modeling.

    Examples
    --------
    Launch the Ansys Geometry service.

    >>> from ansys.geometry.core import launch_modeler
    >>> modeler = launch_modeler()
    """
    # A local Docker container of the Geometry service or PyPIM is required for
    # this to work. Neither is integrated, but we can consider adding them later.

    # Another alternative is to run Docker locally from this method.

    # Start PyGeometry with PyPIM if the environment is configured for it
    # and a directive on how to launch it was not passed.
    if pypim.is_configured():
        logger.info("Starting Geometry service remotely. The startup configuration is ignored.")
        return launch_remote_modeler()

    # Otherwise, we are in the "local Docker Container" scenario
    if LocalDockerInstance.is_docker_installed():
        logger.info("Starting Geometry service locally from Docker container.")
        # return launch_local_instance()
        pass

    # If we reached this point...
    raise NotImplementedError("Geometry service cannot be initialized.")


def launch_remote_modeler(
    version: Optional[str] = None,
) -> "Modeler":
    """Start the Geometry service remotely using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where PyPIM is configured. PyPIM is the Pythonic
    interface to communicate with the PIM (Product Instance Management)
    API. You can use the
    :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if PyPIM is configured.

    Parameters
    ----------
    version : str, default: None
        Version of the Geometry service to run in the three-digit format.
        For example, "212". If you do not specify the version, the server
        chooses the version.

    Returns
    -------
    ansys.geometry.core.modeler.Modeler
        Instance of the Geometry service.
    """
    from ansys.geometry.core.modeler import Modeler

    check_type(version, (type(None), str))

    if not _HAS_PIM:  # pragma: no cover
        raise ModuleNotFoundError(
            "The package 'ansys-platform-instancemanagement' is required to use this function."
        )

    pim = pypim.connect()
    instance = pim.create_instance(product_name="geometry", product_version=version)
    instance.wait_for_ready()
    channel = instance.build_grpc_channel(
        options=[
            ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
        ]
    )
    return Modeler(channel=channel, remote_instance=instance)
