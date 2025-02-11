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
"""Module for repair tool message."""

from typing import TYPE_CHECKING

from ansys.api.geometry.v0.repairtools_pb2 import RepairGeometryRequest
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.tools.repair_tool_message import RepairToolMessage

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body


class GeometryIssue:
    """Provides return message for the repair tool methods."""

    def __init__(
        self,
        message_type: str,
        message_id: str,
        message: str,
        edges: list[str],
        faces: list[str],
    ):
        """Initialize a new instance of a geometry issue found during geometry inspect.

        Parameters
        ----------
        message_type: str
            Type of the message (warning, error, info).
        message_id: str
            Identifier for the message.
        message
            Message that describes the geometry issue.
        edges: list[str]
            List of edges (if any) that are part of the issue.
        modified_bodies: list[str]
            List of faces that are part of the issue.
        """
        self._message_type = message_type
        self._message_id = message_id
        self._message = message
        self._edges = edges
        self._faces = faces

    @property
    def message_type(self) -> str:
        """The type of the message (warning, error, info)."""
        return self._message_type

    @property
    def message_id(self) -> str:
        """The identifier for the message."""
        return self._message_id

    @property
    def message(self) -> str:
        """The content of the message."""
        return self._message

    @property
    def edges(self) -> list[str]:
        """The List of edges (if any) that are part of the issue."""
        return self._edges

    @property
    def faces(self) -> list[str]:
        """The List of faces (if any) that are part of the issue."""
        return self._faces


class InspectResult:
    """Provides the result of the inspect geometry operation."""

    def __init__(self, grpc_client: GrpcClient, body: "Body", issues: list[GeometryIssue]):
        """Initialize a new instance of the result of the inspect geometry operation.

        Parameters
        ----------
        body: Body
            Body for which issues are found.
        issues: list[GeometryIssue]
            List of issues for the body.
        """
        self._body = body
        self._issues = issues
        self._repair_stub = RepairToolsStub(grpc_client.channel)

    @property
    def body(self) -> "Body":
        """The body for which issues are found."""
        return self._body

    @property
    def issues(self) -> list[GeometryIssue]:
        """The list of issues for the body."""
        return self._issues

    def repair(self) -> RepairToolMessage:
        """Repair the problem area.

        Returns
        -------
        RepairToolMessage
            Message containing created and/or modified bodies.
        """
        if not self.body:
            return RepairToolMessage(False, [], [])

        repair_result_response = self._repair_stub.RepairGeometry(
            RepairGeometryRequest(bodies=[self.body._grpc_id])
        )

        return RepairToolMessage(repair_result_response.result.success, [], [])
