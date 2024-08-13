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
"""Provides for creating and managing a line."""

from functools import cached_property
import math

from beartype import beartype as check_input_types
import numpy as np

from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.accuracy import LENGTH_ACCURACY
from ansys.geometry.core.shapes.curves.curve import Curve
from ansys.geometry.core.shapes.curves.curve_evaluation import CurveEvaluation
from ansys.geometry.core.shapes.parameterization import (
    Interval,
    Parameterization,
    ParamForm,
    ParamType,
)
from ansys.geometry.core.typing import Real, RealSequence


class Line(Curve):
    """Provides 3D line representation.

    Parameters
    ----------
    origin : ~numpy.ndarray | RealSequence | Point3D
        Origin of the line.
    direction : ~numpy.ndarray | RealSequence | UnitVector3D | Vector3D
        Direction of the line.
    """

    @check_input_types
    def __init__(
        self,
        origin: np.ndarray | RealSequence | Point3D,
        direction: np.ndarray | RealSequence | UnitVector3D | Vector3D,
    ):
        """Initialize the ``Line`` class."""
        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin
        self._direction = (
            UnitVector3D(direction) if not isinstance(direction, UnitVector3D) else direction
        )

    @property
    def origin(self) -> Point3D:
        """Origin of the line."""
        return self._origin

    @property
    def direction(self) -> UnitVector3D:
        """Direction of the line."""
        return self._direction

    def __eq__(self, other: object) -> bool:
        """Equals operator for the ``Line`` class."""
        if isinstance(other, Line):
            return self._origin == other.origin and self._direction == other.direction
        return False

    def evaluate(self, parameter: float) -> "LineEvaluation":
        """Evaluate the line at a given parameter.

        Parameters
        ----------
        parameter : Real
            Parameter to evaluate the line at.

        Returns
        -------
        LineEvaluation
            Resulting evaluation.
        """
        return LineEvaluation(self, parameter)

    def transformed_copy(self, matrix: Matrix44) -> "Line":
        """Create a transformed copy of the line from a transformation matrix.

        Parameters
        ----------
        matrix : Matrix44
            4X4 transformation matrix to apply to the line.

        Returns
        -------
        Line
           New line that is the transformed copy of the original line.
        """
        old_origin_4d = np.array([[self.origin[0]], [self.origin[1]], [self.origin[2]], [1]])
        new_origin_4d = matrix * old_origin_4d
        new_point = Point3D([new_origin_4d[0], new_origin_4d[1], new_origin_4d[2]])
        new_axis = matrix * np.append(self._direction, 0)
        return Line(new_point, UnitVector3D(new_axis[0:3]))

    def project_point(self, point: Point3D) -> "LineEvaluation":
        """Project a point onto the line and evaluate the line.

        Parameters
        ----------
        point : Point3D
            Point to project onto the line.

        Returns
        -------
        LineEvaluation
            Resulting evaluation.
        """
        origin_to_point = point - self.origin
        t = origin_to_point.dot(self.direction)
        return LineEvaluation(self, t)

    def is_coincident_line(self, other: "Line") -> bool:
        """Determine if the line is coincident with another line.

        Parameters
        ----------
        other : Line
            Line to determine coincidence with.

        Returns
        -------
        bool
            ``True`` if the line is coincident with another line, ``False`` otherwise.
        """
        if self == other:
            return True
        if not self.direction.is_parallel_to(other.direction):
            return False

        between = Vector3D(self.origin - other.origin)

        return math.pow((self.direction % between).magnitude, 2) <= math.pow(
            LENGTH_ACCURACY, 2
        ) and math.pow((self.direction % between).magnitude, 2) <= math.pow(LENGTH_ACCURACY, 2)

    def is_opposite_line(self, other: "Line") -> bool:
        """Determine if the line is opposite another line.

        Parameters
        ----------
        other : Line
            Line to determine opposition with.

        Returns
        -------
        bool
            ``True`` if the line is opposite to another line.
        """
        if self.is_coincident_line(other):
            return self.direction.is_opposite(other.direction)
        return False

    def parameterization(self) -> Parameterization:
        """Get the parametrization of the line.

        The parameter of a line specifies the distance from the `origin` in the
        direction of `direction`.

        Returns
        -------
        Parameterization
            Information about how the line is parameterized.
        """
        return Parameterization(ParamForm.OPEN, ParamType.LINEAR, Interval(-np.inf, np.inf))

    def contains_param(self, param: Real) -> bool:  # noqa: D102
        raise NotImplementedError("contains_param() is not implemented.")

    def contains_point(self, point: Point3D) -> bool:  # noqa: D102
        raise NotImplementedError("contains_point() is not implemented.")


class LineEvaluation(CurveEvaluation):
    """Provides for evaluating a line."""

    def __init__(self, line: Line, parameter: float = None) -> None:
        """Initialize the ``LineEvaluation`` class."""
        self._line = line
        self._parameter = parameter

    @property
    def line(self) -> Line:
        """Line being evaluated."""
        return self._line

    @property
    def parameter(self) -> float:
        """Parameter that the evaluation is based upon."""
        return self._parameter

    @cached_property
    def position(self) -> Point3D:
        """Position of the evaluation.

        Returns
        -------
        Point3D
            Point that lies on the line at this evaluation.
        """
        return self.line.origin + self.parameter * self.line.direction

    @cached_property
    def tangent(self) -> UnitVector3D:
        """Tangent of the evaluation.

        Notes
        -----
        This is always equal to the direction of the line.

        Returns
        -------
        UnitVector3D
            Tangent unit vector to the line at this evaluation.
        """
        return self.line.direction

    @cached_property
    def first_derivative(self) -> Vector3D:
        """First derivative of the evaluation.

        The first derivative is always equal to the direction of the line.

        Returns
        -------
        Vector3D
            First derivative of the evaluation.
        """
        return self.line.direction

    @cached_property
    def second_derivative(self) -> Vector3D:
        """Second derivative of the evaluation.

        The second derivative is always equal to a zero vector ``Vector3D([0, 0, 0])``.

        Returns
        -------
        Vector3D
            Second derivative of the evaluation, which is always ``Vector3D([0, 0, 0])``.
        """
        return Vector3D([0, 0, 0])

    @cached_property
    def curvature(self) -> float:
        """Curvature of the line, which is always ``0``.

        Returns
        -------
        Real
            Curvature of the line, which is always ``0``.
        """
        return 0
