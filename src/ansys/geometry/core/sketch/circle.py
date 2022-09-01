"""``CircleSketch`` class module."""
from typing import Optional, Union

import numpy as np

from ansys.geometry.core.primitives.point import Point2D
from ansys.geometry.core.sketch.curve import SketchCurve


class CircleSketch(SketchCurve):
    """Provides circle representation within a sketch environment."""

    def __init__(self, points: list[Point2D], origin: Point2D):
        """Initialize an instance of ``CircleSketch``.

        Parameters
        ----------
        points : list[Point2D]
            A list defining the ellipse.
        origin : Point2D
            A ``Point2D`` representing the origin of the ellipse.

        """
        super().__init__(points, origin)
        self._radius = np.linalg.norm(origin - points[0])

    @classmethod
    def from_radius(
        cls,
        radius: Union[int, float],
        origin: Optional[Point2D] = Point2D([0, 0]),
        resolution: Optional[int] = 150,
    ):
        """Create a circle from its radius and center.

        Parameters
        ----------
        radius : int, float
            The radius of the circle.
        origin : Point2D
            A ``Point2D`` representing the origin of the ellipse.
        resolution : int
            Number of points to be used when generating points for the ellipse.

        Returns
        -------
        CircleSketch
            An object for modelling circle sketches.

        """
        # Collect the coordinates of the points for the point
        theta = np.linspace(0, 2 * np.pi, resolution)
        x_coords = origin.x + radius * np.cos(theta)
        y_coords = origin.y + radius * np.sin(theta)

        # Generate all the point instances
        points = [Point2D([x, y]) for x, y in zip(x_coords, y_coords)]
        return cls(points, origin)

    @property
    def radius(self):
        """Return the radius of the circle."""
        return self._radius
