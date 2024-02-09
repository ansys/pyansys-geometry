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
"""Trimmed curve class."""
from ansys.api.geometry.v0.commands_pb2 import IntersectCurvesRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from beartype.typing import List
from pint import Quantity

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.conversions import trimmed_curve_to_grpc_trimmed_curve
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.geometry.curves.curve import Curve
from ansys.geometry.core.geometry.curves.curve_evaluation import CurveEvaluation
from ansys.geometry.core.geometry.parameterization import Interval
from ansys.geometry.core.math import Point3D
from ansys.geometry.core.typing import Real


class TrimmedCurve:
    """
    Represents a trimmed curve.

    A trimmed curve is a curve that has a boundary. This boundary comes in the form of an Interval.

    Parameters
    ----------
    geometry : Curve
        The underlying mathematical representation of the curve.
    start : Point3D
        The start point of the curve.
    end : Point3D
        The end point of the curve.
    interval : Interval
        The parametric interval that bounds the curve.
    length : Quantity
        The length of the curve.
    grpc_client : GrpcClient, default: None
        Optional gRPC client that is required for advanced functions such as `intersect_curve()`.
    """

    def __init__(
        self,
        geometry: Curve,
        start: Point3D,
        end: Point3D,
        interval: Interval,
        length: Quantity,
        grpc_client: GrpcClient = None,
    ):
        """Initialize ``TrimmedCurve`` class."""
        self._geometry = geometry
        self._start = start
        self._end = end
        self._interval = interval
        self._length = length
        self._grpc_client = grpc_client
        if grpc_client is not None:
            self._commands_stub = CommandsStub(self._grpc_client.channel)

    @property
    def geometry(self) -> Curve:
        """The underlying mathematical curve."""
        return self._geometry

    @property
    def start(self) -> Point3D:
        """The start point of the curve."""
        return self._start

    @property
    def end(self) -> Point3D:
        """The end point of the curve."""
        return self._end

    @property
    @protect_grpc
    def length(self) -> Quantity:
        """Calculated length of the edge."""
        return self._length

    @property
    @protect_grpc
    def interval(self) -> Interval:
        """Interval of the curve that provides its boundary."""
        return self._interval

    def evaluate_proportion(self, param: Real) -> CurveEvaluation:
        """
        Evaluate the curve at a proportional value.

        A parameter of 0 would correspond to the start of the curve, while a parameter of 1 would
        correspond to the end of the curve.

        Parameters
        ----------
        param : Real
            Parameter in the proportional range [0,1].

        Returns
        -------
        CurveEvaluation
            The resulting curve evaluation.
        """
        bounds = self.interval
        return self.geometry.evaluate(bounds.start + bounds.get_span() * param)

    def intersect_curve(self, other: "TrimmedCurve") -> List[Point3D]:
        """
        Intersect this trimmed curve with another to receive the points of intersection.

        If the curves do not intersect, an empty list is returned.

        Parameters
        ----------
        other : TrimmedCurve
            The trimmed curve to intersect with.

        Returns
        -------
        List[Point3D]
            All points of intersection between the curves.
        """
        if self._grpc_client is None:
            raise ValueError(
                """This TrimmedCurve was not initialized with a grpc client,
                so this method cannot be called."""
            )
        first = trimmed_curve_to_grpc_trimmed_curve(self)
        second = trimmed_curve_to_grpc_trimmed_curve(other)
        res = self._commands_stub.IntersectCurves(
            IntersectCurvesRequest(first=first, second=second)
        )
        if res.intersect is False:
            return []
        return [Point3D([point.x, point.y, point.z]) for point in res.points]

    def __repr__(self) -> str:
        """Represent the trimmed curve as a string."""
        return (
            f"TrimmedCurve(geometry: {type(self.geometry)}, start: {self.start}, end: {self.end}, "
            f"interval: {self.interval}, length: {self.length})"
        )


class ReversedTrimmedCurve(TrimmedCurve):
    """
    Represents a reversed TrimmedCurve.

    When a curve is reversed, its start and end points are swapped, and parameters for evaluations
    are handled to provide expected results conforming to the direction of the curve. For example,
    evaluating a TrimmedCurve proportionally at 0 would evaluate at the start point of the curve,
    but evaluating a ReversedTrimmedCurve proportionally at 0 will evaluate at what was previously
    the end point of the curve but is now the start point.

    Parameters
    ----------
    geometry : Curve
        The underlying mathematical representation of the curve.
    start : Point3D
        The original start point of the curve.
    end : Point3D
        The original end point of the curve.
    interval : Interval
        The parametric interval that bounds the curve.
    length : Quantity
        The length of the curve.
    grpc_client : GrpcClient, default: None
        Optional gRPC client that is required for advanced functions such as `intersect_curve()`.
    """

    def __init__(
        self,
        geometry: Curve,
        start: Point3D,
        end: Point3D,
        interval: Interval,
        length: Quantity,
        grpc_client: GrpcClient = None,
    ):
        """Initialize ``ReversedTrimmedCurve`` class."""
        super().__init__(geometry, start, end, interval, length, grpc_client)

        # Swap start and end points
        temp = self._start
        self._start = self._end
        self._end = temp

    def evaluate_proportion(self, param: Real) -> CurveEvaluation:  # noqa: D102
        # Evaluate starting from the end
        return self.geometry.evaluate(self.interval.end - self.interval.get_span() * param)
