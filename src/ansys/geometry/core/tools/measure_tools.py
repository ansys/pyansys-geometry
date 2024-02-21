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
"""Provides tools for measuring."""

from ansys.api.geometry.v0.measuretools_pb2 import (
    MinDistanceBetweenObjectsRequest,
    MinDistanceBetweenObjectsResponse,
)
from ansys.api.geometry.v0.measuretools_pb2_grpc import MeasureToolsStub
from beartype.typing import TYPE_CHECKING

from ansys.geometry.core.connection import GrpcClient

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body


class Gap:
    """Gap between two bodies."""

    def __init__(self, grpc_client: GrpcClient, distance: float = None):
        """Initialize Gap class."""
        self._grpc_client = grpc_client
        self._measure_stub = MeasureToolsStub(self._grpc_client.channel)
        self._distance = distance

    @property
    def distance(self):
        """Get the calculated distance."""
        return self._distance

    @classmethod
    def from_distance_response(
        cls, grpc_client: GrpcClient, response: MinDistanceBetweenObjectsResponse
    ):
        """Construct Gap object from distance response."""
        return cls(grpc_client, response.gap.distance)


class MeasureTools:
    """Measure Tools for PyAnsys Geometry."""

    def __init__(self, grpc_client: GrpcClient):
        """Initialize Measure Tools class."""
        self._grpc_client = grpc_client
        self._measure_stub = MeasureToolsStub(self._grpc_client.channel)

    def min_distance_between_objects(self, body1: "Body", body2: "Body"):
        """Find the gap between objects."""
        body_ids = [body1.id, body2.id]
        response = self._measure_stub.MinDistanceBetweenObjects(
            MinDistanceBetweenObjectsRequest(bodies=body_ids)
        )
        gap = Gap.from_distance_response(self._grpc_client, response)
        return gap
