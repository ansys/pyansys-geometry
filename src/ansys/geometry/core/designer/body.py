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
"""Provides for managing a body."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from enum import Enum, unique
from functools import cached_property, wraps
from typing import TYPE_CHECKING, Union

from beartype import beartype as check_input_types
import matplotlib.colors as mcolors
from pint import Quantity

from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
from ansys.api.geometry.v0.bodies_pb2 import (
    BooleanRequest,
    CopyRequest,
    GetCollisionRequest,
    GetTessellationRequest,
    MapRequest,
    MirrorRequest,
    RotateRequest,
    ScaleRequest,
    SetAssignedMaterialRequest,
    SetColorRequest,
    SetFillStyleRequest,
    SetNameRequest,
    SetSuppressedRequest,
    TranslateRequest,
)
from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
from ansys.api.geometry.v0.commands_pb2 import (
    AssignMidSurfaceOffsetTypeRequest,
    AssignMidSurfaceThicknessRequest,
    CombineIntersectBodiesRequest,
    CombineMergeBodiesRequest,
    ImprintCurvesRequest,
    ProjectCurvesRequest,
    RemoveFacesRequest,
    ShellRequest,
)
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from ansys.api.geometry.v0.models_pb2 import TessellationOptions as GRPCTessellationOptions
from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.conversions import (
    frame_to_grpc_frame,
    grpc_material_to_material,
    grpc_point_to_point3d,
    plane_to_grpc_plane,
    point3d_to_grpc_point,
    sketch_shapes_to_grpc_geometries,
    tess_to_pd,
    trimmed_curve_to_grpc_trimmed_curve,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.designer.edge import CurveType, Edge
from ansys.geometry.core.designer.face import Face, SurfaceType
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.materials.material import Material
from ansys.geometry.core.math.bbox import BoundingBox
from ansys.geometry.core.math.constants import IDENTITY_MATRIX44
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc.auxiliary import (
    DEFAULT_COLOR,
    convert_color_to_hex,
    convert_opacity_to_hex,
    get_design_from_body,
)
from ansys.geometry.core.misc.checks import (
    check_type,
    check_type_all_elements_in_iterable,
    ensure_design_is_active,
    graphics_required,
    min_backend_version,
)
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Angle, Distance
from ansys.geometry.core.misc.options import TessellationOptions
from ansys.geometry.core.shapes.curves.trimmed_curve import TrimmedCurve
from ansys.geometry.core.sketch.sketch import Sketch
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from pyvista import MultiBlock, PolyData

    from ansys.geometry.core.designer.component import Component

# TODO: Temporary fix for boolean operations
# This is a temporary fix for the boolean operations issue. The issue is that the
# boolean operations are not working as expected with command-based operations. The
# goal is to fix this issue in the future.
# https://github.com/ansys/pyansys-geometry/issues/1733
__TEMPORARY_BOOL_OPS_FIX__ = (99, 0, 0)


@unique
class MidSurfaceOffsetType(Enum):
    """Provides values for mid-surface offsets supported."""

    MIDDLE = 0
    TOP = 1
    BOTTOM = 2
    VARIABLE = 3
    CUSTOM = 4


@unique
class CollisionType(Enum):
    """Provides values for collision types between bodies."""

    NONE = 0
    TOUCH = 1
    INTERSECT = 2
    CONTAINED = 3
    CONTAINEDTOUCH = 4


@unique
class FillStyle(Enum):
    """Provides values for fill styles supported."""

    DEFAULT = 0
    OPAQUE = 1
    TRANSPARENT = 2


class IBody(ABC):
    """Defines the common methods for a body, providing the abstract body interface.

    Both the ``MasterBody`` class and ``Body`` class both inherit from the ``IBody``
    class. All child classes must implement all abstract methods.
    """

    @abstractmethod
    def id(self) -> str:
        """Get the ID of the body as a string."""
        return

    @abstractmethod
    def _grpc_id(self) -> EntityIdentifier:
        """Entity identifier of this body on the server side."""
        return

    @abstractmethod
    def name(self) -> str:
        """Get the name of the body."""
        return

    @abstractmethod
    def set_name(self, str) -> None:
        """Set the name of the body."""
        return

    @abstractmethod
    def fill_style(self) -> FillStyle:
        """Get the fill style of the body."""
        return

    @abstractmethod
    def set_fill_style(self, fill_style: FillStyle) -> None:
        """Set the fill style of the body."""
        return

    @abstractmethod
    def is_suppressed(self) -> bool:
        """Get the body suppression state."""
        return

    @abstractmethod
    def set_suppressed(self, suppressed: bool) -> None:
        """Set the body suppression state."""
        return

    @abstractmethod
    def color(self) -> str:
        """Get the color of the body."""
        return

    @abstractmethod
    def opacity(self) -> float:
        """Get the float value of the opacity for the body."""
        return

    @abstractmethod
    def set_color(self, color: str | tuple[float, float, float]) -> None:
        """Set the color of the body.

        Parameters
        ----------
        color : str | tuple[float, float, float]
            Color to set the body to. This can be a string representing a color name
            or a tuple of RGB values in the range [0, 1] (RGBA) or [0, 255] (pure RGB).
        """
        return

    @abstractmethod
    def faces(self) -> list[Face]:
        """Get a list of all faces within the body.

        Returns
        -------
        list[Face]
        """
        return

    @abstractmethod
    def edges(self) -> list[Edge]:
        """Get a list of all edges within the body.

        Returns
        -------
        list[Edge]
        """
        return

    @abstractmethod
    def is_alive(self) -> bool:
        """Check if the body is still alive and has not been deleted."""
        return

    @abstractmethod
    def is_surface(self) -> bool:
        """Check if the body is a planar body."""
        return

    @abstractmethod
    def surface_thickness(self) -> Quantity | None:
        """Get the surface thickness of a surface body.

        Notes
        -----
        This method is only for surface-type bodies that have been assigned a surface thickness.
        """
        return

    @abstractmethod
    def surface_offset(self) -> Union["MidSurfaceOffsetType", None]:
        """Get the surface offset type of a surface body.

        Notes
        -----
        This method is only for surface-type bodies that have been assigned a surface offset.
        """
        return

    @abstractmethod
    def volume(self) -> Quantity:
        """Calculate the volume of the body.

        Notes
        -----
        When dealing with a planar surface, a value of ``0`` is returned as a volume.
        """
        return

    @abstractmethod
    def material(self) -> Material:
        """Get the assigned material of the body.

        Returns
        -------
        Material
            Material assigned to the body.
        """
        return

    @abstractmethod
    def bounding_box(self) -> BoundingBox:
        """Get the bounding box of the body.

        Returns
        -------
        BoundingBox
            Bounding box of the body.
        """
        return

    @abstractmethod
    def assign_material(self, material: Material) -> None:
        """Assign a material against the active design.

        Parameters
        ----------
        material : Material
            Source material data.
        """
        return

    @abstractmethod
    def get_assigned_material(self) -> Material:
        """Get the assigned material of the body.

        Returns
        -------
        Material
            Material assigned to the body.
        """
        return

    @abstractmethod
    def add_midsurface_thickness(self, thickness: Quantity) -> None:
        """Add a mid-surface thickness to a surface body.

        Parameters
        ----------
        thickness : ~pint.Quantity
            Thickness to assign.

        Notes
        -----
        Only surface bodies are eligible for mid-surface thickness assignment.
        """
        return

    @abstractmethod
    def add_midsurface_offset(self, offset: "MidSurfaceOffsetType") -> None:
        """Add a mid-surface offset to a surface body.

        Parameters
        ----------
        offset_type : MidSurfaceOffsetType
            Surface offset to assign.

        Notes
        -----
        Only surface bodies are eligible for mid-surface offset assignment.
        """
        return

    @abstractmethod
    def imprint_curves(self, faces: list[Face], sketch: Sketch) -> tuple[list[Edge], list[Face]]:
        """Imprint all specified geometries onto specified faces of the body.

        Parameters
        ----------
        faces: list[Face]
            list of faces to imprint the curves of the sketch onto.
        sketch: Sketch
            All curves to imprint on the faces.

        Returns
        -------
        tuple[list[Edge], list[Face]]
            All impacted edges and faces from the imprint operation.
        """
        return

    @abstractmethod
    def project_curves(
        self,
        direction: UnitVector3D,
        sketch: Sketch,
        closest_face: bool,
        only_one_curve: bool = False,
    ) -> list[Face]:
        """Project all specified geometries onto the body.

        Parameters
        ----------
        direction: UnitVector3D
            Direction of the projection.
        sketch: Sketch
            All curves to project on the body.
        closest_face: bool
            Whether to target the closest face with the projection.
        only_one_curve: bool, default: False
            Whether to project only one curve of the entire sketch. When
            ``True``, only one curve is projected.

        Returns
        -------
        list[Face]
            All faces from the project curves operation.

        Notes
        -----
        The ``only_one_curve`` parameter allows you to optimize the server call because
        projecting curves is an expensive operation. This reduces the workload on the
        server side.
        """
        return

    @abstractmethod
    def imprint_projected_curves(
        self,
        direction: UnitVector3D,
        sketch: Sketch,
        closest_face: bool,
        only_one_curve: bool = False,
    ) -> list[Face]:  # noqa: D102
        """Project and imprint specified geometries onto the body.

        This method combines the ``project_curves()`` and ``imprint_curves()`` method into
        one method. It has higher performance than calling them back-to-back when dealing
        with many curves. Because it is a specialized function, this method only returns
        the faces (and not the edges) from the imprint operation.

        Parameters
        ----------
        direction: UnitVector3D
            Direction of the projection.
        sketch: Sketch
            All curves to project on the body.
        closest_face: bool
            Whether to target the closest face with the projection.
        only_one_curve: bool, default: False
            Whether to project only one curve of the entire sketch. When
            ``True``, only one curve is projected.

        Returns
        -------
        list[Face]
            All imprinted faces from the operation.

        Notes
        -----
        The ``only_one_curve`` parameter allows you to optimize the server call because
        projecting curves is an expensive operation. This reduces the workload on the
        server side.
        """
        return

    @abstractmethod
    def translate(self, direction: UnitVector3D, distance: Quantity | Distance | Real) -> None:
        """Translate the body in a specified direction and distance.

        Parameters
        ----------
        direction: UnitVector3D
            Direction of the translation.
        distance: ~pint.Quantity | Distance | Real
            Distance (magnitude) of the translation.

        Returns
        -------
        None
        """
        return

    @abstractmethod
    def rotate(
        self,
        axis_origin: Point3D,
        axis_direction: UnitVector3D,
        angle: Quantity | Angle | Real,
    ) -> None:
        """Rotate the geometry body around the specified axis by a given angle.

        Parameters
        ----------
        axis_origin: Point3D
            Origin of the rotational axis.
        axis_direction: UnitVector3D
            The axis of rotation.
        angle: ~pint.Quantity | Angle | Real
            Angle (magnitude) of the rotation.

        Returns
        -------
        None
        """
        return

    @abstractmethod
    def scale(self, value: Real) -> None:
        """Scale the geometry body by the given value.

        Parameters
        ----------
        value: Real
            Value to scale the body by.

        Notes
        -----
        The calling object is directly modified when this method is called.
        Thus, it is important to make copies if needed.
        """
        return

    @abstractmethod
    def map(self, frame: Frame) -> None:
        """Map the geometry body to the new specified frame.

        Parameters
        ----------
        frame: Frame
            Structure defining the orientation of the body.

        Notes
        -----
        The calling object is directly modified when this method is called.
        Thus, it is important to make copies if needed.
        """
        return

    @abstractmethod
    def mirror(self, plane: Plane) -> None:
        """Mirror the geometry body across the specified plane.

        Parameters
        ----------
        plane: Plane
            Represents the mirror.

        Notes
        -----
        The calling object is directly modified when this method is called.
        Thus, it is important to make copies if needed.
        """
        return

    @abstractmethod
    def get_collision(self, body: "Body") -> CollisionType:
        """Get the collision state between bodies.

        Parameters
        ----------
        body: Body
            Object that the collision state is checked with.

        Returns
        -------
        CollisionType
            Enum that defines the collision state between bodies.
        """
        return

    @abstractmethod
    def copy(self, parent: "Component", name: str = None) -> "Body":
        """Create a copy of the body under the specified parent.

        Parameters
        ----------
        parent: Component
            Parent component to place the new body under within the design assembly.
        name: str
            Name to give the new body.

        Returns
        -------
        Body
            Copy of the body.
        """
        return

    @abstractmethod
    def tessellate(
        self, merge: bool = False, tess_options: TessellationOptions | None = None
    ) -> Union["PolyData", "MultiBlock"]:
        """Tessellate the body and return the geometry as triangles.

        Parameters
        ----------
        merge : bool, default: False
            Whether to merge the body into a single mesh. When ``False`` (default), the
            number of triangles are preserved and only the topology is merged.
            When ``True``, the individual faces of the tessellation are merged.
        tess_options : TessellationOptions | None, default: None
            A set of options to determine the tessellation quality.

        Returns
        -------
        ~pyvista.PolyData, ~pyvista.MultiBlock
            Merged :class:`pyvista.PolyData` if ``merge=True`` or a composite dataset.

        Examples
        --------
        Extrude a box centered at the origin to create a rectangular body and
        tessellate it:

        >>> from ansys.geometry.core.misc.units import UNITS as u
        >>> from ansys.geometry.core.sketch import Sketch
        >>> from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
        >>> from ansys.geometry.core import Modeler
        >>> modeler = Modeler()
        >>> origin = Point3D([0, 0, 0])
        >>> plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 0, 1])
        >>> sketch = Sketch(plane)
        >>> box = sketch.box(Point2D([2, 0]), 4, 4)
        >>> design = modeler.create_design("my-design")
        >>> my_comp = design.add_component("my-comp")
        >>> body = my_comp.extrude_sketch("my-sketch", sketch, 1 * u.m)
        >>> blocks = body.tessellate()
        >>> blocks
        >>> MultiBlock(0x7F94EC757460)
             N Blocks:	6
             X Bounds:	0.000, 4.000
             Y Bounds:	-1.000, 0.000
             Z Bounds:	-0.500, 4.500

        Merge the body:

        >>> mesh = body.tessellate(merge=True)
        >>> mesh
        PolyData (0x7f94ec75f3a0)
          N Cells:	12
          N Points:	24
          X Bounds:	0.000e+00, 4.000e+00
          Y Bounds:	-1.000e+00, 0.000e+00
          Z Bounds:	-5.000e-01, 4.500e+00
          N Arrays:	0
        """
        return

    @abstractmethod
    def shell_body(self, offset: Real) -> bool:
        """Shell the body to the thickness specified.

        Parameters
        ----------
        offset : Real
            Shell thickness.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        return

    @abstractmethod
    def remove_faces(self, selection: Face | Iterable[Face], offset: Real) -> bool:
        """Shell by removing a given set of faces.

        Parameters
        ----------
        selection : Face | Iterable[Face]
            Face or faces to be removed.
        offset : Real
            Shell thickness.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        return

    @abstractmethod
    def plot(
        self,
        merge: bool = True,
        screenshot: str | None = None,
        use_trame: bool | None = None,
        use_service_colors: bool | None = None,
        **plotting_options: dict | None,
    ) -> None:
        """Plot the body.

        Parameters
        ----------
        merge : bool, default: True
            Whether to merge the body into a single mesh. Performance improved when ``True``.
            When ``True`` (default), the individual faces of the tessellation are merged.
            When ``False``, the number of triangles are preserved and only the topology
            is merged.
        screenshot : str, default: None
            Path for saving a screenshot of the image that is being represented.
        use_trame : bool, default: None
            Whether to enable the use of `trame <https://kitware.github.io/trame/index.html>`_.
            The default is ``None``, in which case the
            ``ansys.tools.visualization_interface.USE_TRAME`` global setting is used.
        use_service_colors : bool, default: None
            Whether to use the colors assigned to the body in the service. The default
            is ``None``, in which case the ``ansys.geometry.core.USE_SERVICE_COLORS``
            global setting is used.
        **plotting_options : dict, default: None
            Keyword arguments for plotting. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        Examples
        --------
        Extrude a box centered at the origin to create rectangular body and
        plot it:

        >>> from ansys.geometry.core.misc.units import UNITS as u
        >>> from ansys.geometry.core.sketch import Sketch
        >>> from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
        >>> from ansys.geometry.core import Modeler
        >>> modeler = Modeler()
        >>> origin = Point3D([0, 0, 0])
        >>> plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 0, 1])
        >>> sketch = Sketch(plane)
        >>> box = sketch.box(Point2D([2, 0]), 4, 4)
        >>> design = modeler.create_design("my-design")
        >>> mycomp = design.add_component("my-comp")
        >>> body = mycomp.extrude_sketch("my-sketch", sketch, 1 * u.m)
        >>> body.plot()

        Plot the body and color each face individually:

        >>> body.plot(multi_colors=True)
        """
        return

    def intersect(self, other: Union["Body", Iterable["Body"]], keep_other: bool = False) -> None:
        """Intersect two (or more) bodies.

        Parameters
        ----------
        other : Body
            Body to intersect with.
        keep_other : bool, default: False
            Whether to retain the intersected body or not.

        Raises
        ------
        ValueError
            If the bodies do not intersect.

        Notes
        -----
        The ``self`` parameter is directly modified with the result, and
        the ``other`` parameter is consumed. Thus, it is important to make
        copies if needed. If the ``keep_other`` parameter is set to ``True``,
        the intersected body is retained.
        """
        return

    @protect_grpc
    def subtract(self, other: Union["Body", Iterable["Body"]], keep_other: bool = False) -> None:
        """Subtract two (or more) bodies.

        Parameters
        ----------
        other : Body
            Body to subtract from the ``self`` parameter.
        keep_other : bool, default: False
            Whether to retain the subtracted body or not.

        Raises
        ------
        ValueError
            If the subtraction results in an empty (complete) subtraction.

        Notes
        -----
        The ``self`` parameter is directly modified with the result, and
        the ``other`` parameter is consumed. Thus, it is important to make
        copies if needed. If the ``keep_other`` parameter is set to ``True``,
        the subtracted body is retained.
        """
        return

    @protect_grpc
    def unite(self, other: Union["Body", Iterable["Body"]], keep_other: bool = False) -> None:
        """Unite two (or more) bodies.

        Parameters
        ----------
        other : Body
            Body to unite with the ``self`` parameter.
        keep_other : bool, default: False
            Whether to retain the united body or not.

        Notes
        -----
        The ``self`` parameter is directly modified with the result, and
        the ``other`` parameter is consumed. Thus, it is important to make
        copies if needed. If the ``keep_other`` parameter is set to ``True``,
        the united body is retained.
        """
        return


class MasterBody(IBody):
    """Represents solids and surfaces organized within the design assembly.

    Solids and surfaces synchronize to a design within a supporting Geometry service instance.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    name : str
        User-defined label for the body.
    parent_component : Component
        Parent component to place the new component under within the design assembly.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    is_surface : bool, default: False
        Whether the master body is a surface or an 3D object (with volume). The default
        is ``False``, in which case the master body is a surface. When ``True``, the
        master body is a 3D object (with volume).
    """

    def __init__(
        self,
        id: str,
        name: str,
        grpc_client: GrpcClient,
        is_surface: bool = False,
    ):
        """Initialize the ``MasterBody`` class."""
        check_type(id, str)
        check_type(name, str)
        check_type(grpc_client, GrpcClient)
        check_type(is_surface, bool)

        self._id = id
        self._name = name
        self._grpc_client = grpc_client
        self._is_surface = is_surface
        self._surface_thickness = None
        self._surface_offset = None
        self._is_alive = True
        self._bodies_stub = BodiesStub(self._grpc_client.channel)
        self._commands_stub = CommandsStub(self._grpc_client.channel)
        self._tessellation = None
        self._fill_style = FillStyle.DEFAULT
        self._color = None

    def reset_tessellation_cache(func):  # noqa: N805
        """Decorate ``MasterBody`` methods that need tessellation cache update.

        Parameters
        ----------
        func : method
            Method to call.

        Returns
        -------
        Any
            Output of the method, if any.
        """

        @wraps(func)
        def wrapper(self: "MasterBody", *args, **kwargs):
            self._tessellation = None
            return func(self, *args, **kwargs)

        return wrapper

    @property
    def id(self) -> str:  # noqa: D102
        return self._id

    @cached_property
    def _grpc_id(self) -> EntityIdentifier:  # noqa: D102
        return EntityIdentifier(id=self._id)

    @property
    def name(self) -> str:  # noqa: D102
        return self._name

    @name.setter
    def name(self, value: str):  # noqa: D102
        self.set_name(value)

    @property
    def fill_style(self) -> str:  # noqa: D102
        return self._fill_style

    @fill_style.setter
    def fill_style(self, value: FillStyle):  # noqa: D102
        self.set_fill_style(value)

    @property
    @protect_grpc
    def is_suppressed(self) -> bool:  # noqa: D102
        response = self._bodies_stub.IsSuppressed(self._grpc_id)
        return response.result

    @is_suppressed.setter
    def is_suppressed(self, value: bool):  # noqa: D102
        self.set_suppressed(value)

    @property
    @protect_grpc
    def color(self) -> str:  # noqa: D102
        """Get the current color of the body."""
        if self._color is None and self.is_alive:
            # Assigning default value first
            self._color = DEFAULT_COLOR

            if self._grpc_client.backend_version < (25, 1, 0):  # pragma: no cover
                # Server does not support color retrieval before version 25.1.0
                self._grpc_client.log.warning(
                    "Server does not support color retrieval. Default value assigned..."
                )
            else:
                # Fetch color from the server if it's not cached
                color_response = self._bodies_stub.GetColor(self._grpc_id)
                if color_response.color:
                    self._color = mcolors.to_hex(color_response.color, keep_alpha=True)

        return self._color

    @property
    def opacity(self) -> float:  # noqa: D102
        opacity_hex = self._color[7:]
        return int(opacity_hex, 16) / 255 if opacity_hex else 1

    @color.setter
    def color(self, value: str | tuple[float, float, float]) -> None:  # noqa: D102
        self.set_color(value)

    @opacity.setter
    def opacity(self, value: float) -> None:  # noqa: D102
        self.set_opacity(value)

    @property
    def is_surface(self) -> bool:  # noqa: D102
        return self._is_surface

    @property
    def surface_thickness(self) -> Quantity | None:  # noqa: D102
        return self._surface_thickness if self.is_surface else None

    @property
    def surface_offset(self) -> Union["MidSurfaceOffsetType", None]:  # noqa: D102
        return self._surface_offset if self.is_surface else None

    @property
    @protect_grpc
    def faces(self) -> list[Face]:  # noqa: D102
        self._grpc_client.log.debug(f"Retrieving faces for body {self.id} from server.")
        grpc_faces = self._bodies_stub.GetFaces(self._grpc_id)
        return [
            Face(
                grpc_face.id,
                SurfaceType(grpc_face.surface_type),
                self,
                self._grpc_client,
                grpc_face.is_reversed,
            )
            for grpc_face in grpc_faces.faces
        ]

    @property
    @protect_grpc
    def edges(self) -> list[Edge]:  # noqa: D102
        self._grpc_client.log.debug(f"Retrieving edges for body {self.id} from server.")
        grpc_edges = self._bodies_stub.GetEdges(self._grpc_id)
        return [
            Edge(
                grpc_edge.id,
                CurveType(grpc_edge.curve_type),
                self,
                self._grpc_client,
                grpc_edge.is_reversed,
            )
            for grpc_edge in grpc_edges.edges
        ]

    @property
    def is_alive(self) -> bool:  # noqa: D102
        return self._is_alive

    @property
    @protect_grpc
    def volume(self) -> Quantity:  # noqa: D102
        if self.is_surface:
            self._grpc_client.log.debug("Dealing with planar surface. Returning 0 as the volume.")
            return Quantity(0, DEFAULT_UNITS.SERVER_VOLUME)
        else:
            self._grpc_client.log.debug(f"Retrieving volume for body {self.id} from server.")
            volume_response = self._bodies_stub.GetVolume(self._grpc_id)
            return Quantity(volume_response.volume, DEFAULT_UNITS.SERVER_VOLUME)

    @property
    def material(self) -> Material:  # noqa: D102
        return self.get_assigned_material()

    @material.setter
    def material(self, value: Material):  # noqa: D102
        self.assign_material(value)

    @property
    @protect_grpc
    @min_backend_version(25, 2, 0)
    def bounding_box(self) -> BoundingBox:  # noqa: D102
        self._grpc_client.log.debug(f"Retrieving bounding box for body {self.id} from server.")
        result = self._bodies_stub.GetBoundingBox(self._grpc_id).box

        min_corner = grpc_point_to_point3d(result.min)
        max_corner = grpc_point_to_point3d(result.max)
        center = grpc_point_to_point3d(result.center)
        return BoundingBox(min_corner, max_corner, center)

    @protect_grpc
    @check_input_types
    def assign_material(self, material: Material) -> None:  # noqa: D102
        self._grpc_client.log.debug(f"Assigning body {self.id} material {material.name}.")
        self._bodies_stub.SetAssignedMaterial(
            SetAssignedMaterialRequest(id=self._id, material=material.name)
        )

    @protect_grpc
    def get_assigned_material(self) -> Material:  # noqa: D102
        self._grpc_client.log.debug(f"Retrieving assigned material for body {self.id}.")
        material_response = self._bodies_stub.GetAssignedMaterial(self._grpc_id)
        return grpc_material_to_material(material_response)

    @protect_grpc
    @check_input_types
    def add_midsurface_thickness(self, thickness: Quantity) -> None:  # noqa: D102
        if self.is_surface:
            self._commands_stub.AssignMidSurfaceThickness(
                AssignMidSurfaceThicknessRequest(
                    bodies_or_faces=[self.id],
                    thickness=thickness.m_as(DEFAULT_UNITS.SERVER_LENGTH),
                )
            )
            self._surface_thickness = thickness
        else:
            self._grpc_client.log.warning(
                f"Body {self.name} cannot be assigned a mid-surface thickness because it is not a surface. Ignoring request."  # noqa : E501
            )

    @protect_grpc
    @check_input_types
    def add_midsurface_offset(self, offset: MidSurfaceOffsetType) -> None:  # noqa: D102
        if self.is_surface:
            self._commands_stub.AssignMidSurfaceOffsetType(
                AssignMidSurfaceOffsetTypeRequest(
                    bodies_or_faces=[self.id], offset_type=offset.value
                )
            )
            self._surface_offset = offset
        else:
            self._grpc_client.log.warning(
                f"Body {self.name} cannot be assigned a mid-surface offset because it is not a surface. Ignoring request."  # noqa : E501
            )

    @protect_grpc
    @check_input_types
    def imprint_curves(  # noqa: D102
        self, faces: list[Face], sketch: Sketch
    ) -> tuple[list[Edge], list[Face]]:
        raise NotImplementedError(
            """
            imprint_curves is not implemented at the MasterBody level.
            Instead, call this method on a body.
            """
        )

    @protect_grpc
    @check_input_types
    def project_curves(  # noqa: D102
        self,
        direction: UnitVector3D,
        sketch: Sketch,
        closest_face: bool,
        only_one_curve: bool = False,
    ) -> list[Face]:
        raise NotImplementedError(
            """
            project_curves is not implemented at the MasterBody level.
            Instead, call this method on a body.
            """
        )

    @check_input_types
    @protect_grpc
    def imprint_projected_curves(  # noqa: D102
        self,
        direction: UnitVector3D,
        sketch: Sketch,
        closest_face: bool,
        only_one_curve: bool = False,
    ) -> list[Face]:
        raise NotImplementedError(
            """
            imprint_projected_curves is not implemented at the MasterBody level.
            Instead, call this method on a body.
            """
        )

    @protect_grpc
    @check_input_types
    @reset_tessellation_cache
    def translate(  # noqa: D102
        self, direction: UnitVector3D, distance: Quantity | Distance | Real
    ) -> None:
        distance = distance if isinstance(distance, Distance) else Distance(distance)

        translation_magnitude = distance.value.m_as(DEFAULT_UNITS.SERVER_LENGTH)

        self._grpc_client.log.debug(f"Translating body {self.id}.")

        self._bodies_stub.Translate(
            TranslateRequest(
                ids=[self.id],
                direction=unit_vector_to_grpc_direction(direction),
                distance=translation_magnitude,
            )
        )

    @protect_grpc
    @check_input_types
    @min_backend_version(25, 1, 0)
    def set_name(  # noqa: D102
        self, name: str
    ) -> None:
        self._grpc_client.log.debug(f"Renaming body {self.id} from '{self.name}' to '{name}'.")
        self._bodies_stub.SetName(
            SetNameRequest(
                body_id=self.id,
                name=name,
            )
        )
        self._name = name

    @protect_grpc
    @check_input_types
    @min_backend_version(25, 1, 0)
    def set_fill_style(  # noqa: D102
        self, fill_style: FillStyle
    ) -> None:
        self._grpc_client.log.debug(f"Setting body fill style {self.id}.")
        self._bodies_stub.SetFillStyle(
            SetFillStyleRequest(
                body_id=self.id,
                fill_style=fill_style.value,
            )
        )
        self._fill_style = fill_style

    @protect_grpc
    @check_input_types
    @min_backend_version(25, 2, 0)
    def set_suppressed(  # noqa: D102
        self, suppressed: bool
    ) -> None:
        """Set the body suppression state."""
        self._grpc_client.log.debug(f"Setting body {self.id}, as suppressed: {suppressed}.")
        self._bodies_stub.SetSuppressed(
            SetSuppressedRequest(
                bodies=[self._grpc_id],
                is_suppressed=suppressed,
            )
        )

    @protect_grpc
    @check_input_types
    @min_backend_version(25, 1, 0)
    def set_color(
        self, color: str | tuple[float, float, float] | tuple[float, float, float, float]
    ) -> None:
        """Set the color of the body."""
        self._grpc_client.log.debug(f"Setting body color of {self.id} to {color}.")
        color = convert_color_to_hex(color)

        self._bodies_stub.SetColor(
            SetColorRequest(
                body_id=self.id,
                color=color,
            )
        )
        self._color = color

    @check_input_types
    @min_backend_version(25, 2, 0)
    def set_opacity(self, opacity: float) -> None:
        """Set the opacity of the body."""
        self._grpc_client.log.debug(f"Setting body opacity of {self.id} to {opacity}.")
        opacity = convert_opacity_to_hex(opacity)

        new_color = self._color[0:7] + opacity
        self.set_color(new_color)

    @protect_grpc
    @check_input_types
    @reset_tessellation_cache
    @min_backend_version(24, 2, 0)
    def rotate(  # noqa: D102
        self,
        axis_origin: Point3D,
        axis_direction: UnitVector3D,
        angle: Quantity | Angle | Real,
    ) -> None:
        angle = angle if isinstance(angle, Angle) else Angle(angle)
        rotation_magnitude = angle.value.m_as(DEFAULT_UNITS.SERVER_ANGLE)
        self._grpc_client.log.debug(f"Rotating body {self.id}.")
        self._bodies_stub.Rotate(
            RotateRequest(
                id=self.id,
                axis_origin=point3d_to_grpc_point(axis_origin),
                axis_direction=unit_vector_to_grpc_direction(axis_direction),
                angle=rotation_magnitude,
            )
        )

    @protect_grpc
    @check_input_types
    @reset_tessellation_cache
    @min_backend_version(24, 2, 0)
    def scale(self, value: Real) -> None:  # noqa: D102
        self._grpc_client.log.debug(f"Scaling body {self.id}.")
        self._bodies_stub.Scale(ScaleRequest(id=self.id, scale=value))

    @protect_grpc
    @check_input_types
    @reset_tessellation_cache
    @min_backend_version(24, 2, 0)
    def map(self, frame: Frame) -> None:  # noqa: D102
        self._grpc_client.log.debug(f"Mapping body {self.id}.")
        self._bodies_stub.Map(MapRequest(id=self.id, frame=frame_to_grpc_frame(frame)))

    @protect_grpc
    @check_input_types
    @reset_tessellation_cache
    @min_backend_version(24, 2, 0)
    def mirror(self, plane: Plane) -> None:  # noqa: D102
        self._grpc_client.log.debug(f"Mirroring body {self.id}.")
        self._bodies_stub.Mirror(MirrorRequest(id=self.id, plane=plane_to_grpc_plane(plane)))

    @protect_grpc
    @min_backend_version(24, 2, 0)
    def get_collision(self, body: "Body") -> CollisionType:  # noqa: D102
        self._grpc_client.log.debug(f"Get collision between body {self.id} and body {body.id}.")
        response = self._bodies_stub.GetCollision(
            GetCollisionRequest(
                body_1_id=self.id,
                body_2_id=body.id,
            )
        )
        return CollisionType(response.collision)

    @protect_grpc
    def copy(self, parent: "Component", name: str = None) -> "Body":  # noqa: D102
        from ansys.geometry.core.designer.component import Component

        # Check input types
        check_type(parent, Component)
        check_type(name, (type(None), str))
        copy_name = self.name if name is None else name

        self._grpc_client.log.debug(f"Copying body {self.id}.")

        # Perform copy request to server
        response = self._bodies_stub.Copy(
            CopyRequest(
                id=self.id,
                parent=parent.id,
                name=copy_name,
            )
        )

        # Assign the new body to its specified parent (and return the new body)
        tb = MasterBody(
            response.master_id, copy_name, self._grpc_client, is_surface=self.is_surface
        )
        parent._master_component.part.bodies.append(tb)
        parent._clear_cached_bodies()
        body_id = f"{parent.id}/{tb.id}" if parent.parent_component else tb.id
        return Body(body_id, response.name, parent, tb)

    @protect_grpc
    @graphics_required
    def tessellate(  # noqa: D102
        self,
        merge: bool = False,
        transform: Matrix44 = IDENTITY_MATRIX44,
        tess_options: TessellationOptions | None = None,
    ) -> Union["PolyData", "MultiBlock"]:
        # lazy import here to improve initial module load time
        import pyvista as pv

        if not self.is_alive:
            return pv.PolyData() if merge else pv.MultiBlock()

        # If the server does not support tessellation options, ignore them
        if tess_options is not None and self._grpc_client.backend_version < (25, 2, 0):
            self._grpc_client.log.warning(
                "Tessellation options are not supported by server"
                f" version {self._grpc_client.backend_version}. Ignoring options."
            )
            tess_options = None

        self._grpc_client.log.debug(f"Requesting tessellation for body {self.id}.")

        # cache tessellation
        if not self._tessellation:
            if tess_options is not None:
                request = GetTessellationRequest(
                    id=self._grpc_id,
                    options=GRPCTessellationOptions(
                        surface_deviation=tess_options.surface_deviation,
                        angle_deviation=tess_options.angle_deviation,
                        maximum_aspect_ratio=tess_options.max_aspect_ratio,
                        maximum_edge_length=tess_options.max_edge_length,
                        watertight=tess_options.watertight,
                    ),
                )
                try:
                    resp = self._bodies_stub.GetTessellationWithOptions(request)
                    self._tessellation = {
                        str(face_id): tess_to_pd(face_tess)
                        for face_id, face_tess in resp.face_tessellation.items()
                    }
                except Exception:
                    tessellation_map = {}
                    for response in self._bodies_stub.GetTessellationStream(request):
                        for key, value in response.face_tessellation.items():
                            tessellation_map[key] = tess_to_pd(value)

                    self._tessellation = tessellation_map
            else:
                try:
                    resp = self._bodies_stub.GetTessellation(self._grpc_id)
                    self._tessellation = {
                        str(face_id): tess_to_pd(face_tess)
                        for face_id, face_tess in resp.face_tessellation.items()
                    }
                except Exception as err:
                    # Streaming is not supported in older versions...
                    if self._grpc_client.backend_version < (25, 2, 0):
                        raise err

                    tessellation_map = {}
                    request = GetTessellationRequest(self._grpc_id)
                    for response in self._bodies_stub.GetTessellationStream(request):
                        for key, value in response.face_tessellation.items():
                            tessellation_map[key] = tess_to_pd(value)

                    self._tessellation = tessellation_map

        pdata = [tess.transform(transform, inplace=False) for tess in self._tessellation.values()]
        comp = pv.MultiBlock(pdata)

        if merge:
            ugrid = comp.combine()
            return pv.PolyData(var_inp=ugrid.points, faces=ugrid.cells)
        else:
            return comp

    @protect_grpc
    @reset_tessellation_cache
    @check_input_types
    @min_backend_version(25, 2, 0)
    def shell_body(self, offset: Real) -> bool:  # noqa: D102
        self._grpc_client.log.debug(f"Shelling body {self.id} to offset {offset}.")

        result = self._commands_stub.Shell(
            ShellRequest(
                selection=self._grpc_id,
                offset=offset,
            )
        )

        if result.success is False:
            self._grpc_client.log.warning(f"Failed to shell body {self.id}.")

        return result.success

    @protect_grpc
    @reset_tessellation_cache
    @check_input_types
    @min_backend_version(25, 2, 0)
    def remove_faces(self, selection: Face | Iterable[Face], offset: Real) -> bool:  # noqa: D102
        selection: list[Face] = selection if isinstance(selection, Iterable) else [selection]
        check_type_all_elements_in_iterable(selection, Face)

        # check if faces belong to this body
        for face in selection:
            if face.body.id != self.id:
                raise ValueError(f"Face {face.id} does not belong to body {self.id}.")

        self._grpc_client.log.debug(f"Removing faces to shell body {self.id}.")

        result = self._commands_stub.RemoveFaces(
            RemoveFacesRequest(
                selection=[face._grpc_id for face in selection],
                offset=offset,
            )
        )

        if result.success is False:
            self._grpc_client.log.warning(f"Failed to remove faces from body {self.id}.")

        return result.success

    def plot(  # noqa: D102
        self,
        merge: bool = True,
        screenshot: str | None = None,
        use_trame: bool | None = None,
        use_service_colors: bool | None = None,
        **plotting_options: dict | None,
    ) -> None:
        raise NotImplementedError(
            "MasterBody does not implement plot methods. Call this method on a body instead."
        )

    def intersect(self, other: Union["Body", Iterable["Body"]], keep_other: bool = False) -> None:  # noqa: D102
        raise NotImplementedError(
            "MasterBody does not implement Boolean methods. Call this method on a body instead."
        )

    def subtract(self, other: Union["Body", Iterable["Body"]], keep_other: bool = False) -> None:  # noqa: D102
        raise NotImplementedError(
            "MasterBody does not implement Boolean methods. Call this method on a body instead."
        )

    def unite(self, other: Union["Body", Iterable["Body"]], keep_other: bool = False) -> None:  # noqa: D102
        raise NotImplementedError(
            "MasterBody does not implement Boolean methods. Call this method on a body instead."
        )

    def __repr__(self) -> str:
        """Represent the master body as a string."""
        lines = [f"ansys.geometry.core.designer.MasterBody {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Exists               : {self.is_alive}")
        lines.append(f"  Surface body         : {self.is_surface}")
        if self.is_surface:
            lines.append(f"  Surface thickness    : {self.surface_thickness}")
            lines.append(f"  Surface offset       : {self.surface_offset}")

        return "\n".join(lines)


class Body(IBody):
    """Represents solids and surfaces organized within the design assembly.

    Solids and surfaces synchronize to a design within a supporting Geometry service instance.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    name : str
        User-defined label for the body.
    parent_component : Component
        Parent component to place the new component under within the design assembly.
    template : MasterBody
        Master body that this body is an occurrence of.
    """

    def __init__(self, id, name, parent_component: "Component", template: MasterBody) -> None:
        """Initialize the ``Body`` class."""
        self._id = id
        self._name = name
        self._parent_component = parent_component
        self._template = template

    def reset_tessellation_cache(func):  # noqa: N805
        """Decorate ``Body`` methods that require a tessellation cache update.

        Parameters
        ----------
        func : method
            Method to call.

        Returns
        -------
        Any
            Output of the method, if any.
        """

        @wraps(func)
        def wrapper(self: "Body", *args, **kwargs):
            self._reset_tessellation_cache()
            return func(self, *args, **kwargs)

        return wrapper

    def _reset_tessellation_cache(self):  # noqa: N805
        """Reset the cached tessellation for a body."""
        self._template._tessellation = None
        # if this reference is stale, reset the real cache in the part
        # this gets the matching id master body in the part
        master_in_part = next(
            (
                b
                for b in self.parent_component._master_component.part.bodies
                if b.id == self._template.id
            ),
            None,
        )
        if master_in_part is not None:
            master_in_part._tessellation = None

    @property
    def id(self) -> str:  # noqa: D102
        return self._id

    @cached_property
    def _grpc_id(self) -> EntityIdentifier:  # noqa: D102
        return EntityIdentifier(id=self._id)

    @property
    def name(self) -> str:  # noqa: D102
        return self._template.name

    @name.setter
    def name(self, value: str):  # noqa: D102
        self._template.name = value

    @property
    def fill_style(self) -> str:  # noqa: D102
        return self._template.fill_style

    @fill_style.setter
    def fill_style(self, fill_style: FillStyle) -> str:  # noqa: D102
        self._template.fill_style = fill_style

    @property
    def is_suppressed(self) -> bool:  # noqa: D102
        return self._template.is_suppressed

    @is_suppressed.setter
    def is_suppressed(self, suppressed: bool):  # noqa: D102
        self._template.is_suppressed = suppressed

    @property
    def color(self) -> str:  # noqa: D102
        return self._template.color

    @property
    def opacity(self) -> float:  # noqa: D102
        return self._template.opacity

    @color.setter
    def color(self, color: str | tuple[float, float, float]) -> None:  # noqa: D102
        return self._template.set_color(color)

    @opacity.setter
    def opacity(self, opacity: float) -> None:  # noqa: D102
        return self._template.set_opacity(opacity)

    @property
    def parent_component(self) -> "Component":  # noqa: D102
        return self._parent_component

    @property
    @protect_grpc
    @ensure_design_is_active
    def faces(self) -> list[Face]:  # noqa: D102
        self._template._grpc_client.log.debug(f"Retrieving faces for body {self.id} from server.")
        grpc_faces = self._template._bodies_stub.GetFaces(self._grpc_id)
        return [
            Face(
                grpc_face.id,
                SurfaceType(grpc_face.surface_type),
                self,
                self._template._grpc_client,
                grpc_face.is_reversed,
            )
            for grpc_face in grpc_faces.faces
        ]

    @property
    @protect_grpc
    @ensure_design_is_active
    def edges(self) -> list[Edge]:  # noqa: D102
        self._template._grpc_client.log.debug(f"Retrieving edges for body {self.id} from server.")
        grpc_edges = self._template._bodies_stub.GetEdges(self._grpc_id)
        return [
            Edge(
                grpc_edge.id,
                CurveType(grpc_edge.curve_type),
                self,
                self._template._grpc_client,
                grpc_edge.is_reversed,
            )
            for grpc_edge in grpc_edges.edges
        ]

    @property
    def _is_alive(self) -> bool:  # noqa: D102
        return self._template.is_alive

    @_is_alive.setter
    def _is_alive(self, value: bool):  # noqa: D102
        self._template._is_alive = value

    @property
    def is_alive(self) -> bool:  # noqa: D102
        return self._is_alive

    @property
    def is_surface(self) -> bool:  # noqa: D102
        return self._template.is_surface

    @property
    def _surface_thickness(self) -> Quantity | None:  # noqa: D102
        return self._template.surface_thickness

    @_surface_thickness.setter
    def _surface_thickness(self, value):  # noqa: D102
        self._template._surface_thickness = value

    @property
    def surface_thickness(self) -> Quantity | None:  # noqa: D102
        return self._surface_thickness

    @property
    def _surface_offset(self) -> Union["MidSurfaceOffsetType", None]:  # noqa: D102
        return self._template._surface_offset

    @_surface_offset.setter
    def _surface_offset(self, value: "MidSurfaceOffsetType"):  # noqa: D102
        self._template._surface_offset = value

    @property
    def surface_offset(self) -> Union["MidSurfaceOffsetType", None]:  # noqa: D102
        return self._surface_offset

    @property
    @ensure_design_is_active
    def volume(self) -> Quantity:  # noqa: D102
        return self._template.volume

    @property
    @ensure_design_is_active
    def material(self) -> Material:  # noqa: D102
        return self._template.material

    @material.setter
    def material(self, value: Material):  # noqa: D102
        self._template.material = value

    @property
    def bounding_box(self) -> BoundingBox:  # noqa: D102
        return self._template.bounding_box

    @ensure_design_is_active
    def assign_material(self, material: Material) -> None:  # noqa: D102
        self._template.assign_material(material)

    @ensure_design_is_active
    def get_assigned_material(self) -> Material:  # noqa: D102
        return self._template.get_assigned_material()

    @ensure_design_is_active
    def add_midsurface_thickness(self, thickness: Quantity) -> None:  # noqa: D102
        self._template.add_midsurface_thickness(thickness)

    @ensure_design_is_active
    def add_midsurface_offset(  # noqa: D102
        self, offset: "MidSurfaceOffsetType"
    ) -> None:
        self._template.add_midsurface_offset(offset)

    @protect_grpc
    @ensure_design_is_active
    def imprint_curves(  # noqa: D102
        self, faces: list[Face], sketch: Sketch = None, trimmed_curves: list[TrimmedCurve] = None
    ) -> tuple[list[Edge], list[Face]]:
        """Imprint curves onto the specified faces using a sketch or edges.

        Parameters
        ----------
        faces : list[Face]
            The list of faces to imprint the curves onto.
        sketch : Sketch, optional
            The sketch containing curves to imprint.
        trimmed_curves : list[TrimmedCurve], optional
            The list of curves to be imprinted. If sketch is provided, this parameter is ignored.

        Returns
        -------
        tuple[list[Edge], list[Face]]
            A tuple containing the list of new edges and faces created by the imprint operation.
        """
        if sketch is None and self._template._grpc_client.backend_version < (25, 2, 0):
            raise ValueError(
                "A sketch must be provided for imprinting when using API versions below 25.2.0."
            )

        if sketch is None and trimmed_curves is None:
            raise ValueError("Either a sketch or edges must be provided for imprinting.")

        # Verify that each of the faces provided are part of this body
        body_faces = self.faces
        for provided_face in faces:
            if not any(provided_face.id == body_face.id for body_face in body_faces):
                raise ValueError(f"Face with ID {provided_face.id} is not part of this body.")

        self._template._grpc_client.log.debug(
            f"Imprinting curves on {self.id} for faces {[face.id for face in faces]}."
        )

        curves = None
        grpc_trimmed_curves = None

        if sketch:
            curves = sketch_shapes_to_grpc_geometries(sketch._plane, sketch.edges, sketch.faces)

        if trimmed_curves:
            grpc_trimmed_curves = [
                trimmed_curve_to_grpc_trimmed_curve(curve) for curve in trimmed_curves
            ]

        imprint_response = self._template._commands_stub.ImprintCurves(
            ImprintCurvesRequest(
                body=self._id,
                curves=curves,
                faces=[face._id for face in faces],
                plane=plane_to_grpc_plane(sketch.plane) if sketch else None,
                trimmed_curves=grpc_trimmed_curves,
            )
        )

        new_edges = [
            Edge(
                grpc_edge.id,
                CurveType(grpc_edge.curve_type),
                self,
                self._template._grpc_client,
            )
            for grpc_edge in imprint_response.edges
        ]

        new_faces = [
            Face(
                grpc_face.id,
                SurfaceType(grpc_face.surface_type),
                self,
                self._template._grpc_client,
            )
            for grpc_face in imprint_response.faces
        ]

        return (new_edges, new_faces)

    @protect_grpc
    @ensure_design_is_active
    def project_curves(  # noqa: D102
        self,
        direction: UnitVector3D,
        sketch: Sketch,
        closest_face: bool,
        only_one_curve: bool = False,
    ) -> list[Face]:
        curves = sketch_shapes_to_grpc_geometries(
            sketch._plane, sketch.edges, sketch.faces, only_one_curve=only_one_curve
        )
        self._template._grpc_client.log.debug(f"Projecting provided curves on {self.id}.")

        project_response = self._template._commands_stub.ProjectCurves(
            ProjectCurvesRequest(
                body=self._id,
                curves=curves,
                direction=unit_vector_to_grpc_direction(direction),
                closest_face=closest_face,
                plane=plane_to_grpc_plane(sketch.plane),
            )
        )

        projected_faces = [
            Face(
                grpc_face.id,
                SurfaceType(grpc_face.surface_type),
                self,
                self._template._grpc_client,
            )
            for grpc_face in project_response.faces
        ]

        return projected_faces

    @check_input_types
    @protect_grpc
    @ensure_design_is_active
    def imprint_projected_curves(  # noqa: D102
        self,
        direction: UnitVector3D,
        sketch: Sketch,
        closest_face: bool,
        only_one_curve: bool = False,
    ) -> list[Face]:
        curves = sketch_shapes_to_grpc_geometries(
            sketch._plane, sketch.edges, sketch.faces, only_one_curve=only_one_curve
        )
        self._template._grpc_client.log.debug(f"Projecting provided curves on {self.id}.")

        response = self._template._commands_stub.ImprintProjectedCurves(
            ProjectCurvesRequest(
                body=self._id,
                curves=curves,
                direction=unit_vector_to_grpc_direction(direction),
                closest_face=closest_face,
                plane=plane_to_grpc_plane(sketch.plane),
            )
        )

        imprinted_faces = [
            Face(
                grpc_face.id,
                SurfaceType(grpc_face.surface_type),
                self,
                self._template._grpc_client,
            )
            for grpc_face in response.faces
        ]

        return imprinted_faces

    @ensure_design_is_active
    def set_name(self, name: str) -> None:  # noqa: D102
        return self._template.set_name(name)

    @ensure_design_is_active
    def set_fill_style(self, fill_style: FillStyle) -> None:  # noqa: D102
        return self._template.set_fill_style(fill_style)

    @ensure_design_is_active
    def set_suppressed(self, suppressed: bool) -> None:  # noqa: D102
        return self._template.set_suppressed(suppressed)

    @ensure_design_is_active
    def set_color(self, color: str | tuple[float, float, float]) -> None:  # noqa: D102
        return self._template.set_color(color)

    @ensure_design_is_active
    def translate(  # noqa: D102
        self, direction: UnitVector3D, distance: Quantity | Distance | Real
    ) -> None:
        return self._template.translate(direction, distance)

    @ensure_design_is_active
    def rotate(  # noqa: D102
        self,
        axis_origin: Point3D,
        axis_direction: UnitVector3D,
        angle: Quantity | Angle | Real,
    ) -> None:
        return self._template.rotate(axis_origin, axis_direction, angle)

    @ensure_design_is_active
    def scale(self, value: Real) -> None:  # noqa: D102
        return self._template.scale(value)

    @ensure_design_is_active
    def map(self, frame: Frame) -> None:  # noqa: D102
        return self._template.map(frame)

    @ensure_design_is_active
    def mirror(self, plane: Plane) -> None:  # noqa: D102
        return self._template.mirror(plane)

    @ensure_design_is_active
    def get_collision(self, body: "Body") -> CollisionType:  # noqa: D102
        return self._template.get_collision(body)

    @ensure_design_is_active
    def copy(self, parent: "Component", name: str = None) -> "Body":  # noqa: D102
        return self._template.copy(parent, name)

    @ensure_design_is_active
    def tessellate(  # noqa: D102
        self, merge: bool = False, tess_options: TessellationOptions | None = None
    ) -> Union["PolyData", "MultiBlock"]:
        return self._template.tessellate(
            merge, self.parent_component.get_world_transform(), tess_options
        )

    @ensure_design_is_active
    def shell_body(self, offset: Real) -> bool:  # noqa: D102
        return self._template.shell_body(offset)

    @ensure_design_is_active
    def remove_faces(self, selection: Face | Iterable[Face], offset: Real) -> bool:  # noqa: D102
        return self._template.remove_faces(selection, offset)

    @graphics_required
    def plot(  # noqa: D102
        self,
        merge: bool = True,
        screenshot: str | None = None,
        use_trame: bool | None = None,
        use_service_colors: bool | None = None,
        **plotting_options: dict | None,
    ) -> None:
        # lazy import here to improve initial module load time
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

        # Add to plotting options as well... to be used by the plotter if necessary
        plotting_options["merge_bodies"] = merge

        # In case that service colors are requested, merge will be ignored.
        # An info message will be issued to the user.
        if use_service_colors and merge:
            self._template._grpc_client.log.info(
                "Ignoring 'merge' option since 'use_service_colors' is set to True."
            )
            plotting_options["merge_bodies"] = False

        mesh_object = (
            self if use_service_colors else MeshObjectPlot(self, self.tessellate(merge=merge))
        )
        pl = GeometryPlotter(use_trame=use_trame, use_service_colors=use_service_colors)
        pl.plot(mesh_object, **plotting_options)
        pl.show(screenshot=screenshot, **plotting_options)

    def intersect(self, other: Union["Body", Iterable["Body"]], keep_other: bool = False) -> None:  # noqa: D102
        if self._template._grpc_client.backend_version < __TEMPORARY_BOOL_OPS_FIX__:
            self.__generic_boolean_op(other, keep_other, "intersect", "bodies do not intersect")
        else:
            self.__generic_boolean_command(
                other, keep_other, "intersect", "bodies do not intersect"
            )

    def subtract(self, other: Union["Body", Iterable["Body"]], keep_other: bool = False) -> None:  # noqa: D102
        if self._template._grpc_client.backend_version < __TEMPORARY_BOOL_OPS_FIX__:
            self.__generic_boolean_op(other, keep_other, "subtract", "empty (complete) subtraction")
        else:
            self.__generic_boolean_command(
                other, keep_other, "subtract", "empty (complete) subtraction"
            )

    def unite(self, other: Union["Body", Iterable["Body"]], keep_other: bool = False) -> None:  # noqa: D102
        if self._template._grpc_client.backend_version < __TEMPORARY_BOOL_OPS_FIX__:
            self.__generic_boolean_op(other, keep_other, "unite", "union operation failed")
        else:
            self.__generic_boolean_command(other, False, "unite", "union operation failed")

    @protect_grpc
    @reset_tessellation_cache
    @ensure_design_is_active
    @check_input_types
    def __generic_boolean_command(
        self,
        other: Union["Body", Iterable["Body"]],
        keep_other: bool,
        type_bool_op: str,
        err_bool_op: str,
    ) -> None:
        parent_design = get_design_from_body(self)
        other_bodies = other if isinstance(other, Iterable) else [other]
        if type_bool_op == "intersect":
            body_ids = [body._grpc_id for body in other_bodies]
            target_ids = [self._grpc_id]
            request = CombineIntersectBodiesRequest(
                target_selection=target_ids,
                tool_selection=body_ids,
                subtract_from_target=False,
                keep_cutter=keep_other,
            )
            response = self._template._commands_stub.CombineIntersectBodies(request)
        elif type_bool_op == "subtract":
            body_ids = [body._grpc_id for body in other_bodies]
            target_ids = [self._grpc_id]
            request = CombineIntersectBodiesRequest(
                target_selection=target_ids,
                tool_selection=body_ids,
                subtract_from_target=True,
                keep_cutter=keep_other,
            )
            response = self._template._commands_stub.CombineIntersectBodies(request)
        elif type_bool_op == "unite":
            bodies = [self]
            bodies.extend(other_bodies)
            body_ids = [body._grpc_id for body in bodies]
            request = CombineMergeBodiesRequest(target_selection=body_ids)
            response = self._template._commands_stub.CombineMergeBodies(request)
        else:
            raise ValueError("Unknown operation requested")
        if not response.success:
            raise ValueError(
                f"Operation of type '{type_bool_op}' failed: {err_bool_op}.\n"
                f"Involving bodies:{self}, {other_bodies}"
            )

        if not keep_other:
            for b in other_bodies:
                b.parent_component.delete_body(b)

        parent_design._update_design_inplace()

    @protect_grpc
    @reset_tessellation_cache
    @ensure_design_is_active
    @check_input_types
    def __generic_boolean_op(
        self,
        other: Union["Body", Iterable["Body"]],
        keep_other: bool,
        type_bool_op: str,
        err_bool_op: str,
    ) -> None:
        grpc_other = other if isinstance(other, Iterable) else [other]
        if keep_other:
            # Make a copy of the other body to keep it...
            # stored temporarily in the parent component - since it will be deleted
            grpc_other = [b.copy(self.parent_component, f"BoolOpCopy_{b.name}") for b in grpc_other]

        try:
            response = self._template._bodies_stub.Boolean(
                BooleanRequest(
                    body1=self.id,
                    tool_bodies=[b.id for b in grpc_other],
                    method=type_bool_op,
                )
            ).empty_result
        except Exception:
            # TODO: to be deleted - old versions did not have "tool_bodies" in the request
            # This is a temporary fix to support old versions of the server - should be deleted
            # once the server is no longer supported.
            # https://github.com/ansys/pyansys-geometry/issues/1319
            if not isinstance(other, Iterable):
                response = self._template._bodies_stub.Boolean(
                    BooleanRequest(body1=self.id, body2=other.id, method=type_bool_op)
                ).empty_result
            else:
                all_response = []
                for body2 in other:
                    response = self._template._bodies_stub.Boolean(
                        BooleanRequest(body1=self.id, body2=body2.id, method=type_bool_op)
                    ).empty_result
                    all_response.append(response)

                if all_response.count(1) > 0:
                    response = 1

        if response == 1:
            raise ValueError(
                f"Boolean operation of type '{type_bool_op}' failed: {err_bool_op}.\n"
                f"Involving bodies:{self}, {grpc_other}"
            )

        for b in grpc_other:
            b.parent_component.delete_body(b)

    def __repr__(self) -> str:
        """Represent the ``Body`` as a string."""
        lines = [f"ansys.geometry.core.designer.Body {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Exists               : {self.is_alive}")
        lines.append(f"  Parent component     : {self._parent_component.name}")
        lines.append(f"  MasterBody           : {self._template.id}")
        lines.append(f"  Surface body         : {self.is_surface}")
        if self.is_surface:
            lines.append(f"  Surface thickness    : {self.surface_thickness}")
            lines.append(f"  Surface offset       : {self.surface_offset}")
        lines.append(f"  Color                : {self.color}")

        nl = "\n"
        return f"{nl}{nl.join(lines)}{nl}"
