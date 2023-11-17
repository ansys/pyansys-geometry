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
"""Provides for creating and managing a sphere."""

from functools import cached_property

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np
from pint import Quantity

from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Z
from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.primitives.parameterization import (
    Interval,
    Parameterization,
    ParamForm,
    ParamType,
    ParamUV,
)
from ansys.geometry.core.primitives.surface_evaluation import SurfaceEvaluation
from ansys.geometry.core.typing import Real, RealSequence


class Sphere:
    """
    Provides 3D sphere representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Origin of the sphere.
    radius : Union[Quantity, Distance, Real]
        Radius of the sphere.
    reference : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-axis direction.
    axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Z-axis direction.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        radius: Union[Quantity, Distance, Real],
        reference: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        axis: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Z,
    ):
        """Initialize the ``Sphere`` class."""
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
        """Origin of the sphere."""
        return self._origin

    @property
    def radius(self) -> Quantity:
        """Radius of the sphere."""
        return self._radius.value

    @property
    def dir_x(self) -> UnitVector3D:
        """X-direction of the sphere."""
        return self._reference

    @property
    def dir_y(self) -> UnitVector3D:
        """Y-direction of the sphere."""
        return self.dir_z.cross(self.dir_x)

    @property
    def dir_z(self) -> UnitVector3D:
        """Z-direction of the sphere."""
        return self._axis

    @property
    def surface_area(self) -> Quantity:
        """Surface area of the sphere."""
        return 4 * np.pi * self.radius**2

    @property
    def volume(self) -> Quantity:
        """Volume of the sphere."""
        return 4.0 / 3.0 * np.pi * self.radius**3

    @check_input_types
    def __eq__(self, other: "Sphere") -> bool:
        """Equals operator for the ``Sphere`` class."""
        return (
            self._origin == other._origin
            and self._radius == other._radius
            and self._reference == other._reference
            and self._axis == other._axis
        )

    def transformed_copy(self, matrix: Matrix44) -> "Sphere":
        """
        Create a transformed copy of the sphere based on a transformation matrix.

        Parameters
        ----------
        matrix : Matrix44
            4X4 transformation matrix to apply to the sphere.

        Returns
        -------
        Sphere
            New sphere that is the transformed copy of the original sphere.
        """
        new_point = self.origin.transform(matrix)
        new_reference = self._reference.transform(matrix)
        new_axis = self._axis.transform(matrix)
        return Sphere(
            new_point,
            self.radius,
            UnitVector3D(new_reference[0:3]),
            UnitVector3D(new_axis[0:3]),
        )

    def mirrored_copy(self) -> "Sphere":
        """
        Create a mirrored copy of the sphere along the y-axis.

        Returns
        -------
        Sphere
            New sphere that is a mirrored copy of the original sphere.
        """
        return Sphere(self.origin, self.radius, -self._reference, -self._axis)

    def evaluate(self, parameter: ParamUV) -> "SphereEvaluation":
        """
        Evaluate the sphere at the given parameters.

        Parameters
        ----------
        parameter : ParamUV
            Parameters (u,v) to evaluate the sphere at.

        Returns
        -------
        SphereEvaluation
            Resulting evaluation.
        """
        return SphereEvaluation(self, parameter)

    def project_point(self, point: Point3D) -> "SphereEvaluation":
        """
        Project a point onto the sphere and evaluate the sphere.

        Parameters
        ----------
        point : Point3D
            Point to project onto the sphere.

        Returns
        -------
        SphereEvaluation
            Resulting evaluation.
        """
        origin_to_point = point - self.origin
        x = origin_to_point.dot(self.dir_x)
        y = origin_to_point.dot(self.dir_y)
        z = origin_to_point.dot(self.dir_z)
        if np.allclose((x * x + y * y + z * z), Point3D([0, 0, 0])):
            return SphereEvaluation(self, ParamUV(0, np.pi / 2))

        u = np.arctan2(y, x)
        v = np.arctan2(z, np.sqrt(x * x + y * y))
        return SphereEvaluation(self, ParamUV(u, v))

    def get_u_parameterization(self) -> Parameterization:
        """
        Get the parametrization conditions for the U parameter.

        The U parameter specifies the longitude angle, increasing clockwise (east) about
        ``dir_z`` (right-hand corkscrew law). It has a zero parameter at ``dir_x`` and a
        period of ``2*pi``.

        Returns
        -------
        Parameterization
            Information about how a sphere's U parameter is parameterized.
        """
        return Parameterization(ParamForm.PERIODIC, ParamType.CIRCULAR, Interval(0, 2 * np.pi))

    def get_v_parameterization(self) -> Parameterization:
        """
        Get the parametrization conditions for the V parameter.

        The V parameter specifies the latitude, increasing north, with a zero parameter
        at the equator and a range of ``[-pi/2, pi/2]``.

        Returns
        -------
        Parameterization
            Information about how a sphere's V parameter is parameterized.
        """
        return Parameterization(ParamForm.CLOSED, ParamType.OTHER, Interval(-np.pi / 2, np.pi / 2))


class SphereEvaluation(SurfaceEvaluation):
    """
    Evaluate a sphere at given parameters.

    Parameters
    ----------
    sphere: ~ansys.geometry.core.primitives.sphere.Sphere
        Sphere to evaluate.
    parameter: ParamUV
        Parameters (u, v) to evaluate the sphere at.
    """

    def __init__(self, sphere: Sphere, parameter: ParamUV) -> None:
        """Initialize the ``SphereEvaluation`` class."""
        self._sphere = sphere
        self._parameter = parameter

    @property
    def sphere(self) -> Sphere:
        """Sphere being evaluated."""
        return self._sphere

    @property
    def parameter(self) -> ParamUV:
        """Parameter that the evaluation is based upon."""
        return self._parameter

    @cached_property
    def position(self) -> Point3D:
        """
        Position of the evaluation.

        Returns
        -------
        Point3D
            Point that lies on the sphere at this evaluation.
        """
        return self.sphere.origin + self.sphere.radius.m * self.normal

    @cached_property
    def normal(self) -> UnitVector3D:
        """
        The normal to the surface.

        Returns
        -------
        UnitVector3D
            Normal unit vector to the sphere at this evaluation.
        """
        return UnitVector3D(
            np.cos(self.parameter.v) * self.__cylinder_normal
            + np.sin(self.parameter.v) * self.sphere.dir_z
        )

    @cached_property
    def __cylinder_normal(self) -> Vector3D:
        """Cylinder normal of the evaluation."""
        return (
            np.cos(self.parameter.u) * self.sphere.dir_x
            + np.sin(self.parameter.u) * self.sphere.dir_y
        )

    @cached_property
    def __cylinder_tangent(self) -> Vector3D:
        """Cylinder tangent of the evaluation."""
        return (
            -np.sin(self.parameter.u) * self.sphere.dir_x
            + np.cos(self.parameter.u) * self.sphere.dir_y
        )

    @cached_property
    def u_derivative(self) -> Vector3D:
        """
        First derivative with respect to the U parameter.

        Returns
        -------
        Vector3D
            First derivative with respect to the U parameter.
        """
        return np.cos(self.parameter.v) * self.sphere.radius.m * self.__cylinder_tangent

    @cached_property
    def v_derivative(self) -> Vector3D:
        """
        First derivative with respect to the V parameter.

        Returns
        -------
        Vector3D
            First derivative with respect to the V parameter.
        """
        return self.sphere.radius.m * (
            np.cos(self.parameter.v) * self.sphere.dir_z
            - np.sin(self.parameter.v) * self.__cylinder_normal
        )

    @cached_property
    def uu_derivative(self) -> Vector3D:
        """
        Second derivative with respect to the U parameter.

        Returns
        -------
        Vector3D
            Second derivative with respect to the U parameter.
        """
        return -np.cos(self.parameter.v) * self.sphere.radius.m * self.__cylinder_normal

    @cached_property
    def uv_derivative(self) -> Vector3D:
        """
        Second derivative with respect to the U and V parameters.

        Returns
        -------
        Vector3D
            The second derivative with respect to the U and V parameters.
        """
        return -np.sin(self.parameter.v) * self.sphere.radius.m * self.__cylinder_tangent

    @cached_property
    def vv_derivative(self) -> Vector3D:
        """
        Second derivative with respect to the V parameter.

        Returns
        -------
        Vector3D
            The second derivative with respect to the V parameter.
        """
        return self.sphere.radius.m * (
            -np.sin(self.parameter.v) * self.sphere.dir_z
            - np.cos(self.parameter.v) * self.__cylinder_normal
        )

    @cached_property
    def min_curvature(self) -> Real:
        """
        Minimum curvature of the sphere.

        Returns
        -------
        Real
            Minimum curvature of the sphere.
        """
        return 1.0 / self.sphere.radius.m

    @cached_property
    def min_curvature_direction(self) -> UnitVector3D:
        """
        Minimum curvature direction.

        Returns
        -------
        UnitVector3D
            Minimum curvature direction.
        """
        return self.normal % self.max_curvature_direction

    @cached_property
    def max_curvature(self) -> Real:
        """
        Maximum curvature of the sphere.

        Returns
        -------
        Real
            Maximum curvature of the sphere.
        """
        return 1.0 / self.sphere.radius.m

    @cached_property
    def max_curvature_direction(self) -> UnitVector3D:
        """
        Maximum curvature direction.

        Returns
        -------
        UnitVector3D
            Maximum curvature direction.
        """
        return UnitVector3D(self.v_derivative)
