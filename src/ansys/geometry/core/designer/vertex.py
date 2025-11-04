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
"""Module for managing a vertex."""

from typing import TYPE_CHECKING

import numpy as np

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.misc.auxiliary import get_design_from_body
from ansys.geometry.core.typing import RealSequence

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.selection import NamedSelection


class Vertex(Point3D):
    """Represents a single vertex of a body within the design assembly.

    This class synchronizes to a design within a supporting Geometry service instance.

    Parameters
    ----------
    id : str
        The unique identifier for the vertex.
    position : np.ndarray or RealSequence
        The position of the vertex in 3D space.
    """

    def __new__(
        cls,
        id: str,
        position: np.ndarray | RealSequence,
        body: "Body",
    ):
        """Initialize ``Vertex`` class."""
        # Only pass position and unit to Point3D.__new__
        obj = super().__new__(cls, position)
        return obj

    def __init__(
        self,
        id: str,
        position: np.ndarray | RealSequence,
        body: "Body",
    ):
        """Initialize the Vertex with a unique identifier."""
        self._id = id
        self._body = body
        super().__init__(position)

        # Make immutable
        self.flags.writeable = False

    @property
    def id(self) -> str:
        """Get the unique identifier of the vertex."""
        return self._id

    @property
    def body(self) -> "Body":
        """Get the body this vertex belongs to."""
        return self._body

    def get_named_selections(self) -> list["NamedSelection"]:
        """Get all named selections that include this vertex.

        Returns
        -------
        list["NamedSelection"]
            List of named selections that include this vertex.
        """
        design = get_design_from_body(self.body)
        named_selections = design.named_selections

        included_ns = []
        for ns in named_selections:
            if self in ns.vertices:
                included_ns.append(ns)

        return included_ns

    def __repr__(self) -> str:
        """Return a string representation of the vertex."""
        lines = [f"ansys.geometry.core.designer.Vertex {hex(id(self))}"]
        lines.append(f"  Id                   : {self.id}")
        lines.append(f"  Position                 : {self.position}")
        lines.append(f"  Body Id                : {self.body.id}")
        return "\n".join(lines)
