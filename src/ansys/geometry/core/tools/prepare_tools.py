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

from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
from ansys.api.geometry.v0.preparetools_pb2 import (
    ExtractVolumeFromEdgeLoopsRequest,
    ExtractVolumeFromFacesRequest,
)
from ansys.api.geometry.v0.preparetools_pb2_grpc import PrepareToolsStub
from beartype.typing import TYPE_CHECKING, List

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.misc.auxiliary import (
    get_bodies_from_ids,
    get_design_from_body,
)

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.edge import Edge
    from ansys.geometry.core.designer.face import Face

class PrepareTools:
    """Prepare tools for PyAnsys Geometry."""

    def __init__(self, grpc_client: GrpcClient):
        """Initialize Prepare Tools class."""
        self._grpc_client = grpc_client
        self._prepare_stub = PrepareToolsStub(self._grpc_client.channel)

    def extract_volume_from_faces(
        self, sealing_faces: List["Face"],  inside_faces: List["Face"]
    ) -> List["Body"]:
        """Extract a volume from input faces.

        Creates a volume (typically a flow volume) from a list of faces that seal the volume
        and one or more faces that define the wetted surface (inside faces of the solid).

        Parameters
        ----------
        sealing_faces : List[Face]
            List of faces that seal the volume.
        inside_faces : List[Face]
            List of faces that define the interior of the solid.

        Returns
        -------
        List[Body]
            List of created bodies.
        """
        if not sealing_faces or not inside_faces:
            return []

        parent_design = get_design_from_body(sealing_faces[0].body)

        sealing_faces_ids = [EntityIdentifier(id = face.id) for face in sealing_faces]
        inside_faces_ids = [EntityIdentifier(id = face.id) for face in inside_faces]


        volume_extract_response = self._prepare_stub.ExtractVolumeFromFaces
        (ExtractVolumeFromFacesRequest(
            sealing_faces=sealing_faces_ids,
            inside_faces=inside_faces_ids)
        )

        bodies_ids = [created_body.id for created_body in volume_extract_response.created_bodies]
        if (len (bodies_ids) > 0):
            parent_design._update_design_inplace()
        return get_bodies_from_ids(parent_design, bodies_ids)

    def extract_volume_from_edge_loops(
        self, sealing_edges: List["Edge"],  inside_faces: List["Face"]
    ) -> List["Body"]:
        """Extract a volume from input edge loops.

        Creates a volume (typically a flow volume) from a list of edge loops that seal the volume.
        and one or more faces that define the wetted surface (inside faces of the solid).

        Parameters
        ----------
        sealing_edges : List[Edge]
            List of faces that seal the volume.
        inside_faces : List[Face]
            List of faces that define the interior of the solid (Not always necessary).

        Returns
        -------
        List[Body]
            List of created bodies.
        """
        if not sealing_edges:
            return []

        parent_body = sealing_edges[0].faces[0].body
        parent_design = get_design_from_body(parent_body)

        sealing_edges_ids = [EntityIdentifier(id = face.id) for face in sealing_edges]
        inside_faces_ids = [EntityIdentifier(id = face.id) for face in inside_faces]


        volume_extract_response = self._prepare_stub.ExtractVolumeFromEdgeLoops
        (ExtractVolumeFromEdgeLoopsRequest(
            sealing_edges=sealing_edges_ids,
            inside_faces=inside_faces_ids)
        )

        bodies_ids = [created_body.id for created_body in volume_extract_response.created_bodies]
        if (len (bodies_ids) > 0):
            parent_design._update_design_inplace()
        return get_bodies_from_ids(parent_design, bodies_ids)


