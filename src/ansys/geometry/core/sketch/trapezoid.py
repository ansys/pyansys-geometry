# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Provides for creating and managing a trapezoid."""

from beartype import beartype as check_input_types
import numpy as np
from pint import Quantity
import pyvista as pv
from scipy.spatial.transform import Rotation as SpatialRotation

from ansys.geometry.core.logger import LOG
from ansys.geometry.core.math.constants import ZERO_POINT2D
from ansys.geometry.core.math.matrix import Matrix33
from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Angle, Distance
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.segment import SketchSegment
from ansys.geometry.core.typing import Real


class Trapezoid(SketchFace):
    """Provides for modeling a 2D trapezoid.

    Parameters
    ----------
    base_width : ~pint.Quantity | Distance | Real
        Width of the lower base of the trapezoid.
    height : ~pint.Quantity | Distance | Real
        Height of the slot.
    base_angle : ~pint.Quantity | Distance | Real
        Angle for trapezoid generation. Represents the angle
        on the base of the trapezoid.
    base_asymmetric_angle : ~pint.Quantity | Angle | Real | None, default: None
        Asymmetrical angles on each side of the trapezoid.
        The default is ``None``, in which case the trapezoid is symmetrical. If
        provided, the trapezoid is asymmetrical and the right corner angle
        at the base of the trapezoid is set to the provided value.
    center: Point2D, default: ZERO_POINT2D
        Center point of the trapezoid.
    angle : ~pint.Quantity | Angle | Real, default: 0
        Placement angle for orientation alignment.

    Notes
    -----
    If an asymmetric base angle is defined, the base angle is
    applied to the left-most angle, and the asymmetric base angle
    is applied to the right-most angle.
    """

    @check_input_types
    def __init__(
        self,
        base_width: Quantity | Distance | Real,
        height: Quantity | Distance | Real,
        base_angle: Quantity | Angle | Real,
        base_asymmetric_angle: Quantity | Angle | Real | None = None,
        center: Point2D = ZERO_POINT2D,
        angle: Quantity | Angle | Real = 0,
    ):
        """Initialize the trapezoid."""
        super().__init__()

        # TODO: Remove this warning in the next major release (v0.8.0)
        # https://github.com/ansys/pyansys-geometry/issues/1359
        LOG.warning(
            "The signature of the Trapezoid class has changed starting on "
            "version 0.7.X. Please refer to the documentation for more information."
        )

        self._center = center
        self._base_width = (
            base_width if isinstance(base_width, Distance) else Distance(base_width, center.unit)
        )
        if self._base_width.value <= 0:
            raise ValueError("Base width must be a real positive value.")
        width_magnitude = self._base_width.value.m_as(center.unit)

        self._height = height if isinstance(height, Distance) else Distance(height, center.unit)
        if self._height.value <= 0:
            raise ValueError("Height must be a real positive value.")
        height_magnitude = self._height.value.m_as(center.unit)

        if isinstance(angle, (int, float)):
            angle = Angle(angle, DEFAULT_UNITS.ANGLE)
        angle = angle if isinstance(angle, Angle) else Angle(angle, angle.units)

        if isinstance(base_angle, (int, float)):
            base_angle = Angle(base_angle, DEFAULT_UNITS.ANGLE)
        base_angle = (
            base_angle if isinstance(base_angle, Angle) else Angle(base_angle, base_angle.units)
        )

        if base_asymmetric_angle is None:
            base_asymmetric_angle = base_angle
        else:
            if isinstance(base_asymmetric_angle, (int, float)):
                base_asymmetric_angle = Angle(base_asymmetric_angle, DEFAULT_UNITS.ANGLE)
            base_asymmetric_angle = (
                base_asymmetric_angle
                if isinstance(base_asymmetric_angle, Angle)
                else Angle(base_asymmetric_angle, base_asymmetric_angle.units)
            )

        # SANITY CHECK: Ensure that the angles are valid (i.e. between 0 and 180 degrees)
        for trapz_angle in [base_angle, base_asymmetric_angle]:
            if (
                trapz_angle.value.m_as(UNITS.radian) < 0
                or trapz_angle.value.m_as(UNITS.radian) > np.pi
            ):
                raise ValueError("The trapezoid angles must be between 0 and 180 degrees.")

        # Check that the sum of both angles is larger than 90 degrees
        base_offset_right = height_magnitude / np.tan(
            base_asymmetric_angle.value.m_as(UNITS.radian)
        )
        base_offset_left = height_magnitude / np.tan(base_angle.value.m_as(UNITS.radian))

        # SANITY CHECK: Ensure that the trapezoid is not degenerate
        if base_offset_right + base_offset_left >= width_magnitude:
            raise ValueError(
                "The trapezoid is degenerate. "
                "The provided angles, width and height do not form a valid trapezoid."
            )

        rotation = Matrix33(
            SpatialRotation.from_euler(
                "xyz", [0, 0, angle.value.m_as(UNITS.radian)], degrees=False
            ).as_matrix()
        )

        half_h = height_magnitude / 2
        half_w = width_magnitude / 2
        rotated_point_1 = rotation @ [center.x.m - half_w, center.y.m - half_h, 0]
        rotated_point_2 = rotation @ [center.x.m + half_w, center.y.m - half_h, 0]
        rotated_point_3 = rotation @ [
            center.x.m + half_w - base_offset_right,
            center.y.m + half_h,
            0,
        ]
        rotated_point_4 = rotation @ [
            center.x.m - half_w + base_offset_left,
            center.y.m + half_h,
            0,
        ]

        self._point1 = Point2D([rotated_point_1[0], rotated_point_1[1]], center.unit)
        self._point2 = Point2D([rotated_point_2[0], rotated_point_2[1]], center.unit)
        self._point3 = Point2D([rotated_point_3[0], rotated_point_3[1]], center.unit)
        self._point4 = Point2D([rotated_point_4[0], rotated_point_4[1]], center.unit)

        # TODO: add plane to SketchSegment when available
        # https://github.com/ansys/pyansys-geometry/issues/1319
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
    def base_width(self) -> Quantity:
        """Width of the trapezoid."""
        return self._base_width.value

    @property
    def height(self) -> Quantity:
        """Height of the trapezoid."""
        return self._height.value

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """VTK polydata representation for PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global Cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            VTK pyvista.Polydata configuration.
        """
        import numpy as np

        return pv.Quadrilateral(
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
                dtype=np.float64,
            )
        )
