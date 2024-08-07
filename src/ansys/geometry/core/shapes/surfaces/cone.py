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
"""Provides for creating and managing a cone."""

from functools import cached_property

from beartype import beartype as check_input_types
import numpy as np
from pint import Quantity

from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Z
from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.measurements import Angle, Distance
from ansys.geometry.core.shapes.curves.line import Line
from ansys.geometry.core.shapes.parameterization import (
    Interval,
    Parameterization,
    ParamForm,
    ParamType,
    ParamUV,
)
from ansys.geometry.core.shapes.surfaces.surface import Surface
from ansys.geometry.core.shapes.surfaces.surface_evaluation import SurfaceEvaluation
from ansys.geometry.core.typing import Real, RealSequence


class Cone(Surface):
    """Provides 3D cone representation.

    Parameters
    ----------
    origin : ~numpy.ndarray | RealSequence | Point3D
        Origin of the cone.
    radius : ~pint.Quantity | Distance | Real
        Radius of the cone.
    half_angle : ~pint.Quantity | Angle | Real
        Half angle of the apex, determining the upward angle.
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
        half_angle: Quantity | Angle | Real,
        reference: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_X,
        axis: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_Z,
    ):
        """Initialize the ``Cone`` class."""
        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin
        self._reference = (
            UnitVector3D(reference) if not isinstance(reference, UnitVector3D) else reference
        )
        self._axis = UnitVector3D(axis) if not isinstance(axis, UnitVector3D) else axis
        if not self._reference.is_perpendicular_to(self._axis):
            raise ValueError("Cone reference (dir_x) and axis (dir_z) must be perpendicular.")

        self._radius = radius if isinstance(radius, Distance) else Distance(radius)
        if self._radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

        self._half_angle = half_angle if isinstance(half_angle, Angle) else Angle(half_angle)

    @property
    def origin(self) -> Point3D:
        """Origin of the cone."""
        return self._origin

    @property
    def radius(self) -> Quantity:
        """Radius of the cone."""
        return self._radius.value

    @property
    def half_angle(self) -> Quantity:
        """Half angle of the apex."""
        return self._half_angle.value

    @property
    def dir_x(self) -> UnitVector3D:
        """X-direction of the cone."""
        return self._reference

    @property
    def dir_y(self) -> UnitVector3D:
        """Y-direction of the cone."""
        return self.dir_z.cross(self.dir_x)

    @property
    def dir_z(self) -> UnitVector3D:
        """Z-direction of the cone."""
        return self._axis

    @property
    def height(self) -> Quantity:
        """Height of the cone."""
        return np.abs(self.radius / np.tan(self.half_angle))

    @property
    def surface_area(self) -> Quantity:
        """Surface area of the cone."""
        return np.pi * self.radius * (self.radius + np.sqrt(self.height**2 + self.radius**2))

    @property
    def volume(self) -> Quantity:
        """Volume of the cone."""
        return np.pi * self.radius**2 * self.height / 3

    def transformed_copy(self, matrix: Matrix44) -> "Cone":
        """Create a transformed copy of the cone from a transformation matrix.

        Parameters
        ----------
        matrix : Matrix44
            4x4 transformation matrix to apply to the cone.

        Returns
        -------
        Cone
            New cone that is the transformed copy of the original cone.
        """
        new_point = self.origin.transform(matrix)
        new_reference = self._reference.transform(matrix)
        new_axis = self._axis.transform(matrix)
        return Cone(
            new_point,
            self.radius,
            self.half_angle,
            UnitVector3D(new_reference[0:3]),
            UnitVector3D(new_axis[0:3]),
        )

    def mirrored_copy(self) -> "Cone":
        """Create a mirrored copy of the cone along the y-axis.

        Returns
        -------
        Cone
            New cone that is a mirrored copy of the original cone.
        """
        return Cone(self.origin, self.radius, self.half_angle, -self._reference, -self._axis)

    @property
    def apex(self) -> Point3D:
        """Apex point of the cone."""
        return self.origin + self.apex_param * self.dir_z

    @property
    def apex_param(self) -> Real:
        """Apex parameter of the cone."""
        return -np.abs(self.radius.m) / np.tan(self.half_angle.m)

    @check_input_types
    def __eq__(self, other: "Cone") -> bool:
        """Equals operator for the ``Cone`` class."""
        return (
            self._origin == other._origin
            and self._radius == other._radius
            and self._half_angle == other._half_angle
            and self._reference == other._reference
            and self._axis == other._axis
        )

    def evaluate(self, parameter: ParamUV) -> "ConeEvaluation":
        """Evaluate the cone at given parameters.

        Parameters
        ----------
        parameter : ParamUV
            Parameters (u,v) to evaluate the cone at.

        Returns
        -------
        ConeEvaluation
            Resulting evaluation.
        """
        return ConeEvaluation(self, parameter)

    def project_point(self, point: Point3D) -> "ConeEvaluation":
        """Project a point onto the cone and evaluate the cone.

        Parameters
        ----------
        point : Point3D
            Point to project onto the cone.

        Returns
        -------
        ConeEvaluation
            Resulting evaluation.
        """
        u = np.arctan2(self.dir_y.dot(point - self.origin), self.dir_x.dot(point - self.origin))
        while u < 0:
            u += 2 * np.pi
        while u > 2 * np.pi:
            u -= 2 * np.pi
        axis = Line(self.origin, self.dir_z)
        line_eval = axis.project_point(point)
        v = line_eval.parameter

        cone_radius = self.radius.m + v * np.tan(self.half_angle.m)
        point_radius = np.linalg.norm(point - line_eval.position)
        dist_to_cone = (point_radius - cone_radius) * np.cos(self.half_angle.m)
        v += dist_to_cone * np.sin(self.half_angle.m)

        return ConeEvaluation(self, ParamUV(u, v))

    def parameterization(self) -> tuple[Parameterization, Parameterization]:
        """Parameterize the cone surface as a tuple (U and V respectively).

        The U parameter specifies the clockwise angle around the axis (right-hand
        corkscrew law), with a zero parameter at ``dir_x`` and a period of 2*pi.

        The V parameter specifies the distance along the axis, with a zero parameter at
        the XY plane of the cone.

        Returns
        -------
        tuple[Parameterization, Parameterization]
            Information about how a cone's u and v parameters are parameterized, respectively.
        """
        u = Parameterization(ParamForm.PERIODIC, ParamType.CIRCULAR, Interval(0, 2 * np.pi))

        start, end = (
            (self.apex_param, np.inf) if self.apex_param < 0 else (-np.inf, self.apex_param)
        )
        v = Parameterization(ParamForm.OPEN, ParamType.LINEAR, Interval(start, end))

        return (u, v)

    def contains_param(self, param_uv: ParamUV) -> bool:  # noqa: D102
        raise NotImplementedError("contains_param() is not implemented.")

    def contains_point(self, point: Point3D) -> bool:  # noqa: D102
        raise NotImplementedError("contains_point() is not implemented.")


class ConeEvaluation(SurfaceEvaluation):
    """Evaluate the cone at given parameters.

    Parameters
    ----------
    cone: ~ansys.geometry.core.shapes.surfaces.cone.Cone
        Cone to evaluate.
    parameter: ParamUV
        Pparameters (u, v) to evaluate the cone at.
    """

    def __init__(self, cone: Cone, parameter: ParamUV) -> None:
        """Initialize the ``ConeEvaluation`` class."""
        self._cone = cone
        self._parameter = parameter

    @property
    def cone(self) -> Cone:
        """Cone being evaluated."""
        return self._cone

    @property
    def parameter(self) -> ParamUV:
        """Parameter that the evaluation is based upon."""
        return self._parameter

    @cached_property
    def position(self) -> Point3D:
        """Position of the evaluation.

        Returns
        -------
        Point3D
            Point that lies on the cone at this evaluation.
        """
        return (
            self.cone.origin
            + self.parameter.v * self.cone.dir_z
            + self.__radius_v * self.__cone_normal
        )

    @cached_property
    def normal(self) -> UnitVector3D:
        """Normal to the surface.

        Returns
        -------
        UnitVector3D
            Normal unit vector to the cone at this evaluation.
        """
        return UnitVector3D(
            self.__cone_normal * np.cos(self.cone.half_angle.m)
            - self.cone.dir_z * np.sin(self.cone.half_angle.m)
        )

    @cached_property
    def __radius_v(self) -> Real:
        """Private radius helper method."""
        return self.cone.radius.m + self.parameter.v * np.tan(self.cone.half_angle.m)

    @cached_property
    def __cone_normal(self) -> Vector3D:
        """Private normal helper method."""
        return (
            np.cos(self.parameter.u) * self.cone.dir_x + np.sin(self.parameter.u) * self.cone.dir_y
        )

    @cached_property
    def __cone_tangent(self) -> Vector3D:
        """Private tangent helper method."""
        return (
            -np.sin(self.parameter.u) * self.cone.dir_x + np.cos(self.parameter.u) * self.cone.dir_y
        )

    @cached_property
    def u_derivative(self) -> Vector3D:
        """First derivative with respect to the U parameter.

        Returns
        -------
        Vector3D
            First derivative with respect to the U parameter.
        """
        return self.__radius_v * self.__cone_tangent

    @cached_property
    def v_derivative(self) -> Vector3D:
        """First derivative with respect to the V parameter.

        Returns
        -------
        Vector3D
            First derivative with respect to the V parameter.
        """
        return self.cone.dir_z + np.tan(self.cone.half_angle.m) * self.__cone_normal

    @cached_property
    def uu_derivative(self) -> Vector3D:
        """Second derivative with respect to the U parameter.

        Returns
        -------
        Vector3D
            Second derivative with respect to the U parameter.
        """
        return -self.__radius_v * self.__cone_normal

    @cached_property
    def uv_derivative(self) -> Vector3D:
        """Second derivative with respect to the U and V parameters.

        Returns
        -------
        Vector3D
            Second derivative with respect to U and V parameters.
        """
        return np.tan(self.cone.half_angle.m) * self.__cone_tangent

    @cached_property
    def vv_derivative(self) -> Vector3D:
        """Second derivative with respect to the V parameter.

        Returns
        -------
        Vector3D
            Second derivative with respect to the V parameter.
        """
        return Vector3D([0, 0, 0])

    @cached_property
    def min_curvature(self) -> Real:
        """Minimum curvature of the cone.

        Returns
        -------
        Real
            Minimum curvature of the cone.
        """
        return 0

    @cached_property
    def min_curvature_direction(self) -> UnitVector3D:
        """Minimum curvature direction.

        Returns
        -------
        UnitVector3D
            Minimum curvature direction.
        """
        return UnitVector3D(self.v_derivative)

    @cached_property
    def max_curvature(self) -> Real:
        """Maximum curvature of the cone.

        Returns
        -------
        Real
            Maximum curvature of the cone.
        """
        return 1.0 / self.__radius_v

    @cached_property
    def max_curvature_direction(self) -> UnitVector3D:
        """Maximum curvature direction.

        Returns
        -------
        UnitVector3D
            Maximum curvature direction.
        """
        return UnitVector3D(self.u_derivative)
