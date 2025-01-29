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
"""Provides tools for repairing bodies."""

from typing import TYPE_CHECKING

from google.protobuf.wrappers_pb2 import BoolValue, DoubleValue

from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
from ansys.api.geometry.v0.repairtools_pb2 import (
    FindAdjustSimplifyRequest,
    FindDuplicateFacesRequest,
    FindExtraEdgesRequest,
    FindInexactEdgesRequest,
    FindInterferenceRequest,
    FindMissingFacesRequest,
    FindShortEdgesRequest,
    FindSmallFacesRequest,
    FindSplitEdgesRequest,
    FindStitchFacesRequest,
)
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.misc.auxiliary import (
    get_bodies_from_ids,
    get_design_from_body,
    get_edges_from_ids,
    get_faces_from_ids,
)
from ansys.geometry.core.misc.checks import (
    check_type,
    check_type_all_elements_in_iterable,
    min_backend_version,
)
from ansys.geometry.core.tools.problem_areas import (
    DuplicateFaceProblemAreas,
    ExtraEdgeProblemAreas,
    InexactEdgeProblemAreas,
    InterferenceProblemAreas,
    MissingFaceProblemAreas,
    ShortEdgeProblemAreas,
    SmallFaceProblemAreas,
    SplitEdgeProblemAreas,
    StitchFaceProblemAreas,
    UnsimplifiedFaceProblemAreas,
)
from ansys.geometry.core.tools.repair_tool_message import RepairToolMessage
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body


class RepairTools:
    """Repair tools for PyAnsys Geometry."""

    def __init__(self, grpc_client: GrpcClient):
        """Initialize a new instance of the ``RepairTools`` class."""
        self._grpc_client = grpc_client
        self._repair_stub = RepairToolsStub(self._grpc_client.channel)
        self._bodies_stub = BodiesStub(self._grpc_client.channel)

    @protect_grpc
    def find_split_edges(
        self, bodies: list["Body"], angle: Real = 0.0, length: Real = 0.0
    ) -> list[SplitEdgeProblemAreas]:
        """Find split edges in the given list of bodies.

        This method finds the split edge problem areas and returns a list of split edge
        problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that split edges are investigated on.
        angle : Real
            The maximum angle between edges.
        length : Real
            The maximum length of the edges.

        Returns
        -------
        list[SplitEdgeProblemAreas]
            List of objects representing split edge problem areas.
        """
        if not bodies:
            return []

        angle_value = DoubleValue(value=float(angle))
        length_value = DoubleValue(value=float(length))
        body_ids = [body.id for body in bodies]

        problem_areas_response = self._repair_stub.FindSplitEdges(
            FindSplitEdgesRequest(
                bodies_or_faces=body_ids, angle=angle_value, distance=length_value
            )
        )
        parent_design = get_design_from_body(bodies[0])
        return [
            SplitEdgeProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.edge_monikers),
            )
            for res in problem_areas_response.result
        ]

    @protect_grpc
    def find_extra_edges(self, bodies: list["Body"]) -> list[ExtraEdgeProblemAreas]:
        """Find the extra edges in the given list of bodies.

        This method find the extra edge problem areas and returns a list of extra edge
        problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that extra edges are investigated on.

        Returns
        -------
        list[ExtraEdgeProblemArea]
            List of objects representing extra edge problem areas.
        """
        if not bodies:
            return []

        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindExtraEdges(
            FindExtraEdgesRequest(selection=body_ids)
        )
        parent_design = get_design_from_body(bodies[0])

        return [
            ExtraEdgeProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.edge_monikers),
            )
            for res in problem_areas_response.result
        ]

    @protect_grpc
    def find_inexact_edges(self, bodies: list["Body"]) -> list[InexactEdgeProblemAreas]:
        """Find inexact edges in the given list of bodies.

        This method find the inexact edge problem areas and returns a list of inexact
        edge problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that inexact edges are investigated on.

        Returns
        -------
        list[InExactEdgeProblemArea]
            List of objects representing inexact edge problem areas.
        """
        if not bodies:
            return []

        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindInexactEdges(
            FindInexactEdgesRequest(selection=body_ids)
        )

        parent_design = get_design_from_body(bodies[0])

        return [
            InexactEdgeProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.edge_monikers),
            )
            for res in problem_areas_response.result
        ]

    @protect_grpc
    def find_short_edges(
        self, bodies: list["Body"], length: Real = 0.0
    ) -> list[ShortEdgeProblemAreas]:
        """Find the short edge problem areas.

        This method finds the short edge problem areas and returns a list of
        these objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that short edges are investigated on.

        Returns
        -------
        list[ShortEdgeProblemAreas]
            List of objects representing short edge problem areas.
        """
        if not bodies:
            return []

        problem_areas_response = self._repair_stub.FindShortEdges(
            FindShortEdgesRequest(
                selection=[body.id for body in bodies],
                max_edge_length=DoubleValue(value=length),
            )
        )

        parent_design = get_design_from_body(bodies[0])
        return [
            ShortEdgeProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.edge_monikers),
            )
            for res in problem_areas_response.result
        ]

    @protect_grpc
    def find_duplicate_faces(self, bodies: list["Body"]) -> list[DuplicateFaceProblemAreas]:
        """Find the duplicate face problem areas.

        This method finds the duplicate face problem areas and returns a list of
        duplicate face problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that duplicate faces are investigated on.

        Returns
        -------
        list[DuplicateFaceProblemAreas]
            List of objects representing duplicate face problem areas.
        """
        if not bodies:
            return []

        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindDuplicateFaces(
            FindDuplicateFacesRequest(faces=body_ids)
        )

        parent_design = get_design_from_body(bodies[0])
        return [
            DuplicateFaceProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_faces_from_ids(parent_design, res.face_monikers),
            )
            for res in problem_areas_response.result
        ]

    @protect_grpc
    def find_missing_faces(self, bodies: list["Body"]) -> list[MissingFaceProblemAreas]:
        """Find the missing faces.

        This method find the missing face problem areas and returns a list of missing
        face problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that missing faces are investigated on.

        Returns
        -------
        list[MissingFaceProblemAreas]
            List of objects representing missing face problem areas.
        """
        if not bodies:
            return []
        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindMissingFaces(
            FindMissingFacesRequest(faces=body_ids)
        )
        parent_design = get_design_from_body(bodies[0])

        return [
            MissingFaceProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.edge_monikers),
            )
            for res in problem_areas_response.result
        ]

    @protect_grpc
    def find_small_faces(self, bodies: list["Body"]) -> list[SmallFaceProblemAreas]:
        """Find the small face problem areas.

        This method finds and returns a list of ids of small face problem areas
        objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that small faces are investigated on.

        Returns
        -------
        list[SmallFaceProblemAreas]
            List of objects representing small face problem areas.
        """
        if not bodies:
            return []

        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindSmallFaces(
            FindSmallFacesRequest(selection=body_ids)
        )
        parent_design = get_design_from_body(bodies[0])

        return [
            SmallFaceProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_faces_from_ids(parent_design, res.face_monikers),
            )
            for res in problem_areas_response.result
        ]

    @protect_grpc
    def find_stitch_faces(self, bodies: list["Body"]) -> list[StitchFaceProblemAreas]:
        """Return the list of stitch face problem areas.

        This method find the stitch face problem areas and returns a list of ids of stitch face
        problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that stitchable faces are investigated on.

        Returns
        -------
        list[StitchFaceProblemAreas]
            List of objects representing stitch face problem areas.
        """
        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindStitchFaces(
            FindStitchFacesRequest(faces=body_ids)
        )
        parent_design = get_design_from_body(bodies[0])
        return [
            StitchFaceProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_bodies_from_ids(parent_design, res.body_monikers),
            )
            for res in problem_areas_response.result
        ]

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def find_simplify(self, bodies: list["Body"]) -> list[UnsimplifiedFaceProblemAreas]:
        """Detect faces in a body that can be simplified.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies to search.

        Returns
        -------
        list[UnsimplifiedFaceProblemAreas]
            List of objects representing unsimplified face problem areas.
        """
        from ansys.geometry.core.designer.body import Body

        check_type_all_elements_in_iterable(bodies, Body)
        body_ids = [body.id for body in bodies]

        parent_design = get_design_from_body(bodies[0])
        problem_areas_response = self._repair_stub.FindAdjustSimplify(
            FindAdjustSimplifyRequest(
                selection=body_ids,
            )
        )

        return [
            UnsimplifiedFaceProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_faces_from_ids(parent_design, res.body_monikers),
            )
            for res in problem_areas_response.result
        ]

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def find_interferences(
        self, bodies: list["Body"], cut_smaller_body: bool = False
    ) -> list[InterferenceProblemAreas]:
        """Find the interference problem areas.

        Notes
        -----
        This method finds and returns a list of ids of interference problem areas
        objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that small faces are investigated on.
        cut_smaller_body : bool, optional
            Whether to cut the smaller body if an intererference is found.
            By default, False.

        Returns
        -------
        list[InterfenceProblemAreas]
            List of objects representing interference problem areas.
        """
        from ansys.geometry.core.designer.body import Body

        if not bodies:
            return []

        # Verify inputs
        check_type_all_elements_in_iterable(bodies, Body)
        check_type(cut_smaller_body, bool)

        parent_design = get_design_from_body(bodies[0])
        body_ids = [body.id for body in bodies]
        cut_smaller_body_bool = BoolValue(value=cut_smaller_body)
        problem_areas_response = self._repair_stub.FindInterference(
            FindInterferenceRequest(bodies=body_ids, cut_smaller_body=cut_smaller_body_bool)
        )

        return [
            InterferenceProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_bodies_from_ids(parent_design, res.body_monikers),
            )
            for res in problem_areas_response.result
        ]

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def find_and_fix_short_edges(
        self, bodies: list["Body"], length: Real = 0.0
    ) -> RepairToolMessage:
        """Find and fix the short edge problem areas.

        Notes
        -----
        This method finds the short edges in the bodies and fixes them.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that short edges are investigated on.
        length : Real, optional
            The maximum length of the edges. By default, 0.0.

        Returns
        -------
        RepairToolMessage
            Message containing created and/or modified bodies.
        """
        from ansys.geometry.core.designer.body import Body

        check_type_all_elements_in_iterable(bodies, Body)
        check_type(length, Real)

        if not bodies:
            return RepairToolMessage(False, [], [])

        response = self._repair_stub.FindAndFixShortEdges(
            FindShortEdgesRequest(
                selection=[body.id for body in bodies],
                max_edge_length=DoubleValue(value=length),
            )
        )

        parent_design = get_design_from_body(bodies[0])
        parent_design._update_design_inplace()
        message = RepairToolMessage(
            response.success,
            response.created_bodies_monikers,
            response.modified_bodies_monikers,
        )
        return message

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def find_and_fix_extra_edges(self, bodies: list["Body"]) -> RepairToolMessage:
        """Find and fix the extra edge problem areas.

        Notes
        -----
        This method finds the extra edges in the bodies and fixes them.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that short edges are investigated on.
        length : Real
            The maximum length of the edges.

        Returns
        -------
        RepairToolMessage
            Message containing created and/or modified bodies.
        """
        from ansys.geometry.core.designer.body import Body

        check_type_all_elements_in_iterable(bodies, Body)

        if not bodies:
            return RepairToolMessage(False, [], [])

        response = self._repair_stub.FindAndFixExtraEdges(
            FindExtraEdgesRequest(
                selection=[body.id for body in bodies],
            )
        )

        parent_design = get_design_from_body(bodies[0])
        parent_design._update_design_inplace()
        message = RepairToolMessage(
            response.success,
            response.created_bodies_monikers,
            response.modified_bodies_monikers,
        )
        return message

    @protect_grpc
    @min_backend_version(25, 2, 0)
    def find_and_fix_split_edges(
        self, bodies: list["Body"], angle: Real = 0.0, length: Real = 0.0
    ) -> RepairToolMessage:
        """Find and fix the split edge problem areas.

        Notes
        -----
        This method finds the extra edges in the bodies and fixes them.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that split edges are investigated on.
        angle : Real, optional
            The maximum angle between edges. By default, 0.0.
        length : Real, optional
            The maximum length of the edges. By default, 0.0.

        Returns
        -------
        RepairToolMessage
            Message containing created and/or modified bodies.
        """
        from ansys.geometry.core.designer.body import Body

        check_type_all_elements_in_iterable(bodies, Body)
        check_type(angle, Real)
        check_type(length, Real)

        if not bodies:
            return RepairToolMessage(False, [], [])

        angle_value = DoubleValue(value=float(angle))
        length_value = DoubleValue(value=float(length))
        body_ids = [body.id for body in bodies]

        response = self._repair_stub.FindAndFixSplitEdges(
            FindSplitEdgesRequest(
                bodies_or_faces=body_ids, angle=angle_value, distance=length_value
            )
        )

        parent_design = get_design_from_body(bodies[0])
        parent_design._update_design_inplace()
        message = RepairToolMessage(
            response.success,
            response.created_bodies_monikers,
            response.modified_bodies_monikers,
        )
        return message
