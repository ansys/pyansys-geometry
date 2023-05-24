"""Provides the ``SketchCircle`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math import Plane, Point2D, Point3D
from ansys.geometry.core.misc import DEFAULT_UNITS, Distance
from ansys.geometry.core.primitives import Circle
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.typing import Real


class SketchCircle(SketchFace, Circle):
    """
    Provides for modeling circles.

    Parameters
    ----------
    center: Point2D
        Point representing the center of the circle.
    radius : Union[Quantity, Distance, Real]
        Radius of the circle.
    plane : Plane, optional
        Plane containing the sketched circle, by default global XY Plane.
    """

    @check_input_types
    def __init__(
        self, center: Point2D, radius: Union[Quantity, Distance, Real], plane: Plane = Plane()
    ):
        """Initialize the circle."""
        # Call SketchFace init method
        SketchFace.__init__(self)

        # Store the 2D center of the circle
        self._center = center

        self._radius = radius if isinstance(radius, Distance) else Distance(radius)
        if self._radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

        # Call Circle init method
        self._init_primitive_circle_from_plane(plane, radius=radius)

    def _init_primitive_circle_from_plane(
        self, plane: Plane, radius: Optional[Union[Quantity, Distance]] = None
    ) -> None:
        """
        Initialize correctly the underlying primitive ``Circle`` class.

        Parameters
        ----------
        plane : Plane
            Plane containing the sketched circle.
        radius : Optional[Union[Quantity, Distance]], optional
            Radius of the circle (if any), by default None.
        """
        # Use the radius given (if any)
        radius = radius if radius else self.radius

        # Call Circle init method
        center_global = plane.origin + Point3D(
            self.center[0] * plane.direction_x + self.center[1] * plane.direction_y,
            unit=self.center.base_unit,
        )
        Circle.__init__(self, center_global, radius, plane.direction_x, plane.direction_z)

    @property
    def center(self) -> Point2D:
        """Center of the circle."""
        return self._center

    @property
    def perimeter(self) -> Quantity:
        """
        Perimeter of the circle.

        Notes
        -----
        This property resolves the dilemma between using the ``SkethFace.perimeter``
        property and the ``Circle.perimeter`` property.
        """
        return Circle.perimeter.fget(self)

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
        circle = pv.Circle(self.radius.m_as(DEFAULT_UNITS.LENGTH))
        return circle.translate(
            [
                self.center.x.m_as(DEFAULT_UNITS.LENGTH),
                self.center.y.m_as(DEFAULT_UNITS.LENGTH),
                0,
            ],
            inplace=True,
        )

    def plane_change(self, plane: Plane) -> None:
        """
        Redefine the plane containing the SketchCircle objects.

        Notes
        -----
        This implies that their 3D definition may suffer changes.

        Parameters
        ----------
        plane : Plane
            Desired new plane which will contain the sketched circle.
        """
        # Reinitialize the Circle definition for the given plane
        self._init_primitive_circle_from_plane(plane)
