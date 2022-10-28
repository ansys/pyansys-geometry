"""A module containing a class for plotting various PyGeometry objects."""
from beartype.typing import Dict, List, Optional
import numpy as np
import pyvista as pv
from pyvista.plotting.tools import create_axes_marker

from ansys.geometry.core.designer import Body, Component
from ansys.geometry.core.math import Frame, Plane
from ansys.geometry.core.sketch import Sketch


class Plotter:
    """A class devoted to plotting sketches and bodies."""

    def __init__(
        self,
        scene: Optional[pv.Plotter] = None,
        background_opts: Optional[Dict] = None,
        num_points: int = 100,
    ):
        """Initializes the plotter.

        Parameters
        ----------
        scene : ~pyvista.Plotter, default: ``None``
            A scene instance for rendering the desired objects.
        background_opts : dict, default: ``None``
            A dictionary containing the desired background and top colors.
        num_points : int, default: 100
            Desired number of points to be used for rendering the shapes. Default is 100.

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

        # Save the desired number of points
        self._num_points = num_points

    @property
    def scene(self) -> pv.Plotter:
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

    def plot_frame(self, frame: Frame, plotting_options: Optional[Dict] = None) -> None:
        """Plot desired frame into the scene.

        Parameters
        ----------
        frame : Frame
            The ``Frame`` instance to be rendered in the scene.
        plotting_options : dict, optional`
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
        """Plot desired plane into the scene.

        Parameters
        ----------
        plane : Plane
            The ``Plane`` instance to be rendered in the scene.
        plane_options : dict, default: ``None``
            A dictionary containing parameters accepted by
            :class:`pyvista.Plane` for customizing the mesh representing the
            plane.
        plotting_options : dict, default: ``None``
            A dictionary containing parameters accepted by
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
        """Plot desired sketch into the scene.

        Parameters
        ----------
        sketch : Sketch
            The ``Sketch`` instance to be rendered in the scene.
        show_plane : bool
            If ``True``, it renders the sketch plane in the scene.
        show_frame : bool
            If ``Frame``, it renders the sketch plane in the scene.
        **kwargs : dict, default: ``None``
            Optional keyword arguments. See :func:`pyvista.Plotter.add_mesh`
            for allowable keyword arguments.
        """
        # Show the sketch plane if required
        if show_plane:
            self.plot_plane(sketch._plane)

        # Show the sketch plane if required
        if show_frame:
            self.plot_frame(sketch._plane)

        self.add_polydata(sketch.sketch_polydata(), **kwargs)

    def add_body(self, body: Body, merge: Optional[bool] = False, **kwargs: Optional[dict]) -> None:
        """Add a body to the scene.

        Parameters
        ----------
        body : ansys.geometry.core.designer.Body
            Body to add to the scene.
        merge : bool, default: False
            Merge the body into a single mesh. Enable this if you wish to
            merge wish to have the individual faces of the tessellation. This
            preserves the number of triangles and only merges the topology.
        **kwargs : dict, default: ``None``
            Optional keyword arguments. See :func:`pyvista.Plotter.add_mesh`
            for allowable keyword arguments.
        """
        kwargs.setdefault("smooth_shading", True)
        self.scene.add_mesh(body.tessellate(merge=merge), **kwargs)

    def add_component(
        self,
        component: Component,
        merge_component: bool = False,
        merge_bodies: bool = False,
        **kwargs
    ) -> None:
        """Add a component to the scene.

        Parameters
        ----------
        component : ansys.geometry.core.designer.Component
            Component to add to the scene.
        merge_component : bool, default: False
            Merge this component into a single dataset. This effectively
            combines all the individual bodies into a single dataset without
            any hierarchy.
        merge_bodies : bool, default: False
            Merge each body into a single dataset. This effectively combines
            all the faces of each individual body into a single dataset
            without.
        **kwargs : dict, default: ``None``
            Optional keyword arguments. See :func:`pyvista.Plotter.add_mesh`
            for allowable keyword arguments.
        """
        dataset = component.tessellate(merge_component=merge_component, merge_bodies=merge_bodies)
        kwargs.setdefault("smooth_shading", True)
        self.scene.add_mesh(dataset, **kwargs)

    def add_polydata(self, polydata_entries: List[pv.PolyData], **kwargs) -> None:
        """Add a sketches to the scene.

        Parameters
        ----------
        polydata : pyvista.PolyData
            pyvista PolyData to add to the scene.
        **kwargs : dict, default: ``None``
            Optional keyword arguments. See :func:`pyvista.Plotter.add_mesh`
            for allowable keyword arguments.
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
        """Display the rendered scene in the screen.

        Parameters
        ----------
        jupyter_backend : str, default: ``None``
            Desired ``pyvista`` jupyter backend.

        **kwargs : dict, default: ``None``
            Plotting keyword arguments. See :func:`pyvista.Plotter.show` for
            all available options.

        Notes
        -----
        Refer to https://docs.pyvista.org/user-guide/jupyter/index.html for more
        information about supported Jupyter backends.

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
            self.scene.add_mesh(plane, color="white", show_edges=True, opacity=0.1)

        # Conditionally set the jupyter backend as not all users will be within
        # a notebook environment to avoid a pyvista warning
        if self.scene.notebook and jupyter_backend is None:
            jupyter_backend = "panel"

        self.scene.show(jupyter_backend=jupyter_backend, **kwargs)
