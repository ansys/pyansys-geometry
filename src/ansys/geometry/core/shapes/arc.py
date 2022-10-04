"""``ArcSketch`` class module."""

from typing import List, Optional

import numpy as np
from pint import Quantity

from ansys.geometry.core.math import Plane, Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc import UNITS, check_type
from ansys.geometry.core.shapes.base import BaseShape


class Arc(BaseShape):
    """A class for modeling arcs."""

    def __init__(
        self,
        plane: Plane,
        center: Point3D,
        start: Point3D,
        end: Point3D,
        axis: Optional[UnitVector3D] = None,
    ):
        """Initializes the arc shape.

        Parameters
        ----------
        plane : Plane
            A :class:`Plane` representing the planar surface where the shape is contained.
        center : Point
            A :class:`Point` representing the center of the arc.
        start: Point
            A :class:`Point` representing the start of the arc.
        end : Point
            A :class:`Point` representing the end of the arc.
        axis : Optional[UnitVector]
            A :class:`UnitVector` determining the rotation direction of the arc.
            It is expected to be orthogonal to the provided plane.
            +z for counter-clockwise rotation. -z for clockwise rotation.
            If not provided, the default will be counter-clockwise rotation.
        """
        super().__init__(plane, is_closed=False)
        # Verify points
        check_type(center, Point3D)
        check_type(start, Point3D)
        check_type(end, Point3D)
        if start == end:
            raise ValueError("Start and end points must be different.")
        if center == start:
            raise ValueError("Center and start points must be different.")
        if center == end:
            raise ValueError("Center and end points must be different.")
        if not self._plane.is_point_contained(center):
            raise ValueError("Center point must be contained in the plane.")
        if not self._plane.is_point_contained(start):
            raise ValueError("Arc start point must be contained in the plane.")
        if not self._plane.is_point_contained(end):
            raise ValueError("Arc end point must be contained in the plane.")

        if isinstance(axis, UnitVector3D):
            neg_direction_z = UnitVector3D(
                [-plane.direction_z.x, -plane.direction_z.y, -plane.direction_z.z]
            )
            if not (axis == self._plane.direction_z or axis == neg_direction_z):
                raise ValueError("Axis must be either the +z or -z of the provided plane.")
        else:
            axis = plane.direction_z

        self._center, self._start, self._end = center, start, end
        self._axis = axis

        to_start_vector = Vector3D.from_points(self._start, self._center)
        self._radius = to_start_vector.norm

        if not self._radius.m > 0:
            raise ValueError("Point configuration does not yield a positive length arc radius.")

        direction_x = UnitVector3D(to_start_vector.normalize())
        direction_y = UnitVector3D((axis % direction_x).normalize())
        to_end_vector = UnitVector3D.from_points(self._end, self._center)
        self._angle = np.arctan2(direction_y * to_end_vector, direction_x * to_end_vector)
        if self._angle < 0:
            self._angle = (2 * np.pi) + self._angle

    @property
    def start(self) -> Point3D:
        """Return the start of the arc line.

        Returns
        -------
        Point
            Starting point of the arc line.

        """
        return self._start

    @property
    def end(self) -> Point3D:
        """Return the end of the arc line.

        Returns
        -------
        Point
            Ending point of the arc line.

        """
        return self._end

    @property
    def radius(self) -> Quantity:
        """The radius of the arc.

        Returns
        -------
        Quantity
            The radius of the arc.

        """
        return self._radius

    @property
    def center(self) -> Point3D:
        """The center of the arc.

        Returns
        -------
        Point
            The center of the arc.

        """
        return self._center

    @property
    def axis(self) -> UnitVector3D:
        """The axis determining arc rotation.

        Returns
        -------
        UnitVector
            The axis determining arc rotation.

        """
        return self._axis

    @property
    def angle(self) -> Quantity:
        """The angle of the arc.

        Returns
        -------
        Quantity
            The angle of the arc.

        """

        return Quantity(self._angle, UNITS.radian)

    @property
    def length(self) -> Quantity:
        """Return the length of the arc.

        Returns
        -------
        Quantity
            The length of the arc.

        """
        return 2 * np.pi * self.radius * (self.angle.m / (2 * np.pi))

    @property
    def sector_area(self) -> Quantity:
        """Return the area of the sector of the arc.

        Returns
        -------
        Quantity
            The area of the sector of the arc.

        """
        return self.radius**2 * self.angle.m / 2

    @property
    def components(self) -> List["BaseShape"]:
        """Returns a list containing all simple geometries forming the shape.

        Returns
        -------
        List[BaseShape]
            A list of component geometries forming the shape.
        """
        return [self]

    def local_points(self, num_points: Optional[int] = 100) -> List[Point3D]:
        """Returns al list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point]
            A list of points representing the shape.
        """
        use_counter_clockwise_rotation = True if self._axis == self._plane.direction_z else False
        start_vector = self.start - self.center
        local_start_vector = (self.plane.global_to_local @ start_vector).tolist()
        start_angle = np.arctan2(
            (Vector3D(local_start_vector).cross(Vector3D([1, 0, 0]))).norm,
            Vector3D(local_start_vector).dot(Vector3D([1, 0, 0])),
        )
        theta = np.linspace(start_angle, start_angle + self.angle.m, num_points)
        center_from_plane_origin = Point3D(
            self.plane.global_to_local @ (self.center - self.plane.origin), self.center.unit
        )

        if use_counter_clockwise_rotation:
            return [
                Point3D(
                    [
                        center_from_plane_origin.x.to(self.radius.units).m
                        - self.radius.m * np.cos(ang),
                        center_from_plane_origin.y.to(self.radius.units).m
                        - self.radius.m * np.sin(ang),
                        center_from_plane_origin.z.to(self.radius.units).m,
                    ],
                    unit=self.radius.units,
                )
                for ang in theta
            ]
        else:
            return [
                Point3D(
                    [
                        center_from_plane_origin.x.to(self.radius.units).m
                        + self.radius.m * np.cos(ang),
                        center_from_plane_origin.y.to(self.radius.units).m
                        + self.radius.m * np.sin(ang),
                        center_from_plane_origin.z.to(self.radius.units).m,
                    ],
                    unit=self.radius.units,
                )
                for ang in theta
            ]
