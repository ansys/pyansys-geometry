"""``Sketch`` class module."""

from typing import Optional, Union

from pint import Quantity

from ansys.geometry.core.math import Plane, Point, UnitVector, Vector
from ansys.geometry.core.misc import Distance
from ansys.geometry.core.shapes import BaseShape, Circle, Ellipse, Line, Polygon, Segment


class Sketch:
    """
    Provides Sketch class for building 2D sketch elements.
    """

    def __init__(
        self,
        plane: Optional[Plane] = Plane(),
    ):
        """Constructor method for ``Sketch``."""
        self._plane = plane
        self._shapes_list = []

    @property
    def shapes_list(self):
        """Returns the sketched curves."""
        return self._shapes_list

    def append_shape(self, shape: BaseShape):
        """Appends a new shape to the list of shapes in the sketch.

        Parameters
        ----------
        shape : BaseShape
            The shape to the added to the sketch.

        """
        self.shapes_list.append(shape)

    def draw_circle(self, center: Point, radius: Union[Quantity, Distance]):
        """Create a circle shape on the sketch.

        Parameters
        ----------
        center: Point
            A :class:`Point` representing the center of the circle.
        radius : Union[Quantity, Distance]
            The radius of the circle.

        Returns
        -------
        Circle
            An object representing the circle added to the sketch.

        """
        circle = Circle(self._plane, center, radius)
        self.append_shape(circle)
        return circle

    def draw_ellipse(
        self,
        semi_major_axis: Union[Quantity, Distance],
        semi_minor_axis: Union[Quantity, Distance],
    ):
        """Create an ellipse shape on the sketch.

        Parameters
        ----------
        semi_major_axis : Union[Quantity, Distance]
            The semi-major axis of the ellipse.
        semi_minor_axis : Union[Quantity, Distance]
            The semi-minor axis of the ellipse.

        Returns
        -------
        Ellipse
            An object representing the ellipse added to the sketch.

        """
        ellipse = Ellipse(self._plane, semi_major_axis, semi_minor_axis)
        self.append_shape(ellipse)
        return ellipse

    def draw_segment(
        self,
        start: Point,
        end: Point,
    ) -> Segment:
        """
        Add a segment sketch object to the sketch plane.

        Parameters
        ----------
        start : Point
            Start of the line segment.
        end : Point
            End of the line segment.

        Returns
        -------
        Segment
            An object representing the segment added to the sketch.

        """
        segment = Segment(self._plane, start, end)
        self.append_shape(segment)
        return segment

    def draw_line(
        self,
        start: Point,
        direction: Union[Vector, UnitVector],
    ) -> Line:
        """
        Add a line sketch object to the sketch plane.

        Parameters
        ----------
        start : Point
            Origin/start of the line.
        direction: Union[Vector, UnitVector]
            Direction of the line.

        Returns
        -------
        Line
            An object representing the line added to the sketch.

        """
        line = Line(self._plane, start, direction)
        self.append_shape(line)
        return line

    def draw_polygon(self, inner_radius: Union[Vector, UnitVector], sides: int):
        """Create a polygon shape on the sketch.

        Parameters
        ----------
        inner_radius : Union[Quantity, Distance]
            The inradius(apothem) of the polygon.
        sides : int
            Number of sides of the polygon.

        Returns
        -------
        Polygon
            An object for modelling polygonal shapes.

        """
        polygon = Polygon(self._plane, inner_radius, sides)
        self.append_shape(polygon)
        return polygon
