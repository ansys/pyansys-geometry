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
"""Provides tools for measurement."""

from typing import TYPE_CHECKING

from ansys.api.geometry.v0.measuretools_pb2 import (
    MinDistanceBetweenObjectsRequest,
    MinDistanceBetweenObjectsResponse,
)
from ansys.api.geometry.v0.measuretools_pb2_grpc import MeasureToolsStub
from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.misc.checks import min_backend_version
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Distance

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body


class Gap:
    """Represents a gap between two bodies.

    Parameters
    ----------
    distance : Distance
        Distance between two sides of the gap.
    """

    def __init__(self, distance: Distance):
        """Initialize ``Gap`` class."""
        self._distance = distance

    @property
    def distance(self) -> Distance:
        """Returns the closest distance between two bodies."""
        return self._distance

    @classmethod
    def _from_distance_response(cls, response: MinDistanceBetweenObjectsResponse) -> "Gap":
        """Construct ``Gap`` object from distance response.

        Notes
        -----
        This method is used internally to construct a ``Gap`` object from a
        gRPC response.

        Parameters
        ----------
        response : MinDistanceBetweenObjectsResponse
            Response from the gRPC server.
        """
        distance = Distance(response.gap.distance, unit=DEFAULT_UNITS.LENGTH)
        return cls(distance)


class MeasurementTools:
    """Measurement tools for PyAnsys Geometry.

    Parameters
    ----------
    grpc_client : GrpcClient
        gRPC client to use for the measurement tools.
    """

    @protect_grpc
    def __init__(self, grpc_client: GrpcClient):
        """Initialize measurement tools class."""
        self._grpc_client = grpc_client
        self._measure_stub = MeasureToolsStub(self._grpc_client.channel)

    @protect_grpc
    @min_backend_version(24, 2, 0)
    def min_distance_between_objects(self, body1: "Body", body2: "Body") -> Gap:
        """Find the gap between two bodies.

        Parameters
        ----------
        body1 : Body
            First body to measure the gap.
        body2 : Body
            Second body to measure the gap.

        Returns
        -------
        Gap
            Gap between two bodies.
        """
        response = self._measure_stub.MinDistanceBetweenObjects(
            MinDistanceBetweenObjectsRequest(bodies=[body1.id, body2.id])
        )
        return Gap._from_distance_response(response)
