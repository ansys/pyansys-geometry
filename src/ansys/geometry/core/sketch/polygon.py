"""Provides the ``polygon`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np
from pint import Quantity
import pyvista as pv
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math import Matrix33, Matrix44, Point2D
from ansys.geometry.core.misc import UNIT_ANGLE, UNIT_LENGTH, Angle, Distance
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.typing import Real


class Polygon(SketchFace):
    """Provides for modeling regular polygons.

    Parameters
    ----------
    center: Point2D
        2D pint representing the center of the circle.
    inner_radius : Union[Quantity, Distance]
        Inner radius (apothem) of the polygon.
    sides : int
        Number of sides of the polygon.
    angle : Union[Quantity, Angle, Real], default: 0
        Placement angle for orientation alignment.
    """

    @check_input_types
    def __init__(
        self,
        center: Point2D,
        inner_radius: Union[Quantity, Distance],
        sides: int,
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Initialize the polygon."""
        super().__init__()

        # Check the inputs
        self._center = center
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
            raise ValueError("The minimum number of sides to construct a polygon is 3.")
        self._n_sides = sides

    @property
    def center(self) -> Point2D:
        """Point that is the center of the polygon."""
        return self._center

    @property
    def inner_radius(self) -> Quantity:
        """Inner radius(apothem) of the polygon."""
        return self._inner_radius.value

    @property
    def n_sides(self) -> int:
        """Number of sides of the polygon."""
        return self._n_sides

    @property
    def angle(self) -> Angle:
        """Orientation angle of the polygon."""
        return self._angle_offset

    @property
    def length(self) -> Quantity:
        """Side length of the polygon."""
        return 2 * self.inner_radius * np.tan(np.pi / self.n_sides)

    @property
    def outer_radius(self) -> Quantity:
        """Outer radius of the polygon."""
        return self.inner_radius / np.cos(np.pi / self.n_sides)

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the polygon."""
        return self.n_sides * self.length

    @property
    def area(self) -> Quantity:
        """Area of the polygon."""
        return (self.inner_radius * self.perimeter) / 2

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
        # Compensate z orientation by -np.pi / 2 to match Geometry service polygon processing
        # TODO : are we sure that the specific vertex we are targeting is the one matching the
        #        previous compensation angle? We could be rotating a different vertex for some
        #        reason. Anyway, it's a regular polygon, everything will look the same.
        #
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
