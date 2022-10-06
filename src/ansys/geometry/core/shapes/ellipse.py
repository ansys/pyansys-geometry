"""A module containing a class for modeling ellipses."""
from typing import List, Optional, Union

import numpy as np
from pint import Quantity
from scipy.integrate import quad

from ansys.geometry.core.math import Plane, Point3D
from ansys.geometry.core.misc import Angle, Distance, check_type
from ansys.geometry.core.misc.measurements import UNIT_ANGLE
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.typing import Real


class Ellipse(BaseShape):
    """A class for modeling ellipses.

    Parameters
    ----------
    plane : Plane
        A :class:`Plane <ansys.geometry.core.math.plane.Plane>` representing
        the planar surface where the shape is contained.
    center : Point3D
        A :class:`Point3D <ansys.geometry.core.math.point.Point3D>` representing
        the center of the ellipse.
    semi_major_axis : Union[Quantity, Distance]
        The semi-major axis of the ellipse.
    semi_minor_axis : Union[Quantity, Distance]
        The semi-minor axis of the ellipse.
    angle : Optional[Union[Quantity, Angle, Real]]
        The placement angle for orientation alignment.
    """

    def __init__(
        self,
        plane: Plane,
        center: Point3D,
        semi_major_axis: Union[Quantity, Distance],
        semi_minor_axis: Union[Quantity, Distance],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Initializes the ellipse shape."""
        super().__init__(plane, is_closed=True)
        check_type(center, Point3D)
        check_type(semi_major_axis, (Quantity, Distance))
        check_type(semi_minor_axis, (Quantity, Distance))
        self._center = center
        self._semi_major_axis = (
            semi_major_axis if isinstance(semi_major_axis, Distance) else Distance(semi_major_axis)
        )
        self._semi_minor_axis = (
            semi_minor_axis if isinstance(semi_minor_axis, Distance) else Distance(semi_minor_axis)
        )
        if not self.plane.is_point_contained(center):
            raise ValueError("Center must be contained in the plane.")
        if self._semi_major_axis.value.m_as(self._semi_major_axis.base_unit) <= 0:
            raise ValueError("Semi-major axis must be a real positive value.")
        if self._semi_minor_axis.value.m_as(self._semi_minor_axis.base_unit) <= 0:
            raise ValueError("Semi-minor axis must be a real positive value.")

        if isinstance(angle, (int, float)):
            angle = Angle(angle, UNIT_ANGLE)
        self._angle_offset = angle if isinstance(angle, Angle) else Angle(angle, angle.units)

        # Align both units if misaligned
        if self._semi_major_axis.unit != self._semi_minor_axis.unit:
            self._semi_minor_axis.unit = self._semi_major_axis.unit

        # Ensure that the semi-major axis is equal or larger than the minor one
        if self._semi_major_axis.value.m < self._semi_minor_axis.value.m:
            raise ValueError("Semi-major axis cannot be shorter than semi-minor axis.")

    @property
    def center(self) -> Point3D:
        """The center of the ellipse.

        Returns
        -------
        Point3D
            The center of the ellipse.
        """
        return self._center

    @property
    def semi_major_axis(self) -> Quantity:
        """Return the semi-major axis of the ellipse.

        Returns
        -------
        Quantity
            Semi-major axis of the ellipse.
        """
        return self._semi_major_axis.value

    @property
    def semi_minor_axis(self) -> Quantity:
        """Return the semi-minor axis of the ellipse.

        Returns
        -------
        Quantity
            Semi-minor axis of the ellipse.
        """
        return self._semi_minor_axis.value

    @property
    def eccentricity(self) -> Real:
        """Return the eccentricity of the ellipse.

        Returns
        -------
        Real
            Eccentricity of the ellipse.
        """
        ecc = (
            self.semi_major_axis.m**2 - self.semi_minor_axis.m**2
        ) ** 0.5 / self.semi_major_axis.m
        if ecc == 1:
            raise ValueError("The curve defined is a parabola not an ellipse.")
        elif ecc > 1:
            raise ValueError("The curve defined is an hyperbola not an ellipse.")
        return ecc

    @property
    def linear_eccentricity(self) -> Quantity:
        """Return the linear eccentricity of the ellipse.

        Returns
        -------
        Quantity
            Linear eccentricity of the ellipse.

        Notes
        -----
        The linear eccentricity is the distance from the center to the focus.
        """
        return (self.semi_major_axis**2 - self.semi_minor_axis**2) ** 0.5

    @property
    def semi_latus_rectum(self) -> Quantity:
        """Return the semi-latus rectum of the ellipse.

        Returns
        -------
        Quantity
            Semi-latus rectum of the ellipse.
        """
        return self.semi_minor_axis**2 / self.semi_major_axis

    @property
    def perimeter(self) -> Quantity:
        """Return the perimeter of the ellipse.

        Returns
        -------
        Quantity
            The perimeter of the ellipse.
        """

        def integrand(theta, ecc):
            return np.sqrt(1 - (ecc * np.sin(theta)) ** 2)

        I, _ = quad(integrand, 0, np.pi / 2, args=(self.eccentricity,))
        return 4 * self.semi_major_axis * I

    @property
    def area(self) -> Quantity:
        """Return the area of the ellipse.

        Returns
        -------
        Quantity
            The area of the ellipse.
        """
        return np.pi * self.semi_major_axis * self.semi_minor_axis

    @property
    def components(self) -> List["BaseShape"]:
        """Returns a list containing all simple geometries forming the shape.

        Returns
        -------
        List[BaseShape]
            A list of component geometries forming the shape.
        """
        return [self]

    def local_points(self, num_points: Optional[int] = 100) -> List[Point3D]:
        """Returns a list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point3D]
            A list of points representing the shape.
        """
        angle_cos = np.cos(self._angle_offset.value.m_as(UNIT_ANGLE))
        angle_sin = np.sin(self._angle_offset.value.m_as(UNIT_ANGLE))
        offset_factor = np.arctan2(
            -self.semi_major_axis.m * angle_sin, self.semi_minor_axis.m * angle_cos
        )
        theta = np.linspace(0, 2 * np.pi, num_points)
        center_from_plane_origin = Point3D(
            self.plane.global_to_local @ (self.center - self.plane.origin), self.center.unit
        )

        points = []
        for ang in theta:
            angle_plus_offset_cos = np.cos(ang + offset_factor)
            angle_plus_offset_sin = np.sin(ang + offset_factor)
            points.append(
                Point3D(
                    [
                        center_from_plane_origin.x.to(self.semi_major_axis.units).m
                        + self.semi_major_axis.m * angle_plus_offset_cos * angle_cos
                        - self.semi_minor_axis.m * angle_plus_offset_sin * angle_sin,
                        center_from_plane_origin.y.to(self.semi_major_axis.units).m
                        + self.semi_major_axis.m * angle_plus_offset_cos * angle_sin
                        + self.semi_minor_axis.m * angle_plus_offset_sin * angle_cos,
                        center_from_plane_origin.z.to(self.semi_major_axis.units).m,
                    ],
                    unit=self.semi_major_axis.units,
                )
            )
        return points

    @classmethod
    def from_axes(
        cls,
        center: Point3D,
        semi_major_axis: Union[Quantity, Distance],
        semi_minor_axis: Union[Quantity, Distance],
        plane: Optional[Plane] = Plane(),
    ):
        """Create an ellipse from its semi-major and semi-minor axes.

        Parameters
        ----------
        center : Point3D
            A :class:`Point3D <ansys.geometry.core.math.point.Point3D>` representing the
            center of the ellipse.
        semi_major_axis : Union[Quantity, Distance]
            The semi-major axis of the ellipse.
        semi_minor_axis : Union[Quantity, Distance]
            The semi-minor axis of the ellipse.
        plane : Plane, optional
            A :class:`Plane <ansys.geometry.core.math.plane.Plane>` representing the
            planar surface where the shape is contained.
            By default, the base XY-Plane.

        Returns
        -------
        Ellipse
            An object for modeling elliptical shapes.
        """
        return cls(plane, center, semi_major_axis, semi_minor_axis)
