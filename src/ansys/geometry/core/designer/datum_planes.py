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
"""Provides for managing a user-defined datum plane."""

from typing import TYPE_CHECKING

from ansys.api.geometry.v0.datumplanes_pb2 import DeleteRequest
from ansys.api.geometry.v0.datumplanes_pb2_grpc import DatumPlanesStub
from ansys.api.geometry.v0.commands_pb2 import CreatePlaneRequest, MoveTranslateRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from ansys.api.geometry.v0.models_pb2 import (DatumPlane as GRPCDatumPlane)
from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.conversions import unit_vector_to_grpc_direction
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.designer.face import Face
from pint import Quantity
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Distance
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.component import Component


class DatumPlanes:
    """Represents a user-defined datum plane within the design assembly.

    This class synchronizes to a design within a supporting Geometry
    service instance.

    Parameters
    ----------
    name : str
        User-defined label for the datum plane.
    frame : Frame
        Frame defining the datum plane bounds.
    parent_component : Component, default: Component
        Parent component the datum plane is assigned against.
    grpc_client : GrpcClient
        Active supporting Geometry service instance for design modeling.
    """

    @protect_grpc
    def __init__(
        self,
        name: str,
        parent_component: "Component",
        grpc_client: GrpcClient,
        bodies: list[Body] | None = None,
        faces: list[Face] | None = None,
        edges: list[Edge] | None = None,
        preexisting_id: str | None = None,
    ):
        """Initialize the ``CoordinateSystem`` class."""
        self._parent_component = parent_component
        self._grpc_client = grpc_client
        self._datum_planes_stub = DatumPlanesStub(grpc_client.channel)
        self._is_alive = True

        # Create without going to server
        if preexisting_id:
            self._name = name
            self._id = preexisting_id
            return
        
        # All ids should be unique - no duplicated values
        ids = list()

        if bodies is None:
            bodies = []
        if faces is None:
            faces = []
        if edges is None:
            edges = []

        # Loop over bodies, faces and edges
        [ids.append(body._grpc_id) for body in bodies]
        [ids.append(face._grpc_id) for face in faces]
        [ids.append(edge._grpc_id) for edge in edges]

        self._grpc_client.log.debug("Requesting creation of a datum plane.")
        commands_stub = CommandsStub(grpc_client.channel)
        new_datum_plane = commands_stub.CreatePlane( CreatePlaneRequest(selection = ids) ).planes[0]
        self._init_data(new_datum_plane)
        
    def _init_data(self, datum_plane:"GRPCDatumPlane") -> None:
        """Initialize the datum plane data."""
        
        self._id = datum_plane.id
        self._name = datum_plane.name
        self._plane = Plane(
            Point3D(
                [
                    datum_plane.plane.frame.origin.x,
                    datum_plane.plane.frame.origin.y,
                    datum_plane.plane.frame.origin.z,
                ],
                DEFAULT_UNITS.SERVER_LENGTH,
            ),
            UnitVector3D(
                [
                    datum_plane.plane.frame.dir_x.x,
                    datum_plane.plane.frame.dir_x.y,
                    datum_plane.plane.frame.dir_x.z,
                ]
            ),
            UnitVector3D(
                [
                    datum_plane.plane.frame.dir_y.x,
                    datum_plane.plane.frame.dir_y.y,
                    datum_plane.plane.frame.dir_y.z,
                ]
            ),
        )
        
        
    def __del__(self): 
        """Delete the datum plane."""
        ids = set()
        ids.add(self._id)
        self._datum_planes_stub.Delete(DeleteRequest(selection = ids))
        
    def Translate(self, direction: UnitVector3D, distance: Quantity | Distance | Real
    ) -> None:
        distance = distance if isinstance(distance, Distance) else Distance(distance)
        translation_magnitude = distance.value.m_as(DEFAULT_UNITS.SERVER_LENGTH)
        grpc_direction = unit_vector_to_grpc_direction(direction)
        self._grpc_client.log.debug(f"Translating body {self.id}.")
        commands_stub = CommandsStub(self._grpc_client.channel)
        ids = list()
        ids.append(self._id)
        commands_stub.MoveTranslate(MoveTranslateRequest(selection=ids, direction=grpc_direction, distance=translation_magnitude))
    
    def update(self)->None:
        updated_datum_plane = self._datum_planes_stub.Get(self._id)
        self._init_data(updated_datum_plane)
    
    @property
    def id(self) -> str:
        """ID of the datum plane."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the datum plane."""
        return self._name

    @property
    def plane(self) -> Plane:
        """Plane of the datum plane."""
        return self._plane

    @property
    def parent_component(self) -> "Component":
        """Parent component of the datum plane."""
        return self._parent_component

    @property
    def is_alive(self) -> bool:
        """Flag indicating if datum plane is still alive on the server."""
        return self._is_alive

    def __repr__(self) -> str:
        """Represent the datum plane as a string."""
        lines = [f"ansys.geometry.core.designer.CoordinateSystem {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Exists               : {self.is_alive}")
        lines.append(f"  Parent component     : {self.parent_component.name}")
        lines.append(
            f"  Frame origin         : [{','.join([str(x) for x in self.plane.origin])}] in meters"
        )
        lines.append(
            f"  Frame X-direction    : [{','.join([str(x) for x in self.plane.direction_x])}]"
        )
        lines.append(
            f"  Frame Y-direction    : [{','.join([str(x) for x in self.plane.direction_y])}]"
        )
        lines.append(
            f"  Frame Z-direction    : [{','.join([str(x) for x in self.plane.direction_z])}]"
        )
        return "\n".join(lines)
