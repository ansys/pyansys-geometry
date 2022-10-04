"""``Sketch`` class module."""

from typing import Optional, Union

from pint import Quantity

from ansys.geometry.core.math import Plane, Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.misc import Angle, Distance
from ansys.geometry.core.shapes import (
    Arc,
    BaseShape,
    Box,
    Circle,
    Ellipse,
    Line,
    Polygon,
    Segment,
    Slot,
)
from ansys.geometry.core.typing import Real


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
        if self._plane == shape.plane:
            self.shapes_list.append(shape)
        else:
            raise ValueError("The provided shape does not belong to the same plane as the Sketch.")

    def draw_box(
        self,
        center: Point3D,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Create a box shape on the sketch.

        Parameters
        ----------
        center: Point3D
            A :class:`Point3D` representing the center of the box.
        width : Union[Quantity, Distance, Real]
            The width of the box.
        height : Union[Quantity, Distance, Real]
            The height of the box.
        angle : Optional[Union[Quantity, Real]]
            The placement angle for orientation alignment.

        Returns
        -------
        Box
            An object representing the box added to the sketch.
        """
        box = Box(self._plane, center, width, height, angle)
        self.append_shape(box)
        return box

    def draw_slot(
        self,
        center: Point3D,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Create a slot shape on the sketch.

        Parameters
        ----------
        center: Point3D
            A :class:`Point3D` representing the center of the slot.
        width : Union[Quantity, Distance, Real]
            The width of the slot.
        height : Union[Quantity, Distance, Real]
            The height of the slot.
        angle : Optional[Union[Quantity, Angle, Real]]
            The placement angle for orientation alignment.

        Returns
        -------
        Slot
            An object representing the slot added to the sketch.
        """
        slot = Slot(self._plane, center, width, height, angle)
        self.append_shape(slot)
        return slot

    def draw_circle(self, center: Point3D, radius: Union[Quantity, Distance]):
        """Create a circle shape on the sketch.

        Parameters
        ----------
        center: Point3D
            A :class:`Point3D` representing the center of the circle.
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
        center: Point3D,
        semi_major_axis: Union[Quantity, Distance],
        semi_minor_axis: Union[Quantity, Distance],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Create an ellipse shape on the sketch.

        Parameters
        ----------
        center: Point3D
            A :class:`Point3D` representing the center of the ellipse.
        semi_major_axis : Union[Quantity, Distance]
            The semi-major axis of the ellipse.
        semi_minor_axis : Union[Quantity, Distance]
            The semi-minor axis of the ellipse.
        angle : Optional[Union[Quantity, Angle, Real]]
            The placement angle for orientation alignment.

        Returns
        -------
        Ellipse
            An object representing the ellipse added to the sketch.

        """
        ellipse = Ellipse(self._plane, center, semi_major_axis, semi_minor_axis, angle)
        self.append_shape(ellipse)
        return ellipse

    def draw_segment(
        self,
        start: Point3D,
        end: Point3D,
    ) -> Segment:
        """
        Add a segment sketch object to the sketch plane.

        Parameters
        ----------
        start : Point3D
            Start of the line segment.
        end : Point3D
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
        start: Point3D,
        direction: Union[Vector3D, UnitVector3D],
    ) -> Line:
        """
        Add a line sketch object to the sketch plane.

        Parameters
        ----------
        start : Point3D
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

    def draw_polygon(
        self,
        center: Point3D,
        inner_radius: Union[Vector3D, UnitVector3D],
        sides: int,
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Create a polygon shape on the sketch.

        Parameters
        ----------
        center: Point3D
            A :class:`Point3D` representing the center of the circle.
        inner_radius : Union[Quantity, Distance]
            The inradius(apothem) of the polygon.
        sides : int
            Number of sides of the polygon.
        angle : Optional[Union[Quantity, Angle, Real]]
            The placement angle for orientation alignment.

        Returns
        -------
        Polygon
            An object for modelling polygonal shapes.

        """
        polygon = Polygon(self._plane, center, inner_radius, sides, angle)
        self.append_shape(polygon)
        return polygon

    def draw_arc(
        self, center: Point3D, start: Point3D, end: Point3D, axis: Optional[UnitVector3D] = None
    ):
        """Create an arc shape on the sketch.

        Parameters
        ----------
        center : Point3D
            A :class:``Point3D`` representing the center of the arc.
        start : Point3D
            A :class:``Point3D`` representing the start of the shape.
        end : Point3D
            A :class:``Point3D`` representing the end of the shape.
        axis : Optional[UnitVector]
            A :class:``UnitVector`` determining the rotation direction of the arc.
            It is expected to be orthogonal to the provided plane.
            +z for counter-clockwise rotation. -z for clockwise rotation.
            If not provided, the default will be counter-clockwise rotation.

        Returns
        -------
        Arc
            An object representing the arc added to the sketch.

        """
        arc = Arc(self._plane, center, start, end, axis)
        self.append_shape(arc)
        return arc
