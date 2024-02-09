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
"""Module for creating and managing design points."""

from beartype.typing import TYPE_CHECKING, Union

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.misc.checks import check_type
from ansys.geometry.core.misc.units import UNITS

if TYPE_CHECKING:  # pragma: no cover
    import pyvista as pv

    from ansys.geometry.core.designer.component import Component


class DesignPoint:
    """
    Provides for creating design points in components.

    Parameters
    ----------
    id : str
        Server-defined ID for the design points.
    name : str
        User-defined label for the design points.
    points : Point3D
        3D point constituting the design points.
    parent_component : Component
        Parent component to place the new design point under within the design assembly.
    """

    def __init__(self, id: str, name: str, point: Point3D, parent_component: "Component"):
        """Initialize the ``DesignPoints`` class."""
        from ansys.geometry.core.designer.component import Component

        check_type(id, str)
        check_type(name, str)
        check_type(point, Point3D)
        check_type(parent_component, Component)

        self._id = id
        self._name = name
        self._value = point
        self._parent_component = parent_component

    @property
    def id(self) -> str:
        """ID of the design point."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the design point."""
        return self._name

    @property
    def value(self) -> Point3D:
        """Value of the design point."""
        return self._value

    @property
    def parent_component(self) -> Union["Component", None]:
        """Component node that the design point is under."""
        return self._parent_component

    def __repr__(self) -> str:
        """Represent the design points as a string."""
        lines = [f"ansys.geometry.core.designer.DesignPoints {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Design Point         : {self.value}")
        return "\n".join(lines)

    def _to_polydata(self) -> "pv.PolyData":
        """Get polydata from DesignPoint object."""
        import pyvista as pv

        # get units to plot proportionally
        # 0.3 is the size for the sphere representation
        # determined empirically for proper representation
        unit = 0.3 * self.value.unit
        return pv.Sphere(center=self.value.flat, radius=unit.to(UNITS.m).magnitude)
