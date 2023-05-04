"""Provides the ``Cylinder`` class."""

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
from ansys.geometry.core.primitives.circle import Circle
from ansys.geometry.core.primitives.line import Line
from ansys.geometry.core.primitives.parameterization import (
    Interval,
    Parameterization,
    ParamForm,
    ParamType,
    ParamUV,
)
from ansys.geometry.core.primitives.surface_evaluation import ParamUV, SurfaceEvaluation
from ansys.geometry.core.typing import Real, RealSequence


class Cylinder:
    """
    Provides 3D ``Cylinder`` representation.

    Parameters
    ----------
    origin : Union[~numpy.ndarray, RealSequence, Point3D]
        Origin of the cylinder.
    radius : Union[Quantity, Distance, Real]
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
        radius: Union[Quantity, Distance, Real],
        reference: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_X,
        axis: Union[np.ndarray, RealSequence, UnitVector3D, Vector3D] = UNITVECTOR3D_Z,
    ):
        """Initialize ``Cylinder`` class."""
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
    def radius(self) -> Quantity:
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

    def surface_area(self, height: Union[Quantity, Distance, Real]) -> Quantity:
        """
        Surface area of the cylinder.

        Parameters
        ----------
        height : Union[Quantity, Distance, Real]
            By nature, a cylinder is infinite. If you want to get the surface area,
            you must bound it by a height. Normally a cylinder surface is not closed
            (does not have "caps" on the ends). This method will assume it is closed
            for the purpose of getting the surface area.

        Returns
        -------
        Quantity
            The surface area of the temporarily bounded cylinder.
        """
        height = height if isinstance(height, Distance) else Distance(height)
        if height.value <= 0:
            raise ValueError("Height must be a real positive value.")

        return 2 * np.pi * self.radius * height.value + 2 * np.pi * self.radius**2

    def volume(self, height: Union[Quantity, Distance, Real]) -> Quantity:
        """
        Volume of the cylinder.

        Parameters
        ----------
        height : Union[Quantity, Distance, Real]
            By nature, a cylinder is infinite. If you want to get the volume,
            you must bound it by a height. Normally a cylinder surface is not closed
            (does not have "caps" on the ends). This method will assume it is closed
            for the purpose of getting the volume.

        Returns
        -------
        Quantity
            The volume of the temporarily bounded cylinder.
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
            The transformation matrix to apply to the cylinder.

        Returns
        -------
        Cylinder
            A new cylinder that is the transformed copy of the original cylinder.
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
            A new cylinder that is a mirrored copy of the original cylinder.
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
            The parameters (u,v) at which to evaluate the cylinder.

        Returns
        -------
        CylinderEvaluation
            The resulting evaluation.
        """
        return CylinderEvaluation(self, parameter)

    def project_point(self, point: Point3D) -> "CylinderEvaluation":
        """
        Project a point onto the cylinder and return its ``CylinderEvaluation``.

        Parameters
        ----------
        point : Point3D
            The point to project onto the cylinder.

        Returns
        -------
        CylinderEvaluation
            The resulting evaluation.
        """
        circle = Circle(self.origin, self.radius, self.dir_x, self.dir_z)
        u = circle.project_point(point).parameter

        line = Line(self.origin, self.dir_z)
        v = line.project_point(point).parameter

        return CylinderEvaluation(self, ParamUV(u, v))

    def get_u_parameterization(self) -> Parameterization:
        """
        Retrieve the U parameter parametrization conditions.

        The U parameter specifies the clockwise angle around the axis (right hand
        corkscrew law), with a zero parameter at `dir_x`, and a period of 2*pi.

        Returns
        -------
        Parameterization
            Information about how a cylinder's u parameter is parameterized.
        """
        return Parameterization(ParamForm.PERIODIC, ParamType.CIRCULAR, Interval(0, 2 * np.pi))

    def get_v_parameterization(self) -> Parameterization:
        """
        Retrieve the V parameter parametrization conditions.

        The V parameter specifies the distance along the axis, with a zero parameter at
        the XY plane of the Cylinder.

        Returns
        -------
        Parameterization
            Information about how a cylinders's v parameter is parameterized.
        """
        return Parameterization(ParamForm.OPEN, ParamType.LINEAR, Interval(np.NINF, np.inf))


class CylinderEvaluation(SurfaceEvaluation):
    """
    Provides ``Cylinder`` evaluation at certain parameters.

    Parameters
    ----------
    cylinder: ~ansys.geometry.core.primitives.cylinder.Cylinder
        The ``Cylinder`` object to be evaluated.
    parameter: ParamUV
        The parameters (u, v) at which the ``Cylinder`` evaluation is requested.
    """

    def __init__(self, cylinder: Cylinder, parameter: ParamUV) -> None:
        """``CylinderEvaluation`` class constructor."""
        self._cylinder = cylinder
        self._parameter = parameter

    @property
    def cylinder(self) -> Cylinder:
        """The cylinder being evaluated."""
        return self._cylinder

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
            The point that lies on the cylinder at this evaluation.
        """
        return (
            self.cylinder.origin
            + self.cylinder.radius.m * self.__cylinder_normal
            + self.parameter.v * self.cylinder.dir_z
        )

    @cached_property
    def normal(self) -> UnitVector3D:
        """
        The normal to the surface.

        Returns
        -------
        UnitVector3D
            The normal unit vector to the cylinder at this evaluation.
        """
        return UnitVector3D(self.__cylinder_normal)

    @cached_property
    def __cylinder_normal(self) -> Vector3D:
        """
        The normal to the surface.

        Returns
        -------
        UnitVector3D
            The normal unit vector to the cylinder at this evaluation.
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
        The first derivative with respect to u.

        Returns
        -------
        Vector3D
            The first derivative with respect to u.
        """
        return self.cylinder.radius.m * self.__cylinder_tangent

    @cached_property
    def v_derivative(self) -> Vector3D:
        """
        The first derivative with respect to v.

        Returns
        -------
        Vector3D
            The first derivative with respect to v.
        """
        return self.cylinder.dir_z

    @cached_property
    def uu_derivative(self) -> Vector3D:
        """
        The second derivative with respect to u.

        Returns
        -------
        Vector3D
            The second derivative with respect to u.
        """
        return -self.cylinder.radius.m * self.__cylinder_normal

    @cached_property
    def uv_derivative(self) -> Vector3D:
        """
        The second derivative with respect to u and v.

        Returns
        -------
        Vector3D
            The second derivative with respect to u and v.
        """
        return Vector3D([0, 0, 0])

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
        The minimum curvature of the cylinder.

        Returns
        -------
        Real
            The minimum curvature of the cylinder.
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
        return UnitVector3D(self.cylinder.dir_z)

    @cached_property
    def max_curvature(self) -> Real:
        """
        The maximum curvature of the cylinder.

        Returns
        -------
        Real
            The maximum curvature of the cylinder.
        """
        return 1.0 / self.cylinder.radius.m

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
