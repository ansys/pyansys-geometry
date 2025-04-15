# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

import grpc

from .._version import GeometryApiProtos, set_proto_version
from .base.admin import GRPCAdminService
from .base.bodies import GRPCBodyService
from .base.dbuapplication import GRPCDbuApplicationService
from .base.measurement_tools import GRPCMeasurementToolsService
from .base.named_selection import GRPCNamedSelectionService
from .base.prepare_tools import GRPCPrepareToolsService


class _GRPCServices:
    """
    Placeholder for the gRPC services (i.e. stubs).

    Notes
    -----
    This class provides a unified interface to access the different
    gRPC services available in the Geometry API. It allows for easy
    switching between different versions of the API by using the
    `version` parameter in the constructor. The services are lazy-loaded
    to avoid unnecessary imports and to improve performance.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    version : GeometryApiProtos | str | None
        The version of the gRPC API protocol to use. If None, the latest
        version is used.
    """

    def __init__(self, channel: grpc.Channel, version: GeometryApiProtos | str | None = None):
        """
        Initialize the GRPCServices class.

        Parameters
        ----------
        channel : grpc.Channel
            The gRPC channel to the server.
        version : GeometryApiProtos | str | None
            The version of the gRPC API protocol to use. If None, the latest
            version is used.
        """
        # Set the proto version to be used
        self.version = set_proto_version(channel, version)
        self.channel = channel

        # Lazy load all the services
        self._admin = None
        self._bodies = None
        self._dbu_application = None
        self._named_selection = None
        self._measurement_tools = None
        self._prepare_tools = None

    @property
    def bodies(self) -> GRPCBodyService:
        """
        Get the body service for the specified version.

        Returns
        -------
        BodyServiceBase
            The body service for the specified version.
        """
        if not self._bodies:
            # Import the appropriate body service based on the version
            from .v0.bodies import GRPCBodyServiceV0
            from .v1.bodies import GRPCBodyServiceV1

            if self.version == GeometryApiProtos.V0:
                self._bodies = GRPCBodyServiceV0(self.channel)
            elif self.version == GeometryApiProtos.V1:  # pragma: no cover
                # V1 is not implemented yet
                self._bodies = GRPCBodyServiceV1(self.channel)
            else:  # pragma: no cover
                # This should never happen as the version is set in the constructor
                raise ValueError(f"Unsupported version: {self.version}")

        return self._bodies

    @property
    def admin(self) -> GRPCAdminService:
        """
        Get the admin service for the specified version.

        Returns
        -------
        AdminServiceBase
            The admin service for the specified version.
        """
        if not self._admin:
            # Import the appropriate admin service based on the version
            from .v0.admin import GRPCAdminServiceV0
            from .v1.admin import GRPCAdminServiceV1

            if self.version == GeometryApiProtos.V0:
                self._admin = GRPCAdminServiceV0(self.channel)
            elif self.version == GeometryApiProtos.V1:  # pragma: no cover
                # V1 is not implemented yet
                self._admin = GRPCAdminServiceV1(self.channel)
            else:  # pragma: no cover
                # This should never happen as the version is set in the constructor
                raise ValueError(f"Unsupported version: {self.version}")

        return self._admin

    @property
    def dbu_application(self) -> GRPCDbuApplicationService:
        """
        Get the DBU application service for the specified version.

        Returns
        -------
        DbuApplicationServiceBase
            The DBU application service for the specified version.
        """
        if not self._dbu_application:
            # Import the appropriate DBU application service based on the version
            from .v0.dbuapplication import GRPCDbuApplicationServiceV0
            from .v1.dbuapplication import GRPCDbuApplicationServiceV1

            if self.version == GeometryApiProtos.V0:
                self._dbu_application = GRPCDbuApplicationServiceV0(self.channel)
            elif self.version == GeometryApiProtos.V1:  # pragma: no cover
                # V1 is not implemented yet
                self._dbu_application = GRPCDbuApplicationServiceV1(self.channel)
            else:  # pragma: no cover
                # This should never happen as the version is set in the constructor
                raise ValueError(f"Unsupported version: {self.version}")

        return self._dbu_application

    @property
    def named_selection(self) -> GRPCNamedSelectionService:
        """
        Get the named selection service for the specified version.

        Returns
        -------
        NamedSelectionServiceBase
            The named selection service for the specified version.
        """
        if not self._named_selection:
            # Import the appropriate named selection service based on the version
            from .v0.named_selection import GRPCNamedSelectionServiceV0
            from .v1.named_selection import GRPCNamedSelectionServiceV1

            if self.version == GeometryApiProtos.V0:
                self._named_selection = GRPCNamedSelectionServiceV0(self.channel)
            elif self.version == GeometryApiProtos.V1:  # pragma: no cover
                # V1 is not implemented yet
                self._named_selection = GRPCNamedSelectionServiceV1(self.channel)
            else:  # pragma: no cover
                # This should never happen as the version is set in the constructor
                raise ValueError(f"Unsupported version: {self.version}")

        return self._named_selection

    @property
    def measurement_tools(self) -> GRPCMeasurementToolsService:
        """
        Get the measurement tools service for the specified version.

        Returns
        -------
        MeasurementToolsServiceBase
            The measurement tools service for the specified version.
        """
        if not self._measurement_tools:
            # Import the appropriate measurement tools service based on the version
            from .v0.measurement_tools import GRPCMeasurementToolsServiceV0
            from .v1.measurement_tools import GRPCMeasurementToolsServiceV1

            if self.version == GeometryApiProtos.V0:
                self._measurement_tools = GRPCMeasurementToolsServiceV0(self.channel)
            elif self.version == GeometryApiProtos.V1:  # pragma: no cover
                # V1 is not implemented yet
                self._measurement_tools = GRPCMeasurementToolsServiceV1(self.channel)
            else:  # pragma: no cover
                # This should never happen as the version is set in the constructor
                raise ValueError(f"Unsupported version: {self.version}")

        return self._measurement_tools
        
    @property
    def prepare_tools(self) -> GRPCPrepareToolsService:
        """
        Get the prepare tools service for the specified version.

        Returns
        -------
        NamedSelectionServiceBase
            The prepare tools service for the specified version.
        """
        if not self._prepare_tools:
            # Import the appropriate prepare tools service based on the version
            from .v0.prepare_tools import GRPCPrepareToolsServiceV0
            from .v1.prepare_tools import GRPCPrepareToolsServiceV1

            if self.version == GeometryApiProtos.V0:
                self._prepare_tools = GRPCPrepareToolsServiceV0(self.channel)
            elif self.version == GeometryApiProtos.V1:  # pragma: no cover
                # V1 is not implemented yet
                self._prepare_tools = GRPCPrepareToolsServiceV1(self.channel)
            else:  # pragma: no cover
                # This should never happen as the version is set in the constructor
                raise ValueError(f"Unsupported version: {self.version}")

        return self._prepare_tools
