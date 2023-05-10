"""Provides the ``Sphere`` class."""

from functools import cached_property

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np
from pint import Quantity

from ansys.geometry.core.math import (
    UNITVECTOR3D_X,
    UNITVECTOR3D_Z,
    Matrix44,
    Point3D,
    UnitVector3D,
    Vector3D,
)
from ansys.geometry.core.misc import Distance
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
    Provides 3D ``Sphere`` representation.

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
        """Initialize ``Sphere`` class."""
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
            The transformation matrix to apply to the sphere.

        Returns
        -------
        Sphere
            A new sphere that is the transformed copy of the original sphere.
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
        Torus
            A new sphere that is a mirrored copy of the original sphere.
        """
        return Sphere(self.origin, self.radius, -self._reference, -self._axis)

    def evaluate(self, parameter: ParamUV) -> "SphereEvaluation":
        """
        Evaluate the sphere at the given parameters.

        Parameters
        ----------
        parameter : ParamUV
            The parameters (u,v) at which to evaluate the sphere.

        Returns
        -------
        SphereEvaluation
            The resulting evaluation.
        """
        return SphereEvaluation(self, parameter)

    def project_point(self, point: Point3D) -> "SphereEvaluation":
        """
        Project a point onto the sphere and return its ``SphereEvaluation``.

        Parameters
        ----------
        point : Point3D
            The point to project onto the sphere.

        Returns
        -------
        SphereEvaluation
            The resulting evaluation.
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
        Retrieve the U parameter parametrization conditions.

        The U parameter specifies the longitude angle, increasing clockwise (East) about
        `dir_z` (right hand corkscrew law). It has a zero parameter at `dir_x`, and a
        period of 2*pi.

        Returns
        -------
        Parameterization
            Information about how a sphere's u parameter is parameterized.
        """
        return Parameterization(ParamForm.PERIODIC, ParamType.CIRCULAR, Interval(0, 2 * np.pi))

    def get_v_parameterization(self) -> Parameterization:
        """
        Retrieve the V parameter parametrization conditions.

        The V parameter specifies the latitude, increasing North, with a zero parameter
        at the equator, and a range of [-pi/2, pi/2].

        Returns
        -------
        Parameterization
            Information about how a sphere's v parameter is parameterized.
        """
        return Parameterization(ParamForm.CLOSED, ParamType.OTHER, Interval(-np.pi / 2, np.pi / 2))


class SphereEvaluation(SurfaceEvaluation):
    """
    Provides ``Sphere`` evaluation at certain parameters.

    Parameters
    ----------
    sphere: ~ansys.geometry.core.primitives.sphere.Sphere
        The ``Sphere`` object to be evaluated.
    parameter: ParamUV
        The parameters (u, v) at which the ``Sphere`` evaluation is requested.
    """

    def __init__(self, sphere: Sphere, parameter: ParamUV) -> None:
        """``SphereEvaluation`` class constructor."""
        self._sphere = sphere
        self._parameter = parameter

    @property
    def sphere(self) -> Sphere:
        """The sphere being evaluated."""
        return self._sphere

    @property
    def parameter(self) -> ParamUV:
        """The parameter that the evaluation is based upon."""
        return self._parameter

    @cached_property
    def position(self) -> Point3D:
        """
        The position of the evaluation.

        Returns
        -------
        Point3D
            The point that lies on the sphere at this evaluation.
        """
        return self.sphere.origin + self.sphere.radius.m * self.normal

    @cached_property
    def normal(self) -> UnitVector3D:
        """
        The normal to the surface.

        Returns
        -------
        UnitVector3D
            The normal unit vector to the sphere at this evaluation.
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
        The first derivative with respect to u.

        Returns
        -------
        Vector3D
            The first derivative with respect to u.
        """
        return np.cos(self.parameter.v) * self.sphere.radius.m * self.__cylinder_tangent

    @cached_property
    def v_derivative(self) -> Vector3D:
        """
        The first derivative with respect to v.

        Returns
        -------
        Vector3D
            The first derivative with respect to v.
        """
        return self.sphere.radius.m * (
            np.cos(self.parameter.v) * self.sphere.dir_z
            - np.sin(self.parameter.v) * self.__cylinder_normal
        )

    @cached_property
    def uu_derivative(self) -> Vector3D:
        """
        The second derivative with respect to u.

        Returns
        -------
        Vector3D
            The second derivative with respect to u.
        """
        return -np.cos(self.parameter.v) * self.sphere.radius.m * self.__cylinder_normal

    @cached_property
    def uv_derivative(self) -> Vector3D:
        """
        The second derivative with respect to u and v.

        Returns
        -------
        Vector3D
            The second derivative with respect to u and v.
        """
        return -np.sin(self.parameter.v) * self.sphere.radius.m * self.__cylinder_tangent

    @cached_property
    def vv_derivative(self) -> Vector3D:
        """
        The second derivative with respect to v.

        Returns
        -------
        Vector3D
            The second derivative with respect to v.
        """
        return self.sphere.radius.m * (
            -np.sin(self.parameter.v) * self.sphere.dir_z
            - np.cos(self.parameter.v) * self.__cylinder_normal
        )

    @cached_property
    def min_curvature(self) -> Real:
        """
        The minimum curvature of the sphere.

        Returns
        -------
        Real
            The minimum curvature of the sphere.
        """
        return 1.0 / self.sphere.radius.m

    @cached_property
    def min_curvature_direction(self) -> UnitVector3D:
        """
        The minimum curvature direction.

        Returns
        -------
        UnitVector3D
            The minimum curvature direction.
        """
        return self.normal % self.max_curvature_direction

    @cached_property
    def max_curvature(self) -> Real:
        """
        The maximum curvature of the sphere.

        Returns
        -------
        Real
            The maximum curvature of the sphere.
        """
        return 1.0 / self.sphere.radius.m

    @cached_property
    def max_curvature_direction(self) -> UnitVector3D:
        """
        The maximum curvature direction.

        Returns
        -------
        UnitVector3D
            The maximum curvature direction.
        """
        return UnitVector3D(self.v_derivative)
