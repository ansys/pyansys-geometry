"""``SketchCurve`` class module."""

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import Vector3D


class BaseShape:
    """Provides mother class for modeling base shape objects."""

    def __init__(self, origin: Point3D, dir_1: Vector3D([1, 0, 0]), dir_2: Vector3D([0, 1, 0])):
        """Initializes the base shape.

        Parameters
        ----------
        origin : Point3D
            A ``Point3D`` representing the origin of the shape.
        dir_1 : Vector3D
            A :class:``Vector3D`` representing the first fundamental direction
            of the reference plane where the sape is contained.
        dir_2 : Vector3D
            A :class:``Vector3D`` representing the second fundamental direction
            of the reference plane where the sape is contained.

        """
        # TODO: assign a reference frame to the base shape
        # self._frame = Frame.from_origin_and_vectors(origin, dir_1, dir_2)
        # self._plane = self._frame.plane
        # self._origin = self._frame.origin

        # TODO: deprecate in favor of reference frame
        if dir_1.dot(dir_2) != 0:
            raise ValueError("Reference vectors are not orthogonal.")
        self._i, self._j = dir_1.normalize(), dir_2.normalize()
        self._k = self.i.cross(self._j)
        self._origin = origin

    @property
    def i(self) -> Vector3D:
        """The fundamental vector along the first axis of the reference frame."""
        return self._i

    @property
    def j(self) -> Vector3D:
        """The fundamental vector along the second axis of the reference frame."""
        return self._j

    @property
    def k(self) -> Vector3D:
        """The fundamental vector along the third axis of the reference frame."""
        return self._k

    @property
    def origin(self) -> Vector3D:
        """The origin of the reference frame."""
        return origin

    def points(self, num_points=100) -> list[Point3D]:
        """Returns al list containing all the points belonging to the sape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        list[Point3D]
            A list of points representing the shape.
        """
        return self.frame.from_local_to_global @ self.local_points

    @property
    def x_coordinates(sefl) -> list[real]:
        """Return all the x coordinates for the points of the shape.

        Returns
        -------
        list[real]
            A list containing the values for the x-coordinates of the shape.

        """
        return [point[0] for point in self._points]

    @property
    def y_coordinates(sefl) -> list[real]:
        """Return all the y coordinates for the points of the shape.

        Returns
        -------
        list[real]
            A list containing the values for the y-coordinates of the shape.

        """
        return [point[1] for point in self._points]

    @property
    def z_coordinates(sefl) -> list[real]:
        """Return all the y coordinates for the points of the shape.

        Returns
        -------
        list[real]
            A list containing the values for the z-coordinates of the shape.

        """
        return [point[2] for point in self._points]

    @property
    def perimeter(self) -> Real:
        """Return the perimeter of the shape.

        Returns
        -------
        Real
            The perimeter of the shape.

        """
        raise NotImplementedError

    @property
    def area(self) -> Real:
        """Return the area of the shape.

        Returns
        -------
        Real
            The area of the shape.

        """
        raise NotImplementedError
