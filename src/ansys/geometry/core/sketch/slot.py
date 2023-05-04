"""Provides the ``Slot`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np
from pint import Quantity
import pyvista as pv
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math import Matrix33, Point2D
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Angle, Distance
from ansys.geometry.core.sketch.arc import Arc
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.segment import SketchSegment
from ansys.geometry.core.typing import Real


class Slot(SketchFace):
    """
    Provides for modeling 2D slots.

    Parameters
    ----------
    center: :class:`Point2D <ansys.geometry.core.math.point.Point2D>`
        Point that represents the center of the slot.
    width : Union[Quantity, Distance, Real]
        Width of the slot main body.
    height : Union[Quantity, Distance, Real]
        Height of the slot.
    angle : Union[Quantity, Angle, Real], default: 0
        Placement angle for orientation alignment.
    """

    @check_input_types
    def __init__(
        self,
        center: Point2D,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Initialize the slot."""
        super().__init__()

        self._center = center
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
            angle = Angle(angle, DEFAULT_UNITS.ANGLE)
        angle = angle if isinstance(angle, Angle) else Angle(angle, angle.units)

        rotation = Matrix33(
            spatial_rotation.from_euler(
                "xyz", [0, 0, angle.value.m_as(UNITS.radian)], degrees=False
            ).as_matrix()
        )

        half_h = height_magnitude / 2
        half_box_w = (width_magnitude - height_magnitude) / 2
        corner_1 = rotation @ [-half_box_w, half_h, 0]
        corner_2 = rotation @ [-half_box_w, -half_h, 0]
        corner_3 = rotation @ [half_box_w, -half_h, 0]
        corner_4 = rotation @ [half_box_w, half_h, 0]
        arc_1_center = rotation @ [-half_box_w, 0, 0]
        arc_2_center = rotation @ [half_box_w, 0, 0]

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

        # TODO: add plane to SketchSegment when available
        self._arc1 = Arc(self._arc_1_center, self._slot_corner_1, self._slot_corner_2)
        self._segment1 = SketchSegment(self._slot_corner_2, self._slot_corner_3)
        self._arc2 = Arc(self._arc_2_center, self._slot_corner_3, self._slot_corner_4)
        self._segment2 = SketchSegment(self._slot_corner_4, self._slot_corner_1)

        self._edges.append(self._arc1)
        self._edges.append(self._segment1)
        self._edges.append(self._arc2)
        self._edges.append(self._segment2)

    @property
    def center(self) -> Point2D:
        """Center of the slot."""
        return self._center

    @property
    def width(self) -> Quantity:
        """Width of the slot."""
        return self._width.value

    @property
    def height(self) -> Quantity:
        """Height of the slot."""
        return self._height.value

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the slot."""
        return np.pi * self._height.value + 2 * (self._width.value - self._height.value)

    @property
    def area(self) -> Quantity:
        """Area of the slot."""
        return (
            np.pi * (self._height.value / 2) ** 2
            + (self._width.value - self._height.value) * self._height.value
        )

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """
        VTK polydata representation for PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global Cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            VTK pyvista.Polydata configuration.
        """
        return pv.merge(
            [
                self._segment1.visualization_polydata,
                self._arc2.visualization_polydata,
                self._segment2.visualization_polydata,
                self._arc1.visualization_polydata,
            ]
        )
