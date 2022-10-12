"""``Trapezoid`` class module."""

from typing import Optional, Union

import numpy as np
from pint import Quantity
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math import Matrix33, Point2D
from ansys.geometry.core.math.constants import ZERO_POINT2D
from ansys.geometry.core.misc import Angle, Distance, check_type
from ansys.geometry.core.misc.measurements import UNIT_ANGLE
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.segment import SketchSegment
from ansys.geometry.core.typing import Real


class Trapezoid(SketchFace):
    """A class for modeling 2D trapezoid shape.

    Parameters
    ----------
    width : Union[Quantity, Distance, Real]
        The width of the slot main body.
    height : Union[Quantity, Distance, Real]
        The height of the slot.
    slant_angle : Union[Quantity, Angle, Real]
        The angle for trapezoid generation.
    nonsymmetrical_slant_angle : Optional[Union[Quantity, Angle, Real]]
        Enables asymmetrical slant angles on each side of the trapezoid.
        If not defined, the trapezoid will be symmetrical.
    center: Optional[Point2D]
        A :class:`Point2D` representing the center of the trapezoid.
        Defaults to (0, 0)
    angle : Optional[Union[Quantity, Angle, Real]]
        The placement angle for orientation alignment.
    """

    def __init__(
        self,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
        slant_angle: Union[Quantity, Angle, Real],
        nonsymmetrical_slant_angle: Optional[Union[Quantity, Angle, Real]] = None,
        center: Optional[Point2D] = ZERO_POINT2D,
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Initializes the slot shape."""
        super().__init__()

        check_type(center, Point2D)
        self._center = center

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

        if isinstance(slant_angle, (int, float)):
            slant_angle = Angle(slant_angle, UNIT_ANGLE)
        slant_angle = (
            slant_angle if isinstance(slant_angle, Angle) else Angle(slant_angle, slant_angle.units)
        )

        if nonsymmetrical_slant_angle == None:
            nonsymmetrical_slant_angle = Angle(np.pi - slant_angle.value.m, UNIT_ANGLE)
        else:
            if isinstance(nonsymmetrical_slant_angle, (int, float)):
                nonsymmetrical_slant_angle = Angle(nonsymmetrical_slant_angle, UNIT_ANGLE)
            nonsymmetrical_slant_angle = (
                nonsymmetrical_slant_angle
                if isinstance(nonsymmetrical_slant_angle, Angle)
                else Angle(nonsymmetrical_slant_angle, nonsymmetrical_slant_angle.units)
            )

        rotation = Matrix33(
            spatial_rotation.from_euler(
                "xyz", [0, 0, angle.value.m_as(UNIT_ANGLE)], degrees=False
            ).as_matrix()
        )

        half_h = height_magnitude / 2
        half_w = width_magnitude / 2

        rotated_point_1 = rotation @ [center.x.m - half_w, center.y.m - half_h, 0]
        rotated_point_2 = rotation @ [center.x.m + half_w, center.y.m - half_h, 0]
        rotated_point_3 = rotation @ [
            center.x.m - half_w + height_magnitude / np.tan(slant_angle.value.m_as(UNIT_ANGLE)),
            center.y.m + half_h,
            0,
        ]
        rotated_point_4 = rotation @ [
            center.x.m
            + half_w
            - height_magnitude / np.tan(nonsymmetrical_slant_angle.value.m_as(UNIT_ANGLE)),
            center.y.m + half_h,
            0,
        ]

        self._point1 = Point2D([rotated_point_1[0], rotated_point_1[1]], center.unit)
        self._point2 = Point2D([rotated_point_2[0], rotated_point_2[1]], center.unit)
        self._point3 = Point2D([rotated_point_3[0], rotated_point_3[1]], center.unit)
        self._point4 = Point2D([rotated_point_4[0], rotated_point_4[1]], center.unit)

        self._segment1 = SketchSegment(self._point1, self._point2)
        self._segment2 = SketchSegment(self._point2, self._point4)
        self._segment3 = SketchSegment(self._point4, self._point3)
        self._segment4 = SketchSegment(self._point3, self._point1)

        self._edges.append(self._segment1)
        self._edges.append(self._segment2)
        self._edges.append(self._segment3)
        self._edges.append(self._segment4)

    @property
    def center(self) -> Point2D:
        """The center of the trapezoid.

        Returns
        -------
        Point2D
            The center of the trapezoid.
        """
        return self._center

    @property
    def width(self) -> Quantity:
        """The width of the trapezoid.

        Returns
        -------
        Quantity
            The width of the trapezoid.
        """
        return self._width.value

    @property
    def height(self) -> Quantity:
        """The height of the trapezoid.

        Returns
        -------
        Quantity
            The height of the trapezoid.
        """
        return self._height.value
