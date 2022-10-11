"""``Slot`` class module."""
import math
from typing import List, Optional, Union

import numpy as np
from pint import Quantity, Unit
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math import Matrix33, Plane, Point3D, UnitVector3D
from ansys.geometry.core.misc import Angle, Distance, check_type
from ansys.geometry.core.misc.measurements import UNIT_ANGLE
from ansys.geometry.core.shapes.arc import Arc
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.shapes.line import Segment
from ansys.geometry.core.typing import Real


class Slot(BaseShape):
    """A class for modeling 2D slot shape.

    Parameters
    ----------
    plane : Plane
        A :class:`Plane` representing the planar surface where the shape is contained.
    center: Point3D
        A :class:`Point3D` representing the center of the slot.
    width : Union[Quantity, Distance, Real]
        The width of the slot main body.
    height : Union[Quantity, Distance, Real]
        The height of the slot.
    angle : Optional[Union[Quantity, Angle, Real]]
        The placement angle for orientation alignment.
    """

    def __init__(
        self,
        plane: Plane,
        center: Point3D,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Initializes the slot shape."""
        super().__init__(plane, is_closed=True)

        check_type(center, Point3D)
        self._center = center
        if not self.plane.is_point_contained(center):
            raise ValueError("Center must be contained in the plane.")

        check_type(width, (Quantity, Distance, int, float))
        check_type(height, (Quantity, Distance, int, float))
        check_type(angle, (Quantity, Angle, int, float))

        self._width = width if isinstance(width, Distance) else Distance(width, center.unit)
        if self._width.value <= 0:
            raise ValueError("Width must be a real positive value.")
        width_magnitude = self._width.value.m_as(center.unit)

        self._height = height if isinstance(height, Distance) else Distance(height, center.unit)
        if self._height.value <= 0:
            raise ValueError("Height must be a real positive value.")
        height_magnitude = self._height.value.m_as(center.unit)

        if height_magnitude > width_magnitude:
            raise ValueError("Width must be greater than height.")

        if isinstance(angle, (int, float)):
            angle = Angle(angle, UNIT_ANGLE)
        angle = angle if isinstance(angle, Angle) else Angle(angle, angle.units)

        rotation = Matrix33(
            spatial_rotation.from_euler(
                "xyz", [0, 0, angle.value.m_as(UNIT_ANGLE)], degrees=False
            ).as_matrix()
        )

        global_center = Point3D(
            (center - self.plane.origin) @ self.plane.local_to_global_rotation, center.base_unit
        )

        half_h = height_magnitude / 2
        half_w = (width_magnitude - height_magnitude) / 2
        offset_u = center.unit
        slot_corner_1 = self.__slot_ref_point(-half_w, half_h, global_center, offset_u, rotation)
        slot_corner_2 = self.__slot_ref_point(half_w, half_h, global_center, offset_u, rotation)
        slot_corner_3 = self.__slot_ref_point(half_w, -half_h, global_center, offset_u, rotation)
        slot_corner_4 = self.__slot_ref_point(-half_w, -half_h, global_center, offset_u, rotation)
        arc_1_center = self.__slot_ref_point(half_w, 0, global_center, offset_u, rotation)
        arc_2_center = self.__slot_ref_point(-half_w, 0, global_center, offset_u, rotation)

        self._arc1 = Arc(
            plane,
            arc_1_center,
            slot_corner_3,
            slot_corner_2,
            plane.direction_z,
        )
        self._arc2 = Arc(
            plane,
            arc_2_center,
            slot_corner_4,
            slot_corner_1,
            UnitVector3D([-plane.direction_z.x, -plane.direction_z.y, -plane.direction_z.z]),
        )
        self._segment1 = Segment(plane, slot_corner_1, slot_corner_2)
        self._segment2 = Segment(plane, slot_corner_3, slot_corner_4)

    @property
    def center(self) -> Point3D:
        """The center of the slot.

        Returns
        -------
        Point3D
            The center of the slot.
        """
        return self._center

    @property
    def width(self) -> Quantity:
        """The width of the slot.

        Returns
        -------
        Quantity
            The width of the slot.
        """
        return self._width.value

    @property
    def height(self) -> Quantity:
        """The height of the slot.

        Returns
        -------
        Quantity
            The height of the slot.
        """
        return self._height.value

    @property
    def perimeter(self) -> Quantity:
        """Return the perimeter of the slot.

        Returns
        -------
        Quantity
            The perimeter of the slot.
        """
        return np.pi * self._height.value + 2 * (self._width.value - self._height.value)

    @property
    def area(self) -> Quantity:
        """Return the area of the slot.

        Returns
        -------
        Quantity
            The area of the slot.
        """
        return (
            np.pi * (self._height.value / 2) ** 2
            + (self._width.value - self._height.value) * self._height.value
        )

    @property
    def components(self) -> List["BaseShape"]:
        """Returns a list containing all components required to generate the shape.

        Returns
        -------
        List[BaseShape]
            A list of component geometries forming the shape.
        """
        return [self._segment1, self._arc1, self._segment2, self._arc2]

    def local_points(self, num_points: Optional[int] = 100) -> List[Point3D]:
        """Returns a list containing all the points belonging to the shape.

        Points are given in the local space.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape. Minimum of 8 required.

        Returns
        -------
        List[Point3D]
            A list of points representing the shape.
        """
        if num_points < 10:
            num_points = 10

        points_per_segment = math.floor(self._width.value.m / self.perimeter.m * num_points)
        points_per_arc = math.floor((num_points - 2 * points_per_segment) / 2)

        segment_1_points = self._segment1.local_points(points_per_segment)
        segment_2_points = self._segment2.local_points(points_per_segment)
        arc_1_points = self._arc1.local_points(points_per_arc)
        arc_2_points = self._arc2.local_points(num_points - 2 * points_per_segment - points_per_arc)
        points = []
        points.extend(segment_2_points)
        points.extend(arc_1_points)
        points.extend(segment_1_points)
        points.extend(arc_2_points)
        return points

    def __slot_ref_point(
        self, x_offset: Real, y_offset: Real, reference: Point3D, unit: Unit, rotation: Matrix33
    ) -> Point3D:
        """Private method for creating the slot reference points from a given X/Y offset
        and its center.

        Parameters
        ----------
        x_offset : Real
            The X axis offset from the slot center.
        y_offset : Real
            The Y axis offset from the slot center.
        reference : Point3D
            The center of the slot.
        unit : Unit
            The units employed for defining the X/Y offsets.
        rotation : Matrix33
            The rotation matrix for the slot orientation.

        Returns
        -------
        Point3D
            The reference point requested of the slot (in the global coordinate system).
        """
        rotated_point = Point3D(rotation @ [x_offset, y_offset, 0], unit)
        transformed_point = Point3D(
            (self._plane.local_to_global_rotation @ (rotated_point + reference))
            + self._plane.origin,
            rotated_point.base_unit,
        )

        return transformed_point
