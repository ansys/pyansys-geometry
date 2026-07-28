# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Module for creating and managing datum lines."""

from typing import TYPE_CHECKING

from ansys.geometry.core.shapes.curves.line import Line

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.component import Component


class DatumLine:
    """Provides for creating datum lines in components.

    Parameters
    ----------
    id : str
        Server-defined ID for the datum line.
    name : str
        User-defined label for the datum line.
    line : Line
        3D line constituting the datum line.
    parent_component : Component
        Parent component to place the new datum line under within the design assembly.
    """

    def __init__(self, id: str, name: str, line: Line, parent_component: "Component"):
        """Initialize the ``DatumLine`` class."""
        self._id = id
        self._name = name
        self._line = line
        self._parent_component = parent_component
        self._is_alive = True

    @property
    def id(self) -> str:
        """ID of the datum line."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the datum line."""
        return self._name

    @property
    def line(self) -> Line:
        """Line of the datum line."""
        return self._line

    @property
    def parent_component(self) -> "Component":
        """Component node that the datum line is under."""
        return self._parent_component

    @property
    def is_alive(self) -> bool:
        """Check if the datum line is still present on the server."""
        return self._is_alive

    def __repr__(self) -> str:
        """Represent the datum line as a string."""
        lines = [f"ansys.geometry.core.designer.DatumLine {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Datum Line           : {self.line}")
        return "\n".join(lines)
