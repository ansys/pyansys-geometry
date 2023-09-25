# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
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
from beartype.typing import TYPE_CHECKING
from pint import Quantity

from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.geometry.curves.curve import Curve
from ansys.geometry.core.geometry.curves.curve_evaluation import CurveEvaluation
from ansys.geometry.core.geometry.parameterization import Interval
from ansys.geometry.core.math import Point3D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:
    from ansys.geometry.core.designer.edge import Edge


class TrimmedCurve:
    """
    Represents a trimmed curve.

    A trimmed curve is a curve that has a boundary. This boundary comes in the form of an Interval.

    Parameters
    ----------
    edge : Edge
        Edge that the TrimmedCurve belongs to.
    geometry : Curve
        The underlying mathematical representation of the curve.
    """

    def __init__(self, edge: "Edge", geometry: Curve):
        """Initialize ``TrimmedCurve`` class."""
        self._edge = edge
        self._geometry = geometry

        self.edge._grpc_client.log.debug("Requesting edge points from server.")
        response = self.edge._edges_stub.GetStartAndEndPoints(self._grpc_id)
        self._start = Point3D([response.start.x, response.start.y, response.start.z])
        self._end = Point3D([response.end.x, response.end.y, response.end.z])

    @property
    def edge(self) -> "Edge":
        """The edge this TrimmedCurve belongs to."""
        return self._edge

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
        self.edge._grpc_client.log.debug("Requesting edge length from server.")
        length_response = self.edge._edges_stub.GetLength(self._grpc_id)
        return Quantity(length_response.length, DEFAULT_UNITS.SERVER_LENGTH)

    @property
    @protect_grpc
    def interval(self) -> Interval:
        """Interval of the curve that provides its boundary."""
        self.edge._grpc_client.log.debug("Requesting edge interval from server.")
        interval = self.edge._edges_stub.GetInterval(self.edge._grpc_id)
        return Interval(interval.start, interval.end)

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
    edge : Edge
        Edge that the TrimmedCurve belongs to.
    geometry : Curve
        The underlying mathematical representation of the curve.
    """

    def __init__(self, edge: "Edge", geometry: Curve):
        """Initialize ``ReversedTrimmedCurve`` class."""
        super().__init__(edge, geometry)

        # Swap start and end points
        temp = self._start
        self._start = self._end
        self._end = temp

    def evaluate_proportion(self, param: Real) -> CurveEvaluation:  # noqa: D102
        return self.geometry.evaluate(self.interval.end - self.interval.get_span() * param)
