"""Provides the ``Trapezoid`` class ."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np
from pint import Quantity
import pyvista as pv
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math import ZERO_POINT2D, Matrix33, Point2D
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Angle, Distance
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.segment import SketchSegment
from ansys.geometry.core.typing import Real


class Trapezoid(SketchFace):
    """
    Provides for modeling 2D trapezoids.

    Parameters
    ----------
    width : Union[Quantity, Distance, Real]
        Width of the trapezoid.
    height : Union[Quantity, Distance, Real]
        Height of the trapezoid.
    slant_angle : Union[Quantity, Angle, Real]
        Angle for trapezoid generation.
    nonsymmetrical_slant_angle : Union[Quantity, Angle, Real], default: None
        Asymmetrical slant angles on each side of the trapezoid.
        By default, the trapezoid is symmetrical.
    center: Point2D, default: ZERO_POINT2D
        Point representing the center of the trapezoid.
    angle : Union[Quantity, Angle, Real], default: 0
        Placement angle for orientation alignment.

    Notes
    -----
    If a nonsymmetrical slant angle is defined, the slant angle is
    applied to the left-most angle and the nonsymmetrical slant angle
    is applied to the right-most angle.
    """

    @check_input_types
    def __init__(
        self,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
        slant_angle: Union[Quantity, Angle, Real],
        nonsymmetrical_slant_angle: Optional[Union[Quantity, Angle, Real]] = None,
        center: Optional[Point2D] = ZERO_POINT2D,
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Initialize the trapezoid."""
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

        if isinstance(angle, (int, float)):
            angle = Angle(angle, DEFAULT_UNITS.ANGLE)
        angle = angle if isinstance(angle, Angle) else Angle(angle, angle.units)

        if isinstance(slant_angle, (int, float)):
            slant_angle = Angle(slant_angle, DEFAULT_UNITS.ANGLE)
        slant_angle = (
            slant_angle if isinstance(slant_angle, Angle) else Angle(slant_angle, slant_angle.units)
        )

        if nonsymmetrical_slant_angle == None:
            nonsymmetrical_slant_angle = slant_angle
        else:
            if isinstance(nonsymmetrical_slant_angle, (int, float)):
                nonsymmetrical_slant_angle = Angle(nonsymmetrical_slant_angle, DEFAULT_UNITS.ANGLE)
            nonsymmetrical_slant_angle = (
                nonsymmetrical_slant_angle
                if isinstance(nonsymmetrical_slant_angle, Angle)
                else Angle(nonsymmetrical_slant_angle, nonsymmetrical_slant_angle.units)
            )

        rotation = Matrix33(
            spatial_rotation.from_euler(
                "xyz", [0, 0, angle.value.m_as(UNITS.radian)], degrees=False
            ).as_matrix()
        )

        half_h = height_magnitude / 2
        half_w = width_magnitude / 2
        rotated_point_1 = rotation @ [center.x.m - half_w, center.y.m - half_h, 0]
        rotated_point_2 = rotation @ [center.x.m + half_w, center.y.m - half_h, 0]
        rotated_point_3 = rotation @ [
            center.x.m - half_w + height_magnitude / np.tan(slant_angle.value.m_as(UNITS.radian)),
            center.y.m + half_h,
            0,
        ]
        rotated_point_4 = rotation @ [
            center.x.m
            + half_w
            - height_magnitude / np.tan(nonsymmetrical_slant_angle.value.m_as(UNITS.radian)),
            center.y.m + half_h,
            0,
        ]

        self._point1 = Point2D([rotated_point_1[0], rotated_point_1[1]], center.unit)
        self._point2 = Point2D([rotated_point_2[0], rotated_point_2[1]], center.unit)
        self._point3 = Point2D([rotated_point_3[0], rotated_point_3[1]], center.unit)
        self._point4 = Point2D([rotated_point_4[0], rotated_point_4[1]], center.unit)

        # TODO: add plane to SketchSegment when available
        self._segment1 = SketchSegment(self._point1, self._point2)
        self._segment2 = SketchSegment(self._point2, self._point3)
        self._segment3 = SketchSegment(self._point3, self._point4)
        self._segment4 = SketchSegment(self._point4, self._point1)

        self._edges.append(self._segment1)
        self._edges.append(self._segment2)
        self._edges.append(self._segment3)
        self._edges.append(self._segment4)

    @property
    def center(self) -> Point2D:
        """Center of the trapezoid."""
        return self._center

    @property
    def width(self) -> Quantity:
        """Width of the trapezoid."""
        return self._width.value

    @property
    def height(self) -> Quantity:
        """Height of the trapezoid."""
        return self._height.value

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
        # TODO: Really, a rectangle???... This should be modified on PyVista... It doesn't make
        #       any sense that a trapezoid can be a rectangle...
        import numpy as np

        return pv.Rectangle(
            np.array(
                [
                    [
                        self._point1.x.m_as(DEFAULT_UNITS.LENGTH),
                        self._point1.y.m_as(DEFAULT_UNITS.LENGTH),
                        0,
                    ],
                    [
                        self._point2.x.m_as(DEFAULT_UNITS.LENGTH),
                        self._point2.y.m_as(DEFAULT_UNITS.LENGTH),
                        0,
                    ],
                    [
                        self._point3.x.m_as(DEFAULT_UNITS.LENGTH),
                        self._point3.y.m_as(DEFAULT_UNITS.LENGTH),
                        0,
                    ],
                    [
                        self._point4.x.m_as(DEFAULT_UNITS.LENGTH),
                        self._point4.y.m_as(DEFAULT_UNITS.LENGTH),
                        0,
                    ],
                ],
                dtype=np.float_,
            )
        )
