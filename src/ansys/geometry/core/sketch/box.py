"""Provides the ``Box`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
from pint import Quantity
import pyvista as pv
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math import Matrix33, Point2D
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Angle, Distance
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.segment import SketchSegment
from ansys.geometry.core.typing import Real


class Box(SketchFace):
    """
    Provides for modeling quadrilaterals.

    Parameters
    ----------
    center: Point2D
        2D point representing the center of the box.
    width : Union[Quantity, Distance, Real]
        Width of the box.
    height : Union[Quantity, Distance, Real]
        Height of the box.
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
        """Initialize the box."""
        super().__init__()

        self._center = center
        if isinstance(angle, (int, float)):
            angle = Angle(angle, DEFAULT_UNITS.ANGLE)
        angle = angle if isinstance(angle, Angle) else Angle(angle, angle.units)

        rotation = Matrix33(
            spatial_rotation.from_euler(
                "xyz", [0, 0, angle.value.m_as(UNITS.radian)], degrees=False
            ).as_matrix()
        )

        self._width = width if isinstance(width, Distance) else Distance(width, center.unit)
        if self._width.value <= 0:
            raise ValueError("Width must be a real positive value.")
        width_magnitude = self._width.value.m_as(center.unit)

        self._height = height if isinstance(height, Distance) else Distance(height, center.unit)
        if self._height.value <= 0:
            raise ValueError("Height must be a real positive value.")
        height_magnitude = self._height.value.m_as(center.unit)

        half_h = height_magnitude / 2
        half_w = width_magnitude / 2
        corner_1 = rotation @ [-half_w, half_h, 0]
        corner_2 = rotation @ [half_w, half_h, 0]
        corner_3 = rotation @ [half_w, -half_h, 0]
        corner_4 = rotation @ [-half_w, -half_h, 0]

        self._corner_1 = Point2D([center.x.m + corner_1[0], center.y.m + corner_1[1]], center.unit)
        self._corner_2 = Point2D([center.x.m + corner_2[0], center.y.m + corner_2[1]], center.unit)
        self._corner_3 = Point2D([center.x.m + corner_3[0], center.y.m + corner_3[1]], center.unit)
        self._corner_4 = Point2D([center.x.m + corner_4[0], center.y.m + corner_4[1]], center.unit)

        # TODO: add plane to SketchSegment when available
        self._width_segment1 = SketchSegment(self._corner_1, self._corner_2)
        self._height_segment1 = SketchSegment(self._corner_2, self._corner_3)
        self._width_segment2 = SketchSegment(self._corner_3, self._corner_4)
        self._height_segment2 = SketchSegment(self._corner_4, self._corner_1)

        self._edges.append(self._width_segment1)
        self._edges.append(self._height_segment1)
        self._edges.append(self._width_segment2)
        self._edges.append(self._height_segment2)

    @property
    def center(self) -> Point2D:
        """Point that is the center of the box."""
        return self._center

    @property
    def width(self) -> Quantity:
        """Width of the box."""
        return self._width.value

    @property
    def height(self) -> Quantity:
        """Height of the box."""
        return self._height.value

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the box."""
        return 2 * self.width + 2 * self.height

    @property
    def area(self) -> Quantity:
        """Area of the box."""
        return self.width * self.height

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """
        VTK polydata representation for PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            VTK pyvista.Polydata configuration.
        """
        import numpy as np

        return pv.Rectangle(
            np.array(
                [
                    [
                        self._corner_1.x.m_as(DEFAULT_UNITS.LENGTH),
                        self._corner_1.y.m_as(DEFAULT_UNITS.LENGTH),
                        0,
                    ],
                    [
                        self._corner_2.x.m_as(DEFAULT_UNITS.LENGTH),
                        self._corner_2.y.m_as(DEFAULT_UNITS.LENGTH),
                        0,
                    ],
                    [
                        self._corner_3.x.m_as(DEFAULT_UNITS.LENGTH),
                        self._corner_3.y.m_as(DEFAULT_UNITS.LENGTH),
                        0,
                    ],
                    [
                        self._corner_4.x.m_as(DEFAULT_UNITS.LENGTH),
                        self._corner_4.y.m_as(DEFAULT_UNITS.LENGTH),
                        0,
                    ],
                ],
                dtype=np.float_,
            )
        )
