"""``Sketch`` class module."""

from typing import Optional, Union

from ansys.geometry.core.math import UNIT_VECTOR_X, UNIT_VECTOR_Y, ZERO_VECTOR3D
from ansys.geometry.core.math.point import Point
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.shapes.circle import Circle
from ansys.geometry.core.shapes.ellipse import Ellipse
from ansys.geometry.core.shapes.line import Line, Segment
from ansys.geometry.core.shapes.polygon import Polygon
from ansys.geometry.core.typing import Real


class Sketch:
    """
    Provides Sketch class for building 2D sketch elements.
    """

    def __init__(
        self,
        origin: Optional[Point] = Point([0, 0, 0]),
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
    ):
        """Constructor method for ``Sketch``."""
        # TODO: assign a reference frame to the base shape
        # self._frame = Frame.from_origin_and_vectors(origin, dir_1, dir_2)
        # self._plane = self._frame.plane
        # self._origin = self._frame.origin

        # TODO: deprecate in favor of reference frame
        # TODO: we should be checking that all added shapes belong to the same plane
        # defined by the origin and the two fundamental directions. For another PR.
        if dir_1.cross(dir_2) == ZERO_VECTOR3D:
            raise ValueError("Reference vectors must be linearly independent.")
        self._i, self._j = dir_1, dir_2
        self._k = self._i.cross(self._j)
        self._origin = origin

        # Collect all shapes in a list
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

    def draw_circle(
        self,
        radius: Real,
        origin: Point,
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
    ):
        """Create a circle shape on the sketch.

        Parameters
        ----------
        radius : Real
            The radius of the circle.
        origin : Point
            A :class:`Point` representing the origin of the shape.
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
        Circle
            An object representing the circle added to the sketch.

        """
        circle = Circle(radius, origin, dir_1, dir_2)
        self.append_shape(circle)
        return circle

    def draw_ellipse(
        self,
        a: Real,
        b: Real,
        origin: Point,
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
    ):
        """Create an ellipse shape on the sketch.

        Parameters
        ----------
        a : Real
            The semi-major axis of the ellipse.
        b : Real
            The semi-minor axis of the ellipse.
        origin : Point
            A :class:`Point` representing the origin of the shape.
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
            An object representing the ellipse added to the sketch.

        """
        ellipse = Ellipse(a, b, origin, dir_1, dir_2)
        self.append_shape(ellipse)
        return ellipse

    def draw_segment(
        self,
        start: Point,
        end: Point,
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
    ) -> Segment:
        """
        Add a segment sketch object to the sketch plane.

        Parameters
        ----------
        start : Point
            Start of the line segment.
        end : Point
            End of the line segment.
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
        Segment
            An object representing the segment added to the sketch.

        """
        segment = Segment(start, end, dir_1=dir_1, dir_2=dir_2)
        self.append_shape(segment)
        return segment

    def draw_line(
        self,
        origin: Point,
        direction: Union[Vector3D, UnitVector3D],
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
    ) -> Line:
        """
        Add a line sketch object to the sketch plane.

        Parameters
        ----------
        origin : Point
            Origin of the line.
        direction: Union[Vector3D, UnitVector3D]
            Direction of the line.
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
        Line
            An object representing the line added to the sketch.

        """
        line = Line(origin, direction, dir_1=dir_1, dir_2=dir_2)
        self.append_shape(line)
        return line

    def draw_polygon(
        self,
        radius: Real,
        sides: int,
        origin: Point,
        dir_1: UnitVector3D = UnitVector3D([1, 0, 0]),
        dir_2: UnitVector3D = UnitVector3D([0, 1, 0]),
    ):
        """Create a polygon shape on the sketch.

        Parameters
        ----------
        radius : Real
            The inradius(apothem) of the polygon.
        sides : int
            Number of sides of the polygon.
        origin : Point
            A :class:``Point`` representing the origin of the polygon.
        dir_1 : UnitVector3D
            A :class:``UnitVector3D`` representing the first fundamental direction
            of the reference plane where the shape is contained.
        dir_2 : UnitVector3D
            A :class:``UnitVector3D`` representing the second fundamental direction
            of the reference plane where the shape is contained.

        Returns
        -------
        PolygonShape
            An object for modelling polygonal shapes.

        """
        polygon = Polygon(radius, sides, origin, dir_1=dir_1, dir_2=dir_2)
        self.append_shape(polygon)
        return polygon
