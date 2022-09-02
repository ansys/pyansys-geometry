"""``CircleSketch`` class module."""
from typing import Optional, Sequence

import numpy as np
from pint import Unit

from ansys.geometry.core import UNIT_LENGTH, Real
from ansys.geometry.core.primitives.point import Point2D
from ansys.geometry.core.sketch.curve import SketchCurve


class CircleSketch(SketchCurve):
    """Provides circle representation within a sketch environment."""

    def __init__(self, points: Sequence[Point2D], origin: Point2D):
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

    @property
    def radius(self) -> Real:
        """Return the radius of the circle.

        Returns
        -------
        Real
            The radius of the circle.
        """
        return self._radius

    @property
    def r(self) -> Real:
        """Return the radius of the circle.

        Returns
        -------
        Real
            The radius of the circle.
        """
        return self.radius

    @classmethod
    def from_radius(
        cls,
        radius: Real,
        origin: Optional[Point2D] = Point2D([0, 0]),
        resolution: Optional[int] = 150,
        unit: Optional[Unit] = UNIT_LENGTH,
    ):
        """Create a circle from its radius and center.

        Parameters
        ----------
        radius : Real
            The radius of the circle.
        origin : Point2D
            A ``Point2D`` representing the origin of the ellipse.
        resolution : int
            Number of points to be used when generating points for the ellipse.
        unit : Unit, optional
            Units employed to define the Point3D values, by default ``UNIT_LENGTH``

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
        points = [Point2D([x, y], unit) for x, y in zip(x_coords, y_coords)]
        circle = cls(points, origin)
        circle._radius = radius
        return circle
