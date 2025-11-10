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

import pint

import ansys.geometry.core as pyansys_geometry
from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import GeometryRuntimeError
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
from ansys.geometry.core.misc.measurements import Angle, Area, Distance
from ansys.geometry.core.tools.check_geometry import GeometryIssue, InspectResult
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
    from ansys.geometry.core.modeler import Modeler


class RepairTools:
    """Repair tools for PyAnsys Geometry.

    Parameters
    ----------
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    modeler : Modeler
        The parent modeler instance.
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
    ``modeler.repair_tools`` instead.
    """

    def __init__(self, grpc_client: GrpcClient, modeler: "Modeler", _internal_use: bool = False):
        """Initialize a new instance of the ``RepairTools`` class."""
        if not _internal_use:
            raise GeometryRuntimeError(
                "RepairTools should not be instantiated directly. "
                "Use 'modeler.repair_tools' to access repair tools."
            )
        self._modeler = modeler
        self._grpc_client = grpc_client

    def find_split_edges(
        self,
        bodies: list["Body"],
        angle: Angle | pint.Quantity | Real = None,
        length: Distance | pint.Quantity | Real = None,
    ) -> list[SplitEdgeProblemAreas]:
        """Find split edges in the given list of bodies.

        This method finds the split edge problem areas and returns a list of split edge
        problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that split edges are investigated on.
        angle : Angle | ~pint.Quantity | Real
            The maximum angle between edges. By default, None.
        length : Distance | ~pint.Quantity | Real
            The maximum length of the edges. By default, None.

        Returns
        -------
        list[SplitEdgeProblemAreas]
            List of objects representing split edge problem areas.
        """
        if not bodies:
            return []

        body_ids = [body.id for body in bodies]

        # Convert the measurement objects
        angle = angle if isinstance(angle, Angle) else Angle(angle) if angle is not None else None
        length = (
            length
            if isinstance(length, Distance)
            else Distance(length)
            if length is not None
            else None
        )

        print("angle:", angle)
        print("length:", length)
        response = self._grpc_client.services.repair_tools.find_split_edges(
            bodies_or_faces=body_ids, angle=angle, distance=length
        )

        parent_design = get_design_from_body(bodies[0])
        return [
            SplitEdgeProblemAreas(
                f"{res.get('id')}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.get("edges")),
            )
            for res in response.get("problems")
        ]

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
        response = self._grpc_client.services.repair_tools.find_extra_edges(selection=body_ids)
        parent_design = get_design_from_body(bodies[0])

        return [
            ExtraEdgeProblemAreas(
                f"{res.get('id')}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.get("edges")),
            )
            for res in response.get("problems")
        ]

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
        response = self._grpc_client.services.repair_tools.find_inexact_edges(selection=body_ids)

        parent_design = get_design_from_body(bodies[0])

        return [
            InexactEdgeProblemAreas(
                f"{res.get('id')}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.get("edges")),
            )
            for res in response.get("problems")
        ]

    def find_short_edges(
        self, bodies: list["Body"], length: Distance | pint.Quantity | Real = 0.0
    ) -> list[ShortEdgeProblemAreas]:
        """Find the short edge problem areas.

        This method finds the short edge problem areas and returns a list of
        these objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that short edges are investigated on.
        length : Distance | ~pint.Quantity | Real, optional
            The maximum length of the edges. By default, 0.0.

        Returns
        -------
        list[ShortEdgeProblemAreas]
            List of objects representing short edge problem areas.
        """
        if not bodies:
            return []

        body_ids = [body.id for body in bodies]

        # Convert the measurement object
        length = length if isinstance(length, Distance) else Distance(length)

        response = self._grpc_client.services.repair_tools.find_short_edges(
            selection=body_ids, length=length
        )

        parent_design = get_design_from_body(bodies[0])
        return [
            ShortEdgeProblemAreas(
                f"{res.get('id')}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.get("edges")),
            )
            for res in response.get("problems")
        ]

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
        response = self._grpc_client.services.repair_tools.find_duplicate_faces(faces=body_ids)

        parent_design = get_design_from_body(bodies[0])
        return [
            DuplicateFaceProblemAreas(
                f"{res.get('id')}",
                self._grpc_client,
                get_faces_from_ids(parent_design, res.get("faces")),
            )
            for res in response.get("problems")
        ]

    def find_missing_faces(
        self,
        bodies: list["Body"],
        angle: Angle | pint.Quantity | Real | None = None,
        distance: Distance | pint.Quantity | Real | None = None,
    ) -> list[MissingFaceProblemAreas]:
        """Find the missing faces.

        This method find the missing face problem areas and returns a list of missing
        face problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that missing faces are investigated on.
        angle : Angle | ~pint.Quantity | Real, optional
            The minimum angle between faces. By default, None.
            This option is only used if the backend version is 26.1 or higher.
        distance : Distance | ~pint.Quantity | Real, optional
            The minimum distance between faces. By default, None.
            This option is only used if the backend version is 26.1 or higher.

        Returns
        -------
        list[MissingFaceProblemAreas]
            List of objects representing missing face problem areas.
        """
        if not bodies:
            return []

        # Perform sanity check
        if angle is not None:
            angle = angle if isinstance(angle, Angle) else Angle(angle)
        if distance is not None:
            distance = distance if isinstance(distance, Distance) else Distance(distance)

        body_ids = [body.id for body in bodies]
        response = self._grpc_client.services.repair_tools.find_missing_faces(
            faces=body_ids,
            angle=angle,
            distance=distance,
            backend_version=self._grpc_client.backend_version,
        )
        parent_design = get_design_from_body(bodies[0])

        return [
            MissingFaceProblemAreas(
                f"{res.get('id')}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.get("edges")),
            )
            for res in response.get("problems")
        ]

    def find_small_faces(
        self,
        bodies: list["Body"],
        area: Area | pint.Quantity | Real | None = None,
        width: Distance | pint.Quantity | Real | None = None,
    ) -> list[SmallFaceProblemAreas]:
        """Find the small face problem areas.

        This method finds and returns a list of ids of small face problem areas
        objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that small faces are investigated on.
        area : Area | ~pint.Quantity | Real, optional
            Maximum area of the faces. By default, None.
            This option is only used if the backend version is 26.1 or higher.
        width : Distance | ~pint.Quantity | Real, optional
            Maximum width of the faces. By default, None.
            This option is only used if the backend version is 26.1 or higher.

        Returns
        -------
        list[SmallFaceProblemAreas]
            List of objects representing small face problem areas.
        """
        if not bodies:
            return []

        body_ids = [body.id for body in bodies]

        if area is not None:
            area = area if isinstance(area, Area) else Area(area)
        if width is not None:
            width = width if isinstance(width, Distance) else Distance(width)

        response = self._grpc_client.services.repair_tools.find_small_faces(
            selection=body_ids,
            area=area,
            width=width,
            backend_version=self._grpc_client.backend_version,
        )
        parent_design = get_design_from_body(bodies[0])

        return [
            SmallFaceProblemAreas(
                f"{res.get('id')}",
                self._grpc_client,
                get_faces_from_ids(parent_design, res.get("faces")),
            )
            for res in response.get("problems")
        ]

    def find_stitch_faces(
        self,
        bodies: list["Body"],
        max_distance: Distance | pint.Quantity | Real | None = None,
    ) -> list[StitchFaceProblemAreas]:
        """Return the list of stitch face problem areas.

        This method find the stitch face problem areas and returns a list of ids of stitch face
        problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that stitchable faces are investigated on.
        max_distance : Distance | ~pint.Quantity | Real, optional
            Maximum distance between faces. By default, None.
            This option is only used if the backend version is 26.1 or higher.

        Returns
        -------
        list[StitchFaceProblemAreas]
            List of objects representing stitch face problem areas.
        """
        from ansys.geometry.core.designer.body import Body

        # Perform sanity check
        check_type_all_elements_in_iterable(bodies, Body)
        if max_distance is not None:
            max_distance = (
                max_distance if isinstance(max_distance, Distance) else Distance(max_distance)
            )

        body_ids = [body.id for body in bodies]
        response = self._grpc_client.services.repair_tools.find_stitch_faces(
            faces=body_ids,
            distance=max_distance,
            backend_version=self._grpc_client.backend_version,
        )
        parent_design = get_design_from_body(bodies[0])
        return [
            StitchFaceProblemAreas(
                f"{res.get('id')}",
                self._grpc_client,
                get_bodies_from_ids(parent_design, res.get("bodies")),
            )
            for res in response.get("problems")
        ]

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

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.body import Body

        check_type_all_elements_in_iterable(bodies, Body)
        body_ids = [body.id for body in bodies]

        parent_design = get_design_from_body(bodies[0])
        response = self._grpc_client.services.repair_tools.find_simplify(selection=body_ids)

        return [
            UnsimplifiedFaceProblemAreas(
                f"{res.get('id')}",
                self._grpc_client,
                get_faces_from_ids(parent_design, res.get("bodies")),
            )
            for res in response.get("problems")
        ]

    @min_backend_version(25, 2, 0)
    def find_interferences(
        self, bodies: list["Body"], cut_smaller_body: bool = False
    ) -> list[InterferenceProblemAreas]:
        """Find the interference problem areas.

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

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.body import Body

        if not bodies:
            return []

        # Verify inputs
        check_type_all_elements_in_iterable(bodies, Body)
        check_type(cut_smaller_body, bool)

        parent_design = get_design_from_body(bodies[0])
        body_ids = [body.id for body in bodies]
        response = self._grpc_client.services.repair_tools.find_interferences(
            bodies=body_ids, cut_smaller_body=cut_smaller_body
        )

        return [
            InterferenceProblemAreas(
                f"{res.get('id')}",
                self._grpc_client,
                get_bodies_from_ids(parent_design, res.get("bodies")),
            )
            for res in response.get("problems")
        ]

    @min_backend_version(25, 2, 0)
    def find_and_fix_short_edges(
        self,
        bodies: list["Body"],
        length: Distance | pint.Quantity | Real = 0.0,
        comprehensive_result: bool = False,
    ) -> RepairToolMessage:
        """Find and fix the short edge problem areas.

        This method finds the short edges in the bodies and fixes them.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that short edges are investigated on.
        length : Distance | ~pint.Quantity | Real, optional
            The maximum length of the edges. By default, 0.0.
        comprehensive_result : bool, optional
            Whether to fix all problem areas individually.
            By default, False.

        Returns
        -------
        RepairToolMessage
            Message containing number of problem areas found/fixed, created and/or modified bodies.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.body import Body

        check_type_all_elements_in_iterable(bodies, Body)
        check_type(length, (Distance, pint.Quantity, Real))
        check_type(comprehensive_result, bool)

        if not bodies:
            return RepairToolMessage(
                success=False, created_bodies=[], modified_bodies=[], found=0, repaired=0
            )

        body_ids = [body.id for body in bodies]
        parent_design = get_design_from_body(bodies[0])
        length = length if isinstance(length, Distance) else Distance(length)

        response = self._grpc_client.services.repair_tools.find_and_fix_short_edges(
            selection=body_ids,
            parent_design=parent_design,
            length=length,
            comprehensive_result=comprehensive_result,
        )

        # Update existing design
        if not pyansys_geometry.USE_TRACKER_TO_UPDATE_DESIGN:
            parent_design._update_design_inplace()
        else:
            parent_design._update_from_tracker(response["complete_command_response"])

        # Build the response message
        return self.__build_repair_tool_message(response)

    @min_backend_version(25, 2, 0)
    def find_and_fix_extra_edges(
        self, bodies: list["Body"], comprehensive_result: bool = False
    ) -> RepairToolMessage:
        """Find and fix the extra edge problem areas.

        This method finds the extra edges in the bodies and fixes them.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that short edges are investigated on.
        comprehensive_result : bool, optional
            Whether to fix all problem areas individually.
            By default, False.

        Returns
        -------
        RepairToolMessage
            Message containing number of problem areas found/fixed, created and/or modified bodies.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.body import Body

        check_type_all_elements_in_iterable(bodies, Body)
        check_type(comprehensive_result, bool)

        if not bodies:
            return RepairToolMessage(
                success=False, created_bodies=[], modified_bodies=[], found=0, repaired=0
            )

        body_ids = [body.id for body in bodies]
        parent_design = get_design_from_body(bodies[0])
        response = self._grpc_client.services.repair_tools.find_and_fix_extra_edges(
            selection=body_ids,
            parent_design=parent_design,
            comprehensive_result=comprehensive_result,
        )

        # Update existing design
        if not pyansys_geometry.USE_TRACKER_TO_UPDATE_DESIGN:
            parent_design._update_design_inplace()
        else:
            parent_design._update_from_tracker(response["complete_command_response"])

        # Build the response message
        return self.__build_repair_tool_message(response)

    @min_backend_version(25, 2, 0)
    def find_and_fix_split_edges(
        self,
        bodies: list["Body"],
        angle: Angle | pint.Quantity | Real = 0.0,
        length: Distance | pint.Quantity | Real = 0.0,
        comprehensive_result: bool = False,
    ) -> RepairToolMessage:
        """Find and fix the split edge problem areas.

        This method finds the extra edges in the bodies and fixes them.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that split edges are investigated on.
        angle : Angle | ~pint.Quantity | Real, optional
            The maximum angle between edges. By default, 0.0.
        length : Distance | ~pint.Quantity | Real, optional
            The maximum length of the edges. By default, 0.0.
        comprehensive_result : bool, optional
            Whether to fix all problem areas individually.
            By default, False.

        Returns
        -------
        RepairToolMessage
            Message containing number of problem areas found/fixed, created and/or modified bodies.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.body import Body

        check_type_all_elements_in_iterable(bodies, Body)
        check_type(angle, (Angle, pint.Quantity, Real))
        check_type(length, (Distance, pint.Quantity, Real))
        check_type(comprehensive_result, bool)

        if not bodies:
            return RepairToolMessage(
                success=False, created_bodies=[], modified_bodies=[], found=0, repaired=0
            )

        body_ids = [body.id for body in bodies]
        parent_design = get_design_from_body(bodies[0])

        # Convert the measurement objects
        angle = angle if isinstance(angle, Angle) else Angle(angle)
        length = length if isinstance(length, Distance) else Distance(length)

        response = self._grpc_client.services.repair_tools.find_and_fix_split_edges(
            bodies_or_faces=body_ids,
            parent_design=parent_design,
            angle=angle,
            length=length,
            comprehensive_result=comprehensive_result,
        )

        # Update existing design
        if not pyansys_geometry.USE_TRACKER_TO_UPDATE_DESIGN:
            parent_design._update_design_inplace()
        else:
            parent_design._update_from_tracker(response["complete_command_response"])

        # Build the response message
        return self.__build_repair_tool_message(response)

    @min_backend_version(25, 2, 0)
    def find_and_fix_simplify(
        self, bodies: list["Body"], comprehensive_result: bool = False
    ) -> RepairToolMessage:
        """Find and simplify the provided geometry.

        This method simplifies the provided geometry.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies to be simplified.
        comprehensive_result : bool, optional
            Whether to fix all problem areas individually.
            By default, False.

        Returns
        -------
        RepairToolMessage
            Message containing number of problem areas found/fixed, created and/or modified bodies.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.body import Body

        check_type_all_elements_in_iterable(bodies, Body)
        check_type(comprehensive_result, bool)

        if not bodies:
            return RepairToolMessage(
                success=False, created_bodies=[], modified_bodies=[], found=0, repaired=0
            )

        body_ids = [body.id for body in bodies]
        parent_design = get_design_from_body(bodies[0])

        response = self._grpc_client.services.repair_tools.find_and_fix_simplify(
            selection=body_ids,
            parent_design=parent_design,
            comprehensive_result=comprehensive_result,
        )

        # Update existing design
        if not pyansys_geometry.USE_TRACKER_TO_UPDATE_DESIGN:
            parent_design._update_design_inplace()
        else:
            parent_design._update_from_tracker(response["complete_command_response"])

        # Build the response message
        return self.__build_repair_tool_message(response)

    @min_backend_version(25, 2, 0)
    def find_and_fix_stitch_faces(
        self,
        bodies: list["Body"],
        max_distance: Distance | pint.Quantity | Real | None = None,
        allow_multiple_bodies: bool = False,
        maintain_components: bool = True,
        check_for_coincidence: bool = False,
        comprehensive_result: bool = False,
    ) -> RepairToolMessage:
        """Find and fix the stitch face problem areas.

        This method finds the stitchable faces and fixes them.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that stitchable faces are investigated on.
        max_distance : Distance | ~pint.Quantity | Real, optional
            The maximum distance between faces to be stitched.
            By default, 0.0001.
        allow_multiple_bodies : bool, optional
            Whether to allow multiple bodies in the result.
            By default, False.
        maintain_components : bool, optional
            Whether to stitch bodies within the components.
            By default, True.
        check_for_coincidence : bool, optional
            Whether coincidence surfaces are searched.
            By default, False.
        comprehensive_result : bool, optional
            Whether to fix all problem areas individually.
            By default, False.

        Returns
        -------
        RepairToolMessage
            Message containing number of problem areas found/fixed, created and/or modified bodies.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.body import Body

        # Perform sanity check
        check_type_all_elements_in_iterable(bodies, Body)
        if max_distance is not None:
            max_distance = (
                max_distance if isinstance(max_distance, Distance) else Distance(max_distance)
            )

        body_ids = [body.id for body in bodies]
        parent_design = get_design_from_body(bodies[0])

        response = self._grpc_client.services.repair_tools.find_and_fix_stitch_faces(
            body_ids=body_ids,
            parent_design=parent_design,
            max_distance=max_distance,
            allow_multiple_bodies=allow_multiple_bodies,
            maintain_components=maintain_components,
            check_for_coincidence=check_for_coincidence,
            comprehensive_result=comprehensive_result,
        )

        # Update existing design
        if not pyansys_geometry.USE_TRACKER_TO_UPDATE_DESIGN:
            parent_design._update_design_inplace()
        else:
            parent_design._update_from_tracker(response["complete_command_response"])

        # Build the response message
        return self.__build_repair_tool_message(response)

    @min_backend_version(25, 2, 0)
    def inspect_geometry(self, bodies: list["Body"] = None) -> list[InspectResult]:
        """Return a list of geometry issues organized by body.

        This method inspects the geometry and returns a list of the issues grouped by
        the body where they are found.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies to inspect the geometry for.
            All bodies are inspected if the argument is not given.

        Returns
        -------
        list[IssuesByBody]
            List of objects representing geometry issues and the bodies where issues are found.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        response = self._grpc_client.services.repair_tools.inspect_geometry(
            body_ids=[] if bodies is None else [b.id for b in bodies]
        )
        return self.__create_inspect_result_from_response(response.get("issues_by_body"))

    def __create_inspect_result_from_response(
        self, inspect_geometry_results: list[dict]
    ) -> list[InspectResult]:
        inspect_results = []
        design = self._modeler.get_active_design()
        for inspect_geometry_result in inspect_geometry_results:
            body = get_bodies_from_ids(design, [inspect_geometry_result["body"]["id"]])
            issues = self.__create_issues_from_response(inspect_geometry_result.get("issues"))
            inspect_result = InspectResult(
                grpc_client=self._grpc_client, body=body[0], issues=issues
            )
            inspect_results.append(inspect_result)

        return inspect_results

    def __create_issues_from_response(
        self,
        inspect_geometry_result_issues: list[dict],
    ) -> list[GeometryIssue]:
        issues = []
        for issue in inspect_geometry_result_issues:
            message_type = issue.get("message_type")
            message_id = issue.get("message_id")
            message = issue.get("message")

            faces = [face["id"] for face in issue.get("faces", [])]
            edges = [edge["id"] for edge in issue.get("edges", [])]

            geometry_issue = GeometryIssue(
                message_type=message_type,
                message_id=message_id,
                message=message,
                faces=faces,
                edges=edges,
            )
            issues.append(geometry_issue)
        return issues

    @min_backend_version(25, 2, 0)
    def repair_geometry(self, bodies: list["Body"] = None) -> RepairToolMessage:
        """Attempt to repair the geometry for the given bodies.

        This method inspects the geometry for the given bodies and attempts to repair them.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies where to attempt to repair the geometry.
            All bodies are repaired if the argument is not given.

        Returns
        -------
        RepairToolMessage
            Message containing success of the operation.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        response = self._grpc_client.services.repair_tools.repair_geometry(
            body_ids=[] if bodies is None else [b.id for b in bodies],
        )

        return self.__build_repair_tool_message(response)

    def __build_repair_tool_message(self, response: dict) -> RepairToolMessage:
        """Build a repair tool message from the service response.

        Parameters
        ----------
        response : dict
            The response from the service containing information about the repair operation.

        Returns
        -------
        RepairToolMessage
            A message containing the success status, created bodies, modified bodies,
            number of found problem areas, and number of repaired problem areas.
        """
        return RepairToolMessage(
            success=response.get("success"),
            created_bodies=response.get("created_bodies_monikers", []),
            modified_bodies=response.get("modified_bodies_monikers", []),
            found=response.get("found", -1),
            repaired=response.get("repaired", -1),
        )
