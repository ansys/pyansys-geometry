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
"""Provides for creating and managing an ellipse."""

from functools import cached_property

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np
from pint import Quantity
from scipy.integrate import quad

from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Z
from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.accuracy import Accuracy
from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.primitives.curve_evaluation import CurveEvaluation
from ansys.geometry.core.primitives.parameterization import (
    Interval,
    Parameterization,
    ParamForm,
    ParamType,
)
from ansys.geometry.core.typing import Real, RealSequence


class Ellipse:
    """
    Provides 3D ellipse representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Origin of the ellipse.
    major_radius : Union[Quantity, Distance, Real]
        Major radius of the ellipse.
    minor_radius : Union[Quantity, Distance, Real]
        Minor radius of the ellipse.
    reference : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-axis direction.
    axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Z-axis direction.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        major_radius: Union[Quantity, Distance, Real],
        minor_radius: Union[Quantity, Distance, Real],
        reference: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        axis: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Z,
    ):
        """Initialize the ``Ellipse`` class."""
        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin

        self._reference = (
            UnitVector3D(reference) if not isinstance(reference, UnitVector3D) else reference
        )
        self._axis = UnitVector3D(axis) if not isinstance(axis, UnitVector3D) else axis

        if not self._reference.is_perpendicular_to(self._axis):
            raise ValueError(
                "Ellipse reference (x-direction) and axis (z-direction) must be perpendicular."
            )

        self._major_radius = (
            major_radius if isinstance(major_radius, Distance) else Distance(major_radius)
        )
        self._minor_radius = (
            minor_radius if isinstance(minor_radius, Distance) else Distance(minor_radius)
        )

        if self._major_radius.value.m_as(self._major_radius.base_unit) <= 0:
            raise ValueError("Major radius must be a real positive value.")
        if self._minor_radius.value.m_as(self._minor_radius.base_unit) <= 0:
            raise ValueError("Minor radius must be a real positive value.")

        # Align both units if misaligned
        if self._major_radius.unit != self._minor_radius.unit:
            self._minor_radius.unit = self._major_radius.unit

        # Ensure that the major radius is equal or larger than the minor one
        if self._major_radius.value.m < self._minor_radius.value.m:
            raise ValueError("Major radius cannot be shorter than the minor radius.")

    @property
    def origin(self) -> Point3D:
        """Origin of the ellipse."""
        return self._origin

    @property
    def major_radius(self) -> Quantity:
        """Major radius of the ellipse."""
        return self._major_radius.value

    @property
    def minor_radius(self) -> Quantity:
        """Minor radius of the ellipse."""
        return self._minor_radius.value

    @property
    def dir_x(self) -> UnitVector3D:
        """X-direction of the ellipse."""
        return self._reference

    @property
    def dir_y(self) -> UnitVector3D:
        """Y-direction of the ellipse."""
        return self.dir_z.cross(self.dir_x)

    @property
    def dir_z(self) -> UnitVector3D:
        """Z-direction of the ellipse."""
        return self._axis

    @check_input_types
    def __eq__(self, other: "Ellipse") -> bool:
        """Equals operator for the ``Ellipse`` class."""
        return (
            self._origin == other._origin
            and self._major_radius == other._major_radius
            and self._minor_radius == other._minor_radius
            and self._reference == other._reference
            and self._axis == other._axis
        )

    def mirrored_copy(self) -> "Ellipse":
        """
        Create a mirrored copy of the ellipse along the y-axis.

        Returns
        -------
        Ellipse
            New ellipse that is a mirrored copy of the original ellipse.
        """
        return Ellipse(
            self.origin, self.major_radius, self.minor_radius, -self._reference, -self._axis
        )

    def evaluate(self, parameter: Real) -> "EllipseEvaluation":
        """
        Evaluate the ellipse at the given parameter.

        Parameters
        ----------
        parameter : Real
            Parameter to evaluate the ellipse at.

        Returns
        -------
        EllipseEvaluation
            Resulting evaluation.
        """
        return EllipseEvaluation(self, parameter)

    def project_point(self, point: Point3D) -> "EllipseEvaluation":
        """
        Project a point onto the ellipse and evaluate the ellipse.

        Parameters
        ----------
        point : Point3D
            Point to project onto the ellipse.

        Returns
        -------
        EllipseEvaluation
            Resulting evaluation.
        """
        origin_to_point = point - self.origin
        dir_in_plane = UnitVector3D.from_points(
            Point3D([0, 0, 0]), origin_to_point - ((origin_to_point * self.dir_z) * self.dir_z)
        )
        if dir_in_plane.is_zero:
            return EllipseEvaluation(self, 0)

        t = np.arctan2(
            self.dir_y.dot(dir_in_plane) * self.major_radius.m,
            self.dir_x.dot(dir_in_plane) * self.minor_radius.m,
        )
        return EllipseEvaluation(self, t)

    def is_coincident_ellipse(self, other: "Ellipse") -> bool:
        """
        Determine if this ellipse is coincident with another.

        Parameters
        ----------
        other : Ellipse
            Ellipse to determine coincidence with.

        Returns
        -------
        bool
            ``True`` if this ellipse is coincident with the other, ``False`` otherwise.
        """
        return (
            Accuracy.length_is_equal(self.major_radius.m, other.major_radius.m)
            and Accuracy.length_is_equal(self.minor_radius.m, other.minor_radius.m)
            and self.origin == other.origin
            and self.dir_z == other.dir_z
        )

    @property
    def eccentricity(self) -> Real:
        """Eccentricity of the ellipse."""
        ecc = (self.major_radius.m**2 - self.minor_radius.m**2) ** 0.5 / self.major_radius.m
        if ecc == 1:
            raise ValueError("The curve defined is a parabola and not an ellipse.")
        elif ecc > 1:
            raise ValueError("The curve defined is an hyperbola and not an ellipse.")
        return ecc

    @property
    def linear_eccentricity(self) -> Quantity:
        """
        Linear eccentricity of the ellipse.

        Notes
        -----
        The linear eccentricity is the distance from the center to the focus.
        """
        return (self.major_radius**2 - self.minor_radius**2) ** 0.5

    @property
    def semi_latus_rectum(self) -> Quantity:
        """Semi-latus rectum of the ellipse."""
        return self.minor_radius**2 / self.major_radius

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the ellipse."""

        def integrand(theta, ecc):
            return np.sqrt(1 - (ecc * np.sin(theta)) ** 2)

        I, _ = quad(integrand, 0, np.pi / 2, args=(self.eccentricity,))
        return 4 * self.major_radius * I

    @property
    def area(self) -> Quantity:
        """Area of the ellipse."""
        return np.pi * self.major_radius * self.minor_radius

    def transformed_copy(self, matrix: Matrix44) -> "Ellipse":
        """
        Create a transformed copy of the ellipse based on a transformation matrix.

        Parameters
        ----------
        matrix : Matrix44
            4x4 transformation matrix to apply to the ellipse.

        Returns
        -------
        Ellipse
            New ellipse that is the transformed copy of the original ellipse.
        """
        new_point = self.origin.transform(matrix)
        new_reference = self._reference.transform(matrix)
        new_axis = self._axis.transform(matrix)
        return Ellipse(
            new_point,
            self.major_radius,
            self.minor_radius,
            UnitVector3D(new_reference[0:3]),
            UnitVector3D(new_axis[0:3]),
        )

    def get_parameterization(self) -> Parameterization:
        """
        Get the parametrization of the ellipse.

        The parameter of an ellipse specifies the clockwise angle around the axis
        (right-hand corkscrew law), with a zero parameter at ``dir_x`` and a period of 2*pi.

        Returns
        -------
        Parameterization
            Information about how the ellipse is parameterized.
        """
        return Parameterization(ParamForm.PERIODIC, ParamType.OTHER, Interval(0, 2 * np.pi))


class EllipseEvaluation(CurveEvaluation):
    """
    Evaluate an ellipse at a given parameter.

    Parameters
    ----------
    ellipse: Ellipse
        Ellipse to evaluate.
    parameter: float, int
        Parameter to evaluate the ellipse at.
    """

    def __init__(self, ellipse: Ellipse, parameter: Real) -> None:
        """``Initialize the ``EllipseEvaluation`` class."""
        self._ellipse = ellipse
        self._parameter = parameter

    @property
    def ellipse(self) -> Ellipse:
        """Ellipse being evaluated."""
        return self._ellipse

    @property
    def parameter(self) -> Real:
        """Parameter that the evaluation is based upon."""
        return self._parameter

    @cached_property
    def position(self) -> Point3D:
        """
        Position of the evaluation.

        Returns
        -------
        Point3D
            Point that lies on the ellipse at this evaluation.
        """
        return (
            self.ellipse.origin
            + ((self.ellipse.major_radius * np.cos(self.parameter)) * self.ellipse.dir_x).m
            + ((self.ellipse.minor_radius * np.sin(self.parameter)) * self.ellipse.dir_y).m
        )

    @cached_property
    def tangent(self) -> UnitVector3D:
        """
        Tangent of the evaluation.

        Returns
        -------
        UnitVector3D
            Tangent unit vector to the ellipse at this evaluation.
        """
        return (
            (self.ellipse.minor_radius * np.cos(self.parameter) * self.ellipse.dir_y).m
            - (self.ellipse.major_radius * np.sin(self.parameter) * self.ellipse.dir_x).m
        ).normalize()

    @cached_property
    def normal(self) -> UnitVector3D:
        """
        Normal of the evaluation.

        Returns
        -------
        UnitVector3D
            Normal unit vector to the ellipse at this evaluation.
        """
        return UnitVector3D.from_points(self.ellipse.origin, self.position)

    @cached_property
    def first_derivative(self) -> Vector3D:
        """
        Girst derivative of the evaluation.

        The first derivative is in the direction of the tangent and has a magnitude
        equal to the velocity (rate of change of position) at that point.

        Returns
        -------
        Vector3D
            First derivative of the evaluation.
        """
        return (self.ellipse.minor_radius * np.cos(self.parameter) * self.ellipse.dir_y).m - (
            self.ellipse.major_radius * np.sin(self.parameter) * self.ellipse.dir_x
        ).m

    @cached_property
    def second_derivative(self) -> Vector3D:
        """
        Second derivative of the evaluation.

        Returns
        -------
        Vector3D
            Second derivative of the evaluation.
        """
        return (
            -self.ellipse.major_radius * np.cos(self.parameter) * self.ellipse.dir_x
            - self.ellipse.minor_radius * np.sin(self.parameter) * self.ellipse.dir_y
        ).m

    @cached_property
    def curvature(self) -> Real:
        """
        Curvature of the ellipse.

        Returns
        -------
        Real
            Curvature of the ellipse.
        """
        return self.second_derivative.magnitude / np.power(self.first_derivative.magnitude, 2)
