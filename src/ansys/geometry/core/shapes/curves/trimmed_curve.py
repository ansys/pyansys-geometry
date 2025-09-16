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
"""Trimmed curve class."""

from ansys.api.geometry.v0.commands_pb2 import IntersectCurvesRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from pint import Quantity

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.conversions import trimmed_curve_to_grpc_trimmed_curve
from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Angle, Distance
from ansys.geometry.core.shapes.curves.curve import Curve
from ansys.geometry.core.shapes.curves.curve_evaluation import CurveEvaluation
from ansys.geometry.core.shapes.parameterization import Interval
from ansys.geometry.core.typing import Real


class TrimmedCurve:
    """Represents a trimmed curve.

    A trimmed curve is a curve that has a boundary. This boundary comes in the form of an interval.

    Parameters
    ----------
    geometry : Curve
        Underlying mathematical representation of the curve.
    start : Point3D
        Start point of the curve.
    end : Point3D
        End point of the curve.
    interval : Interval
        Parametric interval that bounds the curve.
    length : Quantity
        Length of the curve.
    grpc_client : GrpcClient, default: None
        gRPC client that is required for advanced functions such as ``intersect_curve()``.
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
        """Underlying mathematical curve."""
        return self._geometry

    @property
    def start(self) -> Point3D:
        """Start point of the curve."""
        return self._start

    @property
    def end(self) -> Point3D:
        """End point of the curve."""
        return self._end

    @property
    def length(self) -> Quantity:
        """Calculated length of the edge."""
        return self._length

    @property
    def interval(self) -> Interval:
        """Interval of the curve that provides its boundary."""
        return self._interval

    def evaluate_proportion(self, param: Real) -> CurveEvaluation:
        """Evaluate the curve at a proportional value.

        A parameter of ``0`` corresponds to the start of the curve, while a parameter of ``1``
        corresponds to the end of the curve.

        Parameters
        ----------
        param : Real
            Parameter in the proportional range [0,1].

        Returns
        -------
        CurveEvaluation
            Resulting curve evaluation.
        """
        bounds = self.interval
        return self.geometry.evaluate(bounds.start + bounds.get_span() * param)

    def intersect_curve(self, other: "TrimmedCurve") -> list[Point3D]:
        """Get the intersect points of this trimmed curve with another one.

        If the two trimmed curves do not intersect, an empty list is returned.

        Parameters
        ----------
        other : TrimmedCurve
            Trimmed curve to intersect with.

        Returns
        -------
        list[Point3D]
            All points of intersection between the curves.
        """
        if self._grpc_client is None:
            raise ValueError(
                """Because this trimmed curve was not initialized with a gRPC client,
                the method cannot be called."""
            )
        first = trimmed_curve_to_grpc_trimmed_curve(self)
        second = trimmed_curve_to_grpc_trimmed_curve(other)
        res = self._commands_stub.IntersectCurves(
            IntersectCurvesRequest(first=first, second=second)
        )
        if res.intersect is False:
            return []
        return [
            Point3D([point.x, point.y, point.z], unit=DEFAULT_UNITS.SERVER_LENGTH)
            for point in res.points
        ]

    def transformed_copy(self, matrix: Matrix44) -> "TrimmedCurve":
        """Return a copy of the trimmed curve transformed by the given matrix.

        Parameters
        ----------
        matrix : Matrix44
            Transformation matrix to apply to the curve.

        Returns
        -------
        TrimmedCurve
            A new trimmed curve with the transformation applied.
        """
        transformed_geometry = self.geometry.transformed_copy(matrix)
        transformed_start = self.start.transform(matrix)
        transformed_end = self.end.transform(matrix)

        return TrimmedCurve(
            transformed_geometry,
            transformed_start,
            transformed_end,
            self.interval,
            self.length,
        )

    def translate(self, direction: UnitVector3D, distance: Real | Quantity | Distance) -> None:
        """Translate the trimmed curve by a given vector and distance.

        Parameters
        ----------
        direction : UnitVector3D
            Direction of translation.
        distance : Real | Quantity | Distance
            Distance to translate.
        """
        distance = distance if isinstance(distance, Distance) else Distance(distance)
        translation_matrix = Matrix44.create_translation(direction * distance.value.m)

        translated_copy = self.transformed_copy(translation_matrix)

        # Update the current instance with the translated copy
        self._geometry = translated_copy.geometry
        self._start = translated_copy.start
        self._end = translated_copy.end
        self._length = translated_copy.length
        self._interval = translated_copy.interval

    def rotate(self, origin: Point3D, axis: UnitVector3D, angle: Real | Quantity | Angle) -> None:
        """Rotate the trimmed curve around a given axis centered at a given point.

        Parameters
        ----------
        origin : Point3D
            Origin point of the rotation.
        axis : UnitVector3D
            Axis of rotation.
        angle : Real | Quantity | Angle
            Angle to rotate in radians.
        """
        angle = angle if isinstance(angle, Angle) else Angle(angle)

        # Translate the curve to the origin
        translate_to_origin_matrix = Matrix44.create_translation(
            Vector3D([-origin.x.m, -origin.y.m, -origin.z.m])
        )
        translated_copy = self.transformed_copy(translate_to_origin_matrix)

        # Rotate the curve around the axis
        rotation_matrix = Matrix44.create_matrix_from_rotation_about_axis(axis, angle.value.m)
        rotated_copy = translated_copy.transformed_copy(rotation_matrix)

        # Translate the curve back to its original position
        translate_back_matrix = Matrix44.create_translation(
            Vector3D([origin.x.m, origin.y.m, origin.z.m])
        )
        translated_back_copy = rotated_copy.transformed_copy(translate_back_matrix)

        # Update the current instance with the rotated copy
        self._geometry = translated_back_copy.geometry
        self._start = translated_back_copy.start
        self._end = translated_back_copy.end
        self._length = translated_back_copy.length
        self._interval = translated_back_copy.interval

    def __repr__(self) -> str:
        """Represent the trimmed curve as a string."""
        return (
            f"TrimmedCurve(geometry: {type(self.geometry)}, start: {self.start}, end: {self.end}, "
            f"interval: {self.interval}, length: {self.length})"
        )


class ReversedTrimmedCurve(TrimmedCurve):
    """Represents a reversed trimmed curve.

    When a curve is reversed, its start and end points are swapped, and parameters for evaluations
    are handled to provide expected results conforming to the direction of the curve. For example,
    evaluating a trimmed curve proportionally at 0 evaluates at the start point of the curve,
    but evaluating a reversed trimmed curve proportionally at 0 evaluates at what was previously
    the end point of the curve but is now the start point.

    Parameters
    ----------
    geometry : Curve
        Underlying mathematical representation of the curve.
    start : Point3D
        Original start point of the curve.
    end : Point3D
        Original end point of the curve.
    interval : Interval
        Parametric interval that bounds the curve.
    length : Quantity
        Length of the curve.
    grpc_client : GrpcClient, default: None
        gRPC client that is required for advanced functions such as `intersect_curve()`.
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
        """Initialize an instance of a reversed trimmed curve."""
        super().__init__(geometry, start, end, interval, length, grpc_client)

        # Swap start and end points
        temp = self._start
        self._start = self._end
        self._end = temp

    def evaluate_proportion(self, param: Real) -> CurveEvaluation:  # noqa: D102
        # Evaluate starting from the end
        return self.geometry.evaluate(self.interval.end - self.interval.get_span() * param)
