"""A module containing a class for modeling ellipses."""
from typing import List, Optional

import numpy as np
from scipy.integrate import quad

from ansys.geometry.core.math import UNIT_VECTOR_X, UNIT_VECTOR_Y
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.typing import Real


class Ellipse(BaseShape):
    """A class for modeling ellipses.

    Parameters
    ----------
    a : Real
        The semi-major axis of the ellipse.
    b : Real
        The semi-minor axis of the ellipse.
    origin : Point3D
        A :class:`Point3D` representing the origin of the shape.
    dir_1 : Optional[UnitVector3D]
        A :class:`UnitVector3D` representing the first fundamental direction
        of the reference plane where the shape is contained.
        By default, ``UNIT_VECTOR_X``.
    dir_2 : Optional[UnitVector3D]
        A :class:`UnitVector3D` representing the second fundamental direction
        of the reference plane where the shape is contained.
        By default, ``UNIT_VECTOR_Y``.
    """

    def __init__(
        self,
        a: Real,
        b: Real,
        origin: Point3D,
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
    ):
        """Initializes the ellipse shape."""
        super().__init__(origin, dir_1=dir_1, dir_2=dir_2, is_closed=True)
        self._semi_major_axis = a
        self._semi_minor_axis = b

    @property
    def semi_major_axis(self) -> Real:
        """Return the semi-major axis of the ellipse.

        Returns
        -------
        Real
            Semi-major axis of the ellipse.
        """
        return self._semi_major_axis

    @property
    def a(self) -> Real:
        """Return the semi-major axis of the ellipse.

        Returns
        -------
        Real
            Semi-major axis of the ellipse.
        """
        return self.semi_major_axis

    @property
    def semi_minor_axis(self) -> Real:
        """Return the semi-minor axis of the ellipse.

        Returns
        -------
        Real
            Semi-minor axis of the ellipse.
        """
        return self._semi_minor_axis

    @property
    def b(self) -> Real:
        """Return the semi-minor axis of the ellipse.

        Returns
        -------
        Real
            Semi-minor axis of the ellipse.
        """
        return self.semi_minor_axis

    @property
    def eccentricity(self) -> Real:
        """Return the eccentricity of the ellipse.

        Returns
        -------
        Real
            Eccentricity of the ellipse.
        """
        ecc = (self.a**2 - self.b**2) ** 0.5 / self.a
        if ecc == 1:
            raise ValueError("The curve defined is a parabola not an ellipse.")
        elif ecc > 1:
            raise ValueError("The curve defined is an hyperbola not an ellipse.")
        return ecc

    @property
    def ecc(self) -> Real:
        """Return the eccentricity of the ellipse.

        Returns
        -------
        Real
            Eccentricity of the ellipse.
        """
        return self.eccentricity

    @property
    def linear_eccentricity(self) -> Real:
        """Return the linear eccentricity of the ellipse.

        Returns
        -------
        Real
            Linear eccentricity of the ellipse.

        Notes
        -----
        The linear eccentricity is the distance from the center to the focus.
        """
        return (self.a**2 - self.b**2) ** 0.5

    @property
    def c(self) -> Real:
        """Return the linear eccentricity of the ellipse.

        Returns
        -------
        Real
            Linear eccentricity of the ellipse.

        Notes
        -----
        The linear eccentricity is the distance from the center to the focus.
        """
        return self.linear_eccentricity

    @property
    def semi_latus_rectum(self) -> Real:
        """Return the semi-latus rectum of the ellipse.

        Returns
        -------
        Real
            Semi-latus rectum of the ellipse.
        """
        return self.b**2 / self.a

    @property
    def l(self) -> Real:
        """Return the semi-latus rectum of the ellipse.

        Returns
        -------
        Real
            Semi-latus rectum of the ellipse.
        """
        return self.semi_latus_rectum

    @property
    def perimeter(self) -> Real:
        """Return the perimeter of the ellipse.

        Returns
        -------
        Real
            The perimeter of the ellipse.
        """

        def integrand(theta, ecc):
            return np.sqrt(1 - (ecc * np.sin(theta)) ** 2)

        I, _ = quad(integrand, 0, np.pi / 2, args=(self.ecc,))
        return 4 * self.a * I

    @property
    def area(self) -> Real:
        """Return the area of the ellipse.

        Returns
        -------
        Real
            The area of the ellipse.
        """
        return np.pi * self.a * self.b

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
        theta = np.linspace(0, 2 * np.pi, num_points)
        x_local = self.a * np.cos(theta)
        y_local = self.b * np.sin(theta)
        z_local = np.zeros(num_points)
        return [x_local, y_local, z_local]

    @classmethod
    def from_axes(
        cls,
        a: Real,
        b: Real,
        origin: Optional[Point3D] = Point3D([0, 0, 0]),
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
    ):
        """Create an ellipse from its semi-major and semi-minor axes.

        Parameters
        ----------
        a : Real
            The semi-major axis of the ellipse.
        b : Real
            The semi-minor axis of the ellipse.
        origin : Optional[Point3D]
            A :class:`Point3D` representing the origin of the ellipse.
            By default, [0, 0, 0].
        dir_1 : Optional[UnitVector3D]
            A :class:`UnitVector3D` representing the first fundamental direction
            of the reference plane where the shape is contained.
            By default, ``UNIT_VECTOR_X``.
        dir_2 : Optional[UnitVector3D]
            A :class:`UnitVector3D` representing the second fundamental direction
            of the reference plane where the shape is contained.
            By default, ``UNIT_VECTOR_Y``.

        Returns
        -------
        Ellipse
            An object for modeling elliptical shapes.
        """
        # Ensure that the semi-major axis is equal or larger than the minor one
        if a < b:
            raise ValueError("Semi-major axis cannot be shorter than semi-minor axis.")
        return cls(a, b, origin, dir_1=dir_1, dir_2=dir_2)
