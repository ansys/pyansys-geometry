"""Provides for plotting various PyGeometry objects."""
from beartype.typing import Dict, List, Optional
import numpy as np
import pyvista as pv
from pyvista.plotting.tools import create_axes_marker

from ansys.geometry.core.designer import Body, Component
from ansys.geometry.core.math import Frame, Plane
from ansys.geometry.core.sketch import Sketch


class Plotter:
    """Provides for plotting sketches and bodies."""

    def __init__(
        self,
        scene: Optional[pv.Plotter] = None,
        background_opts: Optional[Dict] = None,
        num_points: int = 100,
    ):
        """Initializes the plotter.

        Parameters
        ----------
        scene : ~pyvista.Plotter, default: None
            Scene instance for rendering the objects.
        background_opts : dict, default: None
            Dictionary containing the background and top colors.
        num_points : int, default: 100
            Number of points to use to render the shapes.

        """
        # Generate custom scene if ``None`` is provided
        if scene is None:
            scene = pv.Plotter()

        # If required, use a white background with no gradient
        if not background_opts:
            background_opts = dict(color="white")

        # Create the scene and assign the background
        self._scene = scene
        scene.set_background(**background_opts)
        view_box = scene.add_axes(line_width=5, box=True)

        # Save the desired number of points
        self._num_points = num_points

    @property
    def scene(self) -> pv.Plotter:
        """Rendered scene object.

        Returns
        -------
        ~pvyista.Plotter
            Rendered scene object.

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

    def plot_frame(self, frame: Frame, plotting_options: Optional[Dict] = None) -> None:
        """Plot a frame in the scene.

        Parameters
        ----------
        frame : Frame
            ``Frame`` instance to render in the scene.
        plotting_options : dict, default: None
            Dictionary containing parameters accepted by the
            :class:`pyvista.plotting.tools.create_axes_marker` class for customizing
            the frame rendering in the scene.

        """
        # Use default plotting options if required
        if plotting_options is None:
            plotting_options = dict(labels_off=True, cone_radius=0.2)

        # Create the axes actor
        axes = create_axes_marker(**plotting_options)

        # Transpose the matrix for fixing rotation sense in VTK
        arr = np.vstack((frame.global_to_local_rotation, frame.origin)).T
        arr = np.vstack((arr, [0, 0, 0, 1]))

        # Apply matrix transformation to the actor
        axes.SetUserMatrix(pv.vtkmatrix_from_array(arr))

        # Render the actor in the scene
        self.scene.add_actor(axes)

    def plot_plane(
        self,
        plane: Plane,
        plane_options: Optional[Dict] = None,
        plotting_options: Optional[Dict] = None,
    ) -> None:
        """Plot a plane in the scene.

        Parameters
        ----------
        plane : Plane
            ``Plane`` instance to render in the scene.
        plane_options : dict, default: None
            Dictionary containing parameters accepted by the
            :class:`pyvista.Plane` for customizing the mesh representing the
            plane.
        plotting_options : dict, default: None
            Dictionary containing parameters accepted by the
            :class:`pyvista.Plotter.plot_mesh` for customizing the mesh
            rendering of the plane.

        """
        # Impose default plane options if required
        if plane_options is None:
            plane_options = dict(i_size=10, j_size=10)

        # Create a plane for showing the plane
        plane_mesh = pv.Plane(
            center=plane.origin.tolist(), direction=plane.direction_z.tolist(), **plane_options
        )

        # Render the plane in the scene
        if not plotting_options:
            plotting_options = dict(color="blue", opacity=0.1)

        # Render the plane in the mesh with desired plotting options
        self.scene.add_mesh(plane_mesh, **plotting_options)

    def plot_sketch(
        self,
        sketch: Sketch,
        show_plane: bool = False,
        show_frame: bool = False,
        **kwargs: Optional[dict]
    ) -> None:
        """Plot a sketch in the scene.

        Parameters
        ----------
        sketch : Sketch
            ``Sketch`` instance to render in the scene.
        show_plane : bool, default: False
            Whether to render the sketch plane in the scene.
        show_frame : bool, default: False
            If ``Frame``, whether to render the sketch plane in the scene.
        **kwargs : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :func:`pyvista.Plotter.add_mesh` method.
        """
        # Show the sketch plane if required
        if show_plane:
            self.plot_plane(sketch._plane)

        # Show the sketch plane if required
        if show_frame:
            self.plot_frame(sketch._plane)

        self.add_polydata(sketch.sketch_polydata(), **kwargs)

    def add_body(self, body: Body, **kwargs: Optional[dict]) -> None:
        """Add a body to the scene.

        Parameters
        ----------
        body : ansys.geometry.core.designer.Body
            Body to add.
        **kwargs : dict, default: None
            Keyword arguments. For allowable keyword arguments,
            see the :func:`pyvista.Plotter.add_mesh` method.
        """
        kwargs.setdefault("smooth_shading", True)
        self.scene.add_mesh(body.tessellate(), **kwargs)

    def add_component(self, component: Component, merge: bool = False, **kwargs) -> None:
        """Add a component to the scene.

        Parameters
        ----------
        component : ansys.geometry.core.designer.Component
            Component to add.
        merge : bool, default: False
            Whether to merge the bodies and child components into a single dataset.
            If ``True``, all the ~pyvista.PolyData from each body and component are
            merged into a single dataset as a single ~pyvista.PolyData.
        **kwargs : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :func:`pyvista.Plotter.add_mesh` method.
        """
        dataset = component.tessellate(merge=merge)
        kwargs.setdefault("smooth_shading", True)
        self.add_polydata(dataset, **kwargs)

    def add_polydata(self, polydata_entries: List[pv.PolyData], **kwargs) -> None:
        """Add sketches to the scene from PyVista polydata.

        Parameters
        ----------
        polydata : pyvista.PolyData
            Polydata to add.
        **kwargs : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :func:`pyvista.Plotter.add_mesh` method.
        """
        for polydata in polydata_entries:
            self.scene.add_mesh(polydata, **kwargs)

    def show(
        self,
        show_axes_at_origin: bool = True,
        show_plane: bool = True,
        jupyter_backend: Optional[str] = None,
        **kwargs: Optional[dict]
    ) -> None:
        """Show the rendered scene on the screen.

        Parameters
        ----------
        jupyter_backend : str, default: None
            PyVista Jupyter backend.

        **kwargs : dict, default: None
            Plotting keyword arguments. For allowable keyword arguments, see the
            :func:`pyvista.Plotter.show` method.

        Notes
        -----
        For more information on supported Jupyter backends, see
        `Jupyter Notebook Plotting <https://docs.pyvista.org/user-guide/jupyter/index.html>`_
        in the PyVista documentation.

        """
        # computue the scaling
        bounds = self.scene.renderer.bounds
        x_length, y_length = bounds[1] - bounds[0], bounds[3] - bounds[2]
        sfac = max(x_length, y_length)

        # # Show origin axes without labels
        # if show_axes_at_origin:
        #     axes = create_axes_marker(labels_off=True)
        #     self.scene.add_actor(axes)

        # Create the fundamental XY plane
        if show_plane:
            # self.scene.bounds
            plane = pv.Plane(i_size=sfac * 1.3, j_size=sfac * 1.3)
            plane_actor = self.scene.add_mesh(plane, color="white", show_edges=True, opacity=0.1)
            plane_actor.pickable = False

        # Conditionally set the Jupyter backend as not all users will be within
        # a notebook environment to avoid a pyvista warning
        if self.scene.notebook and jupyter_backend is None:
            jupyter_backend = "panel"

        self.scene.enable_mesh_picking(left_clicking=True, style="surface", color="red")

        self.scene.show(jupyter_backend=jupyter_backend, **kwargs)
