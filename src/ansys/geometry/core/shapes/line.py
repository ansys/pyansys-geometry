"""``LineShape`` class module."""

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.shapes.base import BaseShape


class LineShape(BaseShape):
    """
    Provides Line representation within a sketch environment.

    Parameters
    ----------
    point_1: Point3D
        Start of the line segment.
    point_2: Point3D
        End of the line segment.
    """

    def __init__(self, point_1: Point3D, point_2: Point3D):
        """Initialize a line shape.

        Parameters
        ----------
        start_point : Point3D
            A ``Point3D`` representing the start point of the line segment.
        end_point : Point3D
            A ``Point3D`` representing the end point of the line segment.

        """
        # Verify both points are not the same
        if point_1 == point_2:
            raise ValueError("Start and end points must be different.")
        super().__init__(start_point, end_point - start_point, TODO)
        self._start_point, self._end_point = (start_point, end_point)

    @property
    def start_point(self) -> Point3D:
        """Return the start of the line segment.

        Returns
        -------
        Point3D
            Starting point of the line segment.

        """
        return self._start_point

    @property
    def end_point(self) -> Point3D:
        """Return the end of the line segment.

        Returns
        -------
        Point3D
            Ending point of the line segment.

        """
        return self._end_point

    @property
    def direction(self) -> UnitVector3D:
        """Return the fundamental direction of the line.

        Returns
        -------
        UnitVector3D
            The fundamental direction of the line.

        """
        return (self.end_point - self.start_point).normalize()

    def local_points(self, num_points=100) -> list[Point3D]:
        """Returns al list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        list[Point3D]
            A list of points representing the shape.

        """
        alpha = np.linspace(self.start_point, self.end_point, num_points)
        return self.start_point + alpha * self.direction
