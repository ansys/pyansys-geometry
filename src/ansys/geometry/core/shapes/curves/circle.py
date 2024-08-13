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
"""Provides for creating and managing a circle."""

from functools import cached_property

from beartype import beartype as check_input_types
import numpy as np
from pint import Quantity

from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Z
from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.accuracy import Accuracy
from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.shapes.curves.curve import Curve
from ansys.geometry.core.shapes.curves.curve_evaluation import CurveEvaluation
from ansys.geometry.core.shapes.parameterization import (
    Interval,
    Parameterization,
    ParamForm,
    ParamType,
)
from ansys.geometry.core.typing import Real, RealSequence


class Circle(Curve):
    """Provides 3D circle representation.

    Parameters
    ----------
    origin : ~numpy.ndarray | RealSequence | Point3D
        Origin of the circle.
    radius : ~pint.Quantity | Distance | Real
        Radius of the circle.
    reference : ~numpy.ndarray | RealSequence | UnitVector3D | Vector3D
        X-axis direction.
    axis : ~numpy.ndarray | RealSequence | UnitVector3D | Vector3D
        Z-axis direction.
    """

    @check_input_types
    def __init__(
        self,
        origin: np.ndarray | RealSequence | Point3D,
        radius: Quantity | Distance | Real,
        reference: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_X,
        axis: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_Z,
    ):
        """Initialize the ``Circle`` class."""
        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin

        self._reference = (
            UnitVector3D(reference) if not isinstance(reference, UnitVector3D) else reference
        )
        self._axis = UnitVector3D(axis) if not isinstance(axis, UnitVector3D) else axis

        if not self._reference.is_perpendicular_to(self._axis):
            raise ValueError("Circle reference (dir_x) and axis (dir_z) must be perpendicular.")

        self._radius = radius if isinstance(radius, Distance) else Distance(radius)
        if self._radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

    @property
    def origin(self) -> Point3D:
        """Origin of the circle."""
        return self._origin

    @property
    def radius(self) -> Quantity:
        """Radius of the circle."""
        return self._radius.value

    @property
    def diameter(self) -> Quantity:
        """Diameter of the circle."""
        return 2 * self.radius

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the circle."""
        return 2 * np.pi * self.radius

    @property
    def area(self) -> Quantity:
        """Area of the circle."""
        return np.pi * self.radius**2

    @property
    def dir_x(self) -> UnitVector3D:
        """X-direction of the circle."""
        return self._reference

    @property
    def dir_y(self) -> UnitVector3D:
        """Y-direction of the circle."""
        return self.dir_z.cross(self.dir_x)

    @property
    def dir_z(self) -> UnitVector3D:
        """Z-direction of the circle."""
        return self._axis

    @check_input_types
    def __eq__(self, other: "Circle") -> bool:
        """Equals operator for the ``Circle`` class."""
        return (
            self._origin == other._origin
            and self._radius == other._radius
            and self._reference == other._reference
            and self._axis == other._axis
        )

    def evaluate(self, parameter: Real) -> "CircleEvaluation":
        """Evaluate the circle at a given parameter.

        Parameters
        ----------
        parameter : Real
            Parameter to evaluate the circle at.

        Returns
        -------
        CircleEvaluation
            Resulting evaluation.
        """
        return CircleEvaluation(self, parameter)

    def transformed_copy(self, matrix: Matrix44) -> "Circle":
        """Create a transformed copy of the circle from a transformation matrix.

        Parameters
        ----------
        matrix : Matrix44
            4x4 transformation matrix to apply to the circle.

        Returns
        -------
        Circle
            New circle that is the transformed copy of the original circle.
        """
        new_point = self.origin.transform(matrix)
        new_reference = self._reference.transform(matrix)
        new_axis = self._axis.transform(matrix)
        return Circle(
            new_point,
            self.radius,
            UnitVector3D(new_reference[0:3]),
            UnitVector3D(new_axis[0:3]),
        )

    def mirrored_copy(self) -> "Circle":
        """Create a mirrored copy of the circle along the y-axis.

        Returns
        -------
        Circle
            A new circle that is a mirrored copy of the original circle.
        """
        return Circle(self.origin, self.radius, -self._reference, -self._axis)

    def project_point(self, point: Point3D) -> "CircleEvaluation":
        """Project a point onto the circle and evauate the circle.

        Parameters
        ----------
        point : Point3D
            Point to project onto the circle.

        Returns
        -------
        CircleEvaluation
            Resulting evaluation.
        """
        origin_to_point = point - self.origin
        dir_in_plane = UnitVector3D.from_points(
            Point3D([0, 0, 0]), origin_to_point - ((origin_to_point * self.dir_z) * self.dir_z)
        )
        if dir_in_plane.is_zero:
            return CircleEvaluation(self, 0)

        t = np.arctan2(self.dir_y.dot(dir_in_plane), self.dir_x.dot(dir_in_plane))
        return CircleEvaluation(self, t)

    def is_coincident_circle(self, other: "Circle") -> bool:
        """Determine if the circle is coincident with another.

        Parameters
        ----------
        other : Circle
            Circle to determine coincidence with.

        Returns
        -------
        bool
            ``True`` if this circle is coincident with the other, ``False`` otherwise.
        """
        return (
            Accuracy.length_is_equal(self.radius.m, other.radius.m)
            and self.origin == other.origin
            and self.dir_z == other.dir_z
        )

    def parameterization(self) -> Parameterization:
        """Get the parametrization of the circle.

        The parameter of a circle specifies the clockwise angle around the axis
        (right-hand corkscrew law), with a zero parameter at ``dir_x`` and a
        period of 2*pi.

        Returns
        -------
        Parameterization
            Information about how the circle is parameterized.
        """
        return Parameterization(ParamForm.PERIODIC, ParamType.CIRCULAR, Interval(0, 2 * np.pi))

    def contains_param(self, param: Real) -> bool:  # noqa: D102
        raise NotImplementedError("contains_param() is not implemented.")

    def contains_point(self, point: Point3D) -> bool:  # noqa: D102
        raise NotImplementedError("contains_point() is not implemented.")


class CircleEvaluation(CurveEvaluation):
    """Provides evaluation of a circle at a given parameter.

    Parameters
    ----------
    circle: ~ansys.geometry.core.shapes.curves.circle.Circle
        Circle to evaluate.
    parameter: Real
        Parameter to evaluate the circle at.
    """

    def __init__(self, circle: Circle, parameter: Real) -> None:
        """``CircleEvaluation`` class constructor."""
        self._circle = circle
        self._parameter = parameter

    @property
    def circle(self) -> Circle:
        """Circle being evaluated."""
        return self._circle

    @property
    def parameter(self) -> Real:
        """Parameter that the evaluation is based upon."""
        return self._parameter

    @cached_property
    def position(self) -> Point3D:
        """Position of the evaluation.

        Returns
        -------
        Point3D
            Point that lies on the circle at this evaluation.
        """
        return (
            self.circle.origin
            + ((self.circle.radius * np.cos(self.parameter)) * self.circle.dir_x).m
            + ((self.circle.radius * np.sin(self.parameter)) * self.circle.dir_y).m
        )

    @cached_property
    def tangent(self) -> UnitVector3D:
        """Tangent of the evaluation.

        Returns
        -------
        UnitVector3D
            Tangent unit vector to the circle at this evaluation.
        """
        return (
            np.cos(self.parameter) * self.circle.dir_y - np.sin(self.parameter) * self.circle.dir_x
        )

    @cached_property
    def normal(self) -> UnitVector3D:
        """Normal to the circle.

        Returns
        -------
        UnitVector3D
            Normal unit vector to the circle at this evaluation.
        """
        return UnitVector3D(
            np.cos(self.parameter) * self.circle.dir_x + np.sin(self.parameter) * self.circle.dir_y
        )

    @cached_property
    def first_derivative(self) -> Vector3D:
        """First derivative of the evaluation.

        The first derivative is in the direction of the tangent and has a
        magnitude equal to the velocity (rate of change of position) at that
        point.

        Returns
        -------
        Vector3D
            First derivative of the evaluation.
        """
        return self.circle.radius.m * (
            np.cos(self.parameter) * self.circle.dir_y - np.sin(self.parameter) * self.circle.dir_x
        )

    @cached_property
    def second_derivative(self) -> Vector3D:
        """Second derivative of the evaluation.

        Returns
        -------
        Vector3D
            Second derivative of the evaluation.
        """
        return -self.circle.radius.m * (
            np.cos(self.parameter) * self.circle.dir_x + np.sin(self.parameter) * self.circle.dir_y
        )

    @cached_property
    def curvature(self) -> Real:
        """Curvature of the circle.

        Returns
        -------
        Real
            Curvature of the circle.
        """
        return 1 / np.abs(self.circle.radius.m)
