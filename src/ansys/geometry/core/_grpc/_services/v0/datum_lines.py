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

"""Module containing the datum lines service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.datum_lines import GRPCDatumLinesService


class GRPCDatumLinesServiceV0(GRPCDatumLinesService):
    """Datum lines service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    datum lines service. It is specifically designed for the v0 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.

    Notes
    -----
    The DatumLine service is only available in the v1 API. All methods in this
    class raise ``NotImplementedError``.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        pass

    @protect_grpc
    def create(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError(
            f"Method '{self.__class__.__name__}.create' is not "
            "implemented in this protofile version."
        )

    @protect_grpc
    def delete(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError(
            f"Method '{self.__class__.__name__}.delete' is not "
            "implemented in this protofile version."
        )

    @protect_grpc
    def get(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError(
            f"Method '{self.__class__.__name__}.get' is not implemented in this protofile version."
        )

    @protect_grpc
    def get_all(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError(
            f"Method '{self.__class__.__name__}.get_all' is not "
            "implemented in this protofile version."
        )

    @protect_grpc
    def get_is_deleted(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError(
            f"Method '{self.__class__.__name__}.get_is_deleted' is not "
            "implemented in this protofile version."
        )
