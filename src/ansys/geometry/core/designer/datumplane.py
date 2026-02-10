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
"""Module for creating and managing datum planes."""

from typing import TYPE_CHECKING

from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point3D

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.component import Component


class DatumPlane:
    """Provides for creating datum planes in components.

    Parameters
    ----------
    id : str
        Server-defined ID for the datum plane.
    name : str
        User-defined label for the datum plane.
    plane : Plane
        Plane constituting the datum plane.
    parent_component : Component
        Parent component to place the new datum plane under within the design assembly.
    """

    def __init__(self, id: str, name: str, plane: Plane, parent_component: "Component"):
        """Initialize the ``DatumPlane`` class."""
        self._id = id
        self._name = name
        self._value = plane
        self._parent_component = parent_component

    @property
    def id(self) -> str:
        """ID of the datum plane."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the datum plane."""
        return self._name

    @property
    def value(self) -> Plane:
        """Plane constituting the datum plane."""
        return self._value

    @property
    def parent_component(self) -> "Component":
        """Parent component of the datum plane."""
        return self._parent_component

    def evaluate(self, u: float, v: float) -> Point3D:
        """Evaluate the plane at UV parametric coordinates.

        This method converts 2D parametric coordinates (u, v) to a 3D Cartesian point
        on the plane using the parametric equation:
        P(u, v) = origin + u * direction_x + v * direction_y

        Parameters
        ----------
        u : float
            First parametric coordinate along the plane's x-direction.
        v : float
            Second parametric coordinate along the plane's y-direction.

        Returns
        -------
        Point3D
            3D Cartesian point on the plane at the given UV coordinates.
        """
        return self.value.origin + u * self.value.direction_x + v * self.value.direction_y

    def __repr__(self):
        """Represent the datum plane as a string."""
        lines = [f"ansys.geometry.core.design.DatumPlane {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Datum Plane          : {self.value}")
        return "\n".join(lines)
