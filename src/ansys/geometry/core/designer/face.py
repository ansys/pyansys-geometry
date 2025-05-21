# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
"""Module for managing a face."""

from enum import Enum, unique
from typing import TYPE_CHECKING

from beartype import beartype as check_input_types
import matplotlib.colors as mcolors
from pint import Quantity

from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
from ansys.api.geometry.v0.commands_pb2 import FaceOffsetRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.errors import GeometryRuntimeError, protect_grpc
from ansys.geometry.core.math.bbox import BoundingBox
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc.auxiliary import (
    DEFAULT_COLOR,
    convert_color_to_hex,
    convert_opacity_to_hex,
)
from ansys.geometry.core.misc.checks import (
    ensure_design_is_active,
    graphics_required,
    min_backend_version,
)
from ansys.geometry.core.misc.options import TessellationOptions
from ansys.geometry.core.shapes.box_uv import BoxUV
from ansys.geometry.core.shapes.curves.trimmed_curve import TrimmedCurve
from ansys.geometry.core.shapes.parameterization import Interval
from ansys.geometry.core.shapes.surfaces.trimmed_surface import (
    ReversedTrimmedSurface,
    TrimmedSurface,
)

if TYPE_CHECKING:  # pragma: no cover
    import pyvista as pv

    from ansys.geometry.core.designer.body import Body


@unique
class SurfaceType(Enum):
    """Provides values for the surface types supported."""

    SURFACETYPE_UNKNOWN = 0
    SURFACETYPE_PLANE = 1
    SURFACETYPE_CYLINDER = 2
    SURFACETYPE_CONE = 3
    SURFACETYPE_TORUS = 4
    SURFACETYPE_SPHERE = 5
    SURFACETYPE_NURBS = 6
    SURFACETYPE_PROCEDURAL = 7


@unique
class FaceLoopType(Enum):
    """Provides values for the face loop types supported."""

    INNER_LOOP = "INNER"
    OUTER_LOOP = "OUTER"


class FaceLoop:
    """Provides an internal class holding the face loops defined.

    Parameters
    ----------
    type : FaceLoopType
        Type of loop.
    length : Quantity
        Length of the loop.
    min_bbox : Point3D
        Minimum point of the bounding box containing the loop.
    max_bbox : Point3D
        Maximum point of the bounding box containing the loop.
    edges : list[Edge]
        Edges contained in the loop.

    Notes
    -----
    This class is to be used only when parsing server side results. It is not
    intended to be instantiated by a user.
    """

    def __init__(
        self,
        type: FaceLoopType,
        length: Quantity,
        min_bbox: Point3D,
        max_bbox: Point3D,
        edges: list[Edge],
    ):
        """Initialize ``FaceLoop`` class."""
        self._type = type
        self._length = length
        self._min_bbox = min_bbox
        self._max_bbox = max_bbox
        self._edges = edges

    @property
    def type(self) -> FaceLoopType:
        """Type of the loop."""
        return self._type

    @property
    def length(self) -> Quantity:
        """Length of the loop."""
        return self._length

    @property
    def min_bbox(self) -> Point3D:
        """Minimum point of the bounding box containing the loop."""
        return self._min_bbox

    @property
    def max_bbox(self) -> Point3D:
        """Maximum point of the bounding box containing the loop."""
        return self._max_bbox

    @property
    def edges(self) -> list[Edge]:
        """Edges contained in the loop."""
        return self._edges


class Face:
    """Represents a single face of a body within the design assembly.

    This class synchronizes to a design within a supporting Geometry service instance.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    surface_type : SurfaceType
        Type of surface that the face forms.
    body : Body
        Parent body that the face constructs.
    grpc_client : GrpcClient
        Active supporting Geometry service instance for design modeling.
    """

    def __init__(
        self,
        id: str,
        surface_type: SurfaceType,
        body: "Body",
        grpc_client: GrpcClient,
        is_reversed: bool = False,
    ):
        """Initialize the ``Face`` class."""
        self._id = id
        self._surface_type = surface_type
        self._body = body
        self._grpc_client = grpc_client
        self._commands_stub = CommandsStub(grpc_client.channel)
        self._is_reversed = is_reversed
        self._shape = None
        self._color = None

    @property
    def id(self) -> str:
        """Face ID."""
        return self._id

    @property
    def _grpc_id(self) -> EntityIdentifier:
        """Entity ID of this face on the server side."""
        return EntityIdentifier(id=self._id)

    @property
    def is_reversed(self) -> bool:
        """Flag indicating if the face is reversed."""
        return self._is_reversed

    @property
    def body(self) -> "Body":
        """Body that the face belongs to."""
        return self._body

    @property
    @ensure_design_is_active
    @min_backend_version(24, 2, 0)
    def shape(self) -> TrimmedSurface:
        """Underlying trimmed surface of the face.

        If the face is reversed, its shape is a ``ReversedTrimmedSurface`` type, which handles the
        direction of the normal vector to ensure it is always facing outward.
        """
        if self._shape is None:
            self._grpc_client.log.debug("Requesting face properties from server.")

            geometry = self._grpc_client.services.faces.get_surface(
                id=self.id, surface_type=self.surface_type
            ).get("surface")
            response = self._grpc_client.services.faces.get_box_uv(id=self.id).get("uv_box")
            u_comp, v_comp = response.get("u"), response.get("v")
            box_uv = BoxUV(Interval(*u_comp), Interval(*v_comp))

            self._shape = (
                ReversedTrimmedSurface(geometry, box_uv)
                if self.is_reversed
                else TrimmedSurface(geometry, box_uv)
            )
        return self._shape

    @property
    def surface_type(self) -> SurfaceType:
        """Surface type of the face."""
        return self._surface_type

    @property
    @ensure_design_is_active
    def area(self) -> Quantity:
        """Calculated area of the face."""
        self._grpc_client.log.debug("Requesting face area from server.")
        return self._grpc_client.services.faces.get_area(id=self.id).get("area")

    @property
    @ensure_design_is_active
    def edges(self) -> list[Edge]:
        """List of all edges of the face."""
        from ansys.geometry.core.designer.edge import CurveType

        self._grpc_client.log.debug("Requesting face edges from server.")
        response = self._grpc_client.services.faces.get_edges(id=self.id)
        return [
            Edge(
                edge.get("id"),
                CurveType(edge.get("curve_type")),
                self._body,
                self._grpc_client,
                edge.get("is_reversed"),
            )
            for edge in response.get("edges")
        ]

    @property
    @ensure_design_is_active
    def loops(self) -> list[FaceLoop]:
        """List of all loops of the face."""
        from ansys.geometry.core.designer.edge import CurveType

        self._grpc_client.log.debug("Requesting face loops from server.")
        response_loops = self._grpc_client.services.faces.get_edges(id=self.id).get("loops")
        loops = []
        for response_loop in response_loops:
            type = FaceLoopType(response_loop.get("type"))
            length = response_loop.get("length")
            min = response_loop.get("min_corner")
            max = response_loop.get("max_corner")
            edges = [
                Edge(
                    edge.get("id"),
                    CurveType(edge.get("curve_type")),
                    self._body,
                    self._grpc_client,
                    edge.get("is_reversed"),
                )
                for edge in response_loop.get("edges")
            ]
            loops.append(
                FaceLoop(type=type, length=length, min_bbox=min, max_bbox=max, edges=edges)
            )

        return loops

    @property
    @min_backend_version(25, 2, 0)
    def color(self) -> str:
        """Get the current color of the face."""
        if self._color is None and self.body.is_alive:
            # Assigning default value first
            self._color = DEFAULT_COLOR

            # If color is not cached, retrieve from the server
            response = self._grpc_client.services.faces.get_color(id=self.id)

            # Return if valid color returned
            if response.get("color"):
                self._color = mcolors.to_hex(response.get("color"), keep_alpha=True)
            else:
                self._color = DEFAULT_COLOR

        return self._color

    @property
    def opacity(self) -> float:
        """Get the opacity of the face."""
        opacity_hex = self._color[7:]
        return int(opacity_hex, 16) / 255 if opacity_hex else 1

    @color.setter
    def color(self, color: str | tuple[float, float, float]) -> None:
        self.set_color(color)

    @opacity.setter
    def opacity(self, opacity: float) -> None:
        self.set_opacity(opacity)

    @property
    @min_backend_version(25, 2, 0)
    def bounding_box(self) -> BoundingBox:
        """Get the bounding box for the face."""
        self._grpc_client.log.debug(f"Getting bounding box for {self.id}.")
        response = self._grpc_client.services.faces.get_bounding_box(id=self.id)
        return BoundingBox(
            response.get("min_corner"), response.get("max_corner"), response.get("center")
        )

    @check_input_types
    @min_backend_version(25, 2, 0)
    def set_color(self, color: str | tuple[float, float, float]) -> None:
        """Set the color of the face."""
        self._grpc_client.log.debug(f"Setting face color of {self.id} to {color}.")
        color = convert_color_to_hex(color)
        response = self._grpc_client.services.faces.set_color(id=self.id, color=color)
        if response.get("success"):
            self._color = color
        else:  # pragma: no cover
            raise GeometryRuntimeError(f"Failed to set color {color} for face {self.id}. ")

    @check_input_types
    @min_backend_version(25, 2, 0)
    def set_opacity(self, opacity: float) -> None:
        """Set the opacity of the face."""
        self._grpc_client.log.debug(f"Setting face color of {self.id} to {opacity}.")
        opacity = convert_opacity_to_hex(opacity)

        new_color = self._color[0:7] + opacity
        self.set_color(new_color)

    @ensure_design_is_active
    def normal(self, u: float = 0.5, v: float = 0.5) -> UnitVector3D:
        """Get the normal direction to the face at certain UV coordinates.

        Parameters
        ----------
        u : float, default: 0.5
            First coordinate of the 2D representation of a surface in UV space.
            The default is ``0.5``, which is the center of the surface.
        v : float, default: 0.5
            Second coordinate of the 2D representation of a surface in UV space.
            The default is ``0.5``, which is the center of the surface.

        Returns
        -------
        UnitVector3D
            :class:`UnitVector3D` object evaluated at the given U and V coordinates.
            This :class:`UnitVector3D` object is perpendicular to the surface at the
            given UV coordinates.

        Notes
        -----
        To properly use this method, you must handle UV coordinates. Thus, you must
        know how these relate to the underlying Geometry service. It is an advanced
        method for Geometry experts only.
        """
        try:
            return self.shape.normal(u, v)
        except GeometryRuntimeError:  # pragma: no cover
            # Only for versions earlier than 24.2.0 (before the introduction of the shape property)
            self._grpc_client.log.debug(f"Requesting face normal from server with (u,v)=({u},{v}).")
            return self._grpc_client.services.faces.get_normal(id=self.id, u=u, v=v).get("normal")

    @ensure_design_is_active
    def point(self, u: float = 0.5, v: float = 0.5) -> Point3D:
        """Get a point of the face evaluated at certain UV coordinates.

        Parameters
        ----------
        u : float, default: 0.5
            First coordinate of the 2D representation of a surface in UV space.
            The default is ``0.5``, which is the center of the surface.
        v : float, default: 0.5
            Second coordinate of the 2D representation of a surface in UV space.
            The default is ``0.5``, which is the center of the surface.

        Returns
        -------
        Point3D
            :class:`Point3D` object evaluated at the given UV coordinates.

        Notes
        -----
        To properly use this method, you must handle UV coordinates. Thus, you must
        know how these relate to the underlying Geometry service. It is an advanced
        method for Geometry experts only.
        """
        try:
            return self.shape.evaluate_proportion(u, v).position
        except GeometryRuntimeError:  # pragma: no cover
            # Only for versions earlier than 24.2.0 (before the introduction of the shape property)
            self._grpc_client.log.debug(f"Requesting face point from server with (u,v)=({u},{v}).")
            return self._grpc_client.services.faces.evaluate(id=self.id, u=u, v=v).get("point")

    @ensure_design_is_active
    def create_isoparametric_curves(
        self, use_u_param: bool, parameter: float
    ) -> list[TrimmedCurve]:
        """Create isoparametic curves at the given proportional parameter.

        Typically, only one curve is created, but if the face has a hole, it is possible that
        more than one curve is created.

        Parameters
        ----------
        use_u_param : bool
            Whether the parameter is the ``u`` coordinate or ``v`` coordinate. If ``True``,
            it is the ``u`` coordinate. If ``False``, it is the ``v`` coordinate.
        parameter : float
            Proportional [0-1] parameter to create the one or more curves at.

        Returns
        -------
        list[TrimmedCurve]
            list of curves that were created.
        """
        self._grpc_client.log.debug(
            f"Creating isoparametric curves on face {self.id} with parameter={parameter}"
            f" and use_u_param={use_u_param}."
        )
        response = self._grpc_client.services.faces.create_iso_parametric_curve(
            id=self.id, use_u_param=use_u_param, parameter=parameter
        )

        trimmed_curves = []
        for curve in response.get("curves"):
            trimmed_curves.append(
                TrimmedCurve(
                    curve.get("geometry"),
                    curve.get("start"),
                    curve.get("end"),
                    curve.get("interval"),
                    curve.get("length"),
                    self._grpc_client,
                )
            )

        return trimmed_curves

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def setup_offset_relationship(
        self, other_face: "Face", set_baselines: bool = False, process_adjacent_faces: bool = False
    ) -> bool:
        """Create an offset relationship between two faces.

        Parameters
        ----------
        other_face : Face
            The face to setup an offset relationship with.
        set_baselines : bool, default: False
            Automatically set baseline faces.
        process_adjacent_faces : bool, default: False
            Look for relationships of the same offset on adjacent faces.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        result = self._commands_stub.FaceOffset(
            FaceOffsetRequest(
                face1=self._grpc_id,
                face2=other_face._grpc_id,
                set_baselines=set_baselines,
                process_adjacent_faces=process_adjacent_faces,
            )
        )

        return result.success

    @graphics_required
    def tessellate(self, tess_options: TessellationOptions | None = None) -> "pv.PolyData":
        """Tessellate the face and return the geometry as triangles.

        Parameters
        ----------
        tess_options : TessellationOptions | None, default: None
            A set of options to determine the tessellation quality.

        Returns
        -------
        ~pyvista.PolyData
            :class:`pyvista.PolyData` object holding the face.

        Notes
        -----
        The tessellation options are ONLY used if the face has not been tessellated before.
        If the face has been tessellated before, the stored tessellation is returned.
        """
        # If tessellation has not been called before... call it
        if self._body._template._tessellation is None:
            self._body.tessellate(tess_options=tess_options)

        # Search the tessellation of the face - if it exists
        # ---> We need to used the last element of the ID since we are looking inside
        # ---> the master body tessellation.
        red_id = self.id.split("/")[-1]
        mb_pdata = self.body._template._tessellation.get(red_id)
        if mb_pdata is None:  # pragma: no cover
            raise ValueError(f"Face {self.id} not found in the tessellation.")

        # Return the stored PolyData
        return mb_pdata.transform(self.body.parent_component.get_world_transform(), inplace=False)

    @graphics_required
    def plot(
        self,
        screenshot: str | None = None,
        use_trame: bool | None = None,
        use_service_colors: bool | None = None,
        **plotting_options: dict | None,
    ) -> None:
        """Plot the face.

        Parameters
        ----------
        screenshot : str, default: None
            Path for saving a screenshot of the image that is being represented.
        use_trame : bool, default: None
            Whether to enable the use of `trame <https://kitware.github.io/trame/index.html>`_.
            The default is ``None``, in which case the
            ``ansys.tools.visualization_interface.USE_TRAME`` global setting is used.
        use_service_colors : bool, default: None
            Whether to use the colors assigned to the face in the service. The default
            is ``None``, in which case the ``ansys.geometry.core.USE_SERVICE_COLORS``
            global setting is used.
        **plotting_options : dict, default: None
            Keyword arguments for plotting. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        """
        # lazy import here to improve initial module loading time
        import ansys.geometry.core as pyansys_geometry
        from ansys.geometry.core.plotting import GeometryPlotter
        from ansys.tools.visualization_interface.types.mesh_object_plot import (
            MeshObjectPlot,
        )

        use_service_colors = (
            use_service_colors
            if use_service_colors is not None
            else pyansys_geometry.USE_SERVICE_COLORS
        )

        mesh_object = self if use_service_colors else MeshObjectPlot(self, self.tessellate())
        pl = GeometryPlotter(use_trame=use_trame, use_service_colors=use_service_colors)
        pl.plot(mesh_object, **plotting_options)
        pl.show(screenshot=screenshot, **plotting_options)
