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
from beartype.typing import Union
import numpy as np
import pint

from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Z
from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.primitives.circle import Circle
from ansys.geometry.core.primitives.line import Line
from ansys.geometry.core.primitives.parameterization import (
    Interval,
    Parameterization,
    ParamForm,
    ParamType,
    ParamUV,
)
from ansys.geometry.core.primitives.surface_evaluation import SurfaceEvaluation
from ansys.geometry.core.typing import Real, RealSequence


class Cylinder:
    """
    Provides 3D cylinder representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Origin of the cylinder.
    radius : Union[~pint.Quantity, Distance, Real]
        Radius of the cylinder.
    reference : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-axis direction.
    axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Z-axis direction.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        radius: Union[pint.Quantity, Distance, Real],
        reference: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        axis: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Z,
    ):
        """Initialize the ``Cylinder`` class."""
        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin
        self._reference = (
            UnitVector3D(reference) if not isinstance(reference, UnitVector3D) else reference
        )
        self._axis = UnitVector3D(axis) if not isinstance(axis, UnitVector3D) else axis
        self._axis = UnitVector3D(axis) if not isinstance(axis, UnitVector3D) else axis
        if not self._reference.is_perpendicular_to(self._axis):
            raise ValueError("Cylinder reference (dir_x) and axis (dir_z) must be perpendicular.")

        self._radius = radius if isinstance(radius, Distance) else Distance(radius)
        if self._radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

    @property
    def origin(self) -> Point3D:
        """Origin of the cylinder."""
        return self._origin

    @property
    def radius(self) -> pint.Quantity:
        """Radius of the cylinder."""
        return self._radius.value

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

    def surface_area(self, height: Union[pint.Quantity, Distance, Real]) -> pint.Quantity:
        """
        Get the surface area of the cylinder.

        Notes
        -----
           By nature, a cylinder is infinite. If you want to get the surface area,
           you must bound it by a height. Normally a cylinder surface is not closed
           (does not have "caps" on the ends). This method assumes that the cylinder
           is closed for the purpose of getting the surface area.

        Parameters
        ----------
        height : Union[~pint.Quantity, Distance, Real]
            Height to bound the cylinder at.

        Returns
        -------
        ~pint.Quantity
            Surface area of the temporarily bounded cylinder.
        """
        height = height if isinstance(height, Distance) else Distance(height)
        if height.value <= 0:
            raise ValueError("Height must be a real positive value.")

        return 2 * np.pi * self.radius * height.value + 2 * np.pi * self.radius**2

    def volume(self, height: Union[pint.Quantity, Distance, Real]) -> pint.Quantity:
        """
        Get the volume of the cylinder.

        Notes
        -----
           By nature, a cylinder is infinite. If you want to get the surface area,
           you must bound it by a height. Normally a cylinder surface is not closed
           (does not have "caps" on the ends). This method assumes that the cylinder
           is closed for the purpose of getting the surface area.

        Parameters
        ----------
        height : Union[~pint.Quantity, Distance, Real]
            Height to bound the cylinder at.

        Returns
        -------
        ~pint.Quantity
            Volume of the temporarily bounded cylinder.
        """
        height = height if isinstance(height, Distance) else Distance(height)
        if height.value <= 0:
            raise ValueError("Height must be a real positive value.")

        return np.pi * self.radius**2 * height.value

    def transformed_copy(self, matrix: Matrix44) -> "Cylinder":
        """
        Create a transformed copy of the cylinder based on a transformation matrix.

        Parameters
        ----------
        matrix : Matrix44
            4X4 transformation matrix to apply to the cylinder.

        Returns
        -------
        Cylinder
            New cylinder that is the transformed copy of the original cylinder.
        """
        new_point = self.origin.transform(matrix)
        new_reference = self._reference.transform(matrix)
        new_axis = self._axis.transform(matrix)
        return Cylinder(
            new_point,
            self.radius,
            UnitVector3D(new_reference[0:3]),
            UnitVector3D(new_axis[0:3]),
        )

    def mirrored_copy(self) -> "Cylinder":
        """
        Create a mirrored copy of the cylinder along the y-axis.

        Returns
        -------
        Cylinder
            New cylinder that is a mirrored copy of the original cylinder.
        """
        return Cylinder(self.origin, self.radius, -self._reference, -self._axis)

    @check_input_types
    def __eq__(self, other: "Cylinder") -> bool:
        """Equals operator for the ``Cylinder`` class."""
        return (
            self._origin == other._origin
            and self._radius == other._radius
            and self._reference == other._reference
            and self._axis == other._axis
        )

    def evaluate(self, parameter: ParamUV) -> "CylinderEvaluation":
        """
        Evaluate the cylinder at the given parameters.

        Parameters
        ----------
        parameter : ParamUV
            Parameters (u,v) to evaluate the cylinder at.

        Returns
        -------
        CylinderEvaluation
            Resulting evaluation.
        """
        return CylinderEvaluation(self, parameter)

    def project_point(self, point: Point3D) -> "CylinderEvaluation":
        """
        Project a point onto the cylinder and evaluate the cylinder.

        Parameters
        ----------
        point : Point3D
            Point to project onto the cylinder.

        Returns
        -------
        CylinderEvaluation
            Resulting evaluation.
        """
        circle = Circle(self.origin, self.radius, self.dir_x, self.dir_z)
        u = circle.project_point(point).parameter

        line = Line(self.origin, self.dir_z)
        v = line.project_point(point).parameter

        return CylinderEvaluation(self, ParamUV(u, v))

    def get_u_parameterization(self) -> Parameterization:
        """
        Get the parametrization conditions for the U parameter.

        The U parameter specifies the clockwise angle around the axis (right-hand
        corkscrew law), with a zero parameter at ``dir_x`` and a period of 2*pi.

        Returns
        -------
        Parameterization
            Information about how the cylinder's U parameter is parameterized.
        """
        return Parameterization(ParamForm.PERIODIC, ParamType.CIRCULAR, Interval(0, 2 * np.pi))

    def get_v_parameterization(self) -> Parameterization:
        """
        Get the parametrization conditions for the V parameter.

        The V parameter specifies the distance along the axis, with a zero parameter at
        the XY plane of the cylinder.

        Returns
        -------
        Parameterization
            Information about how the cylinders's V parameter is parameterized.
        """
        return Parameterization(ParamForm.OPEN, ParamType.LINEAR, Interval(np.NINF, np.inf))


class CylinderEvaluation(SurfaceEvaluation):
    """
    Provides evaluation of a cylinder at given parameters.

    Parameters
    ----------
    cylinder: Cylinder
        Cylinder to evaluate.
    parameter: ParamUV
        Parameters (u, v) to evaluate the cylinder at.
    """

    def __init__(self, cylinder: Cylinder, parameter: ParamUV) -> None:
        """Initialize the ``CylinderEvaluation`` class."""
        self._cylinder = cylinder
        self._parameter = parameter

    @property
    def cylinder(self) -> Cylinder:
        """Cylinder being evaluated."""
        return self._cylinder

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
            Point that lies on the cylinder at this evaluation.
        """
        return (
            self.cylinder.origin
            + self.cylinder.radius.m * self.__cylinder_normal
            + self.parameter.v * self.cylinder.dir_z
        )

    @cached_property
    def normal(self) -> UnitVector3D:
        """
        Normal to the surface.

        Returns
        -------
        UnitVector3D
            Normal unit vector to the cylinder at this evaluation.
        """
        return UnitVector3D(self.__cylinder_normal)

    @cached_property
    def __cylinder_normal(self) -> Vector3D:
        """
        Normal to the surface.

        Returns
        -------
        UnitVector3D
            Normal unit vector to the cylinder at this evaluation.
        """
        return (
            np.cos(self.parameter.u) * self.cylinder.dir_x
            + np.sin(self.parameter.u) * self.cylinder.dir_y
        )

    @cached_property
    def __cylinder_tangent(self) -> Vector3D:
        """Private tangent helper method."""
        return (
            -np.sin(self.parameter.u) * self.cylinder.dir_x
            + np.cos(self.parameter.u) * self.cylinder.dir_y
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
        return self.cylinder.radius.m * self.__cylinder_tangent

    @cached_property
    def v_derivative(self) -> Vector3D:
        """
        First derivative with respect to the V parameter.

        Returns
        -------
        Vector3D
            First derivative with respect to the V parameter.
        """
        return self.cylinder.dir_z

    @cached_property
    def uu_derivative(self) -> Vector3D:
        """
        Second derivative with respect to the U parameter.

        Returns
        -------
        Vector3D
            Second derivative with respect to the U parameter.
        """
        return -self.cylinder.radius.m * self.__cylinder_normal

    @cached_property
    def uv_derivative(self) -> Vector3D:
        """
        Second derivative with respect to the U and V parameters.

        Returns
        -------
        Vector3D
            Second derivative with respect to the U and v parameters.
        """
        return Vector3D([0, 0, 0])

    @cached_property
    def vv_derivative(self) -> Vector3D:
        """
        Second derivative with respect to the V parameter.

        Returns
        -------
        Vector3D
            Second derivative with respect to the V parameter.
        """
        return Vector3D([0, 0, 0])

    @cached_property
    def min_curvature(self) -> Real:
        """
        Minimum curvature of the cylinder.

        Returns
        -------
        Real
            Minimum curvature of the cylinder.
        """
        return 0

    @cached_property
    def min_curvature_direction(self) -> UnitVector3D:
        """
        Minimum curvature direction.

        Returns
        -------
        UnitVector3D
            Mminimum curvature direction.
        """
        return UnitVector3D(self.cylinder.dir_z)

    @cached_property
    def max_curvature(self) -> Real:
        """
        Maximum curvature of the cylinder.

        Returns
        -------
        Real
            Maximum curvature of the cylinder.
        """
        return 1.0 / self.cylinder.radius.m

    @cached_property
    def max_curvature_direction(self) -> UnitVector3D:
        """
        Maximum curvature direction.

        Returns
        -------
        UnitVector3D
            Maximum curvature direction.
        """
        return UnitVector3D(self.u_derivative)
