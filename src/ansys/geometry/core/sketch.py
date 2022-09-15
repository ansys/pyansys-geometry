"""``Sketch`` class module."""

from typing import Optional, Union

from pint import Quantity

from ansys.geometry.core.math import Plane, Point, UnitVector, Vector
from ansys.geometry.core.misc import Distance
from ansys.geometry.core.shapes import Arc, BaseShape, Circle, Ellipse, Line, Polygon, Segment


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
    def plane(self) -> Plane:
        """Return the fundamental plane where all sketch shapes are contained.

        Returns
        -------
        Plane
            The fundamental plane where all sketch shapes are contained.

        """
        return self._plane

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
        if self._plane == shape.plane:
            self.shapes_list.append(shape)
        else:
            raise ValueError("The provided shape does not belong to the same plane as the Sketch.")

    def draw_circle(self, center: Union[tuple, Point], radius: Union[Quantity, Distance]):
        """Create a circle shape on the sketch.

        Parameters
        ----------
        center: Point, tuple
            A :class:`tuple` or :class:`Point` representing the local x and y
            coordinates of the center for the circle.
        radius : Union[Quantity, Distance]
            The radius of the circle.

        Returns
        -------
        Circle
            An object representing the circle added to the sketch.

        """
        # Force to point class conversion if required
        if not isinstance(center, Point):
            center = Point(center.magnitude, center.units)

        # Validate dimensions of the point
        if not point.is_2d:
            raise ValueError("Center of the point must be defined by x and y coordinates.")

        # Express the center of the circle in the global coordinate system
        center = self.plane.frame.local_to_global @ np.hstack((center, 0))

        # Instantiate the circle, add it to the list of shapes and return it
        circle = Circle(self._plane, center, radius)
        self.append_shape(circle)
        return circle

    def draw_ellipse(
        self,
        center: Union[tuple, Point],
        semi_major_axis: Union[Quantity, Distance],
        semi_minor_axis: Union[Quantity, Distance],
    ):
        """Create an ellipse shape on the sketch.

        Parameters
        ----------
        center: tuple, Point
            A :class:`Point` representing the center of the ellipse.
        semi_major_axis : Union[Quantity, Distance]
            The semi-major axis of the ellipse.
        semi_minor_axis : Union[Quantity, Distance]
            The semi-minor axis of the ellipse.

        Returns
        -------
        Ellipse
            An object representing the ellipse added to the sketch.

        """
        # Force to point class conversion if required
        if not isinstance(center, Point):
            center = Point(center.magnitude, center.units)

        # Validate dimensions of the point
        if not point.is_2d:
            raise ValueError("Center of the point must be defined by x and y coordinates.")

        # Express the center of the circle in the global coordinate system
        center = self.plane.frame.local_to_global @ np.hstack((center, 0))

        # Instantiate the ellipse, add it to the list of shapes and return it
        ellipse = Ellipse(self.plane, center, semi_major_axis, semi_minor_axis)
        self.append_shape(ellipse)
        return ellipse

    def draw_segment(
        self,
        start_point: Union[tuple, Point],
        end_point: Union[tuple, Point],
    ) -> Segment:
        """
        Add a segment sketch object to the sketch plane.

        Parameters
        ----------
        start_point : tuple, Point
            Start of the line segment.
        end_point : tuple, Point
            End of the line segment.

        Returns
        -------
        Segment
            An object representing the segment added to the sketch.

        """
        # Force to point class conversion if required
        start_point, end_point = [
            Point(point.magnitude, point.units)
            for point in [start_point, end_point]
            if not isinstance(point, Point)
        ]

        # Validate dimensions of the point
        for point in [start_point, end_point]:
            if not point.is_2d:
                raise ValueError("Center of the point must be defined by x and y coordinates.")

        # Express the center of the circle in the global coordinate system
        start_point, end_point = [
            self.plane.frame.local_to_global @ np.hstack((point, 0))
            for point in [start_point, end_point]
        ]

        # Instantiate the segment, add it to the list of shapes and return it
        segment = Segment(self.plane, start_point, end_point)
        self.append_shape(segment)
        return segment

    def draw_line(
        self,
        start_point: Union[tuple, Point],
        direction: Union[tuple, UnitVector, Vector],
    ) -> Line:
        """
        Add a line sketch object to the sketch plane.

        Parameters
        ----------
        start_point : Point
            Origin/start of the line.
        direction: Union[Vector, UnitVector]
            Direction of the line.

        Returns
        -------
        Line
            An object representing the line added to the sketch.

        """
        # Convert to point class if required
        if not isinstance(start_point, Point):
            center = Point(start_point.magnitude, start_point.units)

        # Validate dimensions of the point
        if not point.is_2d:
            raise ValueError("Start point of the line must be defined by a 2D point.")

        # Convert to vector class if required
        if not isinstance(direction, [UnitVector, Vector]):
            direction = UnitVector(direction.magnitude, direction.units)

        # Validate dimensions of the point
        if not point.is_2d:
            raise ValueError("Fundamental direction of the line must be defined by a 2D vector.")

        # Express the start point and the direction in the global coordinates
        # space
        start_point, direction = [
            self.plane.frame.local_to_global @ np.hstack((attr, 0))
            for attr in [start_point, direction]
        ]

        # Instantiate the line, add it to the list of shapes and return it
        line = Line(self.plane, start_point, direction)
        self.append_shape(line)
        return line

    def draw_polygon(
        self, center: Union[tuple, Point], inner_radius: Union[Quantity, Distance], sides: int
    ):
        """Create a polygon shape on the sketch.

        Parameters
        ----------
        center: tuple, Point
            A :class:`Point` representing the center of the circle.
        inner_radius : Union[Quantity, Distance]
            The inradius(apothem) of the polygon.
        sides : int
            Number of sides of the polygon.

        Returns
        -------
        Polygon
            An object for modelling polygonal shapes.

        """
        # Force to point class conversion if required
        if not isinstance(center, Point):
            center = Point(center.magnitude, center.units)

        # Validate dimensions of the point
        if not point.is_2d:
            raise ValueError("Center of the polygon must be a 2D point.")

        # Express the center of the polygon in the global coordinate system
        center = self.plane.frame.local_to_global @ np.hstack((center, 0))

        # Instantiate the polygon, add it to the list of shapes and return it
        polygon = Polygon(self_plane, center, inner_radius, sides)
        self.append_shape(polygon)
        return polygon

    def draw_arc(
        self,
        center: Union[tuple, Point],
        start_point: Union[tuple, Point],
        end_point: Union[tuple, Point],
    ):
        """Create an arc of circumference shape on the sketch.

        Parameters
        ----------
        center : tuple, Point
            A :class:`tuple` or :class:``Point`` representing the center of the shape.
        start_point : tuple, Point
            A :class:`tuple` or :class:``Point`` representing the start of the shape.
        end_points : tuple, Point
            A :class:`tuple` or :class:``Point`` representing the end of the shape.

        Returns
        -------
        Arc
            An object representing the arc added to the sketch.

        """
        # Force to point class conversion if required
        center, start_point, end_point = [
            Point(point.magnitude, point.units)
            for point in [center, start_point, end_point]
            if not isinstance(point, Point)
        ]

        # Validate dimensions of the point
        for point in [center, start_point, end_point]:
            if not point.is_2d:
                raise ValueError("Center of the point must be defined by x and y coordinates.")

        # Express the center of the arc in the global coordinate system
        center, start_point, end_point = [
            self.plane.frame.local_to_global @ np.hstack((point, 0))
            for point in [center, start_point, end_point]
        ]

        # Instantiate the arc, add it to the list of shapes and return it
        arc = Arc(self.plane, center, start_point, end_point)
        self.append_shape(arc)
        return arc
