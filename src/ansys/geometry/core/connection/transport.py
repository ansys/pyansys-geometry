# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Helpers for configuring gRPC transport modes."""

import os
from pathlib import Path
import uuid

from ansys.tools.common.cyberchannel import verify_transport_mode, verify_uds_socket

from ansys.geometry.core.logger import LOG


def _handle_transport_mode(
    host: str,
    transport_mode: str | None = None,
    uds_dir: Path | str | None = None,
    uds_id: str | None = None,
    certs_dir: Path | str | None = None,
    launch_backend: bool = False,
) -> tuple[list[str], dict[str, str | None]]:
    """Select and validate transport settings for a connection or backend launch.

    Parameters
    ----------
    host : str
        Host where the backend is running.
    transport_mode : str | None
        Requested mode, or ``None`` to select one based on the host and OS.
    uds_dir : Path | str | None
        Directory for a Unix domain socket.
    uds_id : str | None
        Optional identifier for a Unix domain socket.
    certs_dir : Path | str | None
        Directory containing TLS certificates.
    launch_backend : bool, default: False
        Whether to prepare backend command-line arguments and launch-only UDS settings.

    Returns
    -------
    tuple[list[str], dict[str, str | None]]
        Backend arguments and normalized transport values.

    When ``launch_backend`` is true, backend command-line arguments are generated, a missing
    UDS ID is created, and an existing UDS socket is rejected.
    """
    loopback_localhosts = ("localhost", "127.0.0.1")
    exe_args: list[str] = []

    if transport_mode is not None:
        verify_transport_mode(transport_mode)
    else:
        if host in loopback_localhosts:
            transport_mode = "wnua" if os.name == "nt" else "uds"
        else:
            transport_mode = "mtls"

        LOG.info(
            f"Transport mode not specified. Selected '{transport_mode}'"
            " based on connection criteria."
        )

    if transport_mode == "mtls":
        if certs_dir is None:
            certs_dir_env = os.getenv("ANSYS_GRPC_CERTIFICATES")
            certs_dir = Path(certs_dir_env) if certs_dir_env else Path.cwd() / "certs"
        else:
            certs_dir = Path(certs_dir)

        if not certs_dir.is_dir():  # pragma: no cover
            raise RuntimeError(
                "Transport mode 'mtls' was selected, but the expected"
                f" certificates directory does not exist: {certs_dir}"
            )
        LOG.info(f"Using certificates directory: {certs_dir.resolve().as_posix()}")

        if launch_backend:
            exe_args.extend(
                (
                    f"--transport-mode={transport_mode}",
                    f"--certs-dir={certs_dir.resolve().as_posix()}",
                )
            )
    elif transport_mode == "uds":
        if host not in loopback_localhosts:
            raise RuntimeError("Transport mode 'uds' is only available for localhost connections.")

        uds_dir = Path(uds_dir) if uds_dir is not None else Path.home() / ".conn"

        if launch_backend:
            uds_dir.mkdir(parents=True, exist_ok=True)
            if uds_id is None:
                uds_id = str(uuid.uuid4())
            if verify_uds_socket("aposdas_socket", uds_dir, uds_id) is True:
                raise RuntimeError("UDS socket file already exists.")
            exe_args.extend(
                (
                    f"--transport-mode={transport_mode}",
                    f"--uds-dir={uds_dir.resolve().as_posix()}",
                    f"--uds-id={uds_id}",
                )
            )
    elif transport_mode == "wnua":
        if os.name != "nt":  # pragma: no cover
            raise RuntimeError("Transport mode 'wnua' is only available on Windows.")
        if host not in loopback_localhosts:
            raise RuntimeError("Transport mode 'wnua' is only available for localhost connections.")
        if launch_backend:
            exe_args.append(f"--transport-mode={transport_mode}")
    elif transport_mode == "insecure":
        if launch_backend:
            exe_args.append(f"--transport-mode={transport_mode}")
    else:  # pragma: no cover
        raise RuntimeError(f"Transport mode '{transport_mode}' is not recognized.")

    transport_values = {
        "transport_mode": transport_mode,
        "uds_dir": str(uds_dir) if transport_mode == "uds" else None,
        "uds_id": uds_id,
        "certs_dir": str(certs_dir) if transport_mode == "mtls" else None,
    }
    return exe_args, transport_values
