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
"""Provides for creating and managing a beam."""

from beartype.typing import TYPE_CHECKING, Union

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc.checks import check_type
from ansys.geometry.core.misc.measurements import Distance

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.component import Component


class BeamProfile:
    """
    Represents a single beam profile organized within the design assembly.

    This profile synchronizes to a design within a supporting Geometry service instance.

    Parameters
    ----------
    id : str
        Server-defined ID for the beam profile.
    name : str
        User-defined label for the beam profile.

    Notes
    -----
    ``BeamProfile`` objects are expected to be created from the ``Design`` object.
    This means that you are not expected to instantiate your own ``BeamProfile``
    object. You should call the specific ``Design`` API for the ``BeamProfile`` desired.
    """

    def __init__(self, id: str, name: str):
        """Initialize ``BeamProfile`` class."""
        self._id = id
        self._name = name

    @property
    def id(self) -> str:
        """ID of the beam profile."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the beam profile."""
        return self._name


class BeamCircularProfile(BeamProfile):
    """
    Represents a single circular beam profile organized within the design assembly.

    This profile synchronizes to a design within a supporting Geometry service instance.

    Parameters
    ----------
    id : str
        Server-defined ID for the beam profile.
    name : str
        User-defined label for the beam profile.
    radius : Distance
        Radius of the circle.
    center: Point3D
        3D point representing the center of the circle.
    direction_x: UnitVector3D
        X-axis direction.
    direction_y: UnitVector3D
        Y-axis direction.

    Notes
    -----
    ``BeamProfile`` objects are expected to be created from the ``Design`` object.
    This means that you are not expected to instantiate your own ``BeamProfile``
    object. You should call the specific ``Design`` API for the ``BeamProfile`` desired.
    """

    def __init__(
        self,
        id: str,
        name: str,
        radius: Distance,
        center: Point3D,
        direction_x: UnitVector3D,
        direction_y: UnitVector3D,
    ):
        """Initialize ``BeamCircularProfile`` class."""
        super().__init__(id, name)

        # Store specific BeamCircularProfile variables
        self._radius = radius
        self._center = center
        self._dir_x = direction_x
        self._dir_y = direction_y

    @property
    def radius(self) -> Distance:
        """Radius of the circular beam profile."""
        return self._radius

    @property
    def center(self) -> Point3D:
        """Center of the circular beam profile."""
        return self._center

    @property
    def direction_x(self) -> UnitVector3D:
        """X-axis direction of the circular beam profile."""
        return self._dir_x

    @property
    def direction_y(self) -> UnitVector3D:
        """Y-axis direction of the circular beam profile."""
        return self._dir_y

    def __repr__(self) -> str:
        """Represent the ``BeamCircularProfile`` as a string."""
        lines = [f"ansys.geometry.core.designer.BeamCircularProfile {hex(id(self))}"]
        lines.append(f"  Name                 : {self.name}")
        lines.append(f"  Radius               : {str(self.radius.value)}")
        lines.append(
            f"  Center               : [{','.join([str(x) for x in self.center])}] in meters"
        )
        lines.append(f"  Direction x          : [{','.join([str(x) for x in self.direction_x])}]")
        lines.append(f"  Direction y          : [{','.join([str(x) for x in self.direction_y])}]")
        return "\n".join(lines)


class Beam:
    """
    Represents a simplified solid body with an assigned 2D cross-section.

    This body synchronizes to a design within a supporting Geometry service instance.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    name : str
        User-defined label for the body.
    start : Point3D
        Start of the beam line segment.
    end : Point3D
        End of the beam line segment.
    profile : BeamProfile
        Beam profile to use to create the beam.
    parent_component : Component
        Parent component to nest the new beam under within the design assembly.
    """

    def __init__(
        self,
        id: str,
        start: Point3D,
        end: Point3D,
        profile: BeamProfile,
        parent_component: "Component",
    ):
        """Initialize ``Beam`` class."""
        from ansys.geometry.core.designer.component import Component

        check_type(id, str)
        check_type(start, Point3D)
        check_type(end, Point3D)
        check_type(profile, BeamProfile)
        check_type(parent_component, Component)

        self._id = id
        self._start = start
        self._end = end
        self._profile = profile
        self._parent_component = parent_component
        self._is_alive = True

    @property
    def id(self) -> str:
        """Service-defined ID of the beam."""
        return self._id

    @property
    def start(self) -> Point3D:
        """Start of the beam line segment."""
        return self._start

    @property
    def end(self) -> Point3D:
        """End of the beam line segment."""
        return self._end

    @property
    def profile(self) -> BeamProfile:
        """Beam profile of the beam line segment."""
        return self._profile

    @property
    def parent_component(self) -> Union["Component", None]:
        """Component node that the beam is under."""
        return self._parent_component

    @property
    def is_alive(self) -> bool:
        """Flag indicating whether the beam is still alive on the server side."""
        return self._is_alive

    def __repr__(self) -> str:
        """Represent the beam as a string."""
        lines = [f"ansys.geometry.core.designer.Beam {hex(id(self))}"]
        lines.append(f"  Exists               : {self.is_alive}")
        lines.append(
            f"  Start                : [{','.join([str(x) for x in self.start])}] in meters"
        )
        lines.append(f"  End                  : [{','.join([str(x) for x in self.end])}] in meters")
        lines.append(f"  Parent component     : {self.parent_component.name}")
        lines.extend(["\n", "  Beam Profile info", "  -----------------", str(self.profile)])
        return "\n".join(lines)
