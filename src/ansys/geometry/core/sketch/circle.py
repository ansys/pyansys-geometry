"""``CircleSketch`` class module."""

import numpy as np

from ansys.geometry.core.primitives.point import Point2D
from ansys.geometry.core.sketch.curve import SketchCurve


class CircleSketch(SketchCurve):
    """Provides circle representation within a sketch environment."""

    def __init__(self, points, origin):
        """Constructor method for ``CircleSketch``."""
        super().__init__(points, origin)
        self._radius = np.linalg.norm(origin - points[0])

    @classmethod
    def from_radius(cls, radius, origin=None, resolution=150):
        """Create a circle from its radius and center."""

        # Unpack the x and y coordinates for the center point
        if origin is None:
            origin = Point2D([0, 0])

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
