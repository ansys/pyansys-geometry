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
"""Module for managing standalone design curves."""

from typing import TYPE_CHECKING

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.misc.checks import ensure_design_is_active
from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.shapes.curves.trimmed_curve import TrimmedCurve
from ansys.geometry.core.shapes.parameterization import Interval

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.component import Component


class DesignCurve:
    """Represents a standalone curve within the design assembly.

    Unlike edges, which are always attached to a body, a ``DesignCurve`` is a free-standing
    curve object that lives directly under the root design object or a component in the design tree.
    These are typically created by operations such as revolving design points.

    Parameters
    ----------
    id : str
        Server-defined ID for the curve.
    name : str
        User-defined label for the curve.
    length : Distance
        Length of the curve.
    start : Point3D
        Start point of the curve.
    end : Point3D
        End point of the curve.
    grpc_client : GrpcClient
        gRPC client for communicating with the server.
    parent_component : Component
        Parent component that the curve belongs to in the design assembly.
    """

    def __init__(
        self,
        id: str,
        name: str,
        length: Distance,
        start: Point3D,
        end: Point3D,
        grpc_client: GrpcClient,
        parent_component: "Component",
    ):
        """Initialize the ``DesignCurve`` class."""
        self._id = id
        self._name = name
        self._length = length
        self._start = start
        self._end = end
        self._grpc_client = grpc_client
        self._parent_component = parent_component
        self._is_alive = True
        self._shape = None

    @property
    def id(self) -> str:
        """ID of the design curve."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the design curve."""
        return self._name

    @property
    def parent_component(self) -> "Component":
        """Parent component of the design curve."""
        return self._parent_component

    @property
    def is_alive(self) -> bool:
        """Flag indicating whether the design curve is still present on the server."""
        return self._is_alive

    @property
    @ensure_design_is_active
    def shape(self) -> TrimmedCurve:
        """Underlying trimmed curve geometry of the design curve.

        The shape is fetched from the server on first access and then cached.
        """
        if self._shape is None:
            self._grpc_client.log.debug(f"Requesting curve properties for {self._id} from server.")

            geometry = self._grpc_client.services.edges.get_curve(id=self._id).get("curve")

            response = self._grpc_client.services.edges.get_start_and_end_points(id=self._id)
            start = response.get("start")
            end = response.get("end")

            length = self._grpc_client.services.edges.get_length(id=self._id).get("length")

            response = self._grpc_client.services.edges.get_interval(id=self._id)
            interval = Interval(response.get("start"), response.get("end"))

            self._shape = TrimmedCurve(geometry, start, end, interval, length.value)

        return self._shape

    @property
    @ensure_design_is_active
    def length(self) -> Distance:
        """Calculated length of the design curve."""
        return self._length

    @property
    @ensure_design_is_active
    def start(self) -> Point3D:
        """Start point of the design curve."""
        return self._start

    @property
    @ensure_design_is_active
    def end(self) -> Point3D:
        """End point of the design curve."""
        return self._end

    def __repr__(self) -> str:
        """Represent the design curve as a string."""
        lines = [f"ansys.geometry.core.designer.DesignCurve {hex(id(self))}"]
        lines.append(f"  ID                   : {self.id}")
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Length               : {self._length}")
        lines.append(f"  Start                : {self._start}")
        lines.append(f"  End                  : {self._end}")
        return "\n".join(lines)
