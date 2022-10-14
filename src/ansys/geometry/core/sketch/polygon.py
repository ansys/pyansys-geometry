"""``Polygon`` class module."""

from typing import Optional, Union

import numpy as np
from pint import Quantity
import pyvista as pv
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.math.matrix import Matrix33, Matrix44
from ansys.geometry.core.misc import Angle, Distance, check_type
from ansys.geometry.core.misc.measurements import UNIT_ANGLE, UNIT_LENGTH
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.typing import Real


class Polygon(SketchFace):
    """A class for modeling regular polygon.

    Parameters
    ----------
    center: Point2D
        A :class:`Point2D` representing the center of the circle.
    inner_radius : Union[Quantity, Distance]
        The inradius(apothem) of the polygon.
    sides : int
        Number of sides of the polygon.
    angle : Optional[Union[Quantity, Angle, Real]]
        The placement angle for orientation alignment.
    """

    def __init__(
        self,
        center: Point2D,
        inner_radius: Union[Quantity, Distance],
        sides: int,
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Initializes the polygon shape."""
        super().__init__()

        # Check the inputs
        check_type(center, Point2D)
        self._center = center

        check_type(inner_radius, (Quantity, Distance))
        self._inner_radius = (
            inner_radius if isinstance(inner_radius, Distance) else Distance(inner_radius)
        )
        if self._inner_radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

        if isinstance(angle, (int, float)):
            angle = Angle(angle, UNIT_ANGLE)
        self._angle_offset = angle if isinstance(angle, Angle) else Angle(angle, angle.units)

        # Verify that the number of sides is valid with preferred range
        if sides < 3:
            raise ValueError("The minimum number of sides to construct a polygon should be 3.")
        self._n_sides = sides

    @property
    def center(self) -> Point2D:
        """The center of the polygon.

        Returns
        -------
        Point2D
            The center of the polygon.
        """
        return self._center

    @property
    def inner_radius(self) -> Quantity:
        """The inradius(apothem) of the polygon.

        Returns
        -------
        Quantity
            The inradius(apothem) of the polygon.

        """
        return self._inner_radius.value

    @property
    def n_sides(self) -> int:
        """The number of sides of the polygon.

        Returns
        -------
        int
            The sides of the polygon.

        """
        return self._n_sides

    @property
    def length(self) -> Quantity:
        """The side length of the polygon.

        Returns
        -------
        Quantity
            The side length of the polygon.

        """
        return 2 * self.inner_radius * np.tan(np.pi / self.n_sides)

    @property
    def outer_radius(self) -> Quantity:
        """The outer radius of the polygon.

        Returns
        -------
        Quantity
            The outer radius of the polygon.

        """
        return self.inner_radius / np.cos(np.pi / self.n_sides)

    @property
    def perimeter(self) -> Quantity:
        """Return the perimeter of the polygon.

        Returns
        -------
        Quantity
            The perimeter of the polygon.

        """
        return self.n_sides * self.length

    @property
    def area(self) -> Quantity:
        """Return the area of the polygon.

        Returns
        -------
        Quantity
            The area of the polygon.

        """
        return (self.inner_radius * self.perimeter) / 2

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
        # Compensate z orientation by -np.pi / 2 to match geometry service polygon processing
        rotation = Matrix33(
            spatial_rotation.from_euler(
                "xyz", [0, 0, -np.pi / 2 + self._angle_offset.value.m_as(UNIT_ANGLE)], degrees=False
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

        return pv.Polygon(
            radius=self.inner_radius.m_as(UNIT_LENGTH),
            n_sides=self.n_sides,
        ).transform(transformation_matrix)
