"""``Polygon`` class module."""

from typing import List, Optional, Union

import numpy as np
from pint import Quantity

from ansys.geometry.core.math import Plane, Point3D
from ansys.geometry.core.misc import Angle, Distance, check_type
from ansys.geometry.core.misc.measurements import UNIT_ANGLE
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.typing import Real


class Polygon(BaseShape):
    """A class for modeling regular polygon.

    Parameters
    ----------
    plane : Plane
        A :class:`Plane` representing the planar surface where the shape is contained.
    center: Point
        A :class:`Point` representing the center of the circle.
    inner_radius : Union[Quantity, Distance]
        The inradius(apothem) of the polygon.
    sides : int
        Number of sides of the polygon.
    angle : Optional[Union[Quantity, Angle, Real]]
        The placement angle for orientation alignment.
    """

    def __init__(
        self,
        plane: Plane,
        center: Point3D,
        inner_radius: Union[Quantity, Distance],
        sides: int,
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Initializes the polygon shape."""
        # Call the BaseShape ctor.
        super().__init__(plane, is_closed=True)

        # Check the inputs
        check_type(center, Point3D)
        self._center = center
        if not self.plane.is_point_contained(center):
            raise ValueError("Center must be contained in the plane.")

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
        # TODO : raise warning if the number of sides greater than 64
        # it cannot be handled server side
        self._n_sides = sides

    @property
    def center(self) -> Point3D:
        """The center of the polygon.

        Returns
        -------
        Point
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
    def components(self) -> List["BaseShape"]:
        """Returns a list containing all components required to generate the shape.

        Returns
        -------
        List[BaseShape]
            A list of component geometries forming the shape.
        """
        return [self]

    def local_points(self) -> List[Point3D]:
        """Returns a list containing all the vertices of the polygon.

        Vertices are given in the local space.

        Returns
        -------
        list[Point]
            A list of vertices representing the shape.

        """
        angle_offset_radians = +self._angle_offset.value.m_as(UNIT_ANGLE)
        theta = np.linspace(
            0 + angle_offset_radians, 2 * np.pi + angle_offset_radians, self.n_sides + 1
        )
        center_from_plane_origin = Point3D(
            self.plane.global_to_local @ (self.center - self.plane.origin), self.center.unit
        )
        return [
            Point3D(
                [
                    center_from_plane_origin.x.to(self.outer_radius.units).m
                    + self.outer_radius.m * np.cos(ang),
                    center_from_plane_origin.y.to(self.outer_radius.units).m
                    + self.outer_radius.m * np.sin(ang),
                    center_from_plane_origin.z.to(self.outer_radius.units).m,
                ],
                unit=self.outer_radius.units,
            )
            for ang in theta
        ]

    def plot(
        self,
        show_points: Optional[bool] = True,
        plotting_options_points: Optional[dict] = None,
        plotting_options_lines: Optional[dict] = None,
    ) -> None:
        """Plot the shape with the desired number of points.

        Parameters
        ----------
        show_points : bool, Optional
            If ``True``, points belonging to the shape are rendered.
        plotting_options_points : dict, optional
            A dictionary containing parameters accepted by
            :class:`pyvista.Plotter.plot_mesh` for customizing the mesh
            rendering of the points.
        plotting_options_lines : dict, optional
            A dictionary containing parameters accepted by
            :class:`pyvista.Plotter.plot_mesh` for customizing the mesh
            rendering of the lines.

        Notes
        -----
        This method overrides the ``BaseShape.plot`` method, as regular polygons
        resolution is not controlled by the number of points when rendering
        those in the scene.

        """
        from ansys.geometry.core.plotting.plotter import Plotter

        pl = Plotter()
        pl.plot_shape(
            self,
            show_points=show_points,
            plotting_options_points=plotting_options_points,
            plotting_options_lines=plotting_options_lines,
        )
        pl.show(jupyter_backend="panel")
