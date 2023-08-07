"""Provides for plotting various PyGeometry objects."""
from typing import Any

from beartype.typing import Dict, List, Optional
import numpy as np
import pyvista as pv
from pyvista.plotting.tools import create_axes_marker

from ansys.geometry.core.designer import Body, Component, Design, MasterBody
from ansys.geometry.core.logger import LOG as logger
from ansys.geometry.core.math import Frame, Plane
from ansys.geometry.core.plotting.trame_gui import _HAS_TRAME, TrameVisualizer
from ansys.geometry.core.plotting.widgets import (
    CameraPanDirection,
    DisplacementArrow,
    PlotterWidget,
    Ruler,
    ViewButton,
    ViewDirection,
)
from ansys.geometry.core.sketch import Sketch


class Plotter:
    """
    Provides for plotting sketches and bodies.

    Parameters
    ----------
    scene : ~pyvista.Plotter, default: None
        Scene instance for rendering the objects.
    color_opts : dict, default: None
        Dictionary containing the background and top colors.
    num_points : int, default: 100
        Number of points to use to render the shapes.
    enable_widgets: bool, default: True
        Enables/disables widget buttons in the plotter window.
        They must be disabled for trame viewer.
    """

    def __init__(
        self,
        scene: Optional[pv.Plotter] = None,
        color_opts: Optional[Dict] = None,
        num_points: int = 100,
        enable_widgets: bool = True,
    ):
        """Initialize the plotter."""
        # Generate custom scene if ``None`` is provided
        if scene is None:
            scene = pv.Plotter()

        # If required, use a white background with no gradient
        if not color_opts:
            color_opts = dict(color="white")

        # Create the scene
        self._scene = scene
        # Scene: assign the background
        self._scene.set_background(**color_opts)
        view_box = self._scene.add_axes(line_width=5, color="black")

        # Save the desired number of points
        self._num_points = num_points

        # Create Plotter widgets
        if enable_widgets:
            self._widgets: List[PlotterWidget] = []
            self._widgets.append(Ruler(self._scene))
            [
                self._widgets.append(DisplacementArrow(self._scene, direction=dir))
                for dir in CameraPanDirection
            ]
            [self._widgets.append(ViewButton(self._scene, direction=dir)) for dir in ViewDirection]

        # Dict where to save relation between generic object and pv.Actor
        self._actor_object_mapping = {}

    @property
    def scene(self) -> pv.Plotter:
        """
        Rendered scene object.

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
        """
        Plot a frame in the scene.

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
        """
        Plot a plane in the scene.

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
            :class:`pyvista.Plotter.add_mesh` for customizing the mesh
            rendering of the plane.
        """
        # Impose default plane options if none provided
        if plane_options is None:
            plane_options = dict(i_size=10, j_size=10)

        plane_mesh = pv.Plane(
            center=plane.origin.tolist(), direction=plane.direction_z.tolist(), **plane_options
        )

        # Impose default plotting options if none provided
        if plotting_options is None:
            plotting_options = dict(color="blue", opacity=0.1)

        self.scene.add_mesh(plane_mesh, **plotting_options)

    def plot_sketch(
        self,
        sketch: Sketch,
        show_plane: bool = False,
        show_frame: bool = False,
        **plotting_options: Optional[Dict],
    ) -> None:
        """
        Plot a sketch in the scene.

        Parameters
        ----------
        sketch : Sketch
            ``Sketch`` instance to render in the scene.
        show_plane : bool, default: False
            Whether to render the sketch plane in the scene.
        show_frame : bool, default: False
            If ``Frame``, whether to render the sketch plane in the scene.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :func:`pyvista.Plotter.add_mesh` method.
        """
        # Show the sketch plane if required
        if show_plane:
            self.plot_plane(sketch._plane)

        # Show the sketch plane if required
        if show_frame:
            self.plot_frame(sketch._plane)

        self.add_sketch_polydata(sketch.sketch_polydata(), **plotting_options)

    def add_body(
        self, body: Body, merge: Optional[bool] = False, **plotting_options: Optional[Dict]
    ) -> None:
        """
        Add a body to the scene.

        Parameters
        ----------
        body : ansys.geometry.core.designer.Body
            Body to add.
        merge : bool, default: False
            Whether to merge the body into a single mesh. If ``True``, the
            individual faces of the tessellation are merged. This
            preserves the number of triangles and only merges the topology.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments,
            see the :func:`pyvista.Plotter.add_mesh` method.

        Returns
        -------
        str:
            Name of the added PyVista Actor.
        """
        # Use the default PyGeometry add_mesh arguments
        self.__set_add_mesh_defaults(plotting_options)
        dataset = body.tessellate(merge=merge)
        if isinstance(dataset, pv.MultiBlock):
            actor = self.scene.add_composite(dataset, **plotting_options)
        else:
            actor = self.scene.add_mesh(dataset, **plotting_options)
        if isinstance(actor, tuple):
            actor = actor[0]
        return actor.name

    def add_component(
        self,
        component: Component,
        merge_component: bool = False,
        merge_bodies: bool = False,
        **plotting_options,
    ) -> None:
        """
        Add a component to the scene.

        Parameters
        ----------
        component : ansys.geometry.core.designer.Component
            Component to add.
        merge_component : bool, default: False
            Whether to merge the component into a single dataset. When
            ``True``, all the individual bodies are effectively combined
            into a single dataset without any hierarchy.
        merge_bodies : bool, default: False
            Whether to merge each body into a single dataset. When ``True``,
            all the faces of each individual body are effectively combineed
            into a single dataset without.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :func:`pyvista.Plotter.add_mesh` method.

        Returns
        -------
        str:
            Name of the added PyVista Actor.
        """
        # Use the default PyGeometry add_mesh arguments
        self.__set_add_mesh_defaults(plotting_options)
        dataset = component.tessellate(merge_component=merge_component, merge_bodies=merge_bodies)
        if isinstance(dataset, pv.MultiBlock):
            actor = self.scene.add_composite(dataset, **plotting_options)
        else:
            actor = self.scene.add_mesh(dataset, **plotting_options)
        return actor.name

    def add_sketch_polydata(self, polydata_entries: List[pv.PolyData], **plotting_options) -> None:
        """
        Add sketches to the scene from PyVista polydata.

        Parameters
        ----------
        polydata : pyvista.PolyData
            Polydata to add.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :func:`pyvista.Plotter.add_mesh` method.

        Returns
        -------
        str:
            Name of the added PyVista Actor.
        """
        # Use the default PyGeometry add_mesh arguments
        for polydata in polydata_entries:
            actor = self.scene.add_mesh(polydata, **plotting_options)
            return actor.name

    def add(
        self,
        object: Any,
        merge_bodies: bool = False,
        merge_components: bool = False,
        **plotting_options,
    ):
        """
        Add any type of object to the scene.

        Add any type of object to the scene. Currently supports
        ``List[pv.PolyData]``, ``pv.MultiBlock``, ``Sketch``,
        ``Component`` and ``Body`` objects.

        Parameters
        ----------
        plotting_list : List[Any]
            List of objects you want to plot.
        merge_component : bool, default: False
            Whether to merge the component into a single dataset. When
            ``True``, all the individual bodies are effectively combined
            into a single dataset without any hierarchy.
        merge_bodies : bool, default: False
            Whether to merge each body into a single dataset. When ``True``,
            all the faces of each individual body are effectively combineed
            into a single dataset without.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :func:`pyvista.Plotter.add_mesh` method.

        Returns
        -------
        Mapping[str, str]:
            Mapping between the pv.Actor and the PyGeometry object.
        """
        logger.debug(f"Adding object type {type(object)} to the PyVista plotter")
        actor_name = None
        if isinstance(object, List) and isinstance(object[0], pv.PolyData):
            self.add_sketch_polydata(object, **plotting_options)
        elif isinstance(object, pv.PolyData):
            self.scene.add_mesh(object, **plotting_options)
        elif isinstance(object, pv.MultiBlock):
            self.scene.add_composite(object, **plotting_options)
        elif isinstance(object, Sketch):
            self.plot_sketch(object, **plotting_options)
        elif isinstance(object, Body) or isinstance(object, MasterBody):
            actor_name = self.add_body(object, merge_bodies, **plotting_options)
        elif isinstance(object, Design) or isinstance(object, Component):
            actor_name = self.add_component(
                object, merge_components, merge_bodies, **plotting_options
            )
        else:
            logger.warning(f"Object type {type(object)} can not be plotted.")

        if actor_name is not None:
            self._actor_object_mapping[actor_name] = object.name
        return self._actor_object_mapping

    def add_list(
        self,
        plotting_list: List[Any],
        merge_bodies: bool = False,
        merge_components: bool = False,
        **plotting_options,
    ):
        """
        Add a list of any type of object to the scene.

        Add a list of any type of object to the scene. Currently supports
        ``List[pv.PolyData]``, ``pv.MultiBlock``, ``Sketch``,
        ``Component`` and ``Body`` objects.

        Parameters
        ----------
        plotting_list : List[Any]
            List of objects you want to plot.
        merge_component : bool, default: False
            Whether to merge the component into a single dataset. When
            ``True``, all the individual bodies are effectively combined
            into a single dataset without any hierarchy.
        merge_bodies : bool, default: False
            Whether to merge each body into a single dataset. When ``True``,
            all the faces of each individual body are effectively combineed
            into a single dataset without.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :func:`pyvista.Plotter.add_mesh` method.

        Returns
        -------
        Mapping[str, str]:
            Dictionary with the mapping between pv.Actor and PyGeometry objects.
        """
        for object in plotting_list:
            self.add(object, merge_bodies, merge_components, **plotting_options)
        return self._actor_object_mapping

    def show(
        self,
        show_axes_at_origin: bool = True,
        show_plane: bool = True,
        jupyter_backend: Optional[str] = None,
        **kwargs: Optional[Dict],
    ) -> None:
        """
        Show the rendered scene on the screen.

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
            self.scene.add_mesh(plane, color="white", show_edges=True, opacity=0.1)

        # Conditionally set the Jupyter backend as not all users will be within
        # a notebook environment to avoid a pyvista warning
        if self.scene.notebook and jupyter_backend is None:
            jupyter_backend = "panel"

        # Enabling anti-aliasing by default on scene
        self.scene.enable_anti_aliasing("ssaa")

        # Update all buttons/widgets
        [widget.update() for widget in self._widgets]

        self.scene.show(jupyter_backend=jupyter_backend, **kwargs)

    def __set_add_mesh_defaults(self, plotting_options: Optional[Dict]) -> None:
        # If the following keys do not exist, set the default values
        #
        # This method should only be applied in 3D objects: bodies, components
        plotting_options.setdefault("smooth_shading", True)
        plotting_options.setdefault("color", "#D6F7D1")


class PlotterHelper:
    """
    This class simplifies the selection of Trame visualizer in plot() functions.

    Parameters
    ----------
    use_trame: bool, optional
        Enables/disables the usage of the trame web visualizer. Defaults to the
        global setting ``USE_TRAME``.
    """

    def __init__(
        self, use_trame: Optional[bool] = None, allow_picking: Optional[bool] = False
    ) -> None:
        """Initialize use_trame and saves current pv.OFF_SCREEN value."""
        # Check if the use of trame was requested
        if use_trame is None:
            import ansys.geometry.core as pygeom

            use_trame = pygeom.USE_TRAME

        self._use_trame = use_trame
        self._allow_picking = allow_picking
        self._pv_off_screen_original = bool(pv.OFF_SCREEN)
        self._actor_object_mapping = {}
        self._pl = None

    def init_plotter(self):
        """
        Initialize the plotter with or without trame visualizer.

        Returns
        -------
        Plotter
            PyGeometry plotter initialized.
        """
        if self._use_trame and _HAS_TRAME:
            # avoids GUI window popping up
            pv.OFF_SCREEN = True
            pl = Plotter(enable_widgets=False)
        elif self._use_trame and not _HAS_TRAME:
            warn_msg = (
                "'use_trame' is active but Trame dependencies are not installed."
                "Consider installing 'pyvista[trame]' to use this functionality."
            )
            logger.warning(warn_msg)
            pl = Plotter()
        else:
            pl = Plotter()

        if self._allow_picking:
            pl.scene.enable_mesh_picking(callback=self.picker_callback, use_actor=True)

        return pl

    def picker_callback(self, actor):
        """Define callback for the element picker."""
        pt = self._pl.scene.picked_point
        self._actor_object_mapping.keys
        if actor.name in self._actor_object_mapping:
            body_name = self._actor_object_mapping[actor.name]
            text = body_name
            self._pl.scene.add_point_labels(
                [pt],
                [text],
                always_visible=True,
                point_size=10,
                render_points_as_spheres=True,
                name="selection-label",
            )

    def plot(
        self,
        object: Any,
        screenshot: Optional[str] = None,
        merge_bodies: bool = False,
        merge_component: bool = False,
        view_2d: Dict = None,
        **plotting_options,
    ):
        """
        Plot and show any PyGeometry object.

        Currently supports ``List[pv.PolyData]``, ``pv.MultiBlock``, ``Sketch``,
        ``Component`` and ``Body`` objects.

        Parameters
        ----------
        object : any
            Any object or list of objects that you want to plot.
        screenshot : str, default: None
            Save a screenshot of the image being represented. The image is
            stored in the path provided as an argument.
        merge_component : bool, default: False
            Whether to merge the component into a single dataset. When
            ``True``, all the individual bodies are effectively combined
            into a single dataset without any hierarchy.
        merge_bodies : bool, default: False
            Whether to merge each body into a single dataset. When ``True``,
            all the faces of each individual body are effectively combineed
            into a single dataset without.
        view_2d : Dict, optional
            Dict with the plane and the viewup vectors of the 2d plane, by default None.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :func:`pyvista.Plotter.add_mesh` method.
        """
        self._pl = self.init_plotter()
        if isinstance(object, List) and not isinstance(object[0], pv.PolyData):
            logger.debug("Plotting objects in list...")
            self._actor_object_mapping = self._pl.add_list(
                object, merge_bodies, merge_component, **plotting_options
            )
        else:
            self._actor_object_mapping = self._pl.add(
                object, merge_bodies, merge_component, **plotting_options
            )

        if view_2d is not None:
            self._pl.scene.view_vector(
                vector=view_2d["vector"],
                viewup=view_2d["viewup"],
            )
        self.show_plotter(self._pl, screenshot)

    def show_plotter(self, plotter: Plotter, screenshot: Optional[str] = None):
        """
        Show the plotter or start the Trame service.

        Parameters
        ----------
        plotter : Plotter
            PyGeometry plotter with the meshes added.
        screenshot : str, default: None
            Save a screenshot of the image being represented. The image is
            stored in the path provided as an argument.
        """
        if self._use_trame and _HAS_TRAME:
            visualizer = TrameVisualizer()
            visualizer.set_scene(plotter)
            visualizer.show()
        else:
            plotter.show(screenshot=screenshot)
        pv.OFF_SCREEN = self._pv_off_screen_original
