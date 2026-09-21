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

"""Module containing the rayfire service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.conversions import from_measurement_to_server_length
from ..base.rayfire import GRPCRayfireService
from .conversions import (
    build_grpc_id,
    from_grpc_point_to_point3d,
    from_point3d_to_grpc_point,
    from_unit_vector_to_grpc_direction,
)


class GRPCRayfireServiceV0(GRPCRayfireService):
    """Rayfire service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    rayfire service. It is specifically designed for the v0 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def fire(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError(
            f"Method '{self.__class__.__name__}.fire' is not "
            "implemented in this protofile version."
        )

    @protect_grpc
    def fire_ordered(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError(
            f"Method '{self.__class__.__name__}.fire_ordered' is not "
            "implemented in this protofile version."
        )

    @protect_grpc
    def fire_faces(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError(
            f"Method '{self.__class__.__name__}.fire_faces' is not "
            "implemented in this protofile version."
        )

    @protect_grpc
    def fire_ordered_uv(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError(
            f"Method '{self.__class__.__name__}.fire_ordered_uv' is not "
            "implemented in this protofile version."
        )
