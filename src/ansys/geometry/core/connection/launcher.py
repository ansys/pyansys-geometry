# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module for connecting to instances of the Geometry service."""

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from ansys.geometry.core.connection.backend import ApiVersions, BackendType
from ansys.geometry.core.connection.client import MAX_MESSAGE_LENGTH
from ansys.geometry.core.connection.defaults import DEFAULT_PIM_CONFIG, DEFAULT_PORT
from ansys.geometry.core.connection.docker_instance import (
    _HAS_DOCKER,
    GeometryContainers,
    LocalDockerInstance,
)
from ansys.geometry.core.connection.product_instance import prepare_and_start_backend
from ansys.geometry.core.logger import LOG
from ansys.geometry.core.misc.checks import check_type, deprecated_argument

try:
    import ansys.platform.instancemanagement as pypim

    _HAS_PIM = True
except ModuleNotFoundError:  # pragma: no cover
    _HAS_PIM = False


if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.modeler import Modeler


def launch_modeler(mode: str = None, **kwargs: dict | None) -> "Modeler":
    """Start the ``Modeler`` interface for PyAnsys Geometry.

    Parameters
    ----------
    mode : str, default: None
        Mode in which to launch the ``Modeler`` service. The default is ``None``,
        in which case the method tries to determine the mode automatically. The
        possible values are:

        * ``"pypim"``: Launches the ``Modeler`` service remotely using the PIM API.
        * ``"docker"``: Launches the ``Modeler`` service locally using Docker.
        * ``"geometry_service"``: Launches the ``Modeler`` service locally using the
          Ansys Geometry Service.
        * ``"spaceclaim"``: Launches the ``Modeler`` service locally using Ansys SpaceClaim.
        * ``"discovery"``: Launches the ``Modeler`` service locally using Ansys Discovery.

    **kwargs : dict, default: None
        Keyword arguments for the launching methods. For allowable keyword arguments, see the
        corresponding methods for each mode:

        * For ``"pypim"`` mode, see the :func:`launch_remote_modeler` method.
        * For ``"docker"`` mode, see the :func:`launch_docker_modeler` method.
        * For ``"geometry_service"`` mode, see the
          :func:`launch_modeler_with_geometry_service` method.
        * For ``"spaceclaim"`` mode, see the :func:`launch_modeler_with_spaceclaim` method.
        * For ``"discovery"`` mode, see the :func:`launch_modeler_with_discovery` method.

    Returns
    -------
    ansys.geometry.core.modeler.Modeler
        Pythonic interface for geometry modeling.

    Examples
    --------
    Launch the Geometry service.

    >>> from ansys.geometry.core import launch_modeler
    >>> modeler = launch_modeler()
    """
    if mode:
        return _launch_with_launchmode(mode, **kwargs)
    else:
        return _launch_with_automatic_detection(**kwargs)


def _launch_with_launchmode(mode: str, **kwargs: dict | None) -> "Modeler":
    """Start the ``Modeler`` interface for PyAnsys Geometry.

    Parameters
    ----------
    mode : str
        Mode in which to launch the ``Modeler`` service. The possible values are:

        * ``"pypim"``: Launches the ``Modeler`` service remotely using the PIM API.
        * ``"docker"``: Launches the ``Modeler`` service locally using Docker.
        * ``"geometry_service"``: Launches the ``Modeler`` service locally using the
          Ansys Geometry Service.
        * ``"spaceclaim"``: Launches the ``Modeler`` service locally using Ansys SpaceClaim.
        * ``"discovery"``: Launches the ``Modeler`` service locally using Ansys Discovery.

    **kwargs : dict, default: None
        Keyword arguments for the launching methods. For allowable keyword arguments, see the
        :func:`launch_remote_modeler` and :func:`launch_docker_modeler` methods. Some of these
        keywords might be unused.

    Returns
    -------
    ansys.geometry.core.modeler.Modeler
        Pythonic interface for geometry modeling.
    """
    # Ensure that the launch mode is a string
    if not isinstance(mode, str):
        raise TypeError("The launch mode must be a string.")

    # Ensure that the launch mode is lowercase
    mode = mode.lower()

    if mode == "pypim":
        return launch_remote_modeler(**kwargs)
    elif mode == "docker":
        return launch_docker_modeler(**kwargs)
    elif mode == "geometry_service":
        return launch_modeler_with_geometry_service(**kwargs)
    elif mode == "spaceclaim":
        return launch_modeler_with_spaceclaim(**kwargs)
    elif mode == "discovery":
        return launch_modeler_with_discovery(**kwargs)
    else:  # pragma: no cover
        raise ValueError(
            f"Invalid launch mode '{mode}'. The valid modes are: "
            "'pypim', 'docker', 'geometry_service', 'spaceclaim', 'discovery'."
        )


def _launch_with_automatic_detection(**kwargs: dict | None) -> "Modeler":
    """Start the ``Modeler`` interface based on automatic detection.

    Parameters
    ----------
    **kwargs : dict, default: None
        Keyword arguments for the launching methods. For allowable keyword arguments, see the
        :func:`launch_remote_modeler` and :func:`launch_docker_modeler` methods. Some of these
        keywords might be unused.

    Returns
    -------
    ansys.geometry.core.modeler.Modeler
        Pythonic interface for geometry modeling.
    """
    # This method is a wrapper for the other launching methods. It is used to
    # determine which method to call based on the environment.
    #
    # The order of the checks is as follows:
    #
    # 1. Check if PyPIM is configured and if the environment is configured for it.
    # 2. Check if Docker is installed and if the environment is configured for it.
    # 3. If you are on a Windows machine:
    #     - check if the Ansys Geometry service is installed.
    #     - check if Ansys SpaceClaim is installed.
    #     - check if Ansys Discovery is installed.

    # 1.Start PyAnsys Geometry with PyPIM if the environment is configured for it
    # and a directive on how to launch it was not passed.
    if _HAS_PIM and pypim.is_configured():
        LOG.info("Starting Geometry service remotely. The startup configuration is ignored.")
        return launch_remote_modeler(**kwargs)

    # Otherwise, we are in the "local Docker Container" scenario
    try:
        if _HAS_DOCKER and LocalDockerInstance.is_docker_installed():
            LOG.info("Starting Geometry service locally from Docker container.")
            return launch_docker_modeler(**kwargs)
    except Exception:
        LOG.warning(
            "The local Docker container could not be started."
            " Trying to start the Geometry service locally."
        )

    # If we are on a Windows machine, we can try to start the Geometry service locally,
    # through various methods: Geometry service, SpaceClaim, Discovery.
    if os.name == "nt":
        try:
            LOG.info("Starting Geometry service locally.")
            return launch_modeler_with_geometry_service(**kwargs)
        except Exception:
            LOG.warning(
                "The Geometry service could not be started locally."
                " Trying to start Ansys SpaceClaim locally."
            )

        try:
            LOG.info("Starting Ansys SpaceClaim with Geometry Service locally.")
            return launch_modeler_with_spaceclaim(**kwargs)
        except Exception:
            LOG.warning(
                "Ansys SpaceClaim could not be started locally."
                " Trying to start Ansys Discovery locally."
            )

        try:
            LOG.info("Starting Ansys Discovery with Geometry Service locally.")
            return launch_modeler_with_discovery(**kwargs)
        except Exception:
            LOG.warning("Ansys Discovery could not be started locally.")

    # If we reached this point...
    raise NotImplementedError("Geometry service cannot be initialized.")


def launch_remote_modeler(
    platform: str = "windows",
    version: str | None = None,
    client_log_level: int = logging.INFO,
    client_log_file: str | None = None,
    **kwargs: dict | None,
) -> "Modeler":
    """Start the Geometry service remotely using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where `PyPIM <https://github.com/ansys/pypim>`_ is
    configured. You can use the
    :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if it is configured.

    Parameters
    ----------
    platform : str, default: None
        **Specific for Ansys Lab**. The platform option for the Geometry service.
        The default is ``"windows"``.
        This parameter is used to specify the operating system on which the
        Geometry service will run. The possible values are:

        * ``"windows"``: The Geometry service runs on a Windows machine.
        * ``"linux"``: The Geometry service runs on a Linux machine.

    version : str, default: None
        Version of the Geometry service to run in the three-digit format.
        For example, "232". If you do not specify the version, the server
        chooses the version.
    client_log_level : int, default: logging.INFO
        Log level for the client. The default is ``logging.INFO``.
    client_log_file : str, default: None
        Path to the log file for the client. The default is ``None``,
        in which case the client logs to the console.
    **kwargs : dict, default: None
        Placeholder to prevent errors when passing additional arguments that
        are not compatible with this method.

    Returns
    -------
    ansys.geometry.core.modeler.Modeler
        Instance of the Geometry service.
    """
    return _launch_pim_instance(
        is_pim_light=False,
        product_name="geometry",
        product_platform=platform,
        product_version=version,
        backend_type=None,
        client_log_level=client_log_level,
        client_log_file=client_log_file,
    )


def launch_docker_modeler(
    port: int = DEFAULT_PORT,
    connect_to_existing_service: bool = True,
    restart_if_existing_service: bool = False,
    name: str | None = None,
    image: GeometryContainers | None = None,
    client_log_level: int = logging.INFO,
    client_log_file: str | None = None,
    **kwargs: dict | None,
) -> "Modeler":
    """Start the Geometry service locally using Docker.

    When calling this method, a Geometry service (as a local Docker container)
    is started. By default, if a container with the Geometry service already exists
    at the given port, it connects to it. Otherwise, it tries to launch its own
    service.

    Parameters
    ----------
    port : int, optional
        Localhost port to deploy the Geometry service on or the
        the ``Modeler`` interface to connect to (if it is already deployed). By default,
        the value is the one for the ``DEFAULT_PORT`` connection parameter.
    connect_to_existing_service : bool, default: True
        Whether the ``Modeler`` interface should connect to a Geometry
        service already deployed at the specified port.
    restart_if_existing_service : bool, default: False
        Whether the Geometry service (which is already running)
        should be restarted when attempting connection.
    name : str, default: None
        Name of the Docker container to deploy. The default is ``None``,
        in which case Docker assigns it a random name.
    image : GeometryContainers, default: None
        The Geometry service Docker image to deploy. The default is ``None``,
        in which case the ``LocalDockerInstance`` class identifies the OS of your
        Docker engine and deploys the latest version of the Geometry service for
        that OS.
    client_log_level : int, default: logging.INFO
        Log level for the client. The default is ``logging.INFO``.
    client_log_file : str, default: None
        Path to the log file for the client. The default is ``None``,
        in which case the client logs to the console.
    **kwargs : dict, default: None
        Placeholder to prevent errors when passing additional arguments that
        are not compatible with this method.

    Returns
    -------
    Modeler
        Instance of the Geometry service.
    """
    from ansys.geometry.core.modeler import Modeler

    if not _HAS_DOCKER:  # pragma: no cover
        raise ModuleNotFoundError("The package 'docker' is required to use this function.")

    # Call the LocalDockerInstance ctor.
    docker_instance = LocalDockerInstance(
        port=port,
        connect_to_existing_service=connect_to_existing_service,
        restart_if_existing_service=restart_if_existing_service,
        name=name,
        image=image,
    )

    # Once the local Docker instance is ready... return the Modeler
    return Modeler(
        host="localhost",
        port=port,
        docker_instance=docker_instance,
        logging_level=client_log_level,
        logging_file=client_log_file,
    )


def launch_modeler_with_discovery_and_pimlight(
    version: str | None = None,
    client_log_level: int = logging.INFO,
    client_log_file: str | None = None,
    **kwargs: dict | None,
) -> "Modeler":
    """Start Ansys Discovery remotely using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where `PyPIM <https://github.com/ansys/pypim>`_ is configured.
    You can use the :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if it is configured.

    Parameters
    ----------
    version : str, default: None
        Version of Discovery to run in the three-digit format.
        For example, "232". If you do not specify the version, the server
        chooses the version.
    client_log_level : int, default: logging.INFO
        Log level for the client. The default is ``logging.INFO``.
    client_log_file : str, default: None
        Path to the log file for the client. The default is ``None``,
        in which case the client logs to the console.
    **kwargs : dict, default: None
        Placeholder to prevent errors when passing additional arguments that
        are not compatible with this method.

    Returns
    -------
    ansys.geometry.core.modeler.Modeler
        Instance of Modeler.
    """
    return _launch_pim_instance(
        is_pim_light=True,
        product_name="discovery",
        product_version=version,
        backend_type=BackendType.DISCOVERY,
        client_log_level=client_log_level,
        client_log_file=client_log_file,
    )


def launch_modeler_with_geometry_service_and_pimlight(
    version: str | None = None,
    client_log_level: int = logging.INFO,
    client_log_file: str | None = None,
    **kwargs: dict | None,
) -> "Modeler":
    """Start the Geometry service remotely using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where `PyPIM <https://github.com/ansys/pypim>`_ is configured.
    You can use the :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if it is configured.

    Parameters
    ----------
    version : str, default: None
        Version of the Geometry service to run in the three-digit format.
        For example, "232". If you do not specify the version, the server
        chooses the version.
    client_log_level : int, default: logging.INFO
        Log level for the client. The default is ``logging.INFO``.
    client_log_file : str, default: None
        Path to the log file for the client. The default is ``None``,
        in which case the client logs to the console.
    **kwargs : dict, default: None
        Placeholder to prevent errors when passing additional arguments that
        are not compatible with this method.

    Returns
    -------
    ansys.geometry.core.modeler.Modeler
        Instance of Modeler.
    """
    return _launch_pim_instance(
        is_pim_light=True,
        product_name="geometryservice",
        product_version=version,
        backend_type=BackendType.WINDOWS_SERVICE,
        client_log_level=client_log_level,
        client_log_file=client_log_file,
    )


def launch_modeler_with_spaceclaim_and_pimlight(
    version: str | None = None,
    client_log_level: int = logging.INFO,
    client_log_file: str | None = None,
    **kwargs: dict | None,
) -> "Modeler":
    """Start Ansys SpaceClaim remotely using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where `PyPIM <https://github.com/ansys/pypim>`_ is configured.
    You can use the :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if it is configured.

    Parameters
    ----------
    version : str, default: None
        Version of SpaceClaim to run in the three-digit format.
        For example, "232". If you do not specify the version, the server
        chooses the version.
    client_log_level : int, default: logging.INFO
        Log level for the client. The default is ``logging.INFO``.
    client_log_file : str, default: None
        Path to the log file for the client. The default is ``None``,
        in which case the client logs to the console.
    **kwargs : dict, default: None
        Placeholder to prevent errors when passing additional arguments that
        are not compatible with this method.

    Returns
    -------
    ansys.geometry.core.modeler.Modeler
        Instance of Modeler.
    """
    return _launch_pim_instance(
        is_pim_light=True,
        product_name="scdm",
        product_version=version,
        backend_type=BackendType.SPACECLAIM,
        client_log_level=client_log_level,
        client_log_file=client_log_file,
    )


@deprecated_argument(arg="log_level", alternative="server_log_level")
@deprecated_argument(arg="logs_folder", alternative="server_logs_folder")
def launch_modeler_with_geometry_service(
    product_version: int = None,
    host: str = "localhost",
    port: int = None,
    enable_trace: bool = False,
    timeout: int = 60,
    server_log_level: int = 2,
    client_log_level: int = logging.INFO,
    server_logs_folder: str = None,
    client_log_file: str = None,
    log_level: int = None,  # DEPRECATED
    logs_folder: str = None,  # DEPRECATED
    **kwargs: dict | None,
) -> "Modeler":
    """Start the Geometry service locally using the ``ProductInstance`` class.

    When calling this method, a standalone Geometry service is started.
    By default, if an endpoint is specified (by defining `host` and `port` parameters)
    but the endpoint is not available, the startup will fail. Otherwise, it will try to
    launch its own service.

    Parameters
    ----------
    product_version: int, optional
        The product version to be started. Goes from v23.2.1 to
        the latest. Default is ``None``.
        If a specific product version is requested but not installed locally,
        a SystemError will be raised.

        **Ansys products versions and their corresponding int values:**

        * ``241`` : Ansys 24R1
    host: str, optional
        IP address at which the Geometry service will be deployed. By default,
        its value will be ``localhost``.
    port : int, optional
        Port at which the Geometry service will be deployed. By default, its
        value will be ``None``.
    enable_trace : bool, optional
        Boolean enabling the logs trace on the Geometry service console window.
        By default its value is ``False``.
    timeout : int, optional
        Timeout for starting the backend startup process. The default is 60.
    server_log_level : int, optional
        Backend's log level from 0 to 3:
            0: Chatterbox
            1: Debug
            2: Warning
            3: Error

        The default is ``2`` (Warning).
    client_log_level : int, optional
        Logging level to apply to the client. By default, INFO level is used.
        Use the logging module's levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    server_logs_folder : str, optional
        Sets the backend's logs folder path. If nothing is defined,
        the backend will use its default path.
    client_log_file : str, optional
        Sets the client's log file path. If nothing is defined,
        the client will log to the console.
    log_level : int, optional
        DEPRECATED. Use ``server_log_level`` instead.
    logs_folder : str, optional
        DEPRECATED. Use ``server_logs_folder`` instead.
    **kwargs : dict, default: None
        Placeholder to prevent errors when passing additional arguments that
        are not compatible with this method.

    Raises
    ------
    ConnectionError
        If the specified endpoint is already in use, a connection
        error will be raised.
    SystemError
        If there is not an Ansys product 23.2 version or later installed
        a SystemError will be raised.

    Returns
    -------
    Modeler
        Instance of the Geometry service.

    Examples
    --------
    Starting a geometry service with the default parameters and getting back a ``Modeler``
    object:

    >>> from ansys.geometry.core import launch_modeler_with_geometry_service
    >>> modeler = launch_modeler_with_geometry_service()

    Starting a geometry service, on address ``10.171.22.44``, port ``5001``, with chatty
    logs, traces enabled and a ``300`` seconds timeout:

    >>> from ansys.geometry.core import launch_modeler_with_geometry_service
    >>> modeler = launch_modeler_with_geometry_service(host="10.171.22.44",
        port=5001,
        enable_trace= True,
        timeout=300,
        server_log_level=0)
    """
    # if api_version is passed, throw a warning saying that it is not used
    if "api_version" in kwargs:
        LOG.warning(
            "The 'api_version' parameter is not used in 'launch_modeler_with_geometry_service'. "
            "Please remove it from the arguments."
        )

    # If we are in a Windows environment, we are going to write down the server
    # logs in the %PUBLIC%/Documents/Ansys/GeometryService folder.
    if os.name == "nt" and server_logs_folder is None:
        # Writing to the "Public" folder by default - no write permissions specifically required.
        server_logs_folder = Path(os.getenv("PUBLIC"), "Documents", "Ansys", "GeometryService")
        LOG.info(f"Writing server logs to the default folder at {server_logs_folder}.")

    return prepare_and_start_backend(
        BackendType.WINDOWS_SERVICE,
        product_version=product_version,
        host=host,
        port=port,
        enable_trace=enable_trace,
        api_version=ApiVersions.LATEST,
        timeout=timeout,
        server_log_level=server_log_level,
        client_log_level=client_log_level,
        server_logs_folder=server_logs_folder,
        client_log_file=client_log_file,
        log_level=log_level,
        logs_folder=logs_folder,
    )


@deprecated_argument(arg="log_level", alternative="server_log_level")
def launch_modeler_with_discovery(
    product_version: int = None,
    host: str = "localhost",
    port: int = None,
    api_version: ApiVersions = ApiVersions.LATEST,
    timeout: int = 150,
    manifest_path: str = None,
    hidden: bool = False,
    server_log_level: int = 2,
    client_log_level: int = logging.INFO,
    client_log_file: str = None,
    log_level: int = None,  # DEPRECATED
    **kwargs: dict | None,
):
    """Start Ansys Discovery locally using the ``ProductInstance`` class.

    .. note::

       Support for Ansys Discovery is restricted to Ansys 24.1 onward.

    When calling this method, a standalone Discovery session is started.
    By default, if an endpoint is specified (by defining `host` and `port` parameters)
    but the endpoint is not available, the startup will fail. Otherwise, it will try to
    launch its own service.

    Parameters
    ----------
    product_version: int, optional
        The product version to be started. Goes from v23.2.1 to
        the latest. Default is ``None``.
        If a specific product version is requested but not installed locally,
        a SystemError will be raised.

        **Ansys products versions and their corresponding int values:**

        * ``241`` : Ansys 24R1
    host: str, optional
        IP address at which the Discovery session will be deployed. By default,
        its value will be ``localhost``.
    port : int, optional
        Port at which the Geometry service will be deployed. By default, its
        value will be ``None``.
    api_version: ApiVersions, optional
        The backend's API version to be used at runtime. Goes from API v21 to
        the latest. Default is ``ApiVersions.LATEST``.
    timeout : int, optional
        Timeout for starting the backend startup process. The default is 150.
    manifest_path : str, optional
        Used to specify a manifest file path for the ApiServerAddin. This way,
        it is possible to run an ApiServerAddin from a version an older product
        version.
    hidden : starts the product hiding its UI. Default is ``False``.
    server_log_level : int, optional
        Backend's log level from 0 to 3:
            0: Chatterbox
            1: Debug
            2: Warning
            3: Error

        The default is ``2`` (Warning).
    client_log_level : int, optional
        Logging level to apply to the client. By default, INFO level is used.
        Use the logging module's levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    client_log_file : str, optional
        Sets the client's log file path. If nothing is defined,
        the client will log to the console.
    log_level : int, optional
        DEPRECATED. Use ``server_log_level`` instead.
    **kwargs : dict, default: None
        Placeholder to prevent errors when passing additional arguments that
        are not compatible with this method.

    Raises
    ------
    ConnectionError
        If the specified endpoint is already in use, a connection error will be raised.
    SystemError:
        If there is not an Ansys product 23.2 version or later installed
        or if a specific product's version is requested but not installed locally then
        a SystemError will be raised.

    Returns
    -------
    Modeler
        Instance of the Geometry service.

    Examples
    --------
    Starting an Ansys Discovery session with the default parameters and getting back a ``Modeler``
    object:

    >>> from ansys.geometry.core import launch_modeler_with_discovery
    >>> modeler = launch_modeler_with_discovery()

    Starting an Ansys Discovery V 23.2 session, on address ``10.171.22.44``, port ``5001``,
    with chatty logs, using API v231 and a ``300`` seconds timeout:

    >>> from ansys.geometry.core import launch_modeler_with_discovery
    >>> modeler = launch_modeler_with_discovery(product_version = 232,
        host="10.171.22.44",
        port=5001,
        api_version= 231,
        timeout=300,
        server_log_level=0)
    """
    for unused_var in ["server_logs_folder", "logs_folder"]:
        if unused_var in kwargs:
            LOG.warning(
                f"The '{unused_var}' parameter is not used in 'launch_modeler_with_discovery'. "
                "Please remove it from the arguments."
            )

    return prepare_and_start_backend(
        BackendType.DISCOVERY,
        product_version=product_version,
        host=host,
        port=port,
        enable_trace=False,
        api_version=api_version,
        timeout=timeout,
        manifest_path=manifest_path,
        hidden=hidden,
        server_log_level=server_log_level,
        client_log_level=client_log_level,
        client_log_file=client_log_file,
        log_level=log_level,
    )


@deprecated_argument(arg="log_level", alternative="server_log_level")
def launch_modeler_with_spaceclaim(
    product_version: int = None,
    host: str = "localhost",
    port: int = None,
    api_version: ApiVersions = ApiVersions.LATEST,
    timeout: int = 150,
    manifest_path: str = None,
    hidden: bool = False,
    server_log_level: int = 2,
    client_log_level: int = logging.INFO,
    client_log_file: str = None,
    log_level: int = None,  # DEPRECATED
    **kwargs: dict | None,
):
    """Start Ansys SpaceClaim locally using the ``ProductInstance`` class.

    When calling this method, a standalone SpaceClaim session is started.
    By default, if an endpoint is specified (by defining `host` and `port` parameters)
    but the endpoint is not available, the startup will fail. Otherwise, it will try to
    launch its own service.

    Parameters
    ----------
    product_version: int, optional
        The product version to be started. Goes from v23.2.1 to
        the latest. Default is ``None``.
        If a specific product version is requested but not installed locally,
        a SystemError will be raised.

        **Ansys products versions and their corresponding int values:**

        * ``232`` : Ansys 23R2 SP1
        * ``241`` : Ansys 24R1
    host: str, optional
        IP address at which the SpaceClaim session will be deployed. By default,
        its value will be ``localhost``.
    port : int, optional
        Port at which the Geometry service will be deployed. By default, its
        value will be ``None``.
    api_version: ApiVersions, optional
        The backend's API version to be used at runtime. Goes from API v21 to
        the latest. Default is ``ApiVersions.LATEST``.
    timeout : int, optional
        Timeout for starting the backend startup process. The default is 150.
    manifest_path : str, optional
        Used to specify a manifest file path for the ApiServerAddin. This way,
        it is possible to run an ApiServerAddin from a version an older product
        version.
    hidden : starts the product hiding its UI. Default is ``False``.
    server_log_level : int, optional
        Backend's log level from 0 to 3:
            0: Chatterbox
            1: Debug
            2: Warning
            3: Error

        The default is ``2`` (Warning).
    client_log_level : int, optional
        Logging level to apply to the client. By default, INFO level is used.
        Use the logging module's levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    client_log_file : str, optional
        Sets the client's log file path. If nothing is defined,
        the client will log to the console.
    log_level : int, optional
        DEPRECATED. Use ``server_log_level`` instead.
    **kwargs : dict, default: None
        Placeholder to prevent errors when passing additional arguments that
        are not compatible with this method.

    Raises
    ------
    ConnectionError
        If the specified endpoint is already in use, a connection error will be raised.
    SystemError
        If there is not an Ansys product 23.2 version or later installed
        or if a specific product's version is requested but not installed locally then
        a SystemError will be raised.

    Returns
    -------
    Modeler
        Instance of the Geometry service.

    Examples
    --------
    Starting an Ansys SpaceClaim session with the default parameters and get back a ``Modeler``
    object:

    >>> from ansys.geometry.core import launch_modeler_with_spaceclaim
    >>> modeler = launch_modeler_with_spaceclaim()

    Starting an Ansys SpaceClaim V 23.2 session, on address ``10.171.22.44``, port ``5001``,
    with chatty logs, using API v231 and a ``300`` seconds timeout:

    >>> from ansys.geometry.core import launch_modeler_with_spaceclaim
    >>> modeler = launch_modeler_with_spaceclaim(product_version = 232,
        host="10.171.22.44",
        port=5001,
        api_version= 231,
        timeout=300,
        server_log_level=0)
    """
    for unused_var in ["server_logs_folder", "logs_folder"]:
        if unused_var in kwargs:
            LOG.warning(
                f"The '{unused_var}' parameter is not used in 'launch_modeler_with_spaceclaim'. "
                "Please remove it from the arguments."
            )

    return prepare_and_start_backend(
        BackendType.SPACECLAIM,
        product_version=product_version,
        host=host,
        port=port,
        enable_trace=False,
        api_version=api_version,
        timeout=timeout,
        manifest_path=manifest_path,
        hidden=hidden,
        server_log_level=server_log_level,
        client_log_level=client_log_level,
        client_log_file=client_log_file,
        log_level=log_level,
    )


def _launch_pim_instance(
    is_pim_light: bool,
    product_name: str,
    product_platform: str | None = None,
    product_version: str | None = None,
    backend_type: BackendType | None = None,
    client_log_level: int = logging.INFO,
    client_log_file: str | None = None,
):
    """
    Start `PyPIM <https://github.com/ansys/pypim>`_ using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where PyPIM is configured. You can use the
    :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if it is configured.

    Parameters
    ----------
    is_pim_light : bool
        Whether PIM Light is being used. For example, whether PIM is
        running on a local machine.
    product_name : str
        Name of the service to run.
    product_platform : str, default: None
        Platform on which the service will run. **Specific for Ansys Lab**.
        This parameter is used to specify the operating system on which the
        Geometry service will run. The possible values are:

        * ``"windows"``: The Geometry service runs on a Windows machine.
        * ``"linux"``: The Geometry service runs on a Linux machine.

    product_version : str, default: None
        Version of the service to run.
    backend_type : BackendType, default: None
        Type of backend that PyAnsys Geometry is communicating with. By default, this
        value is unknown, which results in ``None`` being the default value.
    client_log_level : int, default: logging.INFO
        Log level for the client. The default is ``logging.INFO``.
    client_log_file : str, default: None
        Path to the log file for the client. The default is ``None``,
        in which case the client logs to the console.

    Returns
    -------
    ansys.geometry.core.modeler.Modeler
        Instance of the Geometry service.
    """
    from ansys.geometry.core.modeler import Modeler

    check_type(product_version, (type(None), str))

    if not _HAS_PIM:  # pragma: no cover
        raise ModuleNotFoundError(
            "The package 'ansys-platform-instancemanagement' is required to use this function."
        )

    # Platform is used mostly for Ansys Lab purposes. If product_version is defined, use it.
    # Higher priority is given to product_version.
    if product_platform:  # pragma: no cover
        if product_version:
            LOG.warning(
                "The 'product_platform' parameter is not used when 'product_version' is defined."
            )
        else:
            product_version = product_platform

    # If PIM Light is being used and PyPIM configuration is not defined... use defaults.
    if is_pim_light and not os.environ.get("ANSYS_PLATFORM_INSTANCEMANAGEMENT_CONFIG", None):
        os.environ["ANSYS_PLATFORM_INSTANCEMANAGEMENT_CONFIG"] = DEFAULT_PIM_CONFIG
        pop_out = True
    else:
        pop_out = False

    # Perform PyPIM connection
    pim = pypim.connect()
    instance = pim.create_instance(product_name=product_name, product_version=product_version)
    instance.wait_for_ready()
    channel = instance.build_grpc_channel(
        options=[
            ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
        ]
    )

    # If the default PyPIM configuration was used... remove
    if pop_out:
        os.environ.pop("ANSYS_PLATFORM_INSTANCEMANAGEMENT_CONFIG")

    return Modeler(
        channel=channel,
        remote_instance=instance,
        backend_type=backend_type,
        logging_level=client_log_level,
        logging_file=client_log_file,
    )
