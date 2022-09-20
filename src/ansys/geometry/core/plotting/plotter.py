"""A module containing a class for plotting various PyGeometry objects."""
from typing import Optional

import numpy as np
import pyvista as pv
from pyvista import Plotter
from pyvista.plotting.tools import create_axes_marker

from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.shapes.base import BaseShape


class Plotter:
    """A class devoted to plotting sketches and bodies."""

    def __init__(
        self,
        scene: Optional[Plotter] = None,
        background_opts: Optional[dict] = None,
        num_points: Optional[int] = 100,
    ):
        """Initializes the plotter.

        Parameters
        ----------
        scene : ~pyvista.Plotter, optional
            A scene instance for rendering the desired objects.
        background_opts : dict, optional
            A dictionary containing the desired background and top colors.
        num_points : int, optional
            Desired number of points to be used when rendering shapes.

        """
        # Generate custom scene if none was provided
        if scene is None:
            scene = pv.Plotter()

        # If required, use a white background with no gradient
        if not background_opts:
            background_opts = dict(color="white")

        # Create the scene and assign the background
        self._scene = scene
        scene.set_background(**background_opts)
        view_box = scene.add_axes(line_width=5, box=True)

        # Show origin axes without labels
        axes = create_axes_marker(labels_off=True)
        scene.add_actor(axes)

        # Create the fundamental XY plane
        plane = pv.Plane(i_size=10, j_size=10)
        scene.add_mesh(plane, color="white", show_edges=True, opacity=0.1)

        # Save the desired number of points
        self._num_points = num_points

    @property
    def scene(self) -> Plotter:
        """Return the rendering scene object.

        Returns
        -------
        ~pvyista.Plotter
            The rendering scene object.

        """
        return self._scene

    def view_xy(self) -> None:
        """View the scene from the XY plane."""
        self.scene.view_xy()

    def view_xz(self) -> None:
        """View the scene from the XZ plane."""
        self.scene.view_xz()

    def view_yx(self) -> None:
        """View the scene from the YX plane."""
        self.scene.view_yx()

    def view_yz(self) -> None:
        """View the scene from the YZ plane."""
        self.scene.view_yz()

    def view_zx(self) -> None:
        """View the scene from the ZX plane."""
        self.scene.view_zx()

    def view_zy(self) -> None:
        """View the scene from the ZY plane."""
        self.scene.view_zy()

    def plot_frame(self, frame: Frame, plotting_options: Optional[dict] = None) -> None:
        """Plot desired frame into the scene.

        Parameters
        ----------
        frame : Frame
            The ``Frame`` instance to be rendered in the scene.
        plotting_options : dict, optional
            A dictionary containing parameters accepted by
            :class:`pyvista.plotting.tools.create_axes_marker` for customizing
            the frame rendering in the scene.

        """
        # Use default plotting options if required
        if plotting_options is None:
            plotting_options = dict(labels_off=True, cone_radius=0.2)

        # Create the axes actor
        axes = create_axes_marker(**plotting_options)

        # Transpose the matrix for fixing rotation sense in VTK
        arr = np.vstack((frame.global_to_local, frame.origin)).T
        arr = np.vstack((arr, [0, 0, 0, 1]))

        # Apply matrix transformation to the actor
        axes.SetUserMatrix(pv.vtkmatrix_from_array(arr))

        # Render the actor in the scene
        self.scene.add_actor(axes)

    def plot_plane(
        self,
        plane: Plane,
        plane_options: Optional[dict] = None,
        plotting_options: Optional[dict] = None,
    ) -> None:
        """Plot desired plane into the scene.

        Parameters
        ----------
        plane : Plane
            The ``Plane`` instance to be rendered in the scene.
        plane_options : dict, optional
            A dictionary containing parameters accepted by
            :class:`pyvista.Plane` for customizing the mesh representing the
            plane.
        plotting_options : dict, optional
            A dictionary containing parameters accepted by
            :class:`pyvista.Plotter.plot_mesh` for customizing the mesh
            rendering of the plane.

        """
        # Impose default plane options if required
        if plane_options is None:
            plane_options = dict(i_size=10, j_size=10)

        # Create a plane for showing the plane
        plane_mesh = pv.Plane(center=plane.origin, direction=plane.direction_z, **plane_options)

        # Render the plane in the scene
        if not plotting_options:
            plotting_options = dict(color="blue", opacity=0.1)

        # Render the plane in the mesh with desired plotting options
        self.scene.add_mesh(plane_mesh, **plotting_options)

    def plot_shape(
        self,
        shape: BaseShape,
        show_points: Optional[bool] = True,
        plotting_options_points: Optional[dict] = None,
        plotting_options_lines: Optional[dict] = None,
    ) -> None:
        """Plot desired shape into the scene.

        Parameters
        ----------
        shape : BaseShape
            The ``BaseShape`` instance to be rendered in the scene.
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

        """
        # Verify no user contradictions input when plotting points
        if show_points is False and plotting_options_points is not None:
            raise ValueError("Use 'show_points=True' for rendering shape points.")

        # Generate the points and the lines
        try:
            points = shape.points(self._num_points)
        # Avoid error if a polygon shape is passed
        except TypeError:
            points = shape.points()
        lines = np.hstack([[2, ith, ith + 1] for ith in range(0, len(points) - 1)])

        # Generate the mesh for the points and the lines
        if show_points:
            mesh_points = pv.PointSet(points)
        mesh_line = pv.PolyData(points, lines=lines)

        # Render points if required with desired rendering options
        if show_points:
            if plotting_options_points is None:
                plotting_options_points = dict(color="red")
            self.scene.add_mesh(mesh_points, **plotting_options_points)

        # Render lines in the scene with desired rendering options
        if plotting_options_lines is None:
            plotting_options_lines = dict(color="black", line_width=3)
        self.scene.add_mesh(mesh_line, **plotting_options_lines)

    def plot_sketch(self, sketch, show_plane=False, show_frame=False) -> None:
        """Plot desired sktch into the scene.

        Parameters
        ----------
        sketch : Sketch
            The ``Sketch`` instance to be rendered in the scene.
        show_plane : bool
            If ``True``, it renders the sketch plane in the scene.
        show_frame : bool
            If ``Frame``, it renders the sketch plane in the scene.

        """
        # Show the sketch plane if required
        if show_plane:
            self.plot_plane(sketch._plane)

        # Show the sketch plane if required
        if show_frame:
            self.plot_frame(sketch._plane)

        # Draw each one of the shapes in the sketch
        for shape in sketch.shapes_list:
            self.plot_shape(shape)

    def show(self, jupyter_backend: Optional[str] = None) -> None:
        """Display the rendered scene in the screen.

        Parameters
        ----------
        backend_jupyter : str, optional
            Desired ``pyvista`` jupyter backend.

        Notes
        -----
        Refer to https://docs.pyvista.org/user-guide/jupyter/index.html for more
        information about supported Jupyter backends.

        """
        self.scene.show(jupyter_backend=jupyter_backend)
