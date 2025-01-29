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
"""Provides for creating and managing a NURBS curve."""

from functools import cached_property
from typing import Optional

from beartype import beartype as check_input_types
import geomdl.NURBS as geomdl_nurbs  # noqa: N811

from ansys.geometry.core.math import Matrix44, Point3D
from ansys.geometry.core.math.vector import Vector3D
from ansys.geometry.core.shapes.curves.curve import Curve
from ansys.geometry.core.shapes.curves.curve_evaluation import CurveEvaluation
from ansys.geometry.core.shapes.parameterization import (
    Interval,
    Parameterization,
    ParamForm,
    ParamType,
)
from ansys.geometry.core.typing import Real


class NURBSCurve(Curve):
    """Represents a NURBS curve.

    Notes
    -----
    This class is a wrapper around the NURBS curve class from the `geomdl` library.
    By leveraging the `geomdl` library, this class provides a high-level interface
    to create and manipulate NURBS curves. The `geomdl` library is a powerful
    library for working with NURBS curves and surfaces. For more information, see
    https://pypi.org/project/geomdl/.

    """

    def __init__(
        self,
    ):
        """Initialize ``NURBSCurve`` class."""
        self._nurbs_curve = geomdl_nurbs.Curve()

    @property
    def geomdl_nurbs_curve(self) -> geomdl_nurbs.Curve:
        """Get the underlying NURBS curve.

        Notes
        -----
        This property gives access to the full functionality of the NURBS curve
        coming from the `geomdl` library. Use with caution.
        """
        return self._nurbs_curve

    @property
    def control_points(self) -> list[Point3D]:
        """Get the control points of the curve."""
        return [Point3D(point) for point in self._nurbs_curve.ctrlpts]

    @property
    def degree(self) -> int:
        """Get the degree of the curve."""
        return self._nurbs_curve.degree

    @property
    def knots(self) -> list[Real]:
        """Get the knot vector of the curve."""
        return self._nurbs_curve.knotvector

    @property
    def weights(self) -> list[Real]:
        """Get the weights of the control points."""
        return self._nurbs_curve.weights

    @classmethod
    @check_input_types
    def from_control_points(
        cls,
        control_points: list[Point3D],
        degree: int,
        knots: list[Real],
        weights: list[Real] = None,
    ) -> "NURBSCurve":
        """Create a NURBS curve from control points.

        Parameters
        ----------
        control_points : list[Point3D]
            Control points of the curve.
        degree : int
            Degree of the curve.
        knots : list[Real]
            Knot vector of the curve.
        weights : list[Real], optional
            Weights of the control points.

        Returns
        -------
        NURBSCurve
            NURBS curve.

        """
        curve = cls()
        curve._nurbs_curve.degree = degree
        curve._nurbs_curve.ctrlpts = control_points
        curve._nurbs_curve.knotvector = knots
        if weights:
            curve._nurbs_curve.weights = weights

        # Verify the curve is valid
        try:
            curve._nurbs_curve._check_variables()
        except ValueError as e:
            raise ValueError(f"Invalid NURBS curve: {e}")

        return curve

    def __eq__(self, other: "NURBSCurve") -> bool:
        """Determine if two curves are equal."""
        if not isinstance(other, NURBSCurve):
            return False
        return (
            self._nurbs_curve.degree == other._nurbs_curve.degree
            and self._nurbs_curve.ctrlpts == other._nurbs_curve.ctrlpts
            and self._nurbs_curve.knotvector == other._nurbs_curve.knotvector
            and self._nurbs_curve.weights == other._nurbs_curve.weights
        )

    def parameterization(self) -> Parameterization:
        """Get the parametrization of the NURBS curve.

        The parameter is defined in the interval [0, 1] by default. Information
        is provided about the parameter type and form.

        Returns
        -------
        Parameterization
            Information about how the NURBS curve is parameterized.
        """
        return Parameterization(
            ParamType.OTHER,
            ParamForm.OTHER,
            Interval(start=self._nurbs_curve.domain[0], end=self._nurbs_curve.domain[1]),
        )

    def transformed_copy(self, matrix: Matrix44) -> "NURBSCurve":
        """Create a transformed copy of the curve.

        Parameters
        ----------
        matrix : Matrix44
            Transformation matrix.

        Returns
        -------
        NURBSCurve
            Transformed copy of the curve.
        """
        control_points = [matrix @ point for point in self._nurbs_curve.ctrlpts]
        return NURBSCurve.from_control_points(
            control_points,
            self._nurbs_curve.degree,
            self._nurbs_curve.knotvector,
            self._nurbs_curve.weights,
        )

    def evaluate(self, parameter: Real) -> CurveEvaluation:
        """Evaluate the curve at the given parameter.

        Parameters
        ----------
        parameter : Real
            Parameter to evaluate the curve at.

        Returns
        -------
        CurveEvaluation
            Evaluation of the curve at the given parameter.
        """
        return NURBSCurveEvaluation(self, parameter)

    def contains_param(self, param: Real) -> bool:  # noqa: D102
        raise NotImplementedError("contains_param() is not implemented.")

    def contains_point(self, point: Point3D) -> bool:  # noqa: D102
        raise NotImplementedError("contains_point() is not implemented.")

    def project_point(
        self, point: Point3D, initial_guess: Optional[Real] = None
    ) -> CurveEvaluation:
        """Project a point to the NURBS curve.

        This method returns the evaluation at the closest point.

        Notes
        -----
        Based on `the NURBS book <https://link.springer.com/book/10.1007/978-3-642-59223-2>`_,
        the projection of a point to a NURBS curve is the solution to the following optimization
        problem: minimize the distance between the point and the curve. The distance is defined
        as the Euclidean distance squared. For more information, please refer to
        the implementation of the `distance_squared` function.

        Parameters
        ----------
        point : Point3D
            Point to project to the curve.
        initial_guess : Real, optional
            Initial guess for the optimization algorithm. If not provided, the midpoint
            of the domain is used.

        Returns
        -------
        CurveEvaluation
            Evaluation at the closest point on the curve.

        """
        import numpy as np
        from scipy.optimize import minimize

        # Function to minimize (distance squared)
        def distance_squared(
            u: float, geomdl_nurbs_curbe: geomdl_nurbs.Curve, point: np.ndarray
        ) -> np.ndarray:
            point_on_curve = np.array(geomdl_nurbs_curbe.evaluate_single(u))
            return np.sum((point_on_curve - point) ** 2)

        # Define the domain and initial guess (midpoint of the domain by default)
        domain = self._nurbs_curve.domain
        initial_guess = initial_guess if initial_guess else (domain[0] + domain[1]) / 2

        # Minimize the distance squared
        result = minimize(
            distance_squared,
            initial_guess,
            bounds=[domain],
            args=(self._nurbs_curve, np.array(point)),
        )

        # Closest point on the curve
        u_min = result.x[0]

        # Return the evaluation at the closest point
        return self.evaluate(u_min)


class NURBSCurveEvaluation(CurveEvaluation):
    """Provides evaluation of a NURBS curve at a given parameter.

    Parameters
    ----------
    nurbs_curve: ~ansys.geometry.core.shapes.curves.nurbs.NURBSCurve
        NURBS curve to evaluate.
    parameter: Real
        Parameter to evaluate the NURBS curve at.
    """

    def __init__(self, nurbs_curve: NURBSCurve, parameter: Real) -> None:
        """Initialize the ``NURBSCurveEvaluation`` class."""
        self._parameter = parameter
        self._point_eval, self._first_deriv_eval, self._second_deriv_eval = (
            nurbs_curve.geomdl_nurbs_curve.derivatives(parameter, 2)
        )

    @property
    def parameter(self) -> Real:
        """Parameter that the evaluation is based upon."""
        return self._parameter

    @cached_property
    def position(self) -> Point3D:
        """Position of the evaluation."""
        return Point3D(self._point_eval)

    @cached_property
    def first_derivative(self) -> Vector3D:
        """First derivative of the evaluation."""
        return Vector3D(self._first_deriv_eval)

    @cached_property
    def second_derivative(self) -> Vector3D:
        """Second derivative of the evaluation."""
        return Vector3D(self._second_deriv_eval)

    @cached_property
    def curvature(self) -> Real:
        """Curvature of the evaluation."""
        # For a curve, the curvature is the magnitude of the cross product
        # of the first and second derivatives divided by the cube of the
        # magnitude of the first derivative. For more information, please refer
        # to https://en.wikipedia.org/wiki/Curvature#General_expressions.
        return (
            self.first_derivative.cross(self.second_derivative).magnitude
            / self.first_derivative.magnitude**3
        )
