"""A module containing a class for modeling ellipses."""
from typing import Optional

import numpy as np

from ansys.geometry.core import Real
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
    def semimajor_axis(self) -> float:
        """Return the semi-major axis of the ellipse.

        Returns
        -------
        float
            Semi-major axis of the ellipse.

        """
        return self._semimajor_axis

    @property
    def a(self) -> float:
        """Return the semi-major axis of the ellipse.

        Returns
        -------
        float
            Semi-major axis of the ellipse.

        """
        return self.semimajor_axis

    @property
    def semiminor_axis(self) -> float:
        """Return the semi-minor axis of the ellipse.

        Returns
        -------
        float
            Semi-major axis of the ellipse.

        """
        return self._semiminor_axis

    @property
    def b(self) -> float:
        """Return the semi-minor axis of the ellipse.

        Returns
        -------
        float
            Semi-major axis of the ellipse.

        """
        return self.semiminor_axis

    @property
    def eccentricity(self) -> float:
        """Return the eccentricity of the ellipse.

        Returns
        -------
        float
            Eccentricity of the ellipse.

        """
        return (self.a**2 - self.b**2) ** 0.5 / self.a

    @property
    def ecc(self) -> float:
        """Return the eccentricity of the ellipse.

        Returns
        -------
        float
            Eccentricity of the ellipse.

        """
        return self.eccentricity

    @property
    def linear_eccentricity(self) -> float:
        """Return the linear eccentricity of the ellipse.

        Returns
        -------
        float
            Eccentricity of the ellipse.

        Notes
        -----
        The linear eccentricity is the distance from the center to the focus.

        """
        return (self.a**2 - self.b**2) ** 0.5

    @property
    def c(self) -> float:
        """Return the linear eccentricity of the ellipse.

        Returns
        -------
        float
            Eccentricity of the ellipse.

        Notes
        -----
        The linear eccentricity is the distance from the center to the focus.

        """
        return self.linear_eccentricity

    @property
    def semilatus_rectum(self) -> float:
        """Return the semi-latus rectum of the ellipse.

        Returns
        -------
        float
            Semi-latus rectum of the ellipse.

        """
        return self.b**2 / a

    @property
    def l(self) -> float:
        """Return the semi-latus rectum of the ellipse.

        Returns
        -------
        float
            Semi-latus rectum of the ellipse.

        """
        return self.semilatus_rectum

    @classmethod
    def from_axes(
        cls,
        a: Real,
        b: Real,
        origin: Optional[Point2D] = Point2D([0, 0]),
        resolution: Optional[int] = 150,
    ):
        """Create an ellipse from its semi-major and semi-minor axes.

        Parameters
        ----------
        a : int, float
            The semi-major axis of the ellipse.
        b : int, float
            The semi-minor axis of the ellipse.
        origin : Point2D
            A ``Point2D`` representing the origin of the ellipse.
        resolution : int
            Number of points to be used when generating points for the ellipse.

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
        points = [Point2D([x, y]) for x, y in zip(x_coords, y_coords)]
        ellipse = cls(points, origin)
        ellipse._semimajor_axis = a
        ellipse._semiminor_axis = b
        return ellipse
