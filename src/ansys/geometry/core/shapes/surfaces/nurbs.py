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
"""Provides for creating and managing a NURBS surface."""

from functools import cached_property
from typing import TYPE_CHECKING

from beartype import beartype as check_input_types

from ansys.geometry.core.math import Point3D
from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Z
from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.shapes.parameterization import (
    Interval,
    Parameterization,
    ParamForm,
    ParamType,
    ParamUV,
)
from ansys.geometry.core.shapes.surfaces.surface import Surface
from ansys.geometry.core.shapes.surfaces.surface_evaluation import SurfaceEvaluation
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    import geomdl.NURBS as geomdl_nurbs  # noqa: N811


class NURBSSurface(Surface):
    """Represents a NURBS surface.

    Notes
    -----
    This class is a wrapper around the NURBS surface class from the `geomdl` library.
    By leveraging the `geomdl` library, this class provides a high-level interface
    to create and manipulate NURBS surfaces. The `geomdl` library is a powerful
    library for working with NURBS curves and surfaces. For more information, see
    https://pypi.org/project/geomdl/.

    """

    def __init__(
        self,
        origin: Point3D,
        reference: UnitVector3D,
        axis: UnitVector3D,
        geomdl_object: "geomdl_nurbs.Surface" = None,
    ):
        """Initialize ``NURBSSurface`` class."""
        try:
            import geomdl.NURBS as geomdl_nurbs  # noqa: N811
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "The `geomdl` library is required to use the NURBSSurface class. "
                "Please install it using `pip install geomdl`."
            ) from e

        self._nurbs_surface = geomdl_object if geomdl_object else geomdl_nurbs.Surface()
        self._origin = Point3D([0.0, 0.0, 0.0])
        self._reference = UNITVECTOR3D_X
        self._axis = UNITVECTOR3D_Z

    @property
    def geomdl_nurbs_surface(self) -> "geomdl_nurbs.Surface":
        """Get the underlying `geomdl` NURBS surface object.

        Notes
        -----
        This property gives access to the full functionality of the NURBS surface
        coming from the `geomdl` library. Use with caution.
        """
        return self._nurbs_surface

    @property
    def control_points(self) -> list[Point3D]:
        """Get the control points of the NURBS surface."""
        return [Point3D(pt) for pt in self._nurbs_surface.ctrlpts]

    @property
    def degree_u(self) -> int:
        """Get the degree of the surface in the U direction."""
        return self._nurbs_surface.degree_u

    @property
    def degree_v(self) -> int:
        """Get the degree of the surface in the V direction."""
        return self._nurbs_surface.degree_v

    @property
    def knotvector_u(self) -> list[Real]:
        """Get the knot vector for the u-direction of the surface."""
        return self._nurbs_surface.knotvector_u

    @property
    def knotvector_v(self) -> list[Real]:
        """Get the knot vector for the v-direction of the surface."""
        return self._nurbs_surface.knotvector_v

    @property
    def weights(self) -> list[Real]:
        """Get the weights of the control points."""
        return self._nurbs_surface.weights
    
    @property
    def origin(self) -> Point3D:
        """Get the origin of the surface."""
        return self._origin
    
    @property
    def dir_x(self) -> UnitVector3D:
        """Get the reference direction of the surface."""
        return self._reference
    
    @property
    def dir_z(self) -> UnitVector3D:
        """Get the axis direction of the surface."""
        return self._axis

    @classmethod
    @check_input_types
    def from_control_points(
        cls,
        degree_u: int,
        degree_v: int,
        knots_u: list[Real],
        knots_v: list[Real],
        control_points: list[Point3D],
        weights: list[Real] = None,
        origin: Point3D = Point3D([0.0, 0.0, 0.0]),
        reference: UnitVector3D = UNITVECTOR3D_X,
        axis: UnitVector3D = UNITVECTOR3D_Z,
    ) -> "NURBSSurface":
        """Create a NURBS surface from control points and knot vectors.

        Parameters
        ----------
        degree_u : int
            Degree of the surface in the U direction.
        degree_v : int
            Degree of the surface in the V direction.
        knots_u : list[Real]
            Knot vector for the U direction.
        knots_v : list[Real]
            Knot vector for the V direction.
        control_points : list[Point3D]
            Control points for the surface.
        weights : list[Real], optional
            Weights for the control points. If not provided, all weights are set to 1.
        delta : float, optional
            Evaluation delta for the surface. Default is 0.01.
        origin : Point3D, optional
            Origin of the surface. Default is (0, 0, 0).
        reference : UnitVector3D, optional
            Reference direction of the surface. Default is (1, 0, 0).
        axis : UnitVector3D, optional
            Axis direction of the surface. Default is (0, 0, 1).

        Returns
        -------
        NURBSSurface
            Created NURBS surface.
        """
        nurbs_surface = cls(origin, reference, axis)
        nurbs_surface._nurbs_surface.degree_u = degree_u
        nurbs_surface._nurbs_surface.degree_v = degree_v

        nurbs_surface._nurbs_surface.ctrlpts_size_u = len(knots_u) - degree_u - 1
        nurbs_surface._nurbs_surface.ctrlpts_size_v = len(knots_v) - degree_v - 1

        # If no weights are provided, set all weights to 1.0
        if not weights:
            weights = [1.0] * len(control_points)
        ctrlpts_homogenous = [[*pt, w] for (pt, w) in zip(control_points, weights)]

        nurbs_surface._nurbs_surface.set_ctrlpts(
            ctrlpts_homogenous,
            nurbs_surface._nurbs_surface.ctrlpts_size_u,
            nurbs_surface._nurbs_surface.ctrlpts_size_v,
        )

        nurbs_surface._nurbs_surface.knotvector_u = knots_u
        nurbs_surface._nurbs_surface.knotvector_v = knots_v

        # Verify the surface is valid
        try:
            nurbs_surface._nurbs_surface._check_variables()
        except ValueError as e:
            raise ValueError(f"Invalid NURBS surface: {e}")
        return nurbs_surface

    @classmethod
    @check_input_types
    def fit_surface_from_points(
        cls,
        points: list[Point3D],
        size_u: int,
        size_v: int,
        degree_u: int,
        degree_v: int,
        origin: Point3D = Point3D([0.0, 0.0, 0.0]),
        reference: UnitVector3D = UNITVECTOR3D_X,
        axis: UnitVector3D = UNITVECTOR3D_Z,
    ) -> "NURBSSurface":
        """Fit a NURBS surface to a set of points.

        Parameters
        ----------
        points : list[Point3D]
            Points to fit the surface to.
        size_u : int
            Number of control points in the U direction.
        size_v : int
            Number of control points in the V direction.
        degree_u : int
            Degree of the surface in the U direction.
        degree_v : int
            Degree of the surface in the V direction.
        origin : Point3D, optional
            Origin of the surface. Default is (0, 0, 0).
        reference : UnitVector3D, optional
            Reference direction of the surface. Default is (1, 0, 0).
        axis : UnitVector3D, optional
            Axis direction of the surface. Default is (0, 0, 1).

        Returns
        -------
        NURBSSurface
            Fitted NURBS surface.
        """
        from geomdl import fitting

        converted_pts = [[*pt] for pt in points]

        surface = fitting.interpolate_surface(
            converted_pts,
            size_u=size_u,
            size_v=size_v,
            degree_u=degree_u,
            degree_v=degree_v,
        )

        nurbs_surface = cls(origin, reference, axis)
        nurbs_surface._nurbs_surface.degree_u = degree_u
        nurbs_surface._nurbs_surface.degree_v = degree_v

        nurbs_surface._nurbs_surface.ctrlpts_size_u = surface.ctrlpts_size_u
        nurbs_surface._nurbs_surface.ctrlpts_size_v = surface.ctrlpts_size_v
        nurbs_surface._nurbs_surface.ctrlpts = surface.ctrlpts
        nurbs_surface._nurbs_surface.knotvector = surface.knotvector
        nurbs_surface._nurbs_surface.weights = surface.weights

        return nurbs_surface

    def __eq__(self, other: "NURBSSurface") -> bool:
        """Determine if two surfaces are equal."""
        if not isinstance(other, NURBSSurface):
            return False
        return (
            self._nurbs_surface.degree == other._nurbs_surface.degree
            and self._nurbs_surface.ctrlpts == other._nurbs_surface.ctrlpts
            and self._nurbs_surface.knotvector == other._nurbs_surface.knotvector
            and self._nurbs_surface.weights == other._nurbs_surface.weights
        )

    def parameterization(self) -> tuple[Parameterization, Parameterization]:
        """Get the parametrization of the NURBS surface.

        The parameter is defined in the interval [0, 1] by default. Information
        is provided about the parameter type and form.

        Returns
        -------
        tuple[Parameterization, Parameterization]
            Parameterization in the U and V directions respectively.
        """
        return (
            Parameterization(
                ParamForm.OTHER,
                ParamType.OTHER,
                Interval(
                    start=self._nurbs_surface.domain[0][0], end=self._nurbs_surface.domain[0][1]
                ),
            ),
            Parameterization(
                ParamForm.OTHER,
                ParamType.OTHER,
                Interval(
                    start=self._nurbs_surface.domain[1][0],
                    end=self._nurbs_surface.domain[1][1],
                ),
            ),
        )

    def transformed_copy(self, matrix: Matrix44) -> "NURBSSurface":  # noqa: D102
        raise NotImplementedError("transformed_copy() is not implemented.")

    def evaluate(self, parameter: ParamUV) -> SurfaceEvaluation:
        """Evaluate the surface at the given parameter.

        Parameters
        ----------
        parameter : ParamUV
            Parameter to evaluate the surface at.

        Returns
        -------
        SurfaceEvaluation
            Evaluation of the surface at the given parameter.
        """
        return NURBSSurfaceEvaluation(self, parameter)

    def contains_param(self, param: ParamUV) -> bool:  # noqa: D102
        raise NotImplementedError("contains_param() is not implemented.")

    def contains_point(self, point: Point3D) -> bool:  # noqa: D102
        raise NotImplementedError("contains_point() is not implemented.")

    def project_point(self, point: Point3D) -> SurfaceEvaluation:  # noqa: D102
        raise NotImplementedError("project_point() is not implemented.")


class NURBSSurfaceEvaluation(SurfaceEvaluation):
    """Provides evaluation of a NURBS surface at a given parameter.

    Parameters
    ----------
    nurbs_surface: ~ansys.geometry.core.shapes.surfaces.nurbs.NURBSSurface
        NURBS surface to evaluate.
    parameter: Real
        Parameter to evaluate the NURBS surface at.
    """

    def __init__(self, nurbs_surface: NURBSSurface, parameter: ParamUV) -> None:
        """Initialize the ``NURBSsurfaceEvaluation`` class."""
        self._surface = nurbs_surface
        self._parameter = parameter

        u, v = parameter.u, parameter.v
        domain = nurbs_surface._nurbs_surface.domain
        u_start, u_end = domain[0][0], domain[0][1]
        v_start, v_end = domain[1][0], domain[1][1]

        if not (u_start <= u <= u_end and v_start <= v <= v_end):
            raise ValueError(
                f"Parameter [u={u}, v={v}] is outside the surface domain: "
                f"U[{u_start}, {u_end}], V[{v_start}, {v_end}]"
            )
        self._derivatives = nurbs_surface.geomdl_nurbs_surface.derivatives(u, v, 2)

    @property
    def surface(self) -> "NURBSSurface":
        """Surface being evaluated."""
        return self._surface

    @property
    def parameter(self) -> ParamUV:
        """Parameter the evaluation is based upon."""
        return self._parameter

    @cached_property
    def position(self) -> Point3D:
        """Position of the evaluation.

        Returns
        -------
        Point3D
            Point on the surface at this evaluation.
        """
        return Point3D(self._derivatives[0][0])

    @cached_property
    def normal(self) -> UnitVector3D:
        """Normal to the surface.

        Returns
        -------
        UnitVector3D
            Normal to the surface at this evaluation.
        """
        from geomdl.operations import normal

        uv = [float(self._parameter.u), float(self._parameter.v)]
        result = normal(self._surface.geomdl_nurbs_surface, uv)

        return UnitVector3D(result[1])

    @cached_property
    def u_derivative(self) -> Vector3D:
        """First derivative with respect to the U parameter.

        Returns
        -------
        Vector3D
            First derivative with respect to the U parameter at this evaluation.
        """
        return Vector3D(self._derivatives[1][0])

    @cached_property
    def v_derivative(self) -> Vector3D:
        """First derivative with respect to the V parameter.

        Returns
        -------
        Vector3D
            First derivative with respect to the V parameter at this evaluation.
        """
        return Vector3D(self._derivatives[0][1])

    @cached_property
    def uu_derivative(self) -> Vector3D:
        """Second derivative with respect to the U parameter.

        Returns
        -------
        Vector3D
            Second derivative with respect to the U parameter at this evaluation.
        """
        return Vector3D(self._derivatives[2][0])

    @cached_property
    def uv_derivative(self) -> Vector3D:
        """The second derivative with respect to the U and V parameters.

        Returns
        -------
        Vector3D
            Second derivative with respect to the U and V parameters at this evaluation.
        """
        return Vector3D(self._derivatives[1][1])

    @cached_property
    def vv_derivative(self) -> Vector3D:
        """The second derivative with respect to v.

        Returns
        -------
        Vector3D
            Second derivative with respect to the V parameter at this evaluation.
        """
        return Vector3D(self._derivatives[0][2])

    @cached_property
    def min_curvature(self) -> Real:
        """Minimum curvature."""
        raise NotImplementedError("min_curvature() is not implemented.")

    @cached_property
    def min_curvature_direction(self) -> UnitVector3D:
        """Minimum curvature direction."""
        raise NotImplementedError("min_curvature_direction() is not implemented.")

    @cached_property
    def max_curvature(self) -> Real:
        """Maximum curvature."""
        raise NotImplementedError("max_curvature() is not implemented.")

    @cached_property
    def max_curvature_direction(self) -> UnitVector3D:
        """Maximum curvature direction."""
        raise NotImplementedError("max_curvature_direction() is not implemented.")
