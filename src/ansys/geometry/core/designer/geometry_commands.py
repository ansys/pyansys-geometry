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
from typing import TYPE_CHECKING, List, Union

from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
from ansys.api.geometry.v0.commands_pb2 import (
    ChamferRequest,
    CreateLinearPatternRequest,
    ExtrudeEdgesRequest,
    ExtrudeEdgesUpToRequest,
    ExtrudeFacesRequest,
    ExtrudeFacesUpToRequest,
    FilletRequest,
    FullFilletRequest,
    ModifyLinearPatternRequest,
    RenameObjectRequest,
)
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.connection.conversions import (
    point3d_to_grpc_point,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.math import Point3D, UnitVector3D
from ansys.geometry.core.misc.auxiliary import (
    get_bodies_from_ids,
    get_design_from_edge,
    get_design_from_face,
)
from ansys.geometry.core.misc.checks import (
    check_is_float_int,
    check_type_all_elements_in_iterable,
    min_backend_version,
)
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
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
        selection: Union["Edge", List["Edge"], "Face", List["Face"]],
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
        self, selection: Union["Edge", List["Edge"], "Face", List["Face"]], radius: Real
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
    def full_fillet(self, faces: List["Face"]) -> bool:
        """Create a full fillet betweens a collection of faces.

        Parameters
        ----------
        faces : List[Face]
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
        faces: Union["Face", List["Face"]],
        distance: Real,
        direction: UnitVector3D = None,
        extrude_type: ExtrudeType = ExtrudeType.ADD,
        offset_mode: OffsetMode = OffsetMode.MOVE_FACES_TOGETHER,
        pull_symmetric: bool = False,
        copy: bool = False,
        force_do_as_extrude: bool = False,
    ) -> List["Body"]:
        """Extrude a selection of faces.

        Parameters
        ----------
        faces : Face | List[Face]
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
        List[Body]
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
        faces: Union["Face", List["Face"]],
        up_to_selection: Union["Face", "Edge", "Body"],
        seed_point: Point3D,
        direction: UnitVector3D,
        extrude_type: ExtrudeType = ExtrudeType.ADD,
        offset_mode: OffsetMode = OffsetMode.MOVE_FACES_TOGETHER,
        pull_symmetric: bool = False,
        copy: bool = False,
        force_do_as_extrude: bool = False,
    ) -> List["Body"]:
        """Extrude a selection of faces up to another object.

        Parameters
        ----------
        faces : Face | List[Face]
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
        List[Body]
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
        edges: Union["Edge", List["Edge"]],
        distance: Real,
        from_face: "Face" = None,
        from_point: Point3D = None,
        direction: UnitVector3D = None,
        extrude_type: ExtrudeType = ExtrudeType.ADD,
        pull_symmetric: bool = False,
        copy: bool = False,
        natural_extension: bool = False,
    ) -> List["Body"]:
        """Extrude a selection of edges. Provide either a face or a direction and point.

        Parameters
        ----------
        edges : Edge | List[Edge]
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
        List[Body]
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
        edges: Union["Edge", List["Edge"]],
        up_to_selection: Union["Face", "Edge", "Body"],
        seed_point: Point3D,
        direction: UnitVector3D,
        extrude_type: ExtrudeType = ExtrudeType.ADD,
    ) -> List["Body"]:
        """Extrude a selection of edges up to another object.

        Parameters
        ----------
        edges : Edge | List[Edge]
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
        List[Body]
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
    def rename_object(self, selection: List[EntityIdentifier], name: str) -> bool:
        """Rename an object.

        Parameters
        ----------
        selection : List[str]
            Selection of the object to rename.
        name : str
            New name for the object.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        result = self._commands_stub.RenameObject(
            RenameObjectRequest(
                selection=[EntityIdentifier(id=entity_id) for entity_id in selection], name=name
            )
        )
        return result.success

    def create_linear_pattern(
        self,
        selection: Union["Face", List["Face"]],
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
        selection : Face | List[Face]
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
        selection: Union["Face", List["Face"]],
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
        selection : Face | List[Face]
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
