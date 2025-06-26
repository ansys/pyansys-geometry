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
"""Provides tools for preparing geometry for use with simulation."""

from typing import TYPE_CHECKING

from beartype import beartype as check_input_types

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.logger import LOG
from ansys.geometry.core.misc.auxiliary import (
    get_bodies_from_ids,
    get_design_from_edge,
    get_design_from_face,
)
from ansys.geometry.core.misc.checks import check_type_all_elements_in_iterable, min_backend_version
from ansys.geometry.core.tools.problem_areas import LogoProblemArea
from ansys.geometry.core.tools.repair_tool_message import RepairToolMessage
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.edge import Edge
    from ansys.geometry.core.designer.face import Face


class PrepareTools:
    """Prepare tools for PyAnsys Geometry.

    Parameters
    ----------
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    """

    def __init__(self, grpc_client: GrpcClient):
        """Initialize Prepare Tools class."""
        self._grpc_client = grpc_client

    @min_backend_version(25, 1, 0)
    def extract_volume_from_faces(
        self, sealing_faces: list["Face"], inside_faces: list["Face"]
    ) -> list["Body"]:
        """Extract a volume from input faces.

        Creates a volume (typically a flow volume) from a list of faces that seal the volume
        and one or more faces that define the wetted surface (inside faces of the solid).

        Parameters
        ----------
        sealing_faces : list[Face]
            List of faces that seal the volume.
        inside_faces : list[Face]
            List of faces that define the interior of the solid.

        Returns
        -------
        list[Body]
            List of created bodies.

        Warnings
        --------
        This method is only available starting on Ansys release 25R1.
        """
        from ansys.geometry.core.designer.face import Face

        if not sealing_faces or not inside_faces:
            self._grpc_client.log.info("No sealing faces or inside faces provided...")
            return []

        # Verify inputs
        check_type_all_elements_in_iterable(sealing_faces, Face)
        check_type_all_elements_in_iterable(inside_faces, Face)

        parent_design = get_design_from_face(sealing_faces[0])

        response = self._grpc_client._services.prepare_tools.extract_volume_from_faces(
            sealing_faces=sealing_faces,
            inside_faces=inside_faces,
        )

        if response.get("success"):
            bodies_ids = response.get("created_bodies")
            if len(bodies_ids) > 0:
                parent_design._update_design_inplace()
            return get_bodies_from_ids(parent_design, bodies_ids)
        else:
            self._grpc_client.log.info("Failed to extract volume from faces...")
            return []

    @min_backend_version(25, 1, 0)
    def extract_volume_from_edge_loops(
        self, sealing_edges: list["Edge"], inside_faces: list["Face"] = None
    ) -> list["Body"]:
        """Extract a volume from input edge loops.

        Creates a volume (typically a flow volume) from a list of edge loops that seal the volume.
        and one or more faces that define the wetted surface (inside faces of the solid).

        Parameters
        ----------
        sealing_edges : list[Edge]
            List of faces that seal the volume.
        inside_faces : list[Face], optional
            List of faces that define the interior of the solid (not always necessary).

        Returns
        -------
        list[Body]
            List of created bodies.

        Warnings
        --------
        This method is only available starting on Ansys release 25R1.
        """
        from ansys.geometry.core.designer.edge import Edge
        from ansys.geometry.core.designer.face import Face

        if not sealing_edges:
            self._grpc_client.log.info("No sealing edges provided...")
            return []

        # Assign default values to inside_faces
        inside_faces = [] if inside_faces is None else inside_faces

        # Verify inputs
        check_type_all_elements_in_iterable(sealing_edges, Edge)
        check_type_all_elements_in_iterable(inside_faces, Face)

        parent_design = get_design_from_edge(sealing_edges[0])

        response = self._grpc_client._services.prepare_tools.extract_volume_from_edge_loops(
            sealing_edges=sealing_edges,
            inside_faces=inside_faces,
        )

        if response.get("success"):
            bodies_ids = response.get("created_bodies")
            if len(bodies_ids) > 0:
                parent_design._update_design_inplace()
            return get_bodies_from_ids(parent_design, bodies_ids)
        else:
            self._grpc_client.log.info("Failed to extract volume from edge loops...")
            return []

    def remove_rounds(self, faces: list["Face"], auto_shrink: bool = False) -> bool:
        """Remove rounds from geometry.

        Tries to remove rounds from geometry. Faces to be removed are input to the method.

        Parameters
        ----------
        round_faces : list[Face]
            List of rounds faces to be removed
        auto_shrink : bool, default: False
            Whether to shrink the geometry after removing rounds. Fills in the gaps
            left by the removed rounds.

        Returns
        -------
        bool
            ``True`` if successful, ``False`` if failed.
        """
        from ansys.geometry.core.designer.face import Face

        if not faces:
            self._grpc_client.log.info("No faces provided...")
            return []

        # Verify inputs
        check_type_all_elements_in_iterable(faces, Face)

        parent_design = get_design_from_face(faces[0])
        response = self._grpc_client._services.prepare_tools.remove_rounds(
            rounds=faces,
            auto_shrink=auto_shrink,
        )

        if response.get("success"):
            parent_design._update_design_inplace()
        else:
            self._grpc_client.log.info("Failed to remove rounds...")

        return response.get("success")

    @min_backend_version(24, 2, 0)
    def share_topology(
        self, bodies: list["Body"], tol: Real = 0.0, preserve_instances: bool = False
    ) -> bool:
        """Share topology between the chosen bodies.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies to share topology between.
        tol : Real
            Maximum distance between bodies.
        preserve_instances : bool
            Whether instances are preserved.

        Returns
        -------
        bool
            ``True`` if successful, ``False`` if failed.

        Warnings
        --------
        This method is only available starting on Ansys release 24R2.
        """
        from ansys.geometry.core.designer.body import Body

        if not bodies:
            return False

        # Verify inputs
        check_type_all_elements_in_iterable(bodies, Body)

        response = self._grpc_client._services.prepare_tools.share_topology(
            bodies=bodies,
            tolerance=tol,
            preserve_instances=preserve_instances,
        )

        return response.get("success")

    @min_backend_version(25, 2, 0)
    def enhanced_share_topology(
        self, bodies: list["Body"], tol: Real = 0.0, preserve_instances: bool = False
    ) -> RepairToolMessage:
        """Share topology between the chosen bodies.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies to share topology between.
        tol : Real
            Maximum distance between bodies.
        preserve_instances : bool
            Whether instances are preserved.

        Returns
        -------
        RepairToolMessage
            Message containing number of problem areas found/fixed, created and/or modified bodies.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.body import Body

        if not bodies:
            return RepairToolMessage(False, [], [], 0, 0)

        # Verify inputs
        check_type_all_elements_in_iterable(bodies, Body)

        response = self._grpc_client._services.prepare_tools.enhanced_share_topology(
            bodies=bodies,
            tolerance=tol,
            preserve_instances=preserve_instances,
        )

        message = RepairToolMessage(
            success=response.get("success"),
            created_bodies=response.get("created_bodies_monikers"),
            modified_bodies=response.get("modified_bodies_monikers"),
            found=response.get("found"),
            repaired=response.get("repaired"),
        )
        return message

    @check_input_types
    @min_backend_version(25, 2, 0)
    def find_logos(
        self, bodies: list["Body"] = None, min_height: Real = None, max_height: Real = None
    ) -> "LogoProblemArea":
        """Detect logos in geometry.

        Detects logos, using a list of bodies if provided.
        The logos are returned as a list of faces.

        Parameters
        ----------
        bodies : list[Body], optional
            List of bodies where logos should be detected
        min_height : real, optional
            The minimum height when searching for logos
        max_height: real, optional
            The minimum height when searching for logos

        Returns
        -------
        LogoProblemArea
            Problem area with logo faces.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.body import Body

        if BackendType.is_linux_service(self._grpc_client.backend_type):
            # not yet available in Linux
            LOG.warning("Logo detection not available on Linux")
            return

        # Verify inputs
        if bodies and len(bodies) > 0:
            check_type_all_elements_in_iterable(bodies, Body)

        bodies = [] if bodies is None else bodies
        response = self._grpc_client._services.prepare_tools.find_logos(
            bodies=bodies,
            min_height=min_height,
            max_height=max_height,
        )

        return LogoProblemArea(
            id=response.get("id"),
            grpc_client=self._grpc_client,
            face_ids=response.get("face_ids"),
        )

    @check_input_types
    @min_backend_version(25, 2, 0)
    def find_and_remove_logos(
        self, bodies: list["Body"] = None, min_height: Real = None, max_height: Real = None
    ) -> bool:
        """Detect and remove logos in geometry.

        Detects and remove logos, using a list of bodies if provided.

        Parameters
        ----------
        bodies : list[Body], optional
            List of bodies where logos should be detected and removed.
        min_height : real, optional
            The minimum height when searching for logos
        max_height: real, optional
            The minimum height when searching for logos

        Returns
        -------
        Boolean value indicating whether the operation was successful.

        Warnings
        --------
        This method is only available starting on Ansys release 25R2.
        """
        from ansys.geometry.core.designer.body import Body

        if BackendType.is_linux_service(self._grpc_client.backend_type):
            # not yet available in Linux
            LOG.warning("Logo detection not available on Linux")
            return

        # Verify inputs
        if bodies and len(bodies) > 0:
            check_type_all_elements_in_iterable(bodies, Body)

        bodies = [] if bodies is None else bodies
        response = self._grpc_client._services.prepare_tools.find_and_remove_logos(
            bodies=bodies,
            min_height=min_height,
            max_height=max_height,
        )

        return response.get("success")
