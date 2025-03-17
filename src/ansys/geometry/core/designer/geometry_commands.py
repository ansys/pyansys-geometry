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

from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
from ansys.api.geometry.v0.commands_pb2 import (
    ChamferRequest,
    CreateCircularPatternRequest,
    CreateFillPatternRequest,
    CreateLinearPatternRequest,
    ExtrudeEdgesRequest,
    ExtrudeEdgesUpToRequest,
    ExtrudeFacesRequest,
    ExtrudeFacesUpToRequest,
    FilletRequest,
    FullFilletRequest,
    ModifyCircularPatternRequest,
    ModifyLinearPatternRequest,
    MoveRotateRequest,
    MoveTranslateRequest,
    OffsetFacesSetRadiusRequest,
    PatternRequest,
    RenameObjectRequest,
    ReplaceFaceRequest,
    RevolveFacesByHelixRequest,
    RevolveFacesRequest,
    RevolveFacesUpToRequest,
    RoundInfoRequest,
    SplitBodyRequest,
)
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.conversions import (
    line_to_grpc_line,
    plane_to_grpc_plane,
    point3d_to_grpc_point,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.designer.selection import NamedSelection
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc.auxiliary import (
    get_bodies_from_ids,
    get_design_from_body,
    get_design_from_edge,
    get_design_from_face,
)
from ansys.geometry.core.misc.checks import (
    check_is_float_int,
    check_type,
    check_type_all_elements_in_iterable,
    min_backend_version,
)
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Angle, Distance
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


class GeometryCommands:
    """Provides geometry commands for PyAnsys Geometry.

    Parameters
    ----------
    grpc_client : GrpcClient
        gRPC client to use for the geometry commands.
    """

    @protect_grpc
    def __init__(self, grpc_client: GrpcClient):
        """Initialize an instance of the ``GeometryCommands`` class."""
        self._grpc_client = grpc_client
        self._commands_stub = CommandsStub(self._grpc_client.channel)

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def chamfer(
        self,
        selection: Union["Edge", list["Edge"], "Face", list["Face"]],
        distance: Real,
    ) -> bool:
        """Create a chamfer on an edge or adjust the chamfer of a face.

        Parameters
        ----------
        selection : Edge | list[Edge] | Face | list[Face]
            One or more edges or faces to act on.
        distance : Real
            Chamfer distance.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        from ansys.geometry.core.designer.edge import Edge
        from ansys.geometry.core.designer.face import Face

        selection: list[Edge | Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, (Edge, Face))
        check_is_float_int(distance, "distance")

        for ef in selection:
            ef.body._reset_tessellation_cache()

        result = self._commands_stub.Chamfer(
            ChamferRequest(ids=[ef._grpc_id for ef in selection], distance=distance)
        )

        return result.success

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def fillet(
        self, selection: Union["Edge", list["Edge"], "Face", list["Face"]], radius: Real
    ) -> bool:
        """Create a fillet on an edge or adjust the fillet of a face.

        Parameters
        ----------
        selection : Edge | list[Edge] | Face | list[Face]
            One or more edges or faces to act on.
        radius : Real
            Fillet radius.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        from ansys.geometry.core.designer.edge import Edge
        from ansys.geometry.core.designer.face import Face

        selection: list[Edge | Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, (Edge, Face))
        check_is_float_int(radius, "radius")

        for ef in selection:
            ef.body._reset_tessellation_cache()

        result = self._commands_stub.Fillet(
            FilletRequest(ids=[ef._grpc_id for ef in selection], radius=radius)
        )

        return result.success

    @protect_grpc
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
        """
        from ansys.geometry.core.designer.face import Face

        check_type_all_elements_in_iterable(faces, Face)

        for face in faces:
            face.body._reset_tessellation_cache()

        result = self._commands_stub.FullFillet(
            FullFilletRequest(faces=[face._grpc_id for face in faces])
        )

        return result.success

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def extrude_faces(
        self,
        faces: Union["Face", list["Face"]],
        distance: Real,
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
        """
        from ansys.geometry.core.designer.face import Face

        faces: list[Face] = faces if isinstance(faces, list) else [faces]
        check_type_all_elements_in_iterable(faces, Face)
        check_is_float_int(distance, "distance")

        for face in faces:
            face.body._reset_tessellation_cache()

        result = self._commands_stub.ExtrudeFaces(
            ExtrudeFacesRequest(
                faces=[face._grpc_id for face in faces],
                distance=distance,
                direction=None if direction is None else unit_vector_to_grpc_direction(direction),
                extrude_type=extrude_type.value,
                pull_symmetric=pull_symmetric,
                offset_mode=offset_mode.value,
                copy=copy,
                force_do_as_extrude=force_do_as_extrude,
            )
        )

        design = get_design_from_face(faces[0])

        if result.success:
            bodies_ids = [created_body.id for created_body in result.created_bodies]
            design._update_design_inplace()
            return get_bodies_from_ids(design, bodies_ids)
        else:
            self._grpc_client.log.info("Failed to extrude faces.")
            return []

    @protect_grpc
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
        """
        from ansys.geometry.core.designer.face import Face

        faces: list[Face] = faces if isinstance(faces, list) else [faces]
        check_type_all_elements_in_iterable(faces, Face)

        for face in faces:
            face.body._reset_tessellation_cache()

        result = self._commands_stub.ExtrudeFacesUpTo(
            ExtrudeFacesUpToRequest(
                faces=[face._grpc_id for face in faces],
                up_to_selection=up_to_selection._grpc_id,
                seed_point=point3d_to_grpc_point(seed_point),
                direction=unit_vector_to_grpc_direction(direction),
                extrude_type=extrude_type.value,
                pull_symmetric=pull_symmetric,
                offset_mode=offset_mode.value,
                copy=copy,
                force_do_as_extrude=force_do_as_extrude,
            )
        )

        design = get_design_from_face(faces[0])

        if result.success:
            bodies_ids = [created_body.id for created_body in result.created_bodies]
            design._update_design_inplace()
            return get_bodies_from_ids(design, bodies_ids)
        else:
            self._grpc_client.log.info("Failed to extrude faces.")
            return []

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def extrude_edges(
        self,
        edges: Union["Edge", list["Edge"]],
        distance: Real,
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
        distance : Real
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
        """
        from ansys.geometry.core.designer.edge import Edge

        edges: list[Edge] = edges if isinstance(edges, list) else [edges]
        check_type_all_elements_in_iterable(edges, Edge)
        check_is_float_int(distance, "distance")
        if from_face is None and None in (from_point, direction):
            raise ValueError(
                "To extrude edges, either a face or a direction and point must be provided."
            )

        for edge in edges:
            edge.body._reset_tessellation_cache()

        result = self._commands_stub.ExtrudeEdges(
            ExtrudeEdgesRequest(
                edges=[edge._grpc_id for edge in edges],
                distance=distance,
                face=from_face._grpc_id,
                point=None if from_point is None else point3d_to_grpc_point(from_point),
                direction=None if direction is None else unit_vector_to_grpc_direction(direction),
                extrude_type=extrude_type.value,
                pull_symmetric=pull_symmetric,
                copy=copy,
                natural_extension=natural_extension,
            )
        )

        design = get_design_from_edge(edges[0])

        if result.success:
            bodies_ids = [created_body.id for created_body in result.created_bodies]
            design._update_design_inplace()
            return get_bodies_from_ids(design, bodies_ids)
        else:
            self._grpc_client.log.info("Failed to extrude edges.")
            return []

    @protect_grpc
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
        """
        from ansys.geometry.core.designer.edge import Edge

        edges: list[Edge] = edges if isinstance(edges, list) else [edges]
        check_type_all_elements_in_iterable(edges, Edge)

        for edge in edges:
            edge.body._reset_tessellation_cache()

        result = self._commands_stub.ExtrudeEdgesUpTo(
            ExtrudeEdgesUpToRequest(
                edges=[edge._grpc_id for edge in edges],
                up_to_selection=up_to_selection._grpc_id,
                seed_point=point3d_to_grpc_point(seed_point),
                direction=unit_vector_to_grpc_direction(direction),
                extrude_type=extrude_type.value,
            )
        )

        design = get_design_from_edge(edges[0])

        if result.success:
            bodies_ids = [created_body.id for created_body in result.created_bodies]
            design._update_design_inplace()
            return get_bodies_from_ids(design, bodies_ids)
        else:
            self._grpc_client.log.info("Failed to extrude edges.")
            return []

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def rename_object(
        self,
        selection: Union[list["Body"], list["Component"], list["Face"], list["Edge"]],
        name: str,
    ) -> bool:
        """Rename an object.

        Parameters
        ----------
        selection : list[Body] | list[Component] | list[Face] | list[Edge]
            Selection of the object to rename.
        name : str
            New name for the object.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        result = self._commands_stub.RenameObject(
            RenameObjectRequest(selection=[object._grpc_id for object in selection], name=name)
        )
        return result.success

    def create_linear_pattern(
        self,
        selection: Union["Face", list["Face"]],
        linear_direction: Union["Edge", "Face"],
        count_x: int,
        pitch_x: Real,
        two_dimensional: bool = False,
        count_y: int = None,
        pitch_y: Real = None,
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
        pitch_x : Real
            The spacing between each pattern member in the x direction.
        two_dimensional : bool, default: False
            If ``True``, create a pattern in the x and y direction.
        count_y : int, default: None
            How many times the pattern repeats in the y direction.
        pitch_y : Real, default: None
            The spacing between each pattern member in the y direction.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
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

        result = self._commands_stub.CreateLinearPattern(
            CreateLinearPatternRequest(
                selection=[object._grpc_id for object in selection],
                linear_direction=linear_direction._grpc_id,
                count_x=count_x,
                pitch_x=pitch_x,
                two_dimensional=two_dimensional,
                count_y=count_y,
                pitch_y=pitch_y,
            )
        )

        return result.result.success

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def modify_linear_pattern(
        self,
        selection: Union["Face", list["Face"]],
        count_x: int = 0,
        pitch_x: Real = 0.0,
        count_y: int = 0,
        pitch_y: Real = 0.0,
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
        pitch_x : Real, default: 0.0
            The spacing between each pattern member in the x direction.
        count_y : int, default: 0
            How many times the pattern repeats in the y direction.
        pitch_y : Real, default: 0.0
            The spacing between each pattern member in the y direction.
        new_seed_index : int, default: 0
            The new seed index of the member.
        old_seed_index : int, default: 0
            The old seed index of the member.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        result = self._commands_stub.ModifyLinearPattern(
            ModifyLinearPatternRequest(
                selection=[object._grpc_id for object in selection],
                count_x=count_x,
                pitch_x=pitch_x,
                count_y=count_y,
                pitch_y=pitch_y,
                new_seed_index=new_seed_index,
                old_seed_index=old_seed_index,
            )
        )

        return result.result.success

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def create_circular_pattern(
        self,
        selection: Union["Face", list["Face"]],
        circular_axis: "Edge",
        circular_count: int,
        circular_angle: Real,
        two_dimensional: bool = False,
        linear_count: int = None,
        linear_pitch: Real = None,
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
        circular_angle : Real
            The angular range of the pattern.
        two_dimensional : bool, default: False
            If ``True``, create a two-dimensional pattern.
        linear_count : int, default: None
            How many times the circular pattern repeats along the radial lines for a
            two-dimensional pattern.
        linear_pitch : Real, default: None
            The spacing along the radial lines for a two-dimensional pattern.
        radial_direction : UnitVector3D, default: None
            The direction from the center out for a two-dimensional pattern.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
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

        result = self._commands_stub.CreateCircularPattern(
            CreateCircularPatternRequest(
                selection=[object._grpc_id for object in selection],
                circular_axis=circular_axis._grpc_id,
                circular_count=circular_count,
                circular_angle=circular_angle,
                two_dimensional=two_dimensional,
                linear_count=linear_count,
                linear_pitch=linear_pitch,
                radial_direction=None
                if radial_direction is None
                else unit_vector_to_grpc_direction(radial_direction),
            )
        )

        return result.result.success

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def modify_circular_pattern(
        self,
        selection: Union["Face", list["Face"]],
        circular_count: int = 0,
        linear_count: int = 0,
        step_angle: Real = 0.0,
        step_linear: Real = 0.0,
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
        step_angle : Real, default: 0.0
            Defines the circular angle.
        step_linear : Real, default: 0.0
            Defines the step, along the radial lines, for a pattern dimension greater than 1.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        result = self._commands_stub.ModifyCircularPattern(
            ModifyCircularPatternRequest(
                selection=[object._grpc_id for object in selection],
                circular_count=circular_count,
                linear_count=linear_count,
                step_angle=step_angle,
                step_linear=step_linear,
            )
        )

        return result.result.success

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def create_fill_pattern(
        self,
        selection: Union["Face", list["Face"]],
        linear_direction: Union["Edge", "Face"],
        fill_pattern_type: FillPatternType,
        margin: Real,
        x_spacing: Real,
        y_spacing: Real,
        row_x_offset: Real = 0,
        row_y_offset: Real = 0,
        column_x_offset: Real = 0,
        column_y_offset: Real = 0,
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
        margin : Real
            Margin defining the border of the fill pattern.
        x_spacing : Real
            Spacing between the pattern members in the x direction.
        y_spacing : Real
            Spacing between the pattern members in the x direction.
        row_x_offset : Real, default: 0
            Offset for the rows in the x direction. Only used with ``FillPattern.SKEWED``.
        row_y_offset : Real, default: 0
            Offset for the rows in the y direction. Only used with ``FillPattern.SKEWED``.
        column_x_offset : Real, default: 0
            Offset for the columns in the x direction. Only used with ``FillPattern.SKEWED``.
        column_y_offset : Real, default: 0
            Offset for the columns in the y direction. Only used with ``FillPattern.SKEWED``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        result = self._commands_stub.CreateFillPattern(
            CreateFillPatternRequest(
                selection=[object._grpc_id for object in selection],
                linear_direction=linear_direction._grpc_id,
                fill_pattern_type=fill_pattern_type.value,
                margin=margin,
                x_spacing=x_spacing,
                y_spacing=y_spacing,
                row_x_offset=row_x_offset,
                row_y_offset=row_y_offset,
                column_x_offset=column_x_offset,
                column_y_offset=column_y_offset,
            )
        )

        return result.result.success

    @protect_grpc
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
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]

        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        result = self._commands_stub.UpdateFillPattern(
            PatternRequest(
                selection=[object._grpc_id for object in selection],
            )
        )

        return result.result.success

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def revolve_faces(
        self,
        selection: Union["Face", list["Face"]],
        axis: Line,
        angle: Real,
        extrude_type: ExtrudeType = ExtrudeType.ADD,
    ) -> list["Body"]:
        """Revolve face around an axis.

        Parameters
        ----------
        selection : Face | list[Face]
            Face(s) to revolve.
        axis : Line
            Axis of revolution.
        angle : Real
            Angular distance to revolve.
        extrude_type : ExtrudeType, default: ExtrudeType.ADD
            Type of extrusion to be performed.

        Returns
        -------
        list[Body]
            Bodies created by the extrusion if any.
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]
        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        result = self._commands_stub.RevolveFaces(
            RevolveFacesRequest(
                selection=[object._grpc_id for object in selection],
                axis=line_to_grpc_line(axis),
                angle=angle,
                extrude_type=extrude_type.value,
            )
        )

        design = get_design_from_face(selection[0])

        if result.success:
            bodies_ids = [created_body.id for created_body in result.created_bodies]
            design._update_design_inplace()
            return get_bodies_from_ids(design, bodies_ids)
        else:
            self._grpc_client.log.info("Failed to revolve faces.")
            return []

    @protect_grpc
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
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]
        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        result = self._commands_stub.RevolveFacesUpTo(
            RevolveFacesUpToRequest(
                selection=[object._grpc_id for object in selection],
                up_to_selection=up_to._grpc_id,
                axis=line_to_grpc_line(axis),
                direction=unit_vector_to_grpc_direction(direction),
                extrude_type=extrude_type.value,
            )
        )

        design = get_design_from_face(selection[0])

        if result.success:
            bodies_ids = [created_body.id for created_body in result.created_bodies]
            design._update_design_inplace()
            return get_bodies_from_ids(design, bodies_ids)
        else:
            self._grpc_client.log.info("Failed to revolve faces.")
            return []

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def revolve_faces_by_helix(
        self,
        selection: Union["Face", list["Face"]],
        axis: Line,
        direction: UnitVector3D,
        height: Real,
        pitch: Real,
        taper_angle: Real,
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
        height : Real,
            Height of the helix.
        pitch : Real,
            Pitch of the helix.
        taper_angle : Real,
            Tape angle of the helix.
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
        """
        from ansys.geometry.core.designer.face import Face

        selection: list[Face] = selection if isinstance(selection, list) else [selection]
        check_type_all_elements_in_iterable(selection, Face)

        for object in selection:
            object.body._reset_tessellation_cache()

        result = self._commands_stub.RevolveFacesByHelix(
            RevolveFacesByHelixRequest(
                selection=[object._grpc_id for object in selection],
                axis=line_to_grpc_line(axis),
                direction=unit_vector_to_grpc_direction(direction),
                height=height,
                pitch=pitch,
                taper_angle=taper_angle,
                right_handed=right_handed,
                both_sides=both_sides,
                extrude_type=extrude_type.value,
            )
        )

        design = get_design_from_face(selection[0])

        if result.success:
            bodies_ids = [created_body.id for created_body in result.created_bodies]
            design._update_design_inplace()
            return get_bodies_from_ids(design, bodies_ids)
        else:
            self._grpc_client.log.info("Failed to revolve faces.")
            return []

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
        """
        target_selection: list["Face"] = (
            target_selection if isinstance(target_selection, list) else [target_selection]
        )
        replacement_selection: list["Face"] = (
            replacement_selection
            if isinstance(replacement_selection, list)
            else [replacement_selection]
        )

        result = self._commands_stub.ReplaceFace(
            ReplaceFaceRequest(
                target_selection=[selection._grpc_id for selection in target_selection],
                replacement_selection=[selection._grpc_id for selection in replacement_selection],
            )
        )

        return result.success

    @protect_grpc
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
        """
        from ansys.geometry.core.designer.body import Body
        from ansys.geometry.core.designer.edge import Edge
        from ansys.geometry.core.designer.face import Face

        check_type_all_elements_in_iterable(bodies, Body)

        for body in bodies:
            body._reset_tessellation_cache()

        plane_item = None
        if plane is not None:
            check_type(plane, Plane)
            plane_item = plane_to_grpc_plane(plane)

        slicer_items = None
        if slicers is not None:
            slicers: list["Face", "Edge"] = slicers if isinstance(slicers, list) else [slicers]
            check_type_all_elements_in_iterable(slicers, (Edge, Face))
            slicer_items = [slicer._grpc_id for slicer in slicers]

        face_items = None
        if faces is not None:
            faces: list["Face"] = faces if isinstance(faces, list) else [faces]
            check_type_all_elements_in_iterable(faces, Face)
            face_items = [face._grpc_id for face in faces]

        result = self._commands_stub.SplitBody(
            SplitBodyRequest(
                selection=[body._grpc_id for body in bodies],
                split_by_plane=plane_item,
                split_by_slicer=slicer_items,
                split_by_faces=face_items,
                extend_surfaces=extendfaces,
            )
        )

        if result.success:
            design = get_design_from_body(bodies[0])
            design._update_design_inplace()

        return result.success

    @protect_grpc
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
        """
        result = self._commands_stub.GetRoundInfo(RoundInfoRequest(face=face._grpc_id))

        return (result.along_u, result.radius)

    @protect_grpc
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
        """
        distance = distance if isinstance(distance, Distance) else Distance(distance)
        translation_magnitude = distance.value.m_as(DEFAULT_UNITS.SERVER_LENGTH)

        result = self._commands_stub.MoveTranslate(
            MoveTranslateRequest(
                selection=[EntityIdentifier(id=selection.id)],
                direction=unit_vector_to_grpc_direction(direction),
                distance=translation_magnitude,
            )
        )

        return result.success

    @protect_grpc
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
        """
        angle = angle if isinstance(angle, Angle) else Angle(angle)
        rotation_angle = angle.value.m_as(DEFAULT_UNITS.SERVER_ANGLE)

        response = self._commands_stub.MoveRotate(
            MoveRotateRequest(
                selection=[EntityIdentifier(id=selection.id)],
                axis=line_to_grpc_line(axis),
                angle=rotation_angle,
            )
        )

        result = {}
        result["success"] = response.success
        result["modified_bodies"] = response.modified_bodies
        result["modified_faces"] = response.modified_faces
        result["modified_edges"] = response.modified_edges

        return result

    @protect_grpc
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
        """
        from ansys.geometry.core.designer.face import Face

        faces: list[Face] = faces if isinstance(faces, list) else [faces]
        check_type_all_elements_in_iterable(faces, Face)

        for face in faces:
            face.body._reset_tessellation_cache()

        radius = radius if isinstance(radius, Distance) else Distance(radius)
        radius_magnitude = radius.value.m_as(DEFAULT_UNITS.SERVER_LENGTH)

        result = self._commands_stub.OffsetFacesSetRadius(
            OffsetFacesSetRadiusRequest(
                faces=[face._grpc_id for face in faces],
                radius=radius_magnitude,
                copy=copy,
                offset_mode=offset_mode.value,
                extrude_type=extrude_type.value,
            )
        )

        return result.success
