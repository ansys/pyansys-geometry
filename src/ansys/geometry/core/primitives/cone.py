"""Provides the ``Cone`` class."""

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
from ansys.geometry.core.misc import Angle, Distance
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
        X-axis direction.
    axis : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Z-axis direction.
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
        """Initialize ``Cone`` class."""
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
        """
        Create a transformed copy of the cone based on a transformation matrix.

        Parameters
        ----------
        matrix : Matrix44
            The transformation matrix to apply to the cone.

        Returns
        -------
        Cone
            A new cone that is the transformed copy of the original cone.
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
        """
        Create a mirrored copy of the cone along the y-axis.

        Returns
        -------
        Cone
            A new cone that is a mirrored copy of the original cone.
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
        """
        Evaluate the cone at the given parameters.

        Parameters
        ----------
        parameter : ParamUV
            The parameters (u,v) at which to evaluate the cone.

        Returns
        -------
        ConeEvaluation
            The resulting evaluation.
        """
        return ConeEvaluation(self, parameter)

    def project_point(self, point: Point3D) -> "ConeEvaluation":
        """
        Project a point onto the cone and return its ``ConeEvaluation``.

        Parameters
        ----------
        point : Point3D
            The point to project onto the cone.

        Returns
        -------
        ConeEvaluation
            The resulting evaluation.
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

    def get_u_parameterization(self) -> Parameterization:
        """
        Retrieve the U parameter parametrization conditions.

        The U parameter specifies the clockwise angle around the axis (right hand
        corkscrew law), with a zero parameter at `dir_x`, and a period of 2*pi.

        Returns
        -------
        Parameterization
            Information about how a cone's u parameter is parameterized.
        """
        return Parameterization(ParamForm.PERIODIC, ParamType.CIRCULAR, Interval(0, 2 * np.pi))

    def get_v_parameterization(self) -> Parameterization:
        """
        Retrieve the V parameter parametrization conditions.

        The V parameter specifies the distance along the axis, with a zero parameter at
        the XY plane of the Cone.

        Returns
        -------
        Parameterization
            Information about how a cone's v parameter is parameterized.
        """
        # V parameter interval depends on which way the cone opens
        start, end = (
            (self.apex_param, np.inf) if self.apex_param < 0 else (np.NINF, self.apex_param)
        )
        return Parameterization(ParamForm.OPEN, ParamType.LINEAR, Interval(start, end))


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
        """``ConeEvaluation`` class constructor."""
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

    @cached_property
    def position(self) -> Point3D:
        """
        The position of the evaluation.

        Returns
        -------
        Point3D
            The point that lies on the cone at this evaluation.
        """
        return (
            self.cone.origin
            + self.parameter.v * self.cone.dir_z
            + self.__radius_v * self.__cone_normal
        )

    @cached_property
    def normal(self) -> UnitVector3D:
        """
        The normal to the surface.

        Returns
        -------
        UnitVector3D
            The normal unit vector to the cone at this evaluation.
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
        """
        The first derivative with respect to u.

        Returns
        -------
        Vector3D
            The first derivative with respect to u.
        """
        return self.__radius_v * self.__cone_tangent

    @cached_property
    def v_derivative(self) -> Vector3D:
        """
        The first derivative with respect to v.

        Returns
        -------
        Vector3D
            The first derivative with respect to v.
        """
        return self.cone.dir_z + np.tan(self.cone.half_angle.m) * self.__cone_normal

    @cached_property
    def uu_derivative(self) -> Vector3D:
        """
        The second derivative with respect to u.

        Returns
        -------
        Vector3D
            The second derivative with respect to u.
        """
        return -self.__radius_v * self.__cone_normal

    @cached_property
    def uv_derivative(self) -> Vector3D:
        """
        The second derivative with respect to u and v.

        Returns
        -------
        Vector3D
            The second derivative with respect to u and v.
        """
        return np.tan(self.cone.half_angle.m) * self.__cone_tangent

    @cached_property
    def vv_derivative(self) -> Vector3D:
        """
        The second derivative with respect to v.

        Returns
        -------
        Vector3D
            The second derivative with respect to v.
        """
        return Vector3D([0, 0, 0])

    @cached_property
    def min_curvature(self) -> Real:
        """
        The minimum curvature of the cone.

        Returns
        -------
        Real
            The minimum curvature of the cone.
        """
        return 0

    @cached_property
    def min_curvature_direction(self) -> UnitVector3D:
        """
        The minimum curvature direction.

        Returns
        -------
        UnitVector3D
            The minimum curvature direction.
        """
        return UnitVector3D(self.v_derivative)

    @cached_property
    def max_curvature(self) -> Real:
        """
        The maximum curvature of the cone.

        Returns
        -------
        Real
            The maximum curvature of the cone.
        """
        return 1.0 / self.__radius_v

    @cached_property
    def max_curvature_direction(self) -> UnitVector3D:
        """
        The maximum curvature direction.

        Returns
        -------
        UnitVector3D
            The maximum curvature direction.
        """
        return UnitVector3D(self.u_derivative)
