# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
"""Module to perform a connection validation check.

The method in this module is only used for testing the default Docker service on
GitHub and can safely be skipped within testing.

This command shows how this method is typically used:

.. code:: bash

   python -c "from ansys.geometry.core.connection import validate; validate()"
"""

from ansys.geometry.core.connection.client import wait_until_healthy
import ansys.geometry.core.connection.defaults as default_settings


def validate(*args, **kwargs):  # pragma: no cover
    """Create a client using the default settings and validate it."""
    # Assume local transport mode for validation if not provided
    channel = None
    if "transport_mode" not in kwargs:
        import platform

        try:
            channel = wait_until_healthy(
                channel=f"{kwargs.get('host', default_settings.DEFAULT_HOST)}:{kwargs.get('port', default_settings.DEFAULT_PORT)}",  # noqa: E501
                timeout=kwargs.get("timeout", 120),
                transport_mode="wnua" if platform.system() == "Windows" else "uds",
            )
        except Exception:
            # Let's give it a try to insecure mode... just in case
            channel = wait_until_healthy(
                channel=f"{kwargs.get('host', default_settings.DEFAULT_HOST)}:{kwargs.get('port', default_settings.DEFAULT_PORT)}",  # noqa: E501
                timeout=kwargs.get("timeout", 120),
                transport_mode="insecure",
            )
    else:
        channel = wait_until_healthy(
            channel=f"{kwargs.get('host', default_settings.DEFAULT_HOST)}:{kwargs.get('port', default_settings.DEFAULT_PORT)}",  # noqa: E501
            timeout=kwargs.get("timeout", 120),
            transport_mode=kwargs["transport_mode"],
            uds_dir=kwargs.get("uds_dir", None),
            uds_id=kwargs.get("uds_id", None),
            certs_dir=kwargs.get("certs_dir", None),
        )

    # If we reach this point, the connection is valid
    print("Connection to Geometry server is valid.")
    print(f"Using gRPC channel connected to {channel._channel.target().decode()}")

    # TODO: consider adding additional server stat reporting
    # https://github.com/ansys/pyansys-geometry/issues/1319
