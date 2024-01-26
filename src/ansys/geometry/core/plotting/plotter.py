# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
from ansys.visualizer import Colors, EdgePlot, MeshObjectPlot, Plotter
from beartype.typing import Any, Dict, List, Optional, Union
import numpy as np
import pyvista as pv
from pyvista.plotting.tools import create_axes_marker

from ansys.geometry.core.designer.body import Body, MasterBody
from ansys.geometry.core.designer.component import Component
from ansys.geometry.core.designer.design import Design
from ansys.geometry.core.designer.designpoint import DesignPoint
from ansys.geometry.core.logger import LOG as logger
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.plotting.widgets import ShowDesignPoints
from ansys.geometry.core.sketch import Sketch


class GeomPlotter(Plotter):
    def __init__(self, use_trame: bool | None = None, allow_picking: bool | None = False) -> None:
        super().__init__(use_trame, allow_picking)
        self.add_widget(ShowDesignPoints(self))

    def add_frame(self, frame: Frame, plotting_options: Optional[Dict] = None) -> None:
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
        self._pl.scene.add_actor(axes)

    def add_plane(
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

        self._pl.scene.add_mesh(plane_mesh, **plotting_options)

    def add_sketch(
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
            self.add_plane(sketch._plane)

        # Show the sketch plane if required
        if show_frame:
            self.add_frame(sketch._plane)

        if "clipping_plane" in plotting_options:
            logger.warning("Clipping is not available in Sketch objects.")
            plotting_options.pop("clipping_plane")

        self.add_sketch_polydata(sketch.sketch_polydata_faces(), opacity=0.7, **plotting_options)
        self.add_sketch_polydata(sketch.sketch_polydata_edges(), **plotting_options)

    def add_body_edges(self, body_plot: MeshObjectPlot, **plotting_options: Optional[dict]) -> None:
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
        for edge in body_plot.custom_object.edges:
            line = pv.Line(edge.start_point, edge.end_point)
            edge_actor = self._pl.scene.add_mesh(
                line, line_width=10, color=Colors.EDGE_COLOR.value, **plotting_options
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
        self._pl.set_add_mesh_defaults(plotting_options)
        dataset = body.tessellate(merge=merge)
        if "clipping_plane" in plotting_options:
            dataset = self.clip(dataset, plotting_options.get("clipping_plane"))
            plotting_options.pop("clipping_plane", None)
        if isinstance(dataset, pv.MultiBlock):
            actor, _ = self._pl.scene.add_composite(dataset, **plotting_options)
        else:
            actor = self._pl.scene.add_mesh(dataset, **plotting_options)

        body_plot = MeshObjectPlot(custom_object=body, mesh=dataset, actor=actor)
        self.add_body_edges(body_plot)
        self._object_to_actors_map[actor] = body_plot

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

        if "clipping_plane" in plotting_options:
            dataset = self.clip(dataset, plotting_options["clipping_plane"])
            plotting_options.pop("clipping_plane", None)

        if isinstance(dataset, pv.MultiBlock):
            actor, _ = self._pl.scene.add_composite(dataset, **plotting_options)
        else:
            actor = self._pl.scene.add_mesh(dataset, **plotting_options)

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
        mb = pv.MultiBlock()
        for polydata in polydata_entries:
            mb.append(polydata)

        if "clipping_plane" in plotting_options:
            mb = self.clip(mb, plane=plotting_options["clipping_plane"])
            plotting_options.pop("clipping_plane", None)

        self._pl.scene.add_mesh(mb, color=Colors.EDGE_COLOR.value, **plotting_options)

    def add_design_point(self, design_point: DesignPoint, **plotting_options) -> None:
        """
        Add a DesignPoint object to the plotter.

        Parameters
        ----------
        design_point : DesignPoint
            DesignPoint to add.
        """
        # get the actor for the DesignPoint
        actor = self._pl.scene.add_mesh(design_point._to_polydata(), **plotting_options)

        # save the actor to the object/actor map
        design_point = MeshObjectPlot(actor=actor, object=design_point, add_body_edges=False)

        self._geom_object_actors_map[actor] = design_point

    # Override add_custom to add custom meshes
    def add_custom(self, object: Any, **plotting_options) -> None:
        """
        Add a custom mesh to the plotter.

        Parameters
        ----------
        object : Any
            Object to add.
        """
        # Check for custom parameters in plotting_options
        if "merge_bodies" in plotting_options:
            merge_bodies = plotting_options["merge_bodies"]
            plotting_options.pop("merge_bodies", None)
        else:
            merge_bodies = None

        if "merge_components" in plotting_options:
            merge_components = plotting_options["merge_components"]
            plotting_options.pop("merge_components", None)
        else:
            merge_components = None

        # Add the custom object to the plotter
        if isinstance(object, DesignPoint):
            self.add_design_point(object, **plotting_options)
        elif isinstance(object, Sketch):
            self.plot_sketch(object, **plotting_options)
        elif isinstance(object, Body) or isinstance(object, MasterBody):
            self.add_body(object, merge_bodies, **plotting_options)
        elif isinstance(object, Design) or isinstance(object, Component):
            self.add_component(object, merge_components, merge_bodies, **plotting_options)
        elif isinstance(object, List) and isinstance(object[0], pv.PolyData):
            self.add_sketch_polydata(object, **plotting_options)
        else:
            self.add(object, **plotting_options)
