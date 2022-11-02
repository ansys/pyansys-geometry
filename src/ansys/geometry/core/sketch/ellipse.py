"""Provides the ``Ellipse`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np
from pint import Quantity
import pyvista as pv
from scipy.integrate import quad
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math import Matrix33, Matrix44, Point2D
from ansys.geometry.core.misc import UNIT_ANGLE, UNIT_LENGTH, Angle, Distance
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.typing import Real


class Ellipse(SketchFace):
    """Provides for modeling ellipses.

    Parameters
    ----------
    center: Point2D
        Point representing the center of the ellipse.
    semi_major_axis : Union[Quantity, Distance]
        Semi-major axis of the ellipse.
    semi_minor_axis : Union[Quantity, Distance]
        Semi-minor axis of the ellipse.
    angle : Union[Quantity, Angle, Real], default: 0
        Placement angle for orientation alignment.
    """

    @check_input_types
    def __init__(
        self,
        center: Point2D,
        semi_major_axis: Union[Quantity, Distance],
        semi_minor_axis: Union[Quantity, Distance],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Initialize the ellipse."""
        super().__init__()

        self._center = center
        self._semi_major_axis = (
            semi_major_axis if isinstance(semi_major_axis, Distance) else Distance(semi_major_axis)
        )
        self._semi_minor_axis = (
            semi_minor_axis if isinstance(semi_minor_axis, Distance) else Distance(semi_minor_axis)
        )

        if self._semi_major_axis.value.m_as(self._semi_major_axis.base_unit) <= 0:
            raise ValueError("Semi-major axis must be a real positive value.")
        if self._semi_minor_axis.value.m_as(self._semi_minor_axis.base_unit) <= 0:
            raise ValueError("Semi-minor axis must be a real positive value.")

        if isinstance(angle, (int, float)):
            angle = Angle(angle, UNIT_ANGLE)
        self._angle_offset = angle if isinstance(angle, Angle) else Angle(angle, angle.units)

        # Align both units if misaligned
        if self._semi_major_axis.unit != self._semi_minor_axis.unit:
            self._semi_minor_axis.unit = self._semi_major_axis.unit

        # Ensure that the semi-major axis is equal or larger than the minor one
        if self._semi_major_axis.value.m < self._semi_minor_axis.value.m:
            raise ValueError("Semi-major axis cannot be shorter than the semi-minor axis.")

    @property
    def center(self) -> Point2D:
        """Point that is the center of the ellipse."""
        return self._center

    @property
    def semi_major_axis(self) -> Quantity:
        """Semi-major axis of the ellipse."""
        return self._semi_major_axis.value

    @property
    def semi_minor_axis(self) -> Quantity:
        """Semi-minor axis of the ellipse."""
        return self._semi_minor_axis.value

    @property
    def angle(self) -> Angle:
        """Orientation angle of the ellipse."""
        return self._angle_offset

    @property
    def eccentricity(self) -> Real:
        """Eccentricity of the ellipse."""
        ecc = (
            self.semi_major_axis.m**2 - self.semi_minor_axis.m**2
        ) ** 0.5 / self.semi_major_axis.m
        if ecc == 1:
            raise ValueError("The curve defined is a parabola and not an ellipse.")
        elif ecc > 1:
            raise ValueError("The curve defined is an hyperbola and not an ellipse.")
        return ecc

    @property
    def linear_eccentricity(self) -> Quantity:
        """Linear eccentricity of the ellipse.

        Notes
        -----
        The linear eccentricity is the distance from the center to the focus.
        """
        return (self.semi_major_axis**2 - self.semi_minor_axis**2) ** 0.5

    @property
    def semi_latus_rectum(self) -> Quantity:
        """Return the semi-latus rectum of the ellipse."""
        return self.semi_minor_axis**2 / self.semi_major_axis

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the ellipse."""

        def integrand(theta, ecc):
            return np.sqrt(1 - (ecc * np.sin(theta)) ** 2)

        I, _ = quad(integrand, 0, np.pi / 2, args=(self.eccentricity,))
        return 4 * self.semi_major_axis * I

    @property
    def area(self) -> Quantity:
        """Area of the ellipse."""
        return np.pi * self.semi_major_axis * self.semi_minor_axis

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
        rotation = Matrix33(
            spatial_rotation.from_euler(
                "xyz", [0, 0, self._angle_offset.value.m_as(UNIT_ANGLE)], degrees=False
            ).as_matrix()
        )

        transformation_matrix = Matrix44(
            [
                [
                    rotation[0, 0],
                    rotation[0, 1],
                    rotation[0, 2],
                    self.center.x.m_as(UNIT_LENGTH),
                ],
                [
                    rotation[1, 0],
                    rotation[1, 1],
                    rotation[1, 2],
                    self.center.y.m_as(UNIT_LENGTH),
                ],
                [
                    rotation[2, 0],
                    rotation[2, 1],
                    rotation[2, 2],
                    0,
                ],
                [0, 0, 0, 1],
            ]
        )

        # TODO: Replace with core pyvista ellipse implementation when released
        points = np.zeros((100, 3))
        theta = np.linspace(0.0, 2.0 * np.pi, 100)
        points[:, 0] = self.semi_major_axis.m_as(UNIT_LENGTH) * np.cos(theta)
        points[:, 1] = self.semi_minor_axis.m_as(UNIT_LENGTH) * np.sin(theta)
        cells = np.array([np.append(np.array([100]), np.arange(100))])
        return pv.wrap(pv.PolyData(points, cells)).transform(transformation_matrix)
