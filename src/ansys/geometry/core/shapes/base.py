"""``BaseShape`` class module."""

from typing import List, Optional

from pint import Quantity, Unit

from ansys.geometry.core.math import Plane, Point, Rotation, Scaling, Translation, UnitVector
from ansys.geometry.core.misc import UNIT_ANGLE, check_type
from ansys.geometry.core.typing import Real


class BaseShape:
    """Provides base class for modeling shapes.

    Parameters
    ----------
    plane : Plane
        A :class:`Plane` representing the planar surface where the shape is contained.
    is_closed: Optional[bool]
        A boolean variable to define whether the shape is open or closed.
        By default, ``False``.
    """

    def __init__(
        self,
        plane: Plane,
        is_closed: Optional[bool] = False,
    ):
        """Initializes the base shape."""

        check_type(plane, Plane)
        self._plane = plane
        self._is_closed = is_closed

    @property
    def plane(self) -> Plane:
        """The Plane in which the shape is contained."""
        return self._plane

    @property
    def i(self) -> UnitVector:
        """The fundamental vector along the first axis of the reference frame."""
        return self.plane.direction_x

    @property
    def j(self) -> UnitVector:
        """The fundamental vector along the second axis of the reference frame."""
        return self.plane.direction_y

    @property
    def k(self) -> UnitVector:
        """The fundamental vector along the third axis of the reference frame."""
        return self.plane.direction_z

    @property
    def origin(self) -> Point:
        """The origin of the reference frame."""
        return self.plane.origin

    def points(self, num_points: Optional[int] = 100) -> List[Point]:
        """Returns a list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point]
            A list of points representing the shape.
        """
        return self.plane.from_local_to_global @ self.local_points

    @property
    def x_coordinates(self) -> List[Real]:
        """Return all the x coordinates for the points of the shape.

        Returns
        -------
        List[Real]
            A list containing the values for the x-coordinates of the shape.

        """
        return [point[0] for point in self._points]

    @property
    def y_coordinates(self) -> List[Real]:
        """Return all the y coordinates for the points of the shape.

        Returns
        -------
        List[Real]
            A list containing the values for the y-coordinates of the shape.

        """
        return [point[1] for point in self._points]

    @property
    def z_coordinates(self) -> List[Real]:
        """Return all the y coordinates for the points of the shape.

        Returns
        -------
        List[Real]
            A list containing the values for the z-coordinates of the shape.

        """
        return [point[2] for point in self._points]

    @property
    def perimeter(self) -> Quantity:
        """Return the perimeter of the shape.

        Returns
        -------
        Quantity
            The perimeter of the shape.

        """
        if self.is_open:
            raise AttributeError("No perimeter can be computed for open BaseShape objects.")
        else:
            raise NotImplementedError

    @property
    def area(self) -> Quantity:
        """Return the area of the shape.

        Returns
        -------
        Quantity
            The area of the shape.

        """
        if self.is_open:
            raise AttributeError("No area can be computed for open BaseShape objects.")
        else:
            raise NotImplementedError

    @property
    def is_closed(self) -> bool:
        """Assert whether the shape is closed or not.

        Returns
        -------
        bool
            ``True`` if the shape is closed, ``False`` otherwise.

        """
        raise self._is_closed

    @property
    def is_open(self) -> bool:
        """Assert whether the shape is open or not.

        Returns
        -------
        bool
            ``True`` if the shape is open, ``False`` otherwise.

        """
        return not self.is_closed

    def rotate(self, center, angle, axis, unit: Optional[Unit] = UNIT_ANGLE) -> Point:
        """Return the rotated shape in the given axis at given angle.

        Parameters
        ----------
        center : Point
            The center of the base shape
        angle : Union[~numpy.ndarray, Real]
            Angle determining the rotation.
        axis : str
            Axis of rotation
        unit : Unit, optional
            Units employed to define the angle of rotation,
            by default ``UNIT_ANGLE``.

        Returns
        -------
        Point
            The rotated center point of shape
        """
        return Rotation(center, angle, axis, unit)

    def translate(self, center, vector) -> Point:
        """Return the translated shape in the the given ``Vector``.

        Parameter
        ---------
        center: Pint
            the center of the shape to gets translated
        vector : Vector
            A :class:`Vector` representing the translating direction.

        Returns
        -------
        Point
            The translated point
        """
        return Translation(center, vector)

    def scale(self, point, vector) -> Point:
        """Return the scaled shape in the the given ``Vector``.

        Parameter
        ---------
        input : Point
            The value of shape to gets scaled
        vector : Vector
            A :class:`Vector` representing the Scaling direction.

        Returns
        -------
        Point
            The scaled point
        """
        return Scaling(point, vector)
