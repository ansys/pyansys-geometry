"""``Box`` class module."""
from typing import Optional, Union

from pint import Quantity
import pyvista as pv
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math import Matrix33, Point2D
from ansys.geometry.core.misc import UNIT_ANGLE, UNIT_LENGTH, Angle, Distance, check_type
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.segment import Segment
from ansys.geometry.core.typing import Real


class Box(SketchFace):
    """A class for modeling quadrilaterals.

    Parameters
    ----------
    center: Point2D
        A :class:`Point2D` representing the center of the box.
    width : Union[Quantity, Distance, Real]
        The width of the box.
    height : Union[Quantity, Distance, Real]
        The height of the box.
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
        """Initializes the box shape."""
        super().__init__()

        check_type(center, Point2D)
        self._center = center

        check_type(width, (Quantity, Distance, int, float))
        check_type(height, (Quantity, Distance, int, float))

        if isinstance(angle, (int, float)):
            angle = Angle(angle, UNIT_ANGLE)
        angle = angle if isinstance(angle, Angle) else Angle(angle, angle.units)

        rotation = Matrix33(
            spatial_rotation.from_euler(
                "xyz", [0, 0, angle.value.m_as(UNIT_ANGLE)], degrees=False
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

        self._width_segment1 = Segment(self._corner_1, self._corner_2)
        self._height_segment1 = Segment(self._corner_2, self._corner_3)
        self._width_segment2 = Segment(self._corner_3, self._corner_4)
        self._height_segment2 = Segment(self._corner_4, self._corner_1)

        self._edges.append(self._width_segment1)
        self._edges.append(self._height_segment1)
        self._edges.append(self._width_segment2)
        self._edges.append(self._height_segment2)

    @property
    def center(self) -> Point2D:
        """The center of the box.

        Returns
        -------
        Point2D
            The center of the box.
        """
        return self._center

    @property
    def width(self) -> Quantity:
        """The width of the box.

        Returns
        -------
        Quantity
            The width of the box.
        """
        return self._width.value

    @property
    def height(self) -> Quantity:
        """The height of the box.

        Returns
        -------
        Quantity
            The height of the box.
        """
        return self._height.value

    @property
    def perimeter(self) -> Quantity:
        """Return the perimeter of the box.

        Returns
        -------
        Quantity
            The perimeter of the box.
        """
        return 2 * self.width + 2 * self.height

    @property
    def area(self) -> Quantity:
        """Return the area of the box.

        Returns
        -------
        Quantity
            The area of the box.
        """
        return self.width * self.height

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
        return pv.Rectangle(
            [
                [self._corner_1.x.m_as(UNIT_LENGTH), self._corner_1.y.m_as(UNIT_LENGTH), 0],
                [self._corner_2.x.m_as(UNIT_LENGTH), self._corner_2.y.m_as(UNIT_LENGTH), 0],
                [self._corner_3.x.m_as(UNIT_LENGTH), self._corner_3.y.m_as(UNIT_LENGTH), 0],
                [self._corner_4.x.m_as(UNIT_LENGTH), self._corner_4.y.m_as(UNIT_LENGTH), 0],
            ]
        )
