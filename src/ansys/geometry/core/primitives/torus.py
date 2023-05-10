"""Provides the ``Torus`` class."""

from functools import cached_property
from typing import Tuple

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


class Torus:
    """
    Provides 3D ``Torus`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D],
        Centered origin of the torus.
    direction_x : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        X-axis direction.
    direction_y : Union[~numpy.ndarray, RealSequence, UnitVector3D, Vector3D]
        Y-axis direction.
    major_radius : Union[Quantity, Distance, Real]
        Major radius of the torus.
    minor_radius : Union[Quantity, Distance, Real]
        Minor radius of the torus.
    """

    @check_input_types
    def __init__(
        self,
        origin: Union[np.ndarray, RealSequence, Point3D],
        major_radius: Union[Quantity, Distance, Real],
        minor_radius: Union[Quantity, Distance, Real],
        reference: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        axis: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Z,
    ):
        """Initialize ``Torus`` class."""
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
        """
        Create a transformed copy of the torus based on a transformation matrix.

        Parameters
        ----------
        matrix : Matrix44
            The transformation matrix to apply to the torus.

        Returns
        -------
        Torus
            A new torus that is the transformed copy of the original torus.
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
        """
        Create a mirrored copy of the torus along the y-axis.

        Returns
        -------
        Torus
            A new torus that is a mirrored copy of the original torus.
        """
        return Torus(
            self.origin, self.major_radius, self.minor_radius, -self._reference, -self._axis
        )

    def evaluate(self, parameter: ParamUV) -> "TorusEvaluation":
        """
        Evaluate the torus at the given parameters.

        Parameters
        ----------
        parameter : ParamUV
            The parameters (u,v) at which to evaluate the torus.

        Returns
        -------
        TorusEvaluation
            The resulting evaluation.
        """
        return TorusEvaluation(self, parameter)

    def get_u_parameterization(self):
        """
        Retrieve the U parameter parametrization conditions.

        The U parameter specifies the longitude angle, increasing clockwise (East) about
        the axis (right hand corkscrew law). It has a zero parameter at
        Geometry.Frame.DirX, and a period of 2*pi.

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
        at the equator. For the donut, where the Geometry.Torus.MajorRadius is greater
        than the Geometry.Torus.MinorRadius, the range is [-pi, pi] and the
        parameterization is periodic. For a degenerate torus, the range is restricted
        accordingly and the parameterization is non- periodic.

        Returns
        -------
        Parameterization
            Information about how a torus's v parameter is parameterized.
        """
        return Parameterization(
            ParamForm.PERIODIC, ParamType.CIRCULAR, Interval(-np.pi / 2, np.pi / 2)
        )

    def project_point(self, point: Point3D) -> "TorusEvaluation":
        """
        Project a point onto the torus and return its ``TorusEvaluation``.

        Parameters
        ----------
        point : Point3D
            The point to project onto the torus.

        Returns
        -------
        TorusEvaluation
            The resulting evaluation.
        """
        vector1 = UnitVector3D.from_points(self.origin, point)
        u = np.arctan2(vector1.dot(self.dir_y), vector1.dot(self.dir_x))
        localX = np.cos(u) * self.dir_x + np.sin(u) * self.dir_y
        delta = self.major_radius.m * localX
        vector2 = vector1 - delta
        if self.major_radius.m >= self.minor_radius.m:
            v = np.arctan2(vector2.dot(self.dir_z), vector2.dot(localX))
            return TorusEvaluation(self, ParamUV(u, v))
        vector3 = vector1 + delta
        v1 = np.arctan2(vector2.dot(self.dir_z), vector2.dot(localX)), -np.pi
        v2 = np.arctan2(vector3.dot(self.dir_z), vector3.dot(localX)), -np.pi
        if np.power(
            np.linalg.norm((TorusEvaluation(self, ParamUV(u, v1)).position() - point)), 2
        ) < np.power(
            np.linalg.norm((TorusEvaluation(self, ParamUV(u + np.pi, v2)).position() - point)), 2
        ):
            return TorusEvaluation(self, ParamUV(u, v1))
        else:
            return TorusEvaluation(self, ParamUV(u + np.pi, v2))


class TorusEvaluation(SurfaceEvaluation):
    """
    ``Torus`` evaluation at certain parameters.

    Parameters
    ----------
    Torus: ~ansys.geometry.core.primitives.torus.Torus
        The ``Torus`` object to be evaluated.
    parameter: ParamUV
        The parameters (u, v) at which the ``Torus`` evaluation is requested.
    """

    def __init__(self, torus: Torus, parameter: ParamUV) -> None:
        """``TorusEvaluation`` class constructor."""
        self._torus = torus
        self._parameter = parameter
        self.cache = {}

    @property
    def torus(self) -> Torus:
        """The torus being evaluated."""
        return self._torus

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
            The point that lies on the torus at this evaluation.
        """
        return (
            self._torus.origin
            + (self._torus.major_radius.m + np.cos(self.parameter.v) * self._torus.minor_radius.m)
            * self.__cylinder_normal
            + np.sin(self.parameter.v) * self._torus.minor_radius.m * self._torus.dir_z
        )

    @cached_property
    def normal(self) -> UnitVector3D:
        """
        The normal to the surface.

        Returns
        -------
        UnitVector3D
            The normal unit vector to the torus at this evaluation.
        """
        return UnitVector3D(
            np.cos(self.parameter.v) * self.__cylinder_normal
            + np.sin(self.parameter.v) * self._torus.dir_z
        )

    @cached_property
    def __cylinder_normal(self) -> Vector3D:
        """
        The normal to the surface.

        Returns
        -------
        UnitVector3D
            The normal unit vector to the torus at this evaluation.
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
        """
        The first derivative with respect to u.

        Returns
        -------
        Vector3D
            The first derivative with respect to u.
        """
        return (
            self._torus.major_radius.m + np.cos(self.parameter.v) * self._torus.minor_radius.m
        ) * self.__cylinder_tangent

    @cached_property
    def v_derivative(self) -> Vector3D:
        """
        The first derivative with respect to v.

        Returns
        -------
        Vector3D
            The first derivative with respect to v.
        """
        return (
            -np.sin(self.parameter.v) * self._torus.minor_radius.m * self.__cylinder_tangent
            + np.cos(self.parameter.v) * self._torus.minor_radius.m * self._torus.dir_z
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
        return (
            -(self._torus.major_radius.m + np.cos(self.parameter.v))
            * self._torus.minor_radius.m
            * self.__cylinder_normal
        )

    @cached_property
    def uv_derivative(self) -> Vector3D:
        """
        The second derivative with respect to u and v.

        Returns
        -------
        Vector3D
            The second derivative with respect to u and v.
        """
        return -np.sin(self.parameter.v) * self._torus.minor_radius.m * self.__cylinder_tangent

    @cached_property
    def vv_derivative(self) -> Vector3D:
        """
        The second derivative with respect to v.

        Returns
        -------
        Vector3D
            The second derivative with respect to v.
        """
        return (
            -np.cos(self.parameter.v) * self._torus.minor_radius.m * self.__cylinder_normal
            - np.sin(self.parameter.v) * self._torus.minor_radius.m * self._torus.dir_z
        )

    @cached_property
    def curvature(self) -> Tuple[Real, Vector3D, Real, Vector3D]:
        """
        The curvature of the ``Torus``.

        Returns
        -------
        Tuple[Real, Vector3D, Real, Vector3D]
            The minimum and maximum curvature value and direction, respectively.
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
        """
        The minimum curvature of the torus.

        Returns
        -------
        Real
            The minimum curvature of the torus.
        """
        return self.curvature[0]

    @cached_property
    def min_curvature_direction(self) -> UnitVector3D:
        """
        The minimum curvature direction.

        Returns
        -------
        UnitVector3D
            The minimum curvature direction.
        """
        return self.curvature[1]

    @cached_property
    def max_curvature(self) -> Real:
        """
        The maximum curvature of the torus.

        Returns
        -------
        Real
            The maximum curvature of the torus.
        """
        return self.curvature[2]

    @cached_property
    def max_curvature_direction(self) -> UnitVector3D:
        """
        The maximum curvature direction.

        Returns
        -------
        UnitVector3D
            The maximum curvature direction.
        """
        return self.curvature[3]
