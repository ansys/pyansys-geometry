"""A module containing a class for modeling ellipses."""
from typing import Optional, Sequence

import numpy as np

from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.sketch.curve import SketchCurve
from ansys.geometry.core.typing import Real


class EllipseSketch(SketchCurve):
    """A class for modelling ellipses."""

    def __init__(self, points: Sequence[Point2D], origin: Point2D):
        """Initialize an instance of ``EllipseSketch``.

        Parameters
        ----------
        points : Sequence[Point2D]
            A list or tuple defining the ellipse.
        origin : Point2D
            A ``Point2D`` representing the origin of the ellipse.

        """
        super().__init__(points, origin)

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

        # Generate all the point instances
        points = [Point2D([x, y]) for x, y in zip(x_coords, y_coords)]
        return cls(points, origin)
