"""``Provides the ``Circle`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Union
import numpy as np
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import UNIT_LENGTH, Distance
from ansys.geometry.core.sketch.face import SketchFace


class Circle(SketchFace):
    """Provides for modeling circles.

    Parameters
    ----------
    center: Point2D
        2D point representing the center of the circle.
    radius : Union[Quantity, Distance]
        Radius of the circle.
    """

    @check_input_types
    def __init__(
        self,
        center: Point2D,
        radius: Union[Quantity, Distance],
    ):
        """Initialize the circle."""
        super().__init__()

        self._center = center
        self._radius = radius if isinstance(radius, Distance) else Distance(radius)
        if self._radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

    @property
    def center(self) -> Point2D:
        """Center of the circle."""
        return self._center

    @property
    def radius(self) -> Quantity:
        """Radius of the circle."""
        return self._radius.value

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
