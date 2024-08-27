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
"""Provides for creating and managing a cylinder."""

from functools import cached_property

from beartype import beartype as check_input_types
import numpy as np

from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Z
from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.point import Point3D
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
from ansys.geometry.core.typing import Real, RealSequence


class PlaneSurface(Surface):
    """Provides 3D plane surface representation.

    Parameters
    ----------
    origin : ~numpy.ndarray | RealSequence | Point3D
        Centered origin of the plane.
    reference : ~numpy.ndarray | RealSequence | UnitVector3D | Vector3D
        X-axis direction.
    axis : ~numpy.ndarray | RealSequence | UnitVector3D | Vector3D
        X-axis direction.
    """

    def __init__(
        self,
        origin: np.ndarray | RealSequence | Point3D,
        reference: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_X,
        axis: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_Z,
    ):
        """Initialize an instance of a plane surface."""
        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin

        self._reference = (
            UnitVector3D(reference) if not isinstance(reference, UnitVector3D) else reference
        )
        self._axis = UnitVector3D(axis) if not isinstance(axis, UnitVector3D) else axis
        if not self._reference.is_perpendicular_to(self._axis):
            raise ValueError("Plane reference (dir_x) and axis (dir_z) must be perpendicular.")

    @property
    def origin(self) -> Point3D:
        """Origin of the cylinder."""
        return self._origin

    @property
    def dir_x(self) -> UnitVector3D:
        """X-direction of the cylinder."""
        return self._reference

    @property
    def dir_y(self) -> UnitVector3D:
        """Y-direction of the cylinder."""
        return self.dir_z.cross(self.dir_x)

    @property
    def dir_z(self) -> UnitVector3D:
        """Z-direction of the cylinder."""
        return self._axis

    @check_input_types
    def __eq__(self, other: "PlaneSurface") -> bool:
        """Check whether two planes are equal."""
        return (
            self._origin == other._origin
            and self._reference == other._reference
            and self._axis == other._axis
        )

    def contains_param(self, param_uv: ParamUV) -> bool:
        """Check a ``ParamUV`` is within the parametric range of the surface."""
        raise NotImplementedError("contains_param() is not implemented.")

    def contains_point(self, point: Point3D) -> bool:
        """Check whether a 3D point is in the domain of the plane."""
        raise NotImplementedError("contains_point() is not implemented.")

    def parameterization(self) -> tuple[Parameterization, Parameterization]:
        """Parametrize the plane."""
        u = Parameterization(ParamForm.OPEN, ParamType.LINEAR, Interval(-np.inf, np.inf))
        v = Parameterization(ParamForm.OPEN, ParamType.LINEAR, Interval(-np.inf, np.inf))

        return (u, v)

    def project_point(self, point: Point3D) -> SurfaceEvaluation:
        """Evaluate the plane at a given 3D point."""
        origin_to_point = point - self._origin
        u = origin_to_point.dot(self.dir_x)
        v = origin_to_point.dot(self.dir_y)
        return PlaneEvaluation(self, ParamUV(u, v))

    def transformed_copy(self, matrix: Matrix44) -> Surface:
        """Get a transformed version of the plane given the transform."""
        new_point = self.origin.transform(matrix)
        new_reference = self._reference.transform(matrix)
        new_axis = self._axis.transform(matrix)
        return PlaneSurface(
            new_point,
            UnitVector3D(new_reference[0:3]),
            UnitVector3D(new_axis[0:3]),
        )

    def evaluate(self, parameter: ParamUV) -> "PlaneEvaluation":
        """Evaluate the plane at a given u and v parameter."""
        return PlaneEvaluation(self, parameter)


class PlaneEvaluation(SurfaceEvaluation):
    """Provides evaluation of a plane at given parameters.

    Parameters
    ----------
    plane: ~ansys.geometry.core.shapes.surfaces.plane.PlaneSurface
        Plane to evaluate.
    parameter: ParamUV
        Parameters (u, v) to evaluate the plane at.
    """

    def __init__(self, plane: PlaneSurface, parameter: ParamUV) -> None:
        """``SphereEvaluation`` class constructor."""
        self._plane = plane
        self._parameter = parameter

    @property
    def plane(self) -> PlaneSurface:
        """Plane being evaluated."""
        return self._plane

    @property
    def parameter(self) -> ParamUV:
        """Parameter that the evaluation is based upon."""
        return self._parameter

    @cached_property
    def position(self) -> Point3D:
        """Point on the surface, based on the evaluation."""
        return (
            self.plane.origin
            + self.parameter.u * self.plane.dir_x
            + self.parameter.v * self.plane.dir_y
        )

    @cached_property
    def normal(self) -> UnitVector3D:
        """Normal to the surface."""
        return self.plane.dir_z

    @cached_property
    def u_derivative(self) -> Vector3D:
        """First derivative with respect to u."""
        return self.plane.dir_z

    @cached_property
    def v_derivative(self) -> Vector3D:
        """First derivative with respect to v."""
        return self.plane.dir_y

    @cached_property
    def uu_derivative(self) -> Vector3D:
        """Second derivative with respect to u."""
        return Vector3D([0, 0, 0])

    @cached_property
    def uv_derivative(self) -> Vector3D:
        """Second derivative with respect to u and v."""
        return Vector3D([0, 0, 0])

    @cached_property
    def vv_derivative(self) -> Vector3D:
        """Second derivative with respect to v."""
        return Vector3D([0, 0, 0])

    @cached_property
    def min_curvature(self) -> Real:
        """Minimum curvature."""
        return 0

    @cached_property
    def min_curvature_direction(self) -> UnitVector3D:
        """Minimum curvature direction."""
        return self.plane.dir_x

    @cached_property
    def max_curvature(self) -> Real:
        """Maximum curvature."""
        return 0

    @cached_property
    def max_curvature_direction(self) -> UnitVector3D:
        """Maximum curvature direction."""
        return self.plane.dir_y
