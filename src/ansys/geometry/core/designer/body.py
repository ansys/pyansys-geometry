# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
from functools import wraps
from typing import TYPE_CHECKING, Union

from beartype import beartype as check_input_types
import matplotlib.colors as mcolors
from pint import Quantity

import ansys.geometry.core as pyansys_geom
from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.designer.edge import CurveType, Edge
from ansys.geometry.core.designer.face import Face, SurfaceType
from ansys.geometry.core.designer.vertex import Vertex
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
    from ansys.geometry.core.designer.selection import NamedSelection

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
    def name(self) -> str:
        """Get the name of the body."""
        return

    @abstractmethod
    def set_name(self, str) -> None:
        """Set the name of the body.

        Warnings
        --------
        This method is only available starting on Ansys release 25R1.
        """
        return

    @abstractmethod
    def fill_style(self) -> FillStyle:
        """Get the fill style of the body."""
        return

    @abstractmethod
    def set_fill_style(self, fill_style: FillStyle) -> None:
        """Set the fill style of the body.

        Warnings
        --------
        This method is only available starting on Ansys release 25R1.
        """
        return

    @abstractmethod
    def is_suppressed(self) -> bool:
        """Get the body suppression state.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        return

    @abstractmethod
    def set_suppressed(self, suppressed: bool) -> None:
        """Set the body suppression state.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
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
    def set_color(
        self, color: str | tuple[float, float, float] | tuple[float, float, float, float]
    ) -> None:
        """Set the color of the body.

        Parameters
        ----------
        color : str | tuple[float, float, float] | tuple[float, float, float, float]
            Color to set the body to. This can be a string representing a color name
            or a tuple of RGB values in the range [0, 1] (RGBA) or [0, 255] (pure RGB).

        Warnings
        --------
        This method is only available starting on Ansys release 25R1.
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
    def vertices(self) -> list[Vertex]:
        """Get a list of all vertices within the body.

        Returns
        -------
        list[Vertex]
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

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
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
    def remove_assigned_material(self) -> None:
        """Remove the material assigned to the body."""
        return

    @abstractmethod
    def add_midsurface_thickness(self, thickness: Distance | Quantity | Real) -> None:
        """Add a mid-surface thickness to a surface body.

        Parameters
        ----------
        thickness : Distance | Quantity | Real
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

        Warnings
        --------
        This method is only available starting on Ansys release 24R2.
        """
        return

    @abstractmethod
    def scale(self, value: Real) -> None:
        """Scale the geometry body by the given value.

        The calling object is directly modified when this method is called.
        Thus, it is important to make copies if needed.

        Parameters
        ----------
        value: Real
            Value to scale the body by.

        Warnings
        --------
        This method is only available starting on Ansys release 24R2.
        """
        return

    @abstractmethod
    def map(self, frame: Frame) -> None:
        """Map the geometry body to the new specified frame.

        The calling object is directly modified when this method is called.
        Thus, it is important to make copies if needed.

        Parameters
        ----------
        frame: Frame
            Structure defining the orientation of the body.

        Warnings
        --------
        This method is only available starting on Ansys release 24R2.
        """
        return

    @abstractmethod
    def mirror(self, plane: Plane) -> None:
        """Mirror the geometry body across the specified plane.

        The calling object is directly modified when this method is called.
        Thus, it is important to make copies if needed.

        Parameters
        ----------
        plane: Plane
            Represents the mirror.

        Warnings
        --------
        This method is only available starting on Ansys release 24R2.
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

        Warnings
        --------
        This method is only available starting on Ansys release 24R2.
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
    def get_named_selections(self) -> list["NamedSelection"]:
        """Get the named selections associated with the body.

        Returns
        -------
        list[NamedSelection]
            List of named selections associated with the body.
        """
        return

    @abstractmethod
    def get_raw_tessellation(
        self,
        transform: Matrix44 = IDENTITY_MATRIX44,
        tess_options: TessellationOptions | None = None,
        reset_cache: bool = False,
        include_faces: bool = True,
        include_edges: bool = False,
    ) -> dict:
        """Tessellate the body and return the raw tessellation data.

        Parameters
        ----------
        transform : Matrix44, default: IDENTITY_MATRIX44
            A transformation matrix to apply to the tessellation.
        tess_options : TessellationOptions | None, default: None
            A set of options to determine the tessellation quality.
        reset_cache : bool, default: False
            Whether to reset the tessellation cache and re-request the tessellation
            from the server.
        include_faces : bool, default: True
            Whether to include face tessellation data in the output.
        include_edges : bool, default: False
            Whether to include edge tessellation data in the output.

        Returns
        -------
        dict
            Dictionary with face and edge IDs as keys and face and edge tessellation data as values.
        """

    @abstractmethod
    def tessellate(
        self,
        merge: bool = False,
        tess_options: TessellationOptions | None = None,
        reset_cache: bool = False,
        include_faces: bool = True,
        include_edges: bool = False,
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
        reset_cache : bool, default: False
            Whether to reset the tessellation cache and re-request the tessellation
            from the server.
        include_faces : bool, default: True
            Whether to include face tessellation data in the output.
        include_edges : bool, default: False
            Whether to include edge tessellation data in the output.

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
    def shell_body(self, offset: Distance | Quantity | Real) -> bool:
        """Shell the body to the thickness specified.

        Parameters
        ----------
        offset : Distance | Quantity | Real
            Shell thickness.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        return

    @abstractmethod
    def remove_faces(
        self, selection: Face | Iterable[Face], offset: Distance | Quantity | Real
    ) -> bool:
        """Shell by removing a given set of faces.

        Parameters
        ----------
        selection : Face | Iterable[Face]
            Face or faces to be removed.
        offset : Distance | Quantity | Real
            Shell thickness.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
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

    def combine_merge(self, other: Union["Body", list["Body"]]) -> None:
        """Combine this body with another body or bodies, merging them into a single body.

        Parameters
        ----------
        other : Union[Body, list[Body]]
            The body or list of bodies to combine with this body.

        Notes
        -----
        The ``self`` parameter is directly modified, and the ``other`` bodies are consumed.
        """
        return

    def _combine_subtract(
        self,
        other: Union["Body", Iterable["Body"]],
        keep_other: bool = False,
        transfer_named_selections=True,
    ) -> None:
        """Subtract bodies from this body.

        Parameters
        ----------
        other : Union[Body, list[Body]]
            The body or list of bodies to combine with this body.
        keep_other : bool, default: False
            Whether to retain the other bodies or not.

        Warnings
        --------
        This is a specialized boolean operation that has the ability to transfer named
        selections. It may behave differently than the encouraged ``subtract()``.

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
        self._tessellation = None
        self._raw_tessellation = None
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
            self._raw_tessellation = None
            return func(self, *args, **kwargs)

        return wrapper

    @property
    def id(self) -> str:  # noqa: D102
        return self._id

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
    @min_backend_version(25, 2, 0)
    def is_suppressed(self) -> bool:  # noqa: D102
        response = self._grpc_client.services.bodies.is_suppressed(id=self.id)
        return response.get("result")

    @is_suppressed.setter
    def is_suppressed(self, value: bool):  # noqa: D102
        self.set_suppressed(value)

    @property
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
                color = self._grpc_client.services.bodies.get_color(id=self.id).get("color")
                if color:
                    self._color = mcolors.to_hex(color, keep_alpha=True)

        return self._color

    @property
    def opacity(self) -> float:  # noqa: D102
        opacity_hex = self.color[7:]
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
    def faces(self) -> list[Face]:  # noqa: D102
        return self._get_faces_from_id(self)

    def _get_faces_from_id(self, body: Union["Body", "MasterBody"]) -> list[Face]:
        """Retrieve faces from a body ID."""
        self._grpc_client.log.debug(f"Retrieving faces for body {body.id} from server.")
        response = self._grpc_client.services.bodies.get_faces(id=body.id)
        return [
            Face(
                face_resp.get("id"),
                SurfaceType(face_resp.get("surface_type")),
                body,
                self._grpc_client,
                face_resp.get("is_reversed"),
            )
            for face_resp in response.get("faces")
        ]

    @property
    def edges(self) -> list[Edge]:  # noqa: D102
        return self._get_edges_from_id(self)

    def _get_edges_from_id(self, body: Union["Body", "MasterBody"]) -> list[Edge]:
        """Retrieve edges from a body ID."""
        self._grpc_client.log.debug(f"Retrieving edges for body {body.id} from server.")
        response = self._grpc_client.services.bodies.get_edges(id=body.id)
        return [
            Edge(
                edge_resp.get("id"),
                CurveType(edge_resp.get("curve_type")),
                body,
                self._grpc_client,
                edge_resp.get("is_reversed"),
            )
            for edge_resp in response.get("edges")
        ]

    @property
    @min_backend_version(26, 1, 0)
    def vertices(self) -> list[Vertex]:  # noqa: D102
        return self._get_vertices_from_id(self)

    def _get_vertices_from_id(self, body: Union["Body", "MasterBody"]) -> list[Vertex]:
        """Retrieve vertices from a body ID."""
        self._grpc_client.log.debug(f"Retrieving vertices for body {body.id} from server.")
        response = self._grpc_client.services.bodies.get_vertices(id=body.id)

        return [
            Vertex(
                vertex_resp.get("id"),
                vertex_resp.get("position"),
                body,
            )
            for vertex_resp in response.get("vertices")
        ]

    @property
    def is_alive(self) -> bool:  # noqa: D102
        return self._is_alive

    @property
    def volume(self) -> Quantity:  # noqa: D102
        if self.is_surface:
            self._grpc_client.log.debug("Dealing with planar surface. Returning 0 as the volume.")
            return Quantity(0, DEFAULT_UNITS.SERVER_VOLUME)
        else:
            self._grpc_client.log.debug(f"Retrieving volume for body {self.id} from server.")
            response = self._grpc_client.services.bodies.get_volume(id=self.id)
            return response.get("volume")

    @property
    def material(self) -> Material:  # noqa: D102
        return self.get_assigned_material()

    @material.setter
    def material(self, value: Material):  # noqa: D102
        self.assign_material(value)

    @property
    @min_backend_version(25, 2, 0)
    def bounding_box(self) -> BoundingBox:  # noqa: D102
        self._grpc_client.log.debug(f"Retrieving bounding box for body {self.id} from server.")
        response = self._grpc_client.services.bodies.get_bounding_box(id=self.id)
        return BoundingBox(
            min_corner=response.get("min"),
            max_corner=response.get("max"),
            center=response.get("center"),
        )

    @check_input_types
    def assign_material(self, material: Material) -> None:  # noqa: D102
        self._grpc_client.log.debug(f"Assigning body {self.id} material {material.name}.")
        self._grpc_client.services.bodies.set_assigned_material(id=self.id, material=material)

    def get_assigned_material(self) -> Material:  # noqa: D102
        self._grpc_client.log.debug(f"Retrieving assigned material for body {self.id}.")
        response = self._grpc_client.services.bodies.get_assigned_material(id=self.id)
        return response.get("material")

    @min_backend_version(26, 1, 0)
    def remove_assigned_material(self) -> None:  # noqa: D102
        self._grpc_client.log.debug(f"Removing assigned material for body {self.id}.")
        self._grpc_client.services.bodies.remove_assigned_material(ids=[self.id])

    @check_input_types
    def add_midsurface_thickness(self, thickness: Distance | Quantity | Real) -> None:  # noqa: D102
        thickness = thickness if isinstance(thickness, Distance) else Distance(thickness)

        if self.is_surface:
            self._grpc_client.services.bodies.assign_midsurface_thickness(
                ids=[self.id], thickness=thickness
            )
            self._surface_thickness = thickness.value
        else:
            self._grpc_client.log.warning(
                f"Body {self.name} cannot be assigned a mid-surface thickness because it is not a surface. Ignoring request."  # noqa : E501
            )

    @check_input_types
    def add_midsurface_offset(self, offset: MidSurfaceOffsetType) -> None:  # noqa: D102
        if self.is_surface:
            self._grpc_client.services.bodies.assign_midsurface_offset(
                ids=[self.id], offset_type=offset
            )
            self._surface_offset = offset
        else:
            self._grpc_client.log.warning(
                f"Body {self.name} cannot be assigned a mid-surface offset because it is not a surface. Ignoring request."  # noqa : E501
            )

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

    @check_input_types
    @reset_tessellation_cache
    def translate(  # noqa: D102
        self, direction: UnitVector3D, distance: Quantity | Distance | Real
    ) -> None:
        distance = distance if isinstance(distance, Distance) else Distance(distance)
        self._grpc_client.log.debug(f"Translating body {self.id}.")
        self._grpc_client.services.bodies.translate(
            ids=[self.id], direction=direction, distance=distance
        )

    @check_input_types
    @min_backend_version(25, 1, 0)
    def set_name(  # noqa: D102
        self, name: str
    ) -> None:
        self._grpc_client.log.debug(f"Renaming body {self.id} from '{self.name}' to '{name}'.")
        self._grpc_client.services.bodies.set_name(id=self.id, name=name)
        self._name = name

    @check_input_types
    @min_backend_version(25, 1, 0)
    def set_fill_style(  # noqa: D102
        self, fill_style: FillStyle
    ) -> None:
        self._grpc_client.log.debug(f"Setting body fill style {self.id}.")
        self._grpc_client.services.bodies.set_fill_style(id=self.id, fill_style=fill_style)
        self._fill_style = fill_style

    @check_input_types
    @min_backend_version(25, 2, 0)
    def set_suppressed(  # noqa: D102
        self, suppressed: bool
    ) -> None:
        self._grpc_client.log.debug(f"Setting body {self.id}, as suppressed: {suppressed}.")
        self._grpc_client.services.bodies.set_suppressed(bodies=[self.id], is_suppressed=suppressed)

    @check_input_types
    @min_backend_version(25, 1, 0)
    def set_color(  # noqa: D102
        self, color: str | tuple[float, float, float] | tuple[float, float, float, float]
    ) -> None:
        self._grpc_client.log.debug(f"Setting body color of {self.id} to {color}.")
        color = convert_color_to_hex(color)
        self._grpc_client.services.bodies.set_color(id=self.id, color=color)
        self._color = color

    @check_input_types
    @min_backend_version(25, 2, 0)
    def set_opacity(self, opacity: float) -> None:
        """Set the opacity of the body.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        self._grpc_client.log.debug(f"Setting body opacity of {self.id} to {opacity}.")
        opacity = convert_opacity_to_hex(opacity)
        new_color = self.color[0:7] + opacity
        self.set_color(new_color)

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
        self._grpc_client.log.debug(f"Rotating body {self.id}.")
        self._grpc_client.services.bodies.rotate(
            id=self.id, axis_origin=axis_origin, axis_direction=axis_direction, angle=angle
        )

    @check_input_types
    @reset_tessellation_cache
    @min_backend_version(24, 2, 0)
    def scale(self, value: Real) -> None:  # noqa: D102
        self._grpc_client.log.debug(f"Scaling body {self.id}.")
        self._grpc_client.services.bodies.scale(id=self.id, value=value)

    @check_input_types
    @reset_tessellation_cache
    @min_backend_version(24, 2, 0)
    def map(self, frame: Frame) -> None:  # noqa: D102
        self._grpc_client.log.debug(f"Mapping body {self.id}.")
        self._grpc_client.services.bodies.map(id=self.id, frame=frame)

    @check_input_types
    @reset_tessellation_cache
    @min_backend_version(24, 2, 0)
    def mirror(self, plane: Plane) -> None:  # noqa: D102
        self._grpc_client.log.debug(f"Mirroring body {self.id}.")
        self._grpc_client.services.bodies.mirror(id=self.id, plane=plane)

    @min_backend_version(24, 2, 0)
    def get_collision(self, body: "Body") -> CollisionType:  # noqa: D102
        self._grpc_client.log.debug(f"Get collision between body {self.id} and body {body.id}.")
        response = self._grpc_client.services.bodies.get_collision(id=self.id, other_id=body.id)
        return CollisionType(response.get("collision_type"))

    def copy(self, parent: "Component", name: str = None) -> "Body":  # noqa: D102
        raise NotImplementedError(
            "Copy method is not implemented on the MasterBody. Call this method on a body instead."
        )

    def get_named_selections(self) -> list["NamedSelection"]:  # noqa: D102
        raise NotImplementedError(
            """
            get_named_selections is not implemented at the MasterBody level.
            Instead, call this method on a body.
            """
        )

    @min_backend_version(26, 1, 0)
    def get_raw_tessellation(  # noqa: D102
        self,
        tess_options: TessellationOptions | None = None,
        reset_cache: bool = False,
        include_faces: bool = True,
        include_edges: bool = False,
    ) -> dict:
        if not self.is_alive:
            return {}

        self._grpc_client.log.debug(f"Requesting tessellation for body {self.id}.")

        # cache tessellation
        if not self._raw_tessellation or reset_cache:
            response = self._grpc_client.services.bodies.get_full_tessellation(
                id=self.id,
                options=tess_options,
                raw_data=True,
                include_faces=include_faces,
                include_edges=include_edges,
            )

            self._raw_tessellation = response.get("tessellation")

        return self._raw_tessellation

    @graphics_required
    def tessellate(  # noqa: D102
        self,
        merge: bool = False,
        transform: Matrix44 = IDENTITY_MATRIX44,
        tess_options: TessellationOptions | None = None,
        reset_cache: bool = False,
        include_faces: bool = True,
        include_edges: bool = False,
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
        if include_edges and self._grpc_client.backend_version < (26, 1, 0):
            self._grpc_client.log.warning(
                "Edge tessellation is not supported by server"
                f" version {self._grpc_client.backend_version}. Ignoring request."
            )
            include_edges = False

        self._grpc_client.log.debug(f"Requesting tessellation for body {self.id}.")

        # cache tessellation
        if not self._tessellation or reset_cache:
            if self._grpc_client.backend_version > (25, 2, 0):
                response = self._grpc_client.services.bodies.get_full_tessellation(
                    id=self.id,
                    options=tess_options,
                    raw_data=False,
                    include_faces=include_faces,
                    include_edges=include_edges,
                )
            elif tess_options is not None:
                response = self._grpc_client.services.bodies.get_tesellation_with_options(
                    id=self.id, options=tess_options, raw_data=False
                )
            else:
                response = self._grpc_client.services.bodies.get_tesellation(
                    id=self.id, backend_version=self._grpc_client.backend_version, raw_data=False
                )

            self._tessellation = response.get("tessellation")

        if transform == IDENTITY_MATRIX44:
            pdata = list(self._tessellation.values())
        else:
            pdata = [
                tess.transform(transform, inplace=False) for tess in self._tessellation.values()
            ]
        comp = pv.MultiBlock(pdata)

        if merge:
            ugrid = comp.combine()
            return pv.PolyData(var_inp=ugrid.points, faces=ugrid.cells)
        else:
            return comp

    @reset_tessellation_cache
    @check_input_types
    @min_backend_version(25, 2, 0)
    def shell_body(self, offset: Distance | Quantity | Real) -> bool:  # noqa: D102
        self._grpc_client.log.debug(f"Shelling body {self.id} to offset {offset}.")

        offset = offset if isinstance(offset, Distance) else Distance(offset)
        result = self._grpc_client.services.bodies.shell(
            id=self.id,
            offset=offset,
        )

        if result.get("success") is False:
            self._grpc_client.log.warning(f"Failed to shell body {self.id}.")

        return result.get("success")

    @reset_tessellation_cache
    @check_input_types
    @min_backend_version(25, 2, 0)
    def remove_faces(  # noqa: D102
        self, selection: Face | Iterable[Face], offset: Distance | Quantity | Real
    ) -> bool:
        selection: list[Face] = selection if isinstance(selection, Iterable) else [selection]
        check_type_all_elements_in_iterable(selection, Face)

        # check if faces belong to this body
        for face in selection:
            if face.body.id != self.id:
                raise ValueError(f"Face {face.id} does not belong to body {self.id}.")

        self._grpc_client.log.debug(f"Removing faces to shell body {self.id}.")

        offset = offset if isinstance(offset, Distance) else Distance(offset)
        result = self._grpc_client.services.bodies.remove_faces(
            face_ids=[face.id for face in selection],
            offset=offset,
        )

        if result.get("success") is False:
            self._grpc_client.log.warning(f"Failed to remove faces from body {self.id}.")

        return result.get("success")

    @min_backend_version(25, 2, 0)
    @check_input_types
    def combine_merge(self, other: Union["Body", list["Body"]]) -> None:  # noqa: D102
        other = other if isinstance(other, list) else [other]
        check_type_all_elements_in_iterable(other, Body)

        self._grpc_client.log.debug(f"Combining and merging to body {self.id}.")
        self._grpc_client.services.bodies.combine_merge(
            body_ids=[self.id] + [body.id for body in other]
        )

    def _combine_subtract(  # noqa: D102
        self,
        other: Union["Body", Iterable["Body"]],
        keep_other: bool = False,
        transfer_named_selections=True,
    ) -> None:
        raise NotImplementedError(
            "MasterBody does not implement combine_subtract. Call this method on a body instead."
        )

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
        self._grpc_client = template._grpc_client

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
        self._template._raw_tessellation = None
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
            master_in_part._raw_tessellation = None

    @property
    def id(self) -> str:  # noqa: D102
        return self._id

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
    @ensure_design_is_active
    def faces(self) -> list[Face]:  # noqa: D102
        return self._template._get_faces_from_id(self)

    @property
    @ensure_design_is_active
    def edges(self) -> list[Edge]:  # noqa: D102
        return self._template._get_edges_from_id(self)

    @property
    @ensure_design_is_active
    def vertices(self) -> list[Vertex]:  # noqa: D102
        return self._template._get_vertices_from_id(self)

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
        self._template._grpc_client.log.debug(
            f"Retrieving bounding box for body {self.id} from server."
        )
        response = self._template._grpc_client.services.bodies.get_bounding_box(id=self.id)
        return BoundingBox(
            min_corner=response.get("min"),
            max_corner=response.get("max"),
            center=response.get("center"),
        )

    @ensure_design_is_active
    def assign_material(self, material: Material) -> None:  # noqa: D102
        self._template.assign_material(material)

    @ensure_design_is_active
    def get_assigned_material(self) -> Material:  # noqa: D102
        return self._template.get_assigned_material()

    @ensure_design_is_active
    def remove_assigned_material(self):  # noqa: D102
        self._template.remove_assigned_material()

    @ensure_design_is_active
    def add_midsurface_thickness(self, thickness: Quantity) -> None:  # noqa: D102
        self._template.add_midsurface_thickness(thickness)

    @ensure_design_is_active
    def add_midsurface_offset(  # noqa: D102
        self, offset: "MidSurfaceOffsetType"
    ) -> None:
        self._template.add_midsurface_offset(offset)

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

        imprint_response = self._template._grpc_client.services.bodies.imprint_curves(
            id=self.id,
            sketch=sketch,
            face_ids=[face.id for face in faces],
            tc=trimmed_curves,
        )

        new_edges = [
            Edge(
                edge.get("id"),
                CurveType(edge.get("curve_type")),
                self,
                self._template._grpc_client,
            )
            for edge in imprint_response.get("edges")
        ]

        new_faces = [
            Face(
                face.get("id"),
                SurfaceType(face.get("surface_type")),
                self,
                self._template._grpc_client,
            )
            for face in imprint_response.get("faces")
        ]

        return (new_edges, new_faces)

    @ensure_design_is_active
    def project_curves(  # noqa: D102
        self,
        direction: UnitVector3D,
        sketch: Sketch,
        closest_face: bool,
        only_one_curve: bool = False,
    ) -> list[Face]:
        self._template._grpc_client.log.debug(f"Projecting provided curves on {self.id}.")

        project_response = self._template._grpc_client.services.bodies.project_curves(
            id=self.id,
            sketch=sketch,
            direction=direction,
            closest_face=closest_face,
            only_one_curve=only_one_curve,
        )

        projected_faces = [
            Face(
                face.get("id"),
                SurfaceType(face.get("surface_type")),
                self,
                self._template._grpc_client,
            )
            for face in project_response.get("faces")
        ]

        return projected_faces

    @check_input_types
    @ensure_design_is_active
    def imprint_projected_curves(  # noqa: D102
        self,
        direction: UnitVector3D,
        sketch: Sketch,
        closest_face: bool,
        only_one_curve: bool = False,
    ) -> list[Face]:
        self._template._grpc_client.log.debug(f"Projecting provided curves on {self.id}.")

        response = self._template._grpc_client.services.bodies.imprint_projected_curves(
            id=self.id,
            direction=direction,
            sketch=sketch,
            closest_face=closest_face,
            only_one_curve=only_one_curve,
        )

        imprinted_faces = [
            Face(
                face.get("id"),
                SurfaceType(face.get("surface_type")),
                self,
                self._template._grpc_client,
            )
            for face in response.get("faces")
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
    def set_color(  # noqa: D102
        self, color: str | tuple[float, float, float] | tuple[float, float, float, float]
    ) -> None:
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
        from ansys.geometry.core.designer.component import Component

        # Check input types
        check_type(parent, Component)
        copy_name = self.name if name is None else name
        check_type(copy_name, str)

        self._template._grpc_client.log.debug(f"Copying body {self.id}.")
        response = self._template._grpc_client.services.bodies.copy(
            id=self.id, parent_id=parent.id, name=copy_name
        )

        # Assign the new body to its specified parent (and return the new body)
        tb = MasterBody(
            response.get("master_id"),
            copy_name,
            self._template._grpc_client,
            is_surface=self.is_surface,
        )
        parent._master_component.part.bodies.append(tb)
        parent._clear_cached_bodies()
        body_id = f"{parent.id}/{tb.id}" if parent.parent_component else tb.id
        return Body(body_id, response.get("name"), parent, tb)

    @ensure_design_is_active
    def get_named_selections(self) -> list["NamedSelection"]:  # noqa: D102
        included_ns = []
        for ns in get_design_from_body(self).named_selections:
            if any(body.id == self.id for body in ns.bodies):
                included_ns.append(ns)

        return included_ns

    @ensure_design_is_active
    def get_raw_tessellation(  # noqa: D102
        self,
        tess_options: TessellationOptions | None = None,
        reset_cache: bool = False,
        include_faces: bool = True,
        include_edges: bool = False,
    ) -> dict:
        raw_tess = self._template.get_raw_tessellation(
            tess_options,
            reset_cache,
            include_faces,
            include_edges,
        )

        # Transform the raw tessellation points for both faces/edges
        from copy import deepcopy

        import numpy as np

        transform = self.parent_component.get_world_transform()
        transformed_map = deepcopy(raw_tess)
        for id, tess in raw_tess.items():
            vertices = np.reshape(np.array(tess.get("vertices")), (-1, 3))
            homogenous_points = np.hstack([vertices, np.ones((vertices.shape[0], 1))])
            transformed_points = (transform @ homogenous_points.T).T[:, :3]
            transformed_map[id]["vertices"] = transformed_points.flatten().tolist()

        return transformed_map

    @ensure_design_is_active
    def tessellate(  # noqa: D102
        self,
        merge: bool = False,
        tess_options: TessellationOptions | None = None,
        reset_cache: bool = False,
        include_faces: bool = True,
        include_edges: bool = False,
    ) -> Union["PolyData", "MultiBlock"]:
        return self._template.tessellate(
            merge,
            self.parent_component.get_world_transform(),
            tess_options,
            reset_cache,
            include_faces,
            include_edges,
        )

    @ensure_design_is_active
    def shell_body(self, offset: Distance | Quantity | Real) -> bool:  # noqa: D102
        return self._template.shell_body(offset)

    @ensure_design_is_active
    def remove_faces(  # noqa: D102
        self,
        selection: Face | Iterable[Face],
        offset: Distance | Quantity | Real,
    ) -> bool:
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
        from ansys.tools.visualization_interface.types.mesh_object_plot import (
            MeshObjectPlot,
        )

        import ansys.geometry.core as pyansys_geometry
        from ansys.geometry.core.plotting import GeometryPlotter

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

    def combine_merge(self, other: Union["Body", list["Body"]]) -> None:  # noqa: D102
        self._template.combine_merge(other)

    @min_backend_version(26, 1, 0)
    def _combine_subtract(  # noqa: D102
        self,
        other: Union["Body", Iterable["Body"]],
        keep_other: bool = False,
        transfer_named_selections=True,
    ) -> None:
        parent_design = get_design_from_body(self)
        other = other if isinstance(other, Iterable) else [other]

        response = self._template._grpc_client.services.bodies.combine(
            target=self.id,
            other=[body.id for body in other],
            type_bool_op="subtract",
            keep_other=keep_other,
            transfer_named_selections=transfer_named_selections,
        )

        if not pyansys_geom.USE_TRACKER_TO_UPDATE_DESIGN:
            parent_design._update_design_inplace()
        else:
            parent_design._update_from_tracker(response["tracker_response"])

    @reset_tessellation_cache
    @ensure_design_is_active
    @check_input_types
    def __generic_boolean_command(
        self,
        other: Union["Body", Iterable["Body"]],
        keep_other: bool,
        method: str,
        err_msg: str,
    ) -> None:
        parent_design = get_design_from_body(self)
        other = other if isinstance(other, Iterable) else [other]

        response = self._template._grpc_client.services.bodies.combine(
            target=self.id,
            other=[body.id for body in other],
            type_bool_op=method,
            err_msg=err_msg,
            keep_other=keep_other,
            transfer_named_selections=False,
        )

        if not pyansys_geom.USE_TRACKER_TO_UPDATE_DESIGN:
            parent_design._update_design_inplace()
        else:
            parent_design._update_from_tracker(response["tracker_response"])

    @reset_tessellation_cache
    @ensure_design_is_active
    @check_input_types
    def __generic_boolean_op(
        self,
        other: Union["Body", Iterable["Body"]],
        keep_other: bool,
        method: str,
        err_msg: str,
    ) -> None:
        grpc_other = other if isinstance(other, Iterable) else [other]
        if not pyansys_geom.USE_TRACKER_TO_UPDATE_DESIGN:
            if keep_other:
                # Make a copy of the other body to keep it...
                # stored temporarily in the parent component - since it will be deleted
                grpc_other = [
                    b.copy(self.parent_component, f"BoolOpCopy_{b.name}") for b in grpc_other
                ]

        response = self._template._grpc_client.services.bodies.boolean(
            target=self.id,
            other=[other.id for other in grpc_other],
            method=method,
            err_msg=err_msg,
            keep_other=keep_other,
        )

        if not pyansys_geom.USE_TRACKER_TO_UPDATE_DESIGN:
            for b in grpc_other:
                b.parent_component.delete_body(b)
        else:
            # If USE_TRACKER_TO_UPDATE_DESIGN is True, we serialize the response
            # and update the parent design with the serialized response.
            parent_design = get_design_from_body(self)
            parent_design._update_from_tracker(response["tracker_response"])

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
