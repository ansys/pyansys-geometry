"""A module containing a class for modeling ellipses."""

import numpy as np

from ansys.geometry.core.primitives.point import Point2D
from ansys.geometry.core.sketch.curve import SketchCurve


class EllipseSketch(SketchCurve):
    """A class for modelling ellipses."""

    def __init__(self, points, origin):
        super().__init__(points, origin)

    @classmethod
    def from_axes(cls, a, b, origin=None, resolution=150):
        """Create an ellipse from its semi-major and semi-minor axes."""
        # Assert that the curve is an ellipse and not a parabola or hyperbola
        ecc = (a ** 2 - b ** 2) ** 0.5 / a
        if ecc >= 1:
            raise ValueError("The curve defined is not an ellipse.")

        # Unpack the x and y coordinates for the origin point
        if origin is None:
            origin = Point2D([0, 0])

        # Generate the points on the ellipse
        theta = np.linspace(0, 2 * np.pi, resolution)
        x_coords = origin.x + a * np.cos(theta)
        y_coords = origin.y + b * np.sin(theta)

        # Generate all the point instances
        points = [Point2D([x, y]) for x, y in zip(x_coords, y_coords)]
        return cls(points, origin)

    @classmethod
    def from_focii_and_point(f1, f2, point, origin=None, resolution=100):
        """Create an ellipse from its focci and a point."""
        raise NotImplementedError
