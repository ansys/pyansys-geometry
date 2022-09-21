"""``BaseShape`` class module."""

from typing import List, Optional

from pint import Quantity

from ansys.geometry.core.math import Plane, Point
from ansys.geometry.core.misc import check_type
from ansys.geometry.core.typing import Real


class BaseShape:
    """Provides base class for modeling shapes.

    Parameters
    ----------
    plane : Plane
        A :class:`Plane` representing the planar surface where the shape is contained.
    is_closed: Optional[bool]
        A boolean variable to define whether the shape is open or closed.
        By default, ``False``.
    """

    def __init__(
        self,
        plane: Plane,
        is_closed: Optional[bool] = False,
    ):
        """Initializes the base shape."""

        check_type(plane, Plane)
        self._plane = plane
        self._is_closed = is_closed

    @property
    def plane(self) -> Plane:
        """The Plane in which the shape is contained."""
        return self._plane

    def points(self, num_points: Optional[int] = 100) -> List[Point]:
        """Returns a list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point]
            A list of points representing the shape.
        """
        try:
            local_points = self.local_points(num_points)
        except TypeError:
            local_points = self.local_points()

        return [(self.plane.origin + self.plane.local_to_global @ point) for point in local_points]

    @property
    def components(self) -> List["BaseShape"]:
        """Returns a list containing all simple geometries forming the shape.

        Returns
        -------
        List[BaseShape]
            A list of component geometries forming the shape.
        """
        raise NotImplementedError("Each shape must provide this definition.")

    @property
    def x_coordinates(self) -> List[Real]:
        """Return all the x coordinates for the points of the shape.

        Returns
        -------
        List[Real]
            A list containing the values for the x-coordinates of the shape.

        """
        return [point[0] for point in self._points]

    @property
    def y_coordinates(self) -> List[Real]:
        """Return all the y coordinates for the points of the shape.

        Returns
        -------
        List[Real]
            A list containing the values for the y-coordinates of the shape.

        """
        return [point[1] for point in self._points]

    @property
    def z_coordinates(self) -> List[Real]:
        """Return all the y coordinates for the points of the shape.

        Returns
        -------
        List[Real]
            A list containing the values for the z-coordinates of the shape.

        """
        return [point[2] for point in self._points]

    @property
    def perimeter(self) -> Quantity:
        """Return the perimeter of the shape.

        Returns
        -------
        Quantity
            The perimeter of the shape.

        """
        if self.is_open:
            raise AttributeError("No perimeter can be computed for open BaseShape objects.")
        else:
            raise NotImplementedError

    @property
    def area(self) -> Quantity:
        """Return the area of the shape.

        Returns
        -------
        Quantity
            The area of the shape.

        """
        if self.is_open:
            raise AttributeError("No area can be computed for open BaseShape objects.")
        else:
            raise NotImplementedError

    @property
    def is_closed(self) -> bool:
        """Assert whether the shape is closed or not.

        Returns
        -------
        bool
            ``True`` if the shape is closed, ``False`` otherwise.

        """
        raise self._is_closed

    @property
    def is_open(self) -> bool:
        """Assert whether the shape is open or not.

        Returns
        -------
        bool
            ``True`` if the shape is open, ``False`` otherwise.

        """
        return not self.is_closed

    def plot(
        self,
        show_points: Optional[bool] = True,
        plotting_options_points: Optional[dict] = None,
        plotting_options_lines: Optional[dict] = None,
        num_points: Optional[int] = 100,
    ) -> None:
        """Plot the shape with the desired number of points.

        Parameters
        ----------
        num_points : int, optional
            Desired number of points to be used for rendering the shape.
        show_points : bool, optional
            If ``True``, points belonging to the shape are rendered.
        plotting_options_points : dict, optional
            A dictionary containing parameters accepted by
            :class:`pyvista.Plotter.plot_mesh` for customizing the mesh
            rendering of the points.
        plotting_options_lines : dict, optional
            A dictionary containing parameters accepted by
            :class:`pyvista.Plotter.plot_mesh` for customizing the mesh
            rendering of the lines.

        """
        from ansys.geometry.core.plotting.plotter import Plotter

        pl = Plotter(num_points=num_points)
        pl.plot_shape(
            self,
            show_points=show_points,
            plotting_options_points=plotting_options_points,
            plotting_options_lines=plotting_options_lines,
        )
        pl.show(jupyter_backend="panel")
