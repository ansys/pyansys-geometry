""" Provides the ``Sphere`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np
from pint import Quantity

from ansys.geometry.core.math import UNITVECTOR3D_X, UNITVECTOR3D_Z, Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import Distance
from ansys.geometry.core.primitives.surface_evaluation import ParamUV, SurfaceEvaluation
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
        X-plane direction.
    axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Z-plane direction.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        radius: Union[Quantity, Distance, Real],
        reference: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        axis: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Z,
    ):
        """Constructor method for the ``Sphere`` class."""

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

    @origin.setter
    @check_input_types
    def origin(self, origin: Point3D) -> None:
        """Set the origin of the sphere."""
        self._origin = origin

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

    def evaluate(self, parameter: ParamUV) -> "SphereEvaluation":
        """Evaluate the sphere at the given parameters."""
        return SphereEvaluation(self, parameter)

    def project_point(self, point: Point3D) -> "SphereEvaluation":
        """Project a point onto the sphere and return its ``SphereEvaluation``."""
        origin_to_point = point - self.origin
        x = origin_to_point.dot(self.dir_x)
        y = origin_to_point.dot(self.dir_y)
        z = origin_to_point.dot(self.dir_z)
        if np.allclose((x * x + y * y + z * z), Point3D([0, 0, 0])):
            return SphereEvaluation(self, ParamUV(0, np.pi / 2))

        u = np.arctan2(y, x)
        v = np.arctan2(z, np.sqrt(x * x + y * y))
        return SphereEvaluation(self, ParamUV(u, v))


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

    def position(self) -> Point3D:
        """The point on the sphere, based on the evaluation."""
        return self.sphere.origin + self.sphere.radius.m * self.normal()

    def normal(self) -> UnitVector3D:
        """The normal to the surface."""
        return UnitVector3D(
            np.cos(self.parameter.v) * self.cylinder_normal()
            + np.sin(self.parameter.v) * self.sphere.dir_z
        )

    def cylinder_normal(self) -> Vector3D:
        """Cylinder normal of the evaluation."""
        return (
            np.cos(self.parameter.u) * self.sphere.dir_x
            + np.sin(self.parameter.u) * self.sphere.dir_y
        )

    def cylinder_tangent(self) -> Vector3D:
        """Cylinder tangent of the evaluation."""
        return (
            -np.sin(self.parameter.u) * self.sphere.dir_x
            + np.cos(self.parameter.u) * self.sphere.dir_y
        )

    def u_derivative(self) -> Vector3D:
        """The first derivative with respect to u."""
        return np.cos(self.parameter.v) * self.sphere.radius.m * self.cylinder_tangent()

    def v_derivative(self) -> Vector3D:
        """The first derivative with respect to v."""
        return self.sphere.radius.m * (
            np.cos(self.parameter.v) * self.sphere.dir_z
            - np.sin(self.parameter.v) * self.cylinder_normal()
        )

    def uu_derivative(self) -> Vector3D:
        """The second derivative with respect to u."""
        return -np.cos(self.parameter.v) * self.sphere.radius.m * self.cylinder_normal()

    def uv_derivative(self) -> Vector3D:
        """The second derivative with respect to u and v."""
        return -np.sin(self.parameter.v) * self.sphere.radius.m * self.cylinder_tangent()

    def vv_derivative(self) -> Vector3D:
        """The second derivative with respect to v."""
        return self.sphere.radius.m * (
            -np.sin(self.parameter.v) * self.sphere.dir_z
            - np.cos(self.parameter.v) * self.cylinder_normal()
        )

    def min_curvature(self) -> Real:
        """The minimum curvature."""
        return 1.0 / self.sphere.radius.m

    def min_curvature_direction(self) -> UnitVector3D:
        """The minimum curvature direction."""
        return self.normal() % self.max_curvature_direction()

    def max_curvature(self) -> Real:
        """The maximum curvature."""
        return 1.0 / self.sphere.radius.m

    def max_curvature_direction(self) -> UnitVector3D:
        """The maximum curvature direction."""
        return UnitVector3D(self.v_derivative())
