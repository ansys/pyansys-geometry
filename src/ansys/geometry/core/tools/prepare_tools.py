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
"""Provides tools for preparing geometry for use with simulation."""

from typing import TYPE_CHECKING

from beartype import beartype as check_input_types
from google.protobuf.wrappers_pb2 import BoolValue, DoubleValue

from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
from ansys.api.geometry.v0.models_pb2 import Body as GRPCBody
from ansys.api.geometry.v0.preparetools_pb2 import (
    ExtractVolumeFromEdgeLoopsRequest,
    ExtractVolumeFromFacesRequest,
    ShareTopologyRequest,
)
from ansys.api.geometry.v0.preparetools_pb2_grpc import PrepareToolsStub
from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.misc.auxiliary import (
    get_bodies_from_ids,
    get_design_from_edge,
    get_design_from_face,
)
from ansys.geometry.core.misc.checks import min_backend_version
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
        self._prepare_stub = PrepareToolsStub(self._grpc_client.channel)

    @protect_grpc
    @check_input_types
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
        """
        if not sealing_faces or not inside_faces:
            self._grpc_client.log.info("No sealing faces or inside faces provided...")
            return []

        parent_design = get_design_from_face(sealing_faces[0])

        response = self._prepare_stub.ExtractVolumeFromFaces(
            ExtractVolumeFromFacesRequest(
                sealing_faces=[EntityIdentifier(id=face.id) for face in sealing_faces],
                inside_faces=[EntityIdentifier(id=face.id) for face in inside_faces],
            )
        )

        if response.success:
            bodies_ids = [created_body.id for created_body in response.created_bodies]
            if len(bodies_ids) > 0:
                parent_design._update_design_inplace()
            return get_bodies_from_ids(parent_design, bodies_ids)
        else:
            self._grpc_client.log.info("Failed to extract volume from faces...")
            return []

    @protect_grpc
    @check_input_types
    @min_backend_version(25, 1, 0)
    def extract_volume_from_edge_loops(
        self, sealing_edges: list["Edge"], inside_faces: list["Face"]
    ) -> list["Body"]:
        """Extract a volume from input edge loops.

        Creates a volume (typically a flow volume) from a list of edge loops that seal the volume.
        and one or more faces that define the wetted surface (inside faces of the solid).

        Parameters
        ----------
        sealing_edges : list[Edge]
            List of faces that seal the volume.
        inside_faces : list[Face]
            List of faces that define the interior of the solid (Not always necessary).

        Returns
        -------
        list[Body]
            List of created bodies.
        """
        if not sealing_edges:
            self._grpc_client.log.info("No sealing edges provided...")
            return []

        parent_design = get_design_from_edge(sealing_edges[0])

        response = self._prepare_stub.ExtractVolumeFromEdgeLoops(
            ExtractVolumeFromEdgeLoopsRequest(
                sealing_edges=[EntityIdentifier(id=face.id) for face in sealing_edges],
                inside_faces=[EntityIdentifier(id=face.id) for face in inside_faces],
            )
        )

        if response.success:
            bodies_ids = [created_body.id for created_body in response.created_bodies]
            if len(bodies_ids) > 0:
                parent_design._update_design_inplace()
            return get_bodies_from_ids(parent_design, bodies_ids)
        else:
            self._grpc_client.log.info("Failed to extract volume from edge loops...")
            return []

    @protect_grpc
    @check_input_types
    @min_backend_version(25, 1, 0)
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
        """
        if not bodies:
            return False

        share_topo_response = self._prepare_stub.ShareTopology(
            ShareTopologyRequest(
                selection=[GRPCBody(id=body.id) for body in bodies],
                tolerance=DoubleValue(value=tol),
                preserve_instances=BoolValue(value=preserve_instances),
            )
        )
        return share_topo_response.result
