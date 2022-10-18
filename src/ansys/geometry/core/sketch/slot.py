"""``Slot`` class module."""
from typing import Optional, Union

import numpy as np
from pint import Quantity
import pyvista as pv
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math import Matrix33, Point2D
from ansys.geometry.core.misc import UNIT_ANGLE, Angle, Distance, check_type
from ansys.geometry.core.sketch.arc import Arc
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.segment import Segment
from ansys.geometry.core.typing import Real


class Slot(SketchFace):
    """A class for modeling 2D slot shape.

    Parameters
    ----------
    center: Point2D
        A :class:`Point2D` representing the center of the slot.
    width : Union[Quantity, Distance, Real]
        The width of the slot main body.
    height : Union[Quantity, Distance, Real]
        The height of the slot.
    angle : Optional[Union[Quantity, Angle, Real]]
        The placement angle for orientation alignment.
    """

    def __init__(
        self,
        center: Point2D,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
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

        rotation = Matrix33(
            spatial_rotation.from_euler(
                "xyz", [0, 0, angle.value.m_as(UNIT_ANGLE)], degrees=False
            ).as_matrix()
        )

        half_h = height_magnitude / 2
        half_w = width_magnitude / 2
        corner_1 = rotation @ [-half_w, half_h, 0]
        corner_2 = rotation @ [-half_w, -half_h, 0]
        corner_3 = rotation @ [half_w, -half_h, 0]
        corner_4 = rotation @ [half_w, half_h, 0]
        arc_1_center = rotation @ [-half_w, 0, 0]
        arc_2_center = rotation @ [half_w, 0, 0]

        self._slot_corner_1 = Point2D(
            [center.x.m + corner_1[0], center.y.m + corner_1[1]], center.unit
        )
        self._slot_corner_2 = Point2D(
            [center.x.m + corner_2[0], center.y.m + corner_2[1]], center.unit
        )
        self._slot_corner_3 = Point2D(
            [center.x.m + corner_3[0], center.y.m + corner_3[1]], center.unit
        )
        self._slot_corner_4 = Point2D(
            [center.x.m + corner_4[0], center.y.m + corner_4[1]], center.unit
        )
        self._arc_1_center = Point2D(
            [center.x.m + arc_1_center[0], center.y.m + arc_1_center[1]],
            center.unit,
        )
        self._arc_2_center = Point2D(
            [center.x.m + arc_2_center[0], center.y.m + arc_2_center[1]],
            center.unit,
        )

        self._arc1 = Arc(self._arc_1_center, self._slot_corner_1, self._slot_corner_2)
        self._segment1 = Segment(self._slot_corner_2, self._slot_corner_3)
        self._arc2 = Arc(self._arc_2_center, self._slot_corner_3, self._slot_corner_4)
        self._segment2 = Segment(self._slot_corner_4, self._slot_corner_1)

        self._edges.append(self._arc1)
        self._edges.append(self._segment1)
        self._edges.append(self._arc2)
        self._edges.append(self._segment2)

    @property
    def center(self) -> Point2D:
        """The center of the slot.

        Returns
        -------
        Point2D
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
    def visualization_polydata(self) -> pv.PolyData:
        """
        Return the vtk polydata representation for PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            The vtk pyvista.Polydata configuration.
        """
        return pv.merge(
            [
                self._segment1.visualization_polydata,
                self._arc2.visualization_polydata,
                self._segment2.visualization_polydata,
                self._arc1.visualization_polydata,
            ]
        )
