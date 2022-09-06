"""``Sketch`` class module."""

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.shapes.circle import CircleShape
from ansys.geometry.core.shapes.ellipse import EllipseShape
from ansys.geometry.core.shapes.line import LineShape
from ansys.geometry.core.typing import Real


class Sketch:
    """
    Provides Sketch class for building 2D sketch elements.
    """

    def __init__(
        self,
        origin: Point3D = Point3D([0, 0, 0]),
        dir_1: UnitVector3D = UnitVector3D([1, 0, 0]),
        dir_2: UnitVector3D = UnitVector3D([0, 1, 0]),
    ):
        """Constructor method for ``Sketch``."""
        # TODO: assign a reference frame to the base shape
        # self._frame = Frame.from_origin_and_vectors(origin, dir_1, dir_2)
        # self._plane = self._frame.plane
        # self._origin = self._frame.origin

        # TODO: deprecate in favor of reference frame
        if dir_1.cross(dir_2) == Vector3D([0, 0, 0]):
            raise ValueError("Reference vectors must be linearly independent.")
        self._i, self._j = dir_1.normalize(), dir_2.normalize()
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
        origin: Point3D,
        dir_1: UnitVector3D = UnitVector3D([1, 0, 0]),
        dir_2: UnitVector3D = UnitVector3D([0, 1, 0]),
    ):
        """Create a circle shape on the sketch.

        Parameters
        ----------
        radius : Real
            The radius of the circle.
        origin : Point3D
            A ``Point3D`` representing the origin of the shape.
        dir_1 : UnitVector3D
            A :class:``UnitVector3D`` representing the first fundamental direction
            of the reference plane where the shape is contained.
        dir_2 : UnitVector3D
            A :class:``UnitVector3D`` representing the second fundamental direction
            of the reference plane where the shape is contained.

        Returns
        -------
        CircleShape
            An object representing the circle added to the sketch.

        """
        circle = CircleShape(radius, origin, dir_1, dir_2)
        self.append_shape(circle)
        return circle

    def draw_ellipse(
        self,
        a: Real,
        b: Real,
        origin: Point3D,
        dir_1: UnitVector3D = UnitVector3D([1, 0, 0]),
        dir_2: UnitVector3D = UnitVector3D([0, 1, 0]),
    ):
        """Create an ellipse shape on the sketch.

        Parameters
        ----------
        a : Real
            The semi-major axis of the ellipse.
        b : Real
            The semi-minor axis of the ellipse.
        origin : Point3D
            A ``Point3D`` representing the origin of the shape.
        dir_1 : UnitVector3D
            A :class:``UnitVector3D`` representing the first fundamental direction
            of the reference plane where the shape is contained.
        dir_2 : UnitVector3D
            A :class:``UnitVector3D`` representing the second fundamental direction
            of the reference plane where the shape is contained.

        Returns
        -------
        EllipseShape
            An object representing the ellipse added to the sketch.

        """
        ellipse = EllipseShape(a, b, origin, dir_1, dir_2)
        self.append_shape(ellipse)
        return ellipse

    def draw_line(self, point_1: Point3D, point_2: Point3D) -> LineShape:
        """
        Add a line segment sketch object to the sketch plane.

        Parameters
        ----------
        point_1 : Point3D
            Start of the line segment.
        point_2 : Point3D
            End of the line segment.

        Returns
        -------
        LineShape
            An object representing the line added to the sketch.

        """
        line = LineShape(point_1, point_2)
        self.append_shape(line)
        return line
