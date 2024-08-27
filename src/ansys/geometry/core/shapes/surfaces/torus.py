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
"""Provides for creating and managing a torus."""

from functools import cached_property

from beartype import beartype as check_input_types
import numpy as np
from pint import Quantity

from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Z
from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.measurements import Distance
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


class Torus(Surface):
    """Provides 3D torus representation.

    Parameters
    ----------
    origin : ~numpy.ndarray | RealSequence | Point3D
        Centered origin of the torus.
    major_radius : ~pint.Quantity | Distance | Real
        Major radius of the torus.
    minor_radius : ~pint.Quantity | Distance | Real
        Minor radius of the torus.
    reference : ~numpy.ndarray | RealSequence | UnitVector3D | Vector3D
        X-axis direction.
    axis : ~numpy.ndarray | RealSequence | UnitVector3D | Vector3D
        Z-axis direction.
    """

    @check_input_types
    def __init__(
        self,
        origin: np.ndarray | RealSequence | Point3D,
        major_radius: Quantity | Distance | Real,
        minor_radius: Quantity | Distance | Real,
        reference: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_X,
        axis: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_Z,
    ):
        """Initialize the ``Torus`` class."""
        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin
        self._reference = (
            UnitVector3D(reference) if not isinstance(reference, UnitVector3D) else reference
        )
        self._axis = UnitVector3D(axis) if not isinstance(axis, UnitVector3D) else axis
        if not self._reference.is_perpendicular_to(self._axis):
            raise ValueError("Torus reference (dir_x) and axis (dir_z) must be perpendicular.")

        # Store values in base unit
        self._major_radius = (
            major_radius if isinstance(major_radius, Distance) else Distance(major_radius)
        )
        self._minor_radius = (
            minor_radius if isinstance(minor_radius, Distance) else Distance(minor_radius)
        )

    @property
    def origin(self) -> Point3D:
        """Origin of the torus."""
        return self._origin

    @property
    def major_radius(self) -> Quantity:
        """Semi-major radius of the torus."""
        return self._major_radius.value

    @property
    def minor_radius(self) -> Quantity:
        """Semi-minor radius of the torus."""
        return self._minor_radius.value

    @property
    def dir_x(self) -> UnitVector3D:
        """X-direction of the torus."""
        return self._reference

    @property
    def dir_y(self) -> UnitVector3D:
        """Y-direction of the torus."""
        return self.dir_z.cross(self.dir_x)

    @property
    def dir_z(self) -> UnitVector3D:
        """Z-direction of the torus."""
        return self._axis

    @property
    def volume(self) -> Quantity:
        """Volume of the torus."""
        return 2 * np.pi**2 * self._major_radius.value * self._minor_radius.value**2

    @property
    def surface_area(self) -> Quantity:
        """Surface_area of the torus."""
        return 4 * np.pi**2 * self._major_radius.value * self._minor_radius.value

    @check_input_types
    def __eq__(self, other: "Torus") -> bool:
        """Equals operator for the ``Torus`` class."""
        return (
            self._origin == other._origin
            and self._major_radius == other._major_radius
            and self._minor_radius == other._minor_radius
            and self._reference == other._reference
            and self._axis == other._axis
        )

    def transformed_copy(self, matrix: Matrix44) -> "Torus":
        """Create a transformed copy of the torus from a transformation matrix.

        Parameters
        ----------
        matrix : Matrix44
            4x4 transformation matrix to apply to the torus.

        Returns
        -------
        Torus
            New torus that is the transformed copy of the original torus.
        """
        new_point = self.origin.transform(matrix)
        new_reference = self._reference.transform(matrix)
        new_axis = self._axis.transform(matrix)
        return Torus(
            new_point,
            self.major_radius,
            self.minor_radius,
            UnitVector3D(new_reference[0:3]),
            UnitVector3D(new_axis[0:3]),
        )

    def mirrored_copy(self) -> "Torus":
        """Create a mirrored copy of the torus along the y-axis.

        Returns
        -------
        Torus
            New torus that is a mirrored copy of the original torus.
        """
        return Torus(
            self.origin, self.major_radius, self.minor_radius, -self._reference, -self._axis
        )

    def evaluate(self, parameter: ParamUV) -> "TorusEvaluation":
        """Evaluate the torus at the given parameters.

        Parameters
        ----------
        parameter : ParamUV
            Parameters (u,v) to evaluate the torus at.

        Returns
        -------
        TorusEvaluation
            Resulting evaluation.
        """
        return TorusEvaluation(self, parameter)

    def parameterization(self) -> tuple[Parameterization, Parameterization]:
        """Parameterize the torus surface as a tuple (U and V respectively).

        The U parameter specifies the longitude angle, increasing clockwise (east) about
        the axis (right-hand corkscrew law). It has a zero parameter at
        ``Geometry.Frame.DirX`` and a period of ``2*pi``.

        The V parameter specifies the latitude, increasing north, with a zero parameter
        at the equator. For the donut, where the major radius is greater
        than the minor radius, the range is [-pi, pi] and the
        parameterization is periodic. For a degenerate torus, the range is restricted
        accordingly and the parameterization is non-periodic.

        Returns
        -------
        tuple[Parameterization, Parameterization]
            Information about how a torus's u and v parameters are parameterized, respectively.
        """
        u = Parameterization(ParamForm.PERIODIC, ParamType.CIRCULAR, Interval(0, 2 * np.pi))
        v = Parameterization(
            ParamForm.PERIODIC, ParamType.CIRCULAR, Interval(-np.pi / 2, np.pi / 2)
        )

        return (u, v)

    def project_point(self, point: Point3D) -> "TorusEvaluation":
        """Project a point onto the torus and evaluate the torus.

        Parameters
        ----------
        point : Point3D
            Point to project onto the torus.

        Returns
        -------
        TorusEvaluation
            Resulting evaluation.
        """
        vector1 = UnitVector3D.from_points(self.origin, point)
        u = np.arctan2(vector1.dot(self.dir_y), vector1.dot(self.dir_x))
        local_x = np.cos(u) * self.dir_x + np.sin(u) * self.dir_y
        delta = self.major_radius.m * local_x
        vector2 = vector1 - delta
        if self.major_radius.m >= self.minor_radius.m:
            v = np.arctan2(vector2.dot(self.dir_z), vector2.dot(local_x))
            return TorusEvaluation(self, ParamUV(u, v))
        vector3 = vector1 + delta
        v1 = np.arctan2(vector2.dot(self.dir_z), vector2.dot(local_x)), -np.pi
        v2 = np.arctan2(vector3.dot(self.dir_z), vector3.dot(local_x)), -np.pi
        if np.power(
            np.linalg.norm((TorusEvaluation(self, ParamUV(u, v1)).position() - point)), 2
        ) < np.power(
            np.linalg.norm((TorusEvaluation(self, ParamUV(u + np.pi, v2)).position() - point)), 2
        ):
            return TorusEvaluation(self, ParamUV(u, v1))
        else:
            return TorusEvaluation(self, ParamUV(u + np.pi, v2))

    def contains_param(self, param_uv: ParamUV) -> bool:  # noqa: D102
        raise NotImplementedError("contains_param() is not implemented.")

    def contains_point(self, point: Point3D) -> bool:  # noqa: D102
        raise NotImplementedError("contains_point() is not implemented.")


class TorusEvaluation(SurfaceEvaluation):
    """Evaluate the torus`` at given parameters.

    Parameters
    ----------
    Torus: ~ansys.geometry.core.shapes.surfaces.torus.Torus
        Torust to evaluate.
    parameter: ParamUV
        Parameters (u, v) to evaluate the torus at.
    """

    def __init__(self, torus: Torus, parameter: ParamUV) -> None:
        """Initiate the ``TorusEvaluation`` class."""
        self._torus = torus
        self._parameter = parameter
        self.cache = {}

    @property
    def torus(self) -> Torus:
        """Torus being evaluated."""
        return self._torus

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
            Point that lies on the torus at this evaluation.
        """
        return (
            self._torus.origin
            + (self._torus.major_radius.m + np.cos(self.parameter.v) * self._torus.minor_radius.m)
            * self.__cylinder_normal
            + np.sin(self.parameter.v) * self._torus.minor_radius.m * self._torus.dir_z
        )

    @cached_property
    def normal(self) -> UnitVector3D:
        """Normal to the surface.

        Returns
        -------
        UnitVector3D
            Normal unit vector to the torus at this evaluation.
        """
        return UnitVector3D(
            np.cos(self.parameter.v) * self.__cylinder_normal
            + np.sin(self.parameter.v) * self._torus.dir_z
        )

    @cached_property
    def __cylinder_normal(self) -> Vector3D:
        """Normal to the surface.

        Returns
        -------
        UnitVector3D
            Normal unit vector to the torus at this evaluation.
        """
        return (
            np.cos(self.parameter.u) * self._torus.dir_x
            + np.sin(self.parameter.u) * self._torus.dir_y
        )

    @cached_property
    def __cylinder_tangent(self) -> Vector3D:
        """Private tangent helper method."""
        return (
            -np.sin(self.parameter.u) * self._torus.dir_x
            + np.cos(self.parameter.u) * self._torus.dir_y
        )

    @cached_property
    def u_derivative(self) -> Vector3D:
        """First derivative with respect to the U parameter.

        Returns
        -------
        Vector3D
            First derivative with respect to the U parameter.
        """
        return (
            self._torus.major_radius.m + np.cos(self.parameter.v) * self._torus.minor_radius.m
        ) * self.__cylinder_tangent

    @cached_property
    def v_derivative(self) -> Vector3D:
        """First derivative with respect to the V parameter.

        Returns
        -------
        Vector3D
            First derivative with respect to the V parameter.
        """
        return (
            -np.sin(self.parameter.v) * self._torus.minor_radius.m * self.__cylinder_tangent
            + np.cos(self.parameter.v) * self._torus.minor_radius.m * self._torus.dir_z
        )

    @cached_property
    def uu_derivative(self) -> Vector3D:
        """Second derivative with respect to the U parameter.

        Returns
        -------
        Vector3D
            Second derivative with respect to the U parameter.
        """
        return (
            -(self._torus.major_radius.m + np.cos(self.parameter.v))
            * self._torus.minor_radius.m
            * self.__cylinder_normal
        )

    @cached_property
    def uv_derivative(self) -> Vector3D:
        """Second derivative with respect to the U and V parameters.

        Returns
        -------
        Vector3D
            Second derivative with respect to the U and V parameters.
        """
        return -np.sin(self.parameter.v) * self._torus.minor_radius.m * self.__cylinder_tangent

    @cached_property
    def vv_derivative(self) -> Vector3D:
        """Second derivative with respect to the V parameter.

        Returns
        -------
        Vector3D
            Second derivative with respect to the V parameter.
        """
        return (
            -np.cos(self.parameter.v) * self._torus.minor_radius.m * self.__cylinder_normal
            - np.sin(self.parameter.v) * self._torus.minor_radius.m * self._torus.dir_z
        )

    @cached_property
    def curvature(self) -> tuple[Real, Vector3D, Real, Vector3D]:
        """Curvature of the torus.

        Returns
        -------
        tuple[Real, Vector3D, Real, Vector3D]
            Minimum and maximum curvature value and direction, respectively.
        """
        min_cur = 1.0 / self._torus.minor_radius.m
        min_dir = UnitVector3D(self.v_derivative)
        start_point = self._torus.origin
        end_point = self.position
        max_cur = 1.0 / np.linalg.norm((end_point - start_point))
        max_dir = UnitVector3D(self.u_derivative)
        if min_cur > max_cur:
            min_cur, max_cur = max_cur, min_cur
            min_dir, max_dir = max_dir, min_dir
        return min_cur, min_dir, max_cur, max_dir

    @cached_property
    def min_curvature(self) -> Real:
        """Minimum curvature of the torus.

        Returns
        -------
        Real
            Minimum curvature of the torus.
        """
        return self.curvature[0]

    @cached_property
    def min_curvature_direction(self) -> UnitVector3D:
        """Minimum curvature direction.

        Returns
        -------
        UnitVector3D
            Minimum curvature direction.
        """
        return self.curvature[1]

    @cached_property
    def max_curvature(self) -> Real:
        """Maximum curvature of the torus.

        Returns
        -------
        Real
            Maximum curvature of the torus.
        """
        return self.curvature[2]

    @cached_property
    def max_curvature_direction(self) -> UnitVector3D:
        """Maximum curvature direction.

        Returns
        -------
        UnitVector3D
            Maximum curvature direction.
        """
        return self.curvature[3]
