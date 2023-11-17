# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
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
"""Module for creating a named selection."""

from ansys.api.geometry.v0.namedselections_pb2 import CreateRequest
from ansys.api.geometry.v0.namedselections_pb2_grpc import NamedSelectionsStub
from beartype import beartype as check_input_types
from beartype.typing import List, Optional

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.designer.beam import Beam
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.designer.designpoint import DesignPoint
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.errors import protect_grpc


class NamedSelection:
    """
    Represents a single named selection within the design assembly.

    This class synchronizes to a design within a supporting Geometry service instance.

    A named selection organizes one or more design entities together for common actions
    against the entire group.

    Parameters
    ----------
    name : str
        User-defined name for the named selection.
    grpc_client : GrpcClient
        Active supporting Geometry service instance for design modeling.
    bodies : List[Body], default: None
        All bodies to include in the named selection.
    faces : List[Face], default: None
        All faces to include in the named selection.
    edges : List[Edge], default: None
        All edges to include in the named selection.
    beams : List[Beam], default: None
        All beams to include in the named selection.
    design_points : List[DesignPoints], default: None
        All design points to include in the named selection.
    """

    @protect_grpc
    @check_input_types
    def __init__(
        self,
        name: str,
        grpc_client: GrpcClient,
        bodies: Optional[List[Body]] = None,
        faces: Optional[List[Face]] = None,
        edges: Optional[List[Edge]] = None,
        beams: Optional[List[Beam]] = None,
        design_points: Optional[List[DesignPoint]] = None,
        preexisting_id: Optional[str] = None,
    ):
        """Initialize the ``NamedSelection`` class."""
        self._grpc_client = grpc_client
        self._named_selections_stub = NamedSelectionsStub(grpc_client.channel)

        if preexisting_id:
            self._id = preexisting_id
            self._name = name
            return

        # All ids should be unique - no duplicated values
        ids = set()

        if bodies is None:
            bodies = []
        if faces is None:
            faces = []
        if edges is None:
            edges = []
        if beams is None:
            beams = []
        if design_points is None:
            design_points = []

        # Loop over bodies, faces and edges
        [ids.add(body.id) for body in bodies]
        [ids.add(face.id) for face in faces]
        [ids.add(edge.id) for edge in edges]
        [ids.add(beam.id) for beam in beams]
        [ids.add(dp.id) for dp in design_points]

        named_selection_request = CreateRequest(name=name, members=ids)
        self._grpc_client.log.debug("Requesting creation of named selection.")
        new_named_selection = self._named_selections_stub.Create(named_selection_request)
        self._id = new_named_selection.id
        self._name = new_named_selection.name

    @property
    def id(self) -> str:
        """ID of the named selection."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the named selection."""
        return self._name
