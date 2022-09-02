"""A module containing a class for modeling ellipses."""
from typing import Optional

import numpy as np
from pint import Unit

from ansys.geometry.core import UNIT_LENGTH, Real
from ansys.geometry.core.primitives.point import Point2D
from ansys.geometry.core.sketch.curve import SketchCurve


class EllipseSketch(SketchCurve):
    """A class for modelling ellipses."""

    def __init__(self, points: list[Point2D], origin: Point2D):
        """Initialize an instance of ``EllipseSketch``.

        Parameters
        ----------
        points : list[Point2D]
            A list defining the ellipse.
        origin : Point2D
            A ``Point2D`` representing the origin of the ellipse.

        """
        super().__init__(points, origin)

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
        return (self.a**2 - self.b**2) ** 0.5 / self.a

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
        return self.b**2 / a

    @property
    def l(self) -> Real:
        """Return the semi-latus rectum of the ellipse.

        Returns
        -------
        Real
            Semi-latus rectum of the ellipse.

        """
        return self.semi_latus_rectum

    @classmethod
    def from_axes(
        cls,
        a: Real,
        b: Real,
        origin: Optional[Point2D] = Point2D([0, 0]),
        resolution: Optional[int] = 150,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Create an ellipse from its semi-major and semi-minor axes.

        Parameters
        ----------
        a : Real
            The semi-major axis of the ellipse.
        b : Real
            The semi-minor axis of the ellipse.
        origin : Point2D
            A ``Point2D`` representing the origin of the ellipse.
        resolution : int
            Number of points to be used when generating points for the ellipse.
        unit : Unit, optional
            Units employed to define the Point3D values, by default ``UNIT_LENGTH``

        Returns
        -------
        EllipseSketch
            An object for modelling ellipse sketches.

        """
        # Assert that the curve is an ellipse and not a parabola or hyperbola
        ecc = (a**2 - b**2) ** 0.5 / a
        if ecc >= 1:
            raise ValueError("The curve defined is not an ellipse.")

        # Generate the points on the ellipse
        theta = np.linspace(0, 2 * np.pi, resolution)
        x_coords = origin.x + a * np.cos(theta)
        y_coords = origin.y + b * np.sin(theta)

        # Generate all the point instances and the ellipse
        points = [Point2D([x, y], unit) for x, y in zip(x_coords, y_coords)]
        ellipse = cls(points, origin)
        ellipse._semi_major_axis = a
        ellipse._semi_minor_axis = b
        return ellipse

    @classmethod
    def from_focii_and_point(
        self,
        f1: Point2D,
        f2: Point2D,
        p: Point2D,
        center: Optional[Point2D] = Point2D([0, 0]),
        resolution: Optional[int] = 150,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Create an ellipse from its focii and a point.

        Parameters
        ----------
        f1 : Point2D
            A ``Point2D`` representing the first focus of the ellipse.
        f2 : Point2D
            A ``Point2D`` representing the second focus of the ellipse.
        origin : Point2D
            A ``Point2D`` representing the origin of the ellipse.
        resolution : int
            Number of points to be used when generating points for the ellipse.
        unit : Unit, optional
            Units employed to define the Point3D values, by default ``UNIT_LENGTH``

        """
        f1_to_p, f2_to_p = (f1 - p).norm, (f1 - p).norm
        a = (f1_to_p + f2_to_p) / 2
        b = (((y - origin.y) ** 2) / (1 - (x - origin.x) ** 2 / a**2)) ** 0.5
        return self.from_axes(a, b, origin, resolution)
