# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Provides plotting for various PyAnsys Geometry objects."""
import re

from beartype.typing import Any, Dict, List, Optional
import numpy as np
import pyvista as pv
from pyvista.plotting.plotter import Plotter as PyVistaPlotter
from pyvista.plotting.tools import create_axes_marker

from ansys.geometry.core.designer.body import Body, MasterBody
from ansys.geometry.core.designer.component import Component
from ansys.geometry.core.designer.design import Design
from ansys.geometry.core.logger import LOG as logger
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.plotting.plotting_types import EdgePlot, GeomObjectPlot
from ansys.geometry.core.sketch.sketch import Sketch

DEFAULT_COLOR = "#D6F7D1"
"""Default color we use for the plotter actors."""

PICKED_COLOR = "#BB6EEE"
"""Color to use for the actors that are currently picked."""

EDGE_COLOR = "#000000"
"""Default color to use for the edges."""

PICKED_EDGE_COLOR = "#9C9C9C"
"""Color to use for the edges that are currently picked."""


class Plotter:
    """
    Provides for plotting sketches and bodies.

    Parameters
    ----------
    scene : ~pyvista.Plotter, default: None
        ``Scene`` instance for rendering the objects.
    color_opts : dict, default: None
        Dictionary containing the background and top colors.
    num_points : int, default: 100
        Number of points to use to render the shapes.
    enable_widgets: bool, default: True
        Whether to enable widget buttons in the plotter window.
        Widget buttons must be disabled when using
        `trame <https://kitware.github.io/trame/index.html>`_
        for visualization.
    """

    def __init__(
        self,
        scene: Optional[pv.Plotter] = None,
        color_opts: Optional[Dict] = None,
        num_points: int = 100,
        enable_widgets: bool = True,
    ) -> None:
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

        # geometry objects to actors mapping
        self._geom_object_actors_map = {}
        self._enable_widgets = enable_widgets

    @property
    def scene(self) -> PyVistaPlotter:
        """
        Rendered scene object.

        Returns
        -------
        ~pyvista.Plotter
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
            Frame to render in the scene.
        plotting_options : dict, default: None
            Dictionary containing parameters accepted by the
            :func:`pyvista.create_axes_marker` class for customizing
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
            Plane to render in the scene.
        plane_options : dict, default: None
            Dictionary containing parameters accepted by the
            :func:`pyvista.Plane  <pyvista.Plane>` function for customizing the mesh
            representing the plane.
        plotting_options : dict, default: None
            Dictionary containing parameters accepted by the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method for
            customizing the mesh rendering of the plane.
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
            Sketch to render in the scene.
        show_plane : bool, default: False
            Whether to render the sketch plane in the scene.
        show_frame : bool, default: False
            Whether to show the frame in the scene.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.
        """
        # Show the sketch plane if required
        if show_plane:
            self.plot_plane(sketch._plane)

        # Show the sketch plane if required
        if show_frame:
            self.plot_frame(sketch._plane)

        self.add_sketch_polydata(sketch.sketch_polydata_faces(), opacity=0.7, **plotting_options)
        self.add_sketch_polydata(sketch.sketch_polydata_edges(), **plotting_options)

    def add_body_edges(self, body_plot: GeomObjectPlot, **plotting_options: Optional[dict]) -> None:
        """
        Add the outer edges of a body to the plot.

        This method has the side effect of adding the edges to the GeomObject that
        you pass through the parameters.

        Parameters
        ----------
        body : GeomObjectPlot
            Body of which to add the edges.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.
        """
        edge_plot_list = []
        for edge in body_plot.object.edges:
            line = pv.Line(edge.start_point, edge.end_point)
            edge_actor = self.scene.add_mesh(
                line, line_width=10, color=EDGE_COLOR, **plotting_options
            )
            edge_actor.SetVisibility(False)
            edge_plot = EdgePlot(edge_actor, edge, body_plot)
            edge_plot_list.append(edge_plot)
        body_plot.edges = edge_plot_list

    def add_body(
        self, body: Body, merge: Optional[bool] = False, **plotting_options: Optional[Dict]
    ) -> None:
        """
        Add a body to the scene.

        Parameters
        ----------
        body : Body
            Body to add.
        merge : bool, default: False
            Whether to merge the body into a single mesh. When ``True``, the
            individual faces of the tessellation are merged. This
            preserves the number of triangles and only merges the topology.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments,
            see the :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.
        """
        # Use the default PyAnsys Geometry add_mesh arguments
        self.__set_add_mesh_defaults(plotting_options)
        dataset = body.tessellate(merge=merge)
        if isinstance(dataset, pv.MultiBlock):
            actor, _ = self.scene.add_composite(dataset, **plotting_options)
        else:
            actor = self.scene.add_mesh(dataset, **plotting_options)

        body_plot = GeomObjectPlot(actor=actor, object=body, add_body_edges=True)
        self.add_body_edges(body_plot)
        self._geom_object_actors_map[actor] = body_plot

    def add_component(
        self,
        component: Component,
        merge_component: bool = False,
        merge_bodies: bool = False,
        **plotting_options,
    ) -> str:
        """
        Add a component to the scene.

        Parameters
        ----------
        component : Component
            Component to add.
        merge_component : bool, default: False
            Whether to merge the component into a single dataset. When
            ``True``, all the individual bodies are effectively combined
            into a single dataset without any hierarchy.
        merge_bodies : bool, default: False
            Whether to merge each body into a single dataset. When ``True``,
            all the faces of each individual body are effectively combined
            into a single dataset without separating faces.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        Returns
        -------
        str
            Name of the added PyVista actor.
        """
        # Use the default PyAnsys Geometry add_mesh arguments
        self.__set_add_mesh_defaults(plotting_options)
        dataset = component.tessellate(merge_component=merge_component, merge_bodies=merge_bodies)
        if isinstance(dataset, pv.MultiBlock):
            actor, _ = self.scene.add_composite(dataset, **plotting_options)
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
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.
        """
        # Use the default PyAnsys Geometry add_mesh arguments
        for polydata in polydata_entries:
            self.scene.add_mesh(polydata, color=EDGE_COLOR, **plotting_options)

    def add(
        self,
        object: Any,
        merge_bodies: bool = False,
        merge_components: bool = False,
        filter: str = None,
        **plotting_options,
    ) -> Dict[pv.Actor, GeomObjectPlot]:
        """
        Add any type of object to the scene.

        These types of objects are supported: ``Body``, ``Component``, ``List[pv.PolyData]``,
        ``pv.MultiBlock``, and ``Sketch``.

        Parameters
        ----------
        plotting_list : List[Any]
            List of objects that you want to plot.
        merge_bodies : bool, default: False
            Whether to merge each body into a single dataset. When ``True``,
            all the faces of each individual body are effectively combined
            into a single dataset without separating faces.
        merge_component : bool, default: False
            Whether to merge the component into a single dataset. When
            ``True``, all the individual bodies are effectively combined
            into a single dataset without any hierarchy.
        filter : str, default: None
            Regular expression with the desired name or names you want to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        Returns
        -------
        Dict[~pyvista.Actor, GeomObjectPlot]
            Mapping between the ~pyvista.Actor and the PyAnsys Geometry object.
        """
        logger.debug(f"Adding object type {type(object)} to the PyVista plotter")
        if filter:
            if hasattr(object, "name"):
                if not re.search(filter, object.name):
                    logger.debug(f"Name {object.name} not found in regex {filter}.")
                    return self._geom_object_actors_map

        # Check what kind of object we are dealing with
        if isinstance(object, List) and isinstance(object[0], pv.PolyData):
            self.add_sketch_polydata(object, **plotting_options)
        elif isinstance(object, pv.PolyData):
            self.scene.add_mesh(object, **plotting_options)
        elif isinstance(object, pv.MultiBlock):
            self.scene.add_composite(object, **plotting_options)
        elif isinstance(object, Sketch):
            self.plot_sketch(object, **plotting_options)
        elif isinstance(object, Body) or isinstance(object, MasterBody):
            self.add_body(object, merge_bodies, **plotting_options)
        elif isinstance(object, Design) or isinstance(object, Component):
            self.add_component(object, merge_components, merge_bodies, **plotting_options)
        else:
            logger.warning(f"Object type {type(object)} can not be plotted.")
        return self._geom_object_actors_map

    def add_list(
        self,
        plotting_list: List[Any],
        merge_bodies: bool = False,
        merge_components: bool = False,
        filter: str = None,
        **plotting_options,
    ) -> Dict[pv.Actor, GeomObjectPlot]:
        """
        Add a list of any type of object to the scene.

        These types of objects are supported: ``Body``, ``Component``, ``List[pv.PolyData]``,
        ``pv.MultiBlock``, and ``Sketch``.

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
            all the faces of each individual body are effectively combined
            into a single dataset without separating faces.
        filter : str, default: None
            Regular expression with the desired name or names you want to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        Returns
        -------
        Dict[~pyvista.Actor, GeomObjectPlot]
            Mapping between the ~pyvista.Actor and the PyAnsys Geometry objects.
        """
        for object in plotting_list:
            _ = self.add(object, merge_bodies, merge_components, filter, **plotting_options)
        return self._geom_object_actors_map

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
            :meth:`Plotter.show <pyvista.Plotter.show>` method.

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

        self.scene.show(jupyter_backend=jupyter_backend, **kwargs)

    def __set_add_mesh_defaults(self, plotting_options: Optional[Dict]) -> None:
        # If the following keys do not exist, set the default values
        #
        # This method should only be applied in 3D objects: bodies, components
        plotting_options.setdefault("smooth_shading", True)
        plotting_options.setdefault("color", DEFAULT_COLOR)
