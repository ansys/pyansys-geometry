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
"""Provides tools for preparing bodies."""

from ansys.api.geometry.v0.models_pb2 import Body as GRPCBody
from ansys.api.geometry.v0.preparetools_pb2 import (
    ShareTopologyRequest,
)
from ansys.api.geometry.v0.preparetools_pb2_grpc import PrepareToolsStub
from beartype.typing import TYPE_CHECKING, List
from google.protobuf.wrappers_pb2 import BoolValue, DoubleValue

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body


class PrepareTools:
    """Exposes body preparation tools for PyAnsys Geometry."""

    def __init__(self, grpc_client: GrpcClient):
        """Initialize ``PrepareTools`` class."""
        self._grpc_client = grpc_client
        self._prepare_stub = PrepareToolsStub(self._grpc_client.channel)

    def share_topology(
        self, bodies: List["Body"], tol: Real = 0.0, preserve_instances: bool = False
    ) -> bool:
        """Share topology between the chosen bodies.

        Parameters
        ----------
        bodies : List[Body]
            List of bodies to share topology between.
        tol : Real
            Maximum distance between bodies.
        preserve_instances : bool
            Whether instances are preserved.

        Returns
        -------
        bool
            ``True`` if successful, ``False`` if failed.
        """
        if not bodies:
            return False

        share_topo_response = self._prepare_stub.ShareTopology(
            ShareTopologyRequest(
                selection=[GRPCBody(id=body.id) for body in bodies],
                tolerance=DoubleValue(value=tol),
                preserve_instances=BoolValue(value=preserve_instances),
            )
        )
        return share_topo_response.result
