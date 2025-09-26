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
"""Provides tools for pulling geometry."""

from enum import Enum, unique
from typing import TYPE_CHECKING, Union

from beartype import beartype as check_input_types
from pint import Quantity

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.designer.component import Component
from ansys.geometry.core.designer.mating_conditions import (
    AlignCondition,
    OrientCondition,
    TangentCondition,
)
from ansys.geometry.core.designer.selection import NamedSelection
from ansys.geometry.core.errors import GeometryRuntimeError
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc.auxiliary import (
    get_bodies_from_ids,
    get_design_from_body,
    get_design_from_component,
    get_design_from_edge,
    get_design_from_face,
    get_faces_from_ids,
)
from ansys.geometry.core.misc.checks import (
    check_type,
    check_type_all_elements_in_iterable,
    min_backend_version,
)
from ansys.geometry.core.misc.measurements import Angle, Distance
from ansys.geometry.core.shapes.curves.line import Line
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.component import Component
    from ansys.geometry.core.designer.edge import Edge
    from ansys.geometry.core.designer.face import Face


@unique
class ExtrudeType(Enum):
    """Provides values for extrusion types."""

    NONE = 0
    ADD = 1
    CUT = 2
    FORCE_ADD = 3
    FORCE_CUT = 4
    FORCE_INDEPENDENT = 5
    FORCE_NEW_SURFACE = 6


@unique
class OffsetMode(Enum):
    """Provides values for offset modes during extrusions."""

    IGNORE_RELATIONSHIPS = 0
    MOVE_FACES_TOGETHER = 1
    MOVE_FACES_APART = 2


@unique
class FillPatternType(Enum):
    """Provides values for types of fill patterns."""

    GRID = 0
    OFFSET = 1
    SKEWED = 2


@unique
class DraftSide(Enum):
    """Provides values for draft sides."""

    NO_SPLIT = 0
    THIS = 1
    OTHER = 2
    BACK = 3


class GeometryCommands:
    """Provides geometry commands for PyAnsys Geometry.

    Parameters
    ----------
    grpc_client : GrpcClient
        gRPC client to use for the geometry commands.
    _internal_use : bool, optional
        Internal flag to prevent direct instantiation by users.
        This parameter is for internal use only.

    Raises
    ------
    GeometryRuntimeError
        If the class is instantiated directly by users instead
        of through the modeler.

    Notes
    -----
    This class should not be instantiated directly. Use
    ``modeler.geometry_commands`` instead.
    """

    def __init__(self, grpc_client: GrpcClient, _internal_use: bool = False):
        """Initialize an instance of the ``GeometryCommands`` class."""
        if not _internal_use:
            raise GeometryRuntimeError(
                "GeometryCommands should not be instantiated directly. "
                "Use 'modeler.geometry_commands' to access geometry commands."
            )
        self._grpc_client = grpc_client

    @min_backend_version(25, 2, 0)
    def chamfer(
        self,
        selection: Union["Edge", list["Edge"], "Face", list["Face"]],
        distance: Distance | Quantity | Real,
    ) -> bool:
        """Create a chamfer on an edge or adjust the chamfer of a face.

        Parameters
        ----------
        selection : Edge | list[Edge] | Face | list[Face]
            One or more edges or faces to act on.
        distance : Distance | Quantity | Real
            Chamfer distance.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.edge import Edge
        from ansys.geometry.core.designer.face import Face

        selection: list[Edge | Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, (Edge, Face))

        # Convert the distance object
        distance = distance if isinstance(distance, Distance) else Distance(distance)

        for ef in selection:
            ef.body._reset_tessellation_cache()

        result = self._grpc_client.services.model_tools.chamfer(
            selection_ids=[ef.id for ef in selection],
            distance=distance,
        )

        return result.get("success")

    @min_backend_version(25, 2, 0)
    def fillet(
        self,
        selection: Union["Edge", list["Edge"], "Face", list["Face"]],
        radius: Distance | Quantity | Real,
    ) -> bool:
        """Create a fillet on an edge or adjust the fillet of a face.

        Parameters
        ----------
        selection : Edge | list[Edge] | Face | list[Face]
            One or more edges or faces to act on.
        radius : Distance | Quantity | Real
            Fillet radius.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.edge import Edge
        from ansys.geometry.core.designer.face import Face

        selection: list[Edge | Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, (Edge, Face))

        # Convert the radius object
        radius = radius if isinstance(radius, Distance) else Distance(radius)

        for ef in selection:
            ef.body._reset_tessellation_cache()

        result = self._grpc_client.services.model_tools.fillet(
            selection_ids=[ef.id for ef in selection],
            radius=radius,
        )

        return result.get("success")

    @min_backend_version(25, 2, 0)
    def full_fillet(self, faces: list["Face"]) -> bool:
        """Create a full fillet betweens a collection of faces.

        Parameters
        ----------
        faces : list[Face]
            Faces to round.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.face import Face

        check_type_all_elements_in_iterable(faces, Face)

        for face in faces:
            face.body._reset_tessellation_cache()

        result = self._grpc_client.services.model_tools.full_fillet(
            selection_ids=[face.id for face in faces],
        )

        return result.get("success")

    @min_backend_version(25, 2, 0)
    def extrude_faces(
        self,
        faces: Union["Face", list["Face"]],
        distance: Distance | Quantity | Real,
        direction: UnitVector3D = None,
        extrude_type: ExtrudeType = ExtrudeType.ADD,
        offset_mode: OffsetMode = OffsetMode.MOVE_FACES_TOGETHER,
        pull_symmetric: bool = False,
        copy: bool = False,
        force_do_as_extrude: bool = False,
    ) -> list["Body"]:
        """Extrude a selection of faces.

        Parameters
        ----------
        faces : Face | list[Face]
            Faces to extrude.
        distance : Real
            Distance to extrude.
        direction : UnitVector3D, default: None
            Direction of extrusion. If no direction is provided, it will be inferred.
        extrude_type : ExtrudeType, default: ExtrudeType.ADD
            Type of extrusion to be performed.
        offset_mode : OffsetMode, default: OffsetMode.MOVE_FACES_TOGETHER
            Mode of how to handle offset relationships.
        pull_symmetric : bool, default: False
            Pull symmetrically on both sides if ``True``.
        copy : bool, default: False
            Copy the face and move it instead of extruding the original face if ``True``.
        force_do_as_extrude : bool, default: False
            Forces to do as an extrusion if ``True``, if ``False`` allows extrusion by offset.

        Returns
        -------
        list[Body]
            Bodies created by the extrusion if any.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.face import Face

        faces: list[Face] = faces if isinstance(faces, list) else [faces]
        check_type_all_elements_in_iterable(faces, Face)

        # Create distance object
        distance = distance if isinstance(distance, Distance) else Distance(distance)

        for face in faces:
            face.body._reset_tessellation_cache()

        result = self._grpc_client.services.faces.extrude_faces(
            face_ids=[face.id for face in faces],
            distance=distance,
            direction=direction,
            extrude_type=extrude_type,
            pull_symmetric=pull_symmetric,
            offset_mode=offset_mode,
            copy=copy,
            force_do_as_extrude=force_do_as_extrude,
        )

        design = get_design_from_face(faces[0])

        if result.get("success"):
            design._update_design_inplace()
            return get_bodies_from_ids(design, result.get("created_bodies"))
        else:
            self._grpc_client.log.info("Failed to extrude faces.")
            return []

    @min_backend_version(25, 2, 0)
    def extrude_faces_up_to(
        self,
        faces: Union["Face", list["Face"]],
        up_to_selection: Union["Face", "Edge", "Body"],
        seed_point: Point3D,
        direction: UnitVector3D,
        extrude_type: ExtrudeType = ExtrudeType.ADD,
        offset_mode: OffsetMode = OffsetMode.MOVE_FACES_TOGETHER,
        pull_symmetric: bool = False,
        copy: bool = False,
        force_do_as_extrude: bool = False,
    ) -> list["Body"]:
        """Extrude a selection of faces up to another object.

        Parameters
        ----------
        faces : Face | list[Face]
            Faces to extrude.
        up_to_selection : Face | Edge | Body
            The object to pull the faces up to.
        seed_point : Point3D
            Origin to define the extrusion.
        direction : UnitVector3D, default: None
            Direction of extrusion. If no direction is provided, it will be inferred.
        extrude_type : ExtrudeType, default: ExtrudeType.ADD
            Type of extrusion to be performed.
        offset_mode : OffsetMode, default: OffsetMode.MOVE_FACES_TOGETHER
            Mode of how to handle offset relationships.
        pull_symmetric : bool, default: False
            Pull symmetrically on both sides if ``True``.
        copy : bool, default: False
            Copy the face and move it instead of extruding the original face if ``True``.
        force_do_as_extrude : bool, default: False
            Forces to do as an extrusion if ``True``, if ``False`` allows extrusion by offset.

        Returns
        -------
        list[Body]
            Bodies created by the extrusion if any.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.face import Face

        faces: list[Face] = faces if isinstance(faces, list) else [faces]
        check_type_all_elements_in_iterable(faces, Face)

        for face in faces:
            face.body._reset_tessellation_cache()

        result = self._grpc_client.services.faces.extrude_faces_up_to(
            face_ids=[face.id for face in faces],
            up_to_selection_id=up_to_selection.id,
            seed_point=seed_point,
            direction=direction,
            extrude_type=extrude_type,
            pull_symmetric=pull_symmetric,
            offset_mode=offset_mode,
            copy=copy,
            force_do_as_extrude=force_do_as_extrude,
        )

        design = get_design_from_face(faces[0])

        if result.get("success"):
            design._update_design_inplace()
            return get_bodies_from_ids(design, result.get("created_bodies"))
        else:
            self._grpc_client.log.info("Failed to extrude faces.")
            return []

    @min_backend_version(25, 2, 0)
    def extrude_edges(
        self,
        edges: Union["Edge", list["Edge"]],
        distance: Distance | Quantity | Real,
        from_face: "Face" = None,
        from_point: Point3D = None,
        direction: UnitVector3D = None,
        extrude_type: ExtrudeType = ExtrudeType.ADD,
        pull_symmetric: bool = False,
        copy: bool = False,
        natural_extension: bool = False,
    ) -> list["Body"]:
        """Extrude a selection of edges. Provide either a face or a direction and point.

        Parameters
        ----------
        edges : Edge | list[Edge]
            Edges to extrude.
        distance : Distance | Quantity | Real
            Distance to extrude.
        from_face : Face, default: None
            Face to pull normal from.
        from_point : Point3D, default: None
            Point to pull from. Must be used with ``direction``.
        direction : UnitVector3D, default: None
            Direction to pull. Must be used with ``from_point``.
        extrude_type : ExtrudeType, default: ExtrudeType.ADD
            Type of extrusion to be performed.
        pull_symmetric : bool, default: False
            Pull symmetrically on both sides if ``True``.
        copy : bool, default: False
            Copy the edge and move it instead of extruding the original edge if ``True``.
        natural_extension : bool, default: False
            Surfaces will extend in a natural or linear shape after exceeding its original range.

        Returns
        -------
        list[Body]
            Bodies created by the extrusion if any.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.edge import Edge

        edges: list[Edge] = edges if isinstance(edges, list) else [edges]
        check_type_all_elements_in_iterable(edges, Edge)

        # Create distance object
        distance = distance if isinstance(distance, Distance) else Distance(distance)

        if from_face is None and None in (from_point, direction):
            raise ValueError(
                "To extrude edges, either a face or a direction and point must be provided."
            )

        for edge in edges:
            edge.body._reset_tessellation_cache()

        result = self._grpc_client.services.edges.extrude_edges(
            edge_ids=[edge.id for edge in edges],
            distance=distance,
            face=from_face.id,
            point=from_point,
            direction=direction,
            extrude_type=extrude_type,
            pull_symmetric=pull_symmetric,
            copy=copy,
            natural_extension=natural_extension,
        )

        design = get_design_from_edge(edges[0])

        if result.get("success"):
            design._update_design_inplace()
            return get_bodies_from_ids(design, result.get("created_bodies"))
        else:
            self._grpc_client.log.info("Failed to extrude edges.")
            return []

    @min_backend_version(25, 2, 0)
    def extrude_edges_up_to(
        self,
        edges: Union["Edge", list["Edge"]],
        up_to_selection: Union["Face", "Edge", "Body"],
        seed_point: Point3D,
        direction: UnitVector3D,
        extrude_type: ExtrudeType = ExtrudeType.ADD,
    ) -> list["Body"]:
        """Extrude a selection of edges up to another object.

        Parameters
        ----------
        edges : Edge | list[Edge]
            Edges to extrude.
        up_to_selection : Face, default: None
            The object to pull the faces up to.
        seed_point : Point3D
            Origin to define the extrusion.
        direction : UnitVector3D, default: None
            Direction of extrusion.
        extrude_type : ExtrudeType, default: ExtrudeType.ADD
            Type of extrusion to be performed.

        Returns
        -------
        list[Body]
            Bodies created by the extrusion if any.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.edge import Edge

        edges: list[Edge] = edges if isinstance(edges, list) else [edges]
        check_type_all_elements_in_iterable(edges, Edge)

        for edge in edges:
            edge.body._reset_tessellation_cache()

        result = self._grpc_client.services.edges.extrude_edges_up_to(
            edge_ids=[edge.id for edge in edges],
            up_to_selection=up_to_selection.id,
            seed_point=seed_point,
            direction=direction,
            extrude_type=extrude_type,
        )

        design = get_design_from_edge(edges[0])

        if result.get("success"):
            design._update_design_inplace()
            return get_bodies_from_ids(design, result.get("created_bodies"))
        else:
            self._grpc_client.log.info("Failed to extrude edges.")
            return []

    @min_backend_version(25, 2, 0)
    def rename_object(
        self,
        selection: Union[list["Body"], list["Component"]],
        name: str,
    ) -> bool:
        """Rename an object.

        Parameters
        ----------
        selection : list[Body] | list[Component]
            Selection of the objects to rename.
        name : str
            New name for the object.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        result = self._grpc_client._services.commands.set_name(
            selection_ids=[object.id for object in selection], name=name
        )
        return result.get("success")

    @min_backend_version(25, 2, 0)
    def create_linear_pattern(
        self,
        selection: Union["Face", list["Face"]],
        linear_direction: Union["Edge", "Face"],
        count_x: int,
        pitch_x: Distance | Quantity | Real,
        two_dimensional: bool = False,
        count_y: int = None,
        pitch_y: Distance | Quantity | Real = None,
    ) -> bool:
        """Create a linear pattern. The pattern can be one or two dimensions.

        Parameters
        ----------
        selection : Face | list[Face]
            Faces to create the pattern out of.
        linear_direction : Edge | Face
            Direction of the linear pattern, determined by the direction of an edge or face normal.
        count_x : int
            How many times the pattern repeats in the x direction.
        pitch_x : Distance | Quantity | Real
            The spacing between each pattern member in the x direction.
        two_dimensional : bool, default: False
            If ``True``, create a pattern in the x and y direction.
        count_y : int, default: None
            How many times the pattern repeats in the y direction.
        pitch_y : Distance | Quantity | Real, default: None
            The spacing between each pattern member in the y direction.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        if two_dimensional and None in (count_y, pitch_y):
            raise ValueError(
                "If the pattern is two dimensional, count_y and pitch_y must be provided."
            )
        if not two_dimensional and None not in (count_y, pitch_y):
            raise ValueError(
                (
                    "You provided count_y and pitch_y. Ensure two_dimensional is True if a "
                    "two-dimensional pattern is desired."
                )
            )

        # Convert pitches to distance objects
        pitch_x = pitch_x if isinstance(pitch_x, Distance) else Distance(pitch_x)
        if pitch_y is not None:
            pitch_y = pitch_y if isinstance(pitch_y, Distance) else Distance(pitch_y)

        result = self._grpc_client.services.patterns.create_linear_pattern(
            selection_ids=[object.id for object in selection],
            linear_direction_id=linear_direction.id,
            count_x=count_x,
            pitch_x=pitch_x,
            two_dimensional=two_dimensional,
            count_y=count_y,
            pitch_y=pitch_y,
        )

        return result.get("success")

    @min_backend_version(25, 2, 0)
    def modify_linear_pattern(
        self,
        selection: Union["Face", list["Face"]],
        count_x: int = 0,
        pitch_x: Distance | Quantity | Real = 0.0,
        count_y: int = 0,
        pitch_y: Distance | Quantity | Real = 0.0,
        new_seed_index: int = 0,
        old_seed_index: int = 0,
    ) -> bool:
        """Modify a linear pattern. Leave an argument at 0 for it to remain unchanged.

        Parameters
        ----------
        selection : Face | list[Face]
            Faces that belong to the pattern.
        count_x : int, default: 0
            How many times the pattern repeats in the x direction.
        pitch_x : Distance | Quantity | Real, default: 0.0
            The spacing between each pattern member in the x direction.
        count_y : int, default: 0
            How many times the pattern repeats in the y direction.
        pitch_y : Distance | Quantity | Real, default: 0.0
            The spacing between each pattern member in the y direction.
        new_seed_index : int, default: 0
            The new seed index of the member.
        old_seed_index : int, default: 0
            The old seed index of the member.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        # Convert pitches to distance objects
        pitch_x = pitch_x if isinstance(pitch_x, Distance) else Distance(pitch_x)
        pitch_y = pitch_y if isinstance(pitch_y, Distance) else Distance(pitch_y)

        result = self._grpc_client.services.patterns.modify_linear_pattern(
            selection_ids=[object.id for object in selection],
            count_x=count_x,
            pitch_x=pitch_x,
            count_y=count_y,
            pitch_y=pitch_y,
            new_seed_index=new_seed_index,
            old_seed_index=old_seed_index,
        )

        return result.get("success")

    @min_backend_version(25, 2, 0)
    def create_circular_pattern(
        self,
        selection: Union["Face", list["Face"]],
        circular_axis: "Edge",
        circular_count: int,
        circular_angle: Angle | Quantity | Real,
        two_dimensional: bool = False,
        linear_count: int = None,
        linear_pitch: Distance | Quantity | Real = None,
        radial_direction: UnitVector3D = None,
    ) -> bool:
        """Create a circular pattern. The pattern can be one or two dimensions.

        Parameters
        ----------
        selection : Face | list[Face]
            Faces to create the pattern out of.
        circular_axis : Edge
            The axis of the circular pattern, determined by the direction of an edge.
        circular_count : int
            How many members are in the circular pattern.
        circular_angle : Angle | Quantity | Real
            The angular range of the pattern.
        two_dimensional : bool, default: False
            If ``True``, create a two-dimensional pattern.
        linear_count : int, default: None
            How many times the circular pattern repeats along the radial lines for a
            two-dimensional pattern.
        linear_pitch : Distance | Quantity | Real, default: None
            The spacing along the radial lines for a two-dimensional pattern.
        radial_direction : UnitVector3D, default: None
            The direction from the center out for a two-dimensional pattern.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        if two_dimensional and None in (linear_count, linear_pitch):
            raise ValueError(
                "If the pattern is two-dimensional, linear_count and linear_pitch must be provided."
            )
        if not two_dimensional and None not in (
            linear_count,
            linear_pitch,
        ):
            raise ValueError(
                (
                    "You provided linear_count and linear_pitch. Ensure two_dimensional is True if "
                    "a two-dimensional pattern is desired."
                )
            )

        # Convert angle and pitch to appropriate objects
        if not isinstance(circular_angle, Angle):
            circular_angle = Angle(circular_angle)
        if linear_pitch is not None and not isinstance(linear_pitch, Distance):
            linear_pitch = Distance(linear_pitch)

        result = self._grpc_client.services.patterns.create_circular_pattern(
            selection_ids=[object.id for object in selection],
            circular_axis_id=circular_axis.id,
            circular_count=circular_count,
            circular_angle=circular_angle,
            two_dimensional=two_dimensional,
            linear_count=linear_count,
            linear_pitch=linear_pitch,
            radial_direction=radial_direction,
        )

        return result.get("success")

    @min_backend_version(25, 2, 0)
    def modify_circular_pattern(
        self,
        selection: Union["Face", list["Face"]],
        circular_count: int = 0,
        linear_count: int = 0,
        step_angle: Angle | Quantity | Real = 0.0,
        step_linear: Distance | Quantity | Real = 0.0,
    ) -> bool:
        """Modify a circular pattern. Leave an argument at 0 for it to remain unchanged.

        Parameters
        ----------
        selection : Face | list[Face]
            Faces that belong to the pattern.
        circular_count : int, default: 0
            How many members are in the circular pattern.
        linear_count : int, default: 0
            How many times the circular pattern repeats along the radial lines for a
            two-dimensional pattern.
        step_angle : Angle | Quantity | Real, default: 0.0
            Defines the circular angle.
        step_linear : Distance | Quantity | Real, default: 0.0
            Defines the step, along the radial lines, for a pattern dimension greater than 1.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        # Convert angle and pitch to appropriate objects
        step_angle = step_angle if isinstance(step_angle, Angle) else Angle(step_angle)
        print(step_linear)
        step_linear = step_linear if isinstance(step_linear, Distance) else Distance(step_linear)

        result = self._grpc_client.services.patterns.modify_circular_pattern(
            selection_ids=[object.id for object in selection],
            circular_count=circular_count,
            linear_count=linear_count,
            step_angle=step_angle,
            step_linear=step_linear,
        )

        return result.get("success")

    @min_backend_version(25, 2, 0)
    def create_fill_pattern(
        self,
        selection: Union["Face", list["Face"]],
        linear_direction: Union["Edge", "Face"],
        fill_pattern_type: FillPatternType,
        margin: Distance | Quantity | Real,
        x_spacing: Distance | Quantity | Real,
        y_spacing: Distance | Quantity | Real,
        row_x_offset: Distance | Quantity | Real = 0,
        row_y_offset: Distance | Quantity | Real = 0,
        column_x_offset: Distance | Quantity | Real = 0,
        column_y_offset: Distance | Quantity | Real = 0,
    ) -> bool:
        """Create a fill pattern.

        Parameters
        ----------
        selection : Face | list[Face]
            Faces to create the pattern out of.
        linear_direction : Edge
            Direction of the linear pattern, determined by the direction of an edge.
        fill_pattern_type : FillPatternType
            The type of fill pattern.
        margin : Distance | Quantity | Real
            Margin defining the border of the fill pattern.
        x_spacing : Distance | Quantity | Real
            Spacing between the pattern members in the x direction.
        y_spacing : Distance | Quantity | Real
            Spacing between the pattern members in the x direction.
        row_x_offset : Distance | Quantity | Real, default: 0
            Offset for the rows in the x direction. Only used with ``FillPattern.SKEWED``.
        row_y_offset : Distance | Quantity | Real, default: 0
            Offset for the rows in the y direction. Only used with ``FillPattern.SKEWED``.
        column_x_offset : Distance | Quantity | Real, default: 0
            Offset for the columns in the x direction. Only used with ``FillPattern.SKEWED``.
        column_y_offset : Distance | Quantity | Real, default: 0
            Offset for the columns in the y direction. Only used with ``FillPattern.SKEWED``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        # Convert measurements to distance objects
        margin = margin if isinstance(margin, Distance) else Distance(margin)
        x_spacing = x_spacing if isinstance(x_spacing, Distance) else Distance(x_spacing)
        y_spacing = y_spacing if isinstance(y_spacing, Distance) else Distance(y_spacing)
        row_x_offset = (
            row_x_offset if isinstance(row_x_offset, Distance) else Distance(row_x_offset)
        )
        row_y_offset = (
            row_y_offset if isinstance(row_y_offset, Distance) else Distance(row_y_offset)
        )
        column_x_offset = (
            column_x_offset if isinstance(column_x_offset, Distance) else Distance(column_x_offset)
        )
        column_y_offset = (
            column_y_offset if isinstance(column_y_offset, Distance) else Distance(column_y_offset)
        )

        result = self._grpc_client.services.patterns.create_fill_pattern(
            selection_ids=[object.id for object in selection],
            linear_direction_id=linear_direction.id,
            fill_pattern_type=fill_pattern_type,
            margin=margin,
            x_spacing=x_spacing,
            y_spacing=y_spacing,
            row_x_offset=row_x_offset,
            row_y_offset=row_y_offset,
            column_x_offset=column_x_offset,
            column_y_offset=column_y_offset,
        )

        return result.get("success")

    @min_backend_version(25, 2, 0)
    def update_fill_pattern(
        self,
        selection: Union["Face", list["Face"]],
    ) -> bool:
        """Update a fill pattern.

        When the face that a fill pattern exists upon changes in size, the
        fill pattern can be updated to fill the new space.

        Parameters
        ----------
        selection : Face | list[Face]
            Face(s) that are part of a fill pattern.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        result = self._grpc_client.services.patterns.update_fill_pattern(
            selection_ids=[object.id for object in selection],
        )

        return result.get("success")

    @min_backend_version(25, 2, 0)
    def revolve_faces(
        self,
        selection: Union["Face", list["Face"]],
        axis: Line,
        angle: Angle | Quantity | Real,
        extrude_type: ExtrudeType = ExtrudeType.ADD,
    ) -> list["Body"]:
        """Revolve face around an axis.

        Parameters
        ----------
        selection : Face | list[Face]
            Face(s) to revolve.
        axis : Line
            Axis of revolution.
        angle : Angle | Quantity | Real
            Angular distance to revolve.
        extrude_type : ExtrudeType, default: ExtrudeType.ADD
            Type of extrusion to be performed.

        Returns
        -------
        list[Body]
            Bodies created by the extrusion if any.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]
        check_type_all_elements_in_iterable(selection, Face)

        angle = angle if isinstance(angle, Angle) else Angle(angle)

        for object in selection:
            object.body._reset_tessellation_cache()

        result = self._grpc_client._services.faces.revolve_faces(
            selection_ids=[object.id for object in selection],
            axis=axis,
            angle=angle,
            extrude_type=extrude_type,
        )

        design = get_design_from_face(selection[0])

        if result.get("success"):
            design._update_design_inplace()
            return get_bodies_from_ids(design, result.get("created_bodies"))
        else:
            self._grpc_client.log.info("Failed to revolve faces.")
            return []

    @min_backend_version(25, 2, 0)
    def revolve_faces_up_to(
        self,
        selection: Union["Face", list["Face"]],
        up_to: Union["Face", "Edge", "Body"],
        axis: Line,
        direction: UnitVector3D,
        extrude_type: ExtrudeType = ExtrudeType.ADD,
    ) -> list["Body"]:
        """Revolve face around an axis up to a certain object.

        Parameters
        ----------
        selection : Face | list[Face]
            Face(s) to revolve.
        up_to : Face | Edge | Body
            Object to revolve the face up to.
        axis : Line
            Axis of revolution.
        direction : UnitVector3D
            Direction of extrusion.
        extrude_type : ExtrudeType, default: ExtrudeType.ADD
            Type of extrusion to be performed.

        Returns
        -------
        list[Body]
            Bodies created by the extrusion if any.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]
        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        result = self._grpc_client._services.faces.revolve_faces_up_to(
            selection_ids=[object.id for object in selection],
            up_to_selection_id=up_to.id,
            axis=axis,
            direction=direction,
            extrude_type=extrude_type,
        )

        design = get_design_from_face(selection[0])

        if result.get("success"):
            design._update_design_inplace()
            return get_bodies_from_ids(design, result.get("created_bodies"))
        else:
            self._grpc_client.log.info("Failed to revolve faces.")
            return []

    @min_backend_version(25, 2, 0)
    def revolve_faces_by_helix(
        self,
        selection: Union["Face", list["Face"]],
        axis: Line,
        direction: UnitVector3D,
        height: Distance | Quantity | Real,
        pitch: Distance | Quantity | Real,
        taper_angle: Angle | Quantity | Real,
        right_handed: bool,
        both_sides: bool,
        extrude_type: ExtrudeType = ExtrudeType.ADD,
    ) -> list["Body"]:
        """Revolve face around an axis in a helix shape.

        Parameters
        ----------
        selection : Face | list[Face]
            Face(s) to revolve.
        axis : Line
            Axis of revolution.
        direction : UnitVector3D
            Direction of extrusion.
        height : Distance | Quantity | Real,
            Height of the helix.
        pitch : Distance | Quantity | Real,
            Pitch of the helix.
        taper_angle : Angle | Quantity | Real,
            Taper angle of the helix.
        right_handed : bool,
            Right-handed helix if ``True``, left-handed if ``False``.
        both_sides : bool,
            Create on both sides if ``True``, one side if ``False``.
        extrude_type : ExtrudeType, default: ExtrudeType.ADD
            Type of extrusion to be performed.

        Returns
        -------
        list[Body]
            Bodies created by the extrusion if any.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]
        check_type_all_elements_in_iterable(selection, Face)

        height = height if isinstance(height, Distance) else Distance(height)
        pitch = pitch if isinstance(pitch, Distance) else Distance(pitch)
        taper_angle = taper_angle if isinstance(taper_angle, Angle) else Angle(taper_angle)

        for object in selection:
            object.body._reset_tessellation_cache()

        result = self._grpc_client._services.faces.revolve_faces_by_helix(
            selection_ids=[object.id for object in selection],
            axis=axis,
            direction=direction,
            height=height,
            pitch=pitch,
            taper_angle=taper_angle,
            right_handed=right_handed,
            both_sides=both_sides,
            extrude_type=extrude_type,
        )

        design = get_design_from_face(selection[0])

        if result.get("success"):
            design._update_design_inplace()
            return get_bodies_from_ids(design, result.get("created_bodies"))
        else:
            self._grpc_client.log.info("Failed to revolve faces.")
            return []

    @min_backend_version(25, 2, 0)
    def replace_face(
        self,
        target_selection: Union["Face", list["Face"]],
        replacement_selection: Union["Face", list["Face"]],
    ) -> bool:
        """Replace a face with another face.

        Parameters
        ----------
        target_selection : Union[Face, list[Face]]
            The face or faces to replace.
        replacement_selection : Union[Face, list[Face]]
            The face or faces to replace with.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        target_selection: list["Face"] = (
            target_selection if isinstance(target_selection, list) else [target_selection]
        )
        replacement_selection: list["Face"] = (
            replacement_selection
            if isinstance(replacement_selection, list)
            else [replacement_selection]
        )

        result = self._grpc_client._services.faces.replace_faces(
            target_ids=[selection.id for selection in target_selection],
            replacement_ids=[selection.id for selection in replacement_selection],
        )

        return result.get("success")

    @min_backend_version(25, 2, 0)
    def split_body(
        self,
        bodies: list["Body"],
        plane: Plane,
        slicers: Union["Edge", list["Edge"], "Face", list["Face"]],
        faces: list["Face"],
        extendfaces: bool,
    ) -> bool:
        """Split bodies with a plane, slicers, or faces.

        Parameters
        ----------
        bodies : list[Body]
            Bodies to split.
        plane : Plane
            Plane to split with
        slicers : Edge | list[Edge] | Face | list[Face]
            Slicers to split with.
        faces : list[Face]
            Faces to split with.
        extendFaces : bool
            Extend faces if split with faces.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.body import Body
        from ansys.geometry.core.designer.edge import Edge
        from ansys.geometry.core.designer.face import Face

        check_type_all_elements_in_iterable(bodies, Body)

        for body in bodies:
            body._reset_tessellation_cache()

        if plane is not None:
            check_type(plane, Plane)

        slicer_items = []
        if slicers is not None:
            slicers: list["Face", "Edge"] = slicers if isinstance(slicers, list) else [slicers]
            check_type_all_elements_in_iterable(slicers, (Edge, Face))
            slicer_items = [slicer.id for slicer in slicers]

        face_items = []
        if faces is not None:
            faces: list["Face"] = faces if isinstance(faces, list) else [faces]
            check_type_all_elements_in_iterable(faces, Face)
            face_items = [face.id for face in faces]

        result = self._grpc_client._services.bodies.split_body(
            body_ids=[body.id for body in bodies],
            plane=plane,
            slicer_ids=slicer_items,
            face_ids=face_items,
            extend_surfaces=extendfaces,
        )

        if result.get("success"):
            design = get_design_from_body(bodies[0])
            design._update_design_inplace()

        return result.get("success")

    @min_backend_version(25, 2, 0)
    def get_round_info(self, face: "Face") -> tuple[bool, Real]:
        """Get info on the rounding of a face.

        Parameters
        ----------
        Face
            The design face to get round info on.

        Returns
        -------
        tuple[bool, Real]
            ``True`` if round is aligned with face's U-parameter direction, ``False`` otherwise.
            Radius of the round.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        result = self._grpc_client._services.faces.get_round_info(face_id=face.id)

        return (result.get("along_u"), result.get("radius"))

    @check_input_types
    @min_backend_version(25, 2, 0)
    def move_translate(
        self,
        selection: NamedSelection,
        direction: UnitVector3D,
        distance: Distance | Quantity | Real,
    ) -> bool:
        """Move a selection by a distance in a direction.

        Parameters
        ----------
        selection : NamedSelection
            Named selection to move.
        direction : UnitVector3D
            Direction to move in.
        distance : Distance | Quantity | Real
            Distance to move. Default units are meters.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        distance = distance if isinstance(distance, Distance) else Distance(distance)

        result = self._grpc_client.services.model_tools.move_translate(
            selection_id=selection.id,
            direction=direction,
            distance=distance,
        )

        return result.get("success")

    @check_input_types
    @min_backend_version(25, 2, 0)
    def move_rotate(
        self,
        selection: NamedSelection,
        axis: Line,
        angle: Angle | Quantity | Real,
    ) -> dict[str, Union[bool, Real]]:
        """Rotate a selection by an angle about a given axis.

        Parameters
        ----------
        selection : NamedSelection
            Named selection to move.
        axis : Line
            Direction to move in.
        Angle : Angle | Quantity | Real
            Angle to rotate by. Default units are radians.

        Returns
        -------
        dict[str, Union[bool, Real]]
            Dictionary containing the useful output from the command result.
            Keys are success, modified_bodies, modified_faces, modified_edges.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        angle = angle if isinstance(angle, Angle) else Angle(angle)

        result = self._grpc_client.services.model_tools.move_rotate(
            selection_id=selection.id,
            axis=axis,
            angle=angle,
        )

        return result

    @check_input_types
    @min_backend_version(25, 2, 0)
    def offset_faces_set_radius(
        self,
        faces: Union["Face", list["Face"]],
        radius: Distance | Quantity | Real,
        copy: bool = False,
        offset_mode: OffsetMode = OffsetMode.IGNORE_RELATIONSHIPS,
        extrude_type: ExtrudeType = ExtrudeType.FORCE_INDEPENDENT,
    ) -> bool:
        """Offset faces with a radius.

        Parameters
        ----------
        faces : Face | list[Face]
            Faces to offset.
        radius : Distance | Quantity | Real
            Radius of the offset.
        copy : bool, default: False
            Copy the face and move it instead of offsetting the original face if ``True``.
        offset_mode : OffsetMode, default: OffsetMode.MOVE_FACES_TOGETHER
            Mode of how to handle offset relationships.
        extrude_type : ExtrudeType, default: ExtrudeType.FORCE_INDEPENDENT
            Type of extrusion to be performed.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.face import Face

        faces: list[Face] = faces if isinstance(faces, list) else [faces]
        check_type_all_elements_in_iterable(faces, Face)

        for face in faces:
            face.body._reset_tessellation_cache()

        radius = radius if isinstance(radius, Distance) else Distance(radius)

        result = self._grpc_client._services.faces.offset_faces_set_radius(
            face_ids=[face.id for face in faces],
            radius=radius,
            copy=copy,
            offset_mode=offset_mode,
            extrude_type=extrude_type,
        )

        return result.get("success")

    @min_backend_version(26, 1, 0)
    def create_align_condition(
        self,
        parent_component: "Component",
        geometry_a: Union["Body", "Face", "Edge"],
        geometry_b: Union["Body", "Face", "Edge"],
    ) -> AlignCondition:
        """Create an align condition between two geometry objects.

        This will move the objects to be aligned with each other.

        Parameters
        ----------
        parent_component : Component
            The common ancestor component of the two geometry objects.
        geometry_a : Body | Face | Edge
            The first geometry object to align to the second.
        geometry_b : Body | Face | Edge
            The geometry object to be aligned to.

        Returns
        -------
        AlignCondition
            The persistent align condition that was created.

        Warnings
        --------
        This method is only available starting on Ansys release 26R1.
        """
        from ansys.geometry.core.designer.body import Body
        from ansys.geometry.core.designer.component import Component
        from ansys.geometry.core.designer.edge import Edge
        from ansys.geometry.core.designer.face import Face

        check_type(parent_component, Component)
        check_type(geometry_a, (Body, Face, Edge))
        check_type(geometry_b, (Body, Face, Edge))

        result = self._grpc_client._services.assembly_controls.create_align_condition(
            parent_id=parent_component.id,
            geometric_a_id=geometry_a.id,
            geometric_b_id=geometry_b.id,
        )

        get_design_from_component(parent_component)._update_design_inplace()

        return AlignCondition(
            result.get("moniker"),
            result.get("is_deleted"),
            result.get("is_enabled"),
            result.get("is_satisfied"),
            result.get("offset"),
            result.get("is_reversed"),
            result.get("is_valid"),
        )

    @min_backend_version(26, 1, 0)
    def create_tangent_condition(
        self,
        parent_component: "Component",
        geometry_a: Union["Body", "Face", "Edge"],
        geometry_b: Union["Body", "Face", "Edge"],
    ) -> TangentCondition:
        """Create a tangent condition between two geometry objects.

        This aligns the objects so that they are tangent.

        Parameters
        ----------
        parent_component : Component
            The common ancestor component of the two geometry objects.
        geometry_a : Body | Face | Edge
            The first geometry object to tangent the second.
        geometry_b : Body | Face | Edge
            The geometry object to be tangent with.

        Returns
        -------
        TangentCondition
            The persistent tangent condition that was created.

        Warnings
        --------
        This method is only available starting on Ansys release 26R1.
        """
        from ansys.geometry.core.designer.body import Body
        from ansys.geometry.core.designer.component import Component
        from ansys.geometry.core.designer.edge import Edge
        from ansys.geometry.core.designer.face import Face

        check_type(parent_component, Component)
        check_type(geometry_a, (Body, Face, Edge))
        check_type(geometry_b, (Body, Face, Edge))

        result = self._grpc_client._services.assembly_controls.create_tangent_condition(
            parent_id=parent_component.id,
            geometric_a_id=geometry_a.id,
            geometric_b_id=geometry_b.id,
        )

        get_design_from_component(parent_component)._update_design_inplace()

        return TangentCondition(
            result.get("moniker"),
            result.get("is_deleted"),
            result.get("is_enabled"),
            result.get("is_satisfied"),
            result.get("offset"),
            result.get("is_reversed"),
            result.get("is_valid"),
        )

    @min_backend_version(26, 1, 0)
    def create_orient_condition(
        self,
        parent_component: "Component",
        geometry_a: Union["Body", "Face", "Edge"],
        geometry_b: Union["Body", "Face", "Edge"],
    ) -> OrientCondition:
        """Create an orient condition between two geometry objects.

        This rotates the objects so that they are oriented in the same direction.

        Parameters
        ----------
        parent_component : Component
            The common ancestor component of the two geometry objects.
        geometry_a : Body | Face | Edge
            The first geometry object to orient with the second.
        geometry_b : Body | Face | Edge
            The geometry object to be oriented with.

        Returns
        -------
        OrientCondition
            The persistent orient condition that was created.

        Warnings
        --------
        This method is only available starting on Ansys release 26R1.
        """
        from ansys.geometry.core.designer.body import Body
        from ansys.geometry.core.designer.component import Component
        from ansys.geometry.core.designer.edge import Edge
        from ansys.geometry.core.designer.face import Face

        check_type(parent_component, Component)
        check_type(geometry_a, (Body, Face, Edge))
        check_type(geometry_b, (Body, Face, Edge))

        result = self._grpc_client.services.assembly_controls.create_orient_condition(
            parent_id=parent_component.id,
            geometric_a_id=geometry_a.id,
            geometric_b_id=geometry_b.id,
        )

        get_design_from_component(parent_component)._update_design_inplace()

        return OrientCondition(
            result.get("moniker"),
            result.get("is_deleted"),
            result.get("is_enabled"),
            result.get("is_satisfied"),
            result.get("offset"),
            result.get("is_reversed"),
            result.get("is_valid"),
        )

    @min_backend_version(26, 1, 0)
    def move_imprint_edges(
        self, edges: list["Edge"], direction: UnitVector3D, distance: Distance | Quantity | Real
    ) -> bool:
        """Move the imprint edges in the specified direction by the specified distance.

        Parameters
        ----------
        edges : list[Edge]
            The edges to move.
        direction : UnitVector3D
            The direction to move the edges.
        distance : Distance | Quantity | Real
            The distance to move the edges.

        Returns
        -------
        bool
            Returns True if the edges were moved successfully, False otherwise.
        """
        distance = distance if isinstance(distance, Distance) else Distance(distance)

        response = self._grpc_client._services.edges.move_imprint_edges(
            edge_ids=[edge.id for edge in edges],
            direction=direction,
            distance=distance,
        )

        return response.get("success")

    @min_backend_version(26, 1, 0)
    def offset_edges(self, edges: list["Edge"], offset: Distance | Quantity | Real) -> bool:
        """Offset the specified edges with the specified distance.

        Parameters
        ----------
        edges : list[Edge]
            The edges to offset.
        offset : Distance | Quantity | Real
            The distance to offset the edges.

        Returns
        -------
        bool
            Returns True if the edges were offset successfully, False otherwise.
        """
        offset = offset if isinstance(offset, Distance) else Distance(offset)

        response = self._grpc_client._services.edges.offset_edges(
            edge_ids=[edge.id for edge in edges],
            offset=offset,
        )

        return response.get("success")

    @min_backend_version(26, 1, 0)
    def draft_faces(
        self,
        faces: list["Face"],
        reference_faces: list["Face"],
        draft_side: DraftSide,
        angle: Angle | Quantity | Real,
        extrude_type: ExtrudeType,
    ) -> list["Face"]:
        """Draft the specified faces in the specified direction by the specified angle.

        Parameters
        ----------
        faces : list[Face]
            The faces to draft.
        reference_faces : list[Face]
            The reference faces to use for the draft.
        draft_side : DraftSide
            The side to draft.
        angle : Angle | Quantity | Real
            The angle to draft the faces.
        extrude_type : ExtrudeType
            The type of extrusion to use.

        Returns
        -------
        list[Face]
            The faces created by the draft operation.
        """
        angle = angle if isinstance(angle, Angle) else Angle(angle)

        response = self._grpc_client._services.faces.draft_faces(
            face_ids=[face.id for face in faces],
            reference_face_ids=[face.id for face in reference_faces],
            draft_side=draft_side,
            angle=angle,
            extrude_type=extrude_type,
        )

        # Return the drafted faces
        design = get_design_from_face(faces[0])
        return get_faces_from_ids(design, [face.id for face in response.get("created_faces")])

    @min_backend_version(26, 1, 0)
    def thicken_faces(
        self,
        faces: list["Face"],
        direction: UnitVector3D,
        thickness: Distance | Quantity | Real,
        extrude_type: ExtrudeType,
        pull_symmetric: bool,
        select_direction: bool,
    ) -> bool:
        """Thicken the specified faces by the specified thickness in the specified direction.

        Parameters
        ----------
        faces : list[Face]
            The faces to thicken.
        direction : UnitVector3D
            The direction to thicken the faces.
        thickness : Distance | Quantity | Real
            The thickness to apply to the faces.
        extrude_type : ExtrudeType
            The type of extrusion to use.
        pull_symmetric : bool
            Whether to pull the faces symmetrically.
        select_direction : bool
            Whether to select the direction.

        Returns
        -------
        bool
            Returns True if the faces were thickened successfully, False otherwise.
        """
        thickness = thickness if isinstance(thickness, Distance) else Distance(thickness)

        result = self._grpc_client._services.faces.thicken_faces(
            face_ids=[face.id for face in faces],
            direction=direction,
            thickness=thickness,
            extrude_type=extrude_type,
            pull_symmetric=pull_symmetric,
            select_direction=select_direction,
        )

        # Update design
        design = get_design_from_face(faces[0])
        if result.get("success"):
            design._update_design_inplace()

        # Return success flag
        return result.get("success")

    @min_backend_version(26, 1, 0)
    def offset_faces(
        self,
        faces: list["Face"],
        distance: Distance | Quantity | Real,
        direction: UnitVector3D,
        extrude_type: ExtrudeType,
    ) -> None:
        """Offset the specified faces by the specified distance in the specified direction.

        Parameters
        ----------
        faces : list[Face]
            The faces to offset.
        distance : Distance | Quantity | Real
            The distance to offset the faces.
        direction : UnitVector3D
            The direction to offset the faces.
        extrude_type : ExtrudeType
            The type of extrusion to use.

        Warnings
        --------
        This method is only available starting on Ansys release 26R1.
        """
        distance = distance if isinstance(distance, Distance) else Distance(distance)

        _ = self._grpc_client._services.faces.offset_faces(
            face_ids=[face.id for face in faces],
            distance=distance,
            direction=direction,
            extrude_type=extrude_type,
        )

    @min_backend_version(25, 2, 0)
    def revolve_edges(
        self,
        edges: Union["Edge", list["Edge"]],
        axis: Line,
        angle: Angle | Quantity | Real,
        symmetric: bool,
    ) -> None:
        """Revolve edges around an axis.

        Parameters
        ----------
        edges : Edge | list[Edge]
            Edge(s) to revolve.
        axis : Line
            Axis of revolution.
        angle : Angle | Quantity | Real
            Angular distance to revolve.
        symmetric : bool
            Revolve symmetrically if ``True``, one side if ``False``.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.edge import Edge

        edges: list[Edge] = edges if isinstance(edges, list) else [edges]
        check_type_all_elements_in_iterable(edges, Edge)

        angle = angle if isinstance(angle, Angle) else Angle(angle)

        _ = self._grpc_client._services.curves.revolve_edges(
            curves=[edge.shape for edge in edges],
            axis=axis,
            angle=angle,
            symmetric=symmetric,
        )

        design = get_design_from_edge(edges[0])
        design._update_design_inplace()
