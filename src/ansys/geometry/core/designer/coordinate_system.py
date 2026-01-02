# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
"""Provides for managing a user-defined coordinate system."""

from typing import TYPE_CHECKING

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.math.frame import Frame

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.component import Component


class CoordinateSystem:
    """Represents a user-defined coordinate system within the design assembly.

    This class synchronizes to a design within a supporting Geometry
    service instance.

    Parameters
    ----------
    name : str
        User-defined label for the coordinate system.
    frame : Frame
        Frame defining the coordinate system bounds.
    parent_component : Component, default: Component
        Parent component the coordinate system is assigned against.
    grpc_client : GrpcClient
        Active supporting Geometry service instance for design modeling.
    """

    def __init__(
        self,
        name: str,
        frame: Frame,
        parent_component: "Component",
        grpc_client: GrpcClient,
        preexisting_id: str | None = None,
    ):
        """Initialize the ``CoordinateSystem`` class."""
        self._parent_component = parent_component
        self._grpc_client = grpc_client
        self._is_alive = True

        # Create without going to server
        if preexisting_id:
            self._name = name
            self._frame = frame
            self._id = preexisting_id
            return

        self._grpc_client.log.debug("Requesting creation of a coordinate system.")
        response = self._grpc_client.services.coordinate_systems.create(
            parent_id=self._parent_component.id,
            name=name,
            frame=frame,
        )

        self._id = response.get("id")
        self._name = response.get("name")
        self._frame = response.get("frame")

    @property
    def id(self) -> str:
        """ID of the coordinate system."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the coordinate system."""
        return self._name

    @property
    def frame(self) -> Frame:
        """Frame of the coordinate system."""
        return self._frame

    @property
    def parent_component(self) -> "Component":
        """Parent component of the coordinate system."""
        return self._parent_component

    @property
    def is_alive(self) -> bool:
        """Flag indicating if coordinate system is still alive on the server."""
        return self._is_alive

    def __repr__(self) -> str:
        """Represent the coordinate system as a string."""
        lines = [f"ansys.geometry.core.designer.CoordinateSystem {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Exists               : {self.is_alive}")
        lines.append(f"  Parent component     : {self.parent_component.name}")
        lines.append(
            f"  Frame origin         : [{','.join([str(x) for x in self.frame.origin])}] in meters"
        )
        lines.append(
            f"  Frame X-direction    : [{','.join([str(x) for x in self.frame.direction_x])}]"
        )
        lines.append(
            f"  Frame Y-direction    : [{','.join([str(x) for x in self.frame.direction_y])}]"
        )
        lines.append(
            f"  Frame Z-direction    : [{','.join([str(x) for x in self.frame.direction_z])}]"
        )
        return "\n".join(lines)
