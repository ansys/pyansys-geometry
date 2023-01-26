"""Provides the ``Cone`` class."""


from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np
from pint import Quantity

from ansys.geometry.core.math import UNITVECTOR3D_X, UNITVECTOR3D_Z, Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import UNIT_ANGLE, Angle, Distance
from ansys.geometry.core.primitives.line import Line
from ansys.geometry.core.primitives.surface_evaluation import ParamUV, SurfaceEvaluation
from ansys.geometry.core.typing import Real, RealSequence


class Cone:
    """
    Provides 3D ``Cone`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Origin of the cone.
    radius : Union[Quantity, Distance, Real]
        Radius of the cone.
    half_angle : Union[Quantity, Angle, Real]
        Half angle of the apex, determining the upward angle.
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
        half_angle: Union[Quantity, Angle, Real],
        reference: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        axis: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Z,
    ):
        """Constructor method for the ``Cone`` class."""

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

        if isinstance(half_angle, (int, float)):
            half_angle = Angle(half_angle, UNIT_ANGLE)
        self._half_angle = (
            half_angle if isinstance(half_angle, Angle) else Angle(half_angle, half_angle.units)
        )

    @property
    def origin(self) -> Point3D:
        """Origin of the cone."""
        return self._origin

    @origin.setter
    @check_input_types
    def origin(self, origin: Point3D) -> None:
        """Set the origin of the cone."""
        self._origin = origin

    @property
    def radius(self) -> Quantity:
        """Radius of the cone."""
        return self._radius.value

    @property
    def half_angle(self) -> Angle:
        """Half angle of the apex."""
        return self._half_angle

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
        """Height of the cone"""
        return np.abs(self.radius / np.tan(self.half_angle.value))

    @property
    def surface_area(self) -> Quantity:
        """Surface area of the cone."""
        return np.pi * self.radius * (self.radius + np.sqrt(self.height**2 + self.radius**2))

    @property
    def volume(self) -> Quantity:
        """Volume of the cone."""
        return np.pi * self.radius**2 * self.height / 3

    @property
    def apex(self) -> Point3D:
        """Apex point of the cone"""
        return self.origin + self.apex_param * self.dir_z

    @property
    def apex_param(self) -> float:
        """Apex parameter of the cone"""
        return -np.abs(self.radius.m) / np.tan(self.half_angle.value.m)

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
        """Evaluate the cone at the given parameters."""
        return ConeEvaluation(self, parameter)

    def project_point(self, point: Point3D) -> "ConeEvaluation":
        """Project a point onto the cone and return its ``ConeEvaluation``."""
        u = np.arctan2(self.dir_y.dot(point - self.origin), self.dir_x.dot(point - self.origin))
        while u < 0:
            u += 2 * np.pi
        while u > 2 * np.pi:
            u -= 2 * np.pi
        axis = Line(self.origin, self.dir_z)
        line_eval = axis.project_point(point)
        v = line_eval.parameter

        cone_radius = self.radius.m + v * np.tan(self.half_angle.value.m)
        point_radius = np.linalg.norm(point - line_eval.position())
        dist_to_cone = (point_radius - cone_radius) * np.cos(self.half_angle.value.m)
        v += dist_to_cone * np.sin(self.half_angle.value.m)

        return ConeEvaluation(self, ParamUV(u, v))


class ConeEvaluation(SurfaceEvaluation):
    """
    Provides ``Cone`` evaluation at certain parameters.

    Parameters
    ----------
    cone: ~ansys.geometry.core.primitives.cone.Cone
        The ``Cone`` object to be evaluated.
    parameter: ParamUV
        The parameters (u, v) at which the ``Cone`` evaluation is requested.
    """

    def __init__(self, cone: Cone, parameter: ParamUV) -> None:
        self._cone = cone
        self._parameter = parameter

    @property
    def cone(self) -> Cone:
        """The cone being evaluated."""
        return self._cone

    @property
    def parameter(self) -> ParamUV:
        """The parameter that the evaluation is based upon."""
        return self._parameter

    def position(self) -> Point3D:
        """The point on the cone, based on the evaluation."""
        return (
            self.cone.origin
            + self.parameter.v * self.cone.dir_z
            + self.__radius_v() * self.__cone_normal()
        )

    def normal(self) -> UnitVector3D:
        """The normal to the surface."""
        return UnitVector3D(
            self.__cone_normal() * np.cos(self.cone.half_angle.value.m)
            - self.cone.dir_z * np.sin(self.cone.half_angle.value.m)
        )

    def __radius_v(self) -> float:
        """Private radius helper method"""
        return self.cone.radius.m + self.parameter.v * np.tan(self.cone.half_angle.value.m)

    def __cone_normal(self) -> Vector3D:
        """Private normal helper method"""
        return (
            np.cos(self.parameter.u) * self.cone.dir_x + np.sin(self.parameter.u) * self.cone.dir_y
        )

    def __cone_tangent(self) -> Vector3D:
        """Private tangent helper method"""
        return (
            -np.sin(self.parameter.u) * self.cone.dir_x + np.cos(self.parameter.u) * self.cone.dir_y
        )

    def u_derivative(self) -> Vector3D:
        """The first derivative with respect to u."""
        return self.__radius_v() * self.__cone_tangent()

    def v_derivative(self) -> Vector3D:
        """The first derivative with respect to v."""
        return self.cone.dir_z + np.tan(self.cone.half_angle.value.m) * self.__cone_normal()

    def uu_derivative(self) -> Vector3D:
        """The second derivative with respect to u."""
        return -self.__radius_v() * self.__cone_normal()

    def uv_derivative(self) -> Vector3D:
        """The second derivative with respect to u and v."""
        return np.tan(self.cone.half_angle.value.m) * self.__cone_tangent()

    def vv_derivative(self) -> Vector3D:
        """The second derivative with respect to v."""
        return Vector3D([0, 0, 0])

    def min_curvature(self) -> Real:
        """The minimum curvature."""
        return 0

    def min_curvature_direction(self) -> UnitVector3D:
        """The minimum curvature direction."""
        return UnitVector3D(self.v_derivative())

    def max_curvature(self) -> Real:
        """The maximum curvature."""
        return 1.0 / self.__radius_v()

    def max_curvature_direction(self) -> UnitVector3D:
        """The maximum curvature direction."""
        return UnitVector3D(self.u_derivative())
