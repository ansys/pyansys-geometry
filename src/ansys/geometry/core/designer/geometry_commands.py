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
"""Provides tools for pulling geometry."""

from typing import TYPE_CHECKING, List, Union

from ansys.api.geometry.v0.commands_pb2 import ChamferRequest, FilletRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.misc.checks import min_backend_version
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.edge import Edge
    from ansys.geometry.core.designer.face import Face


class GeometryCommands:
    """Provides geometry commands for PyAnsys Geometry.

    Parameters
    ----------
    grpc_client : GrpcClient
        gRPC client to use for the geometry commands.
    """

    @protect_grpc
    def __init__(self, grpc_client: GrpcClient):
        """Initialize an instance of the ``GeometryCommands`` class."""
        self._grpc_client = grpc_client
        self._commands_stub = CommandsStub(self._grpc_client.channel)

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def chamfer(
        self, selection: Union["Edge", List["Edge"], "Face", List["Face"]], distance: Real
    ) -> bool:
        """Create a chamfer on an edge or adjust the chamfer of a face.

        Parameters
        ----------
        selection : Edge | list[Edge] | Face | list[Face]
            One or more edges or faces to act on.
        distance : Real
            Chamfer distance.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        selection: list[Edge | Face] = selection if isinstance(selection, list) else [selection]

        for ef in selection:
            ef.body._reset_tessellation_cache()

        result = self._commands_stub.Chamfer(
            ChamferRequest(ids=[ef._grpc_id for ef in selection], distance=distance)
        )

        return result.success

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def fillet(
        self, selection: Union["Edge", List["Edge"], "Face", List["Face"]], radius: Real
    ) -> bool:
        """Create a fillet on an edge or adjust the fillet of a face.

        Parameters
        ----------
        selection : Edge | list[Edge] | Face | list[Face]
            One or more edges or faces to act on.
        radius : Real
            Fillet radius.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        selection: list[Edge | Face] = selection if isinstance(selection, list) else [selection]

        for ef in selection:
            ef.body._reset_tessellation_cache()

        result = self._commands_stub.Fillet(
            FilletRequest(ids=[ef._grpc_id for ef in selection], radius=radius)
        )

        return result.success
