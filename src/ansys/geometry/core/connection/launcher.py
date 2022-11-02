"""Module for connecting to geometry service instances."""

from beartype import beartype as check_input_types
from beartype.typing import Optional

from ansys.geometry.core import LOG as logger
from ansys.geometry.core.modeler import Modeler

try:
    import ansys.platform.instancemanagement as pypim

    _HAS_PIM = True
except ModuleNotFoundError:  # pragma: no cover
    _HAS_PIM = False

from ansys.geometry.core.connection.client import MAX_MESSAGE_LENGTH


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

    # Start PyGeometry with PyPIM if the environment is configured for it
    # and the user did not pass a directive on how to launch it.
    if pypim.is_configured():
        logger.info(
            "Starting Geometry service remotely. The startup configuration will be ignored."
        )
        return launch_remote_modeler()

    raise NotImplementedError("Not yet implemented.")


@check_input_types
def launch_remote_modeler(
    version: Optional[str] = None,
) -> Modeler:
    """Start the Geometry Service remotely using the product instance management API.
    When calling this method, you need to ensure that you are in an
    environment where PyPIM is configured. This can be verified with
    :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`.

    Parameters
    ----------
    version : str, default: None
        The Geometry Service version to run, in the 3 digits format, such as "212".
        If unspecified, the version will be chosen by the server.

    Returns
    -------
    ansys.geometry.core.modeler.Modeler
        An instance of the Geometry Service.
    """
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
