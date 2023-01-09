"""``Provides the ``SketchCircle`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math import Plane, Point2D, Point3D
from ansys.geometry.core.misc import UNIT_LENGTH, Distance
from ansys.geometry.core.primitives import Circle
from ansys.geometry.core.sketch.face import SketchFace


class SketchCircle(SketchFace, Circle):
    """Provides for modeling circles.

    Parameters
    ----------
    center: Point2D
        Point representing the center of the circle.
    radius : Union[Quantity, Distance]
        Radius of the circle.
    """

    @check_input_types
    def __init__(
        self,
        center: Point2D,
        radius: Union[Quantity, Distance],
        plane: Plane = Plane(),  # Default XY-plane
    ):
        """Initialize the circle."""
        # Call SketchFace init method
        SketchFace.__init__(self)

        # Call Circle init method
        center_global = plane.origin + Point3D(
            center[0] * plane.direction_x + center[1] * plane.direction_y, unit=center.base_unit
        )
        Circle.__init__(self, center_global, radius, plane.direction_x, plane.direction_z)

        # Store the 2D center of the circle
        self._center = center

    @property
    def center(self) -> Point2D:
        """Center of the circle."""
        return self._center

    @property
    def diameter(self) -> Quantity:
        """Diameter of the circle."""
        return 2 * self.radius

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the circle."""
        return 2 * np.pi * self.radius

    @property
    def area(self) -> Quantity:
        """Area of the circle."""
        return np.pi * self.radius**2

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
        circle = pv.Circle(self.radius.m_as(UNIT_LENGTH))
        return circle.translate(
            [self.center.x.m_as(UNIT_LENGTH), self.center.y.m_as(UNIT_LENGTH), 0], inplace=True
        )

    def plane_change(self, plane: Plane) -> None:
        """
        Method for SketchCircle objects to redefine the plane
        containing them. This implies that their 3D definition may suffer
        changes.

        Parameters
        ----------
        plane : Plane
            Desired new plane which will contain the sketched circle.
        """
        # Reinitialize the Circle definition for the given plane
        center_global = plane.origin + Point3D(
            self._center[0] * plane.direction_x + self._center[1] * plane.direction_y,
            unit=self._center.base_unit,
        )
        Circle.__init__(self, center_global, self._radius, plane.direction_x, plane.direction_z)
