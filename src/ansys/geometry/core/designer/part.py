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
"""Module providing fundamental data of an assembly."""
from beartype.typing import TYPE_CHECKING, List

from ansys.geometry.core.designer.body import MasterBody
from ansys.geometry.core.math.constants import IDENTITY_MATRIX44
from ansys.geometry.core.math.matrix import Matrix44

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.component import Component


class Part:
    """
    Represents a part master.

    This class should not be accessed by users. The ``Part`` class holds fundamental
    data of an assembly.

    Parameters
    ----------
    id : str
        Unique identifier for the part.
    name : str
        Name of the part.
    components : List[MasterComponent]
        List of ``MasterComponent`` children that the part contains.
    bodies : List[MasterBody]
        List of ``MasterBody`` children that the part contains. These are master bodies.
    """

    def __init__(
        self, id: str, name: str, components: List["MasterComponent"], bodies: List[MasterBody]
    ) -> None:
        """Initialize the ``Part`` class."""
        self._id: str = id
        self._name: str = name
        self._components: List["MasterComponent"] = components
        self._bodies: List[MasterBody] = bodies

    @property
    def id(self) -> str:
        """ID of the part."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the part."""
        return self._name

    @property
    def components(self) -> List["MasterComponent"]:
        """``MasterComponent`` children that the part contains."""
        return self._components

    @components.setter
    def components(self, components: List["MasterComponent"]) -> None:
        self._components = components

    @property
    def bodies(self) -> List[MasterBody]:
        """
        ``MasterBody`` children that the part contains.

        These are master bodies.
        """
        return self._bodies

    @bodies.setter
    def bodies(self, bodies: List["MasterBody"]) -> None:
        self._bodies = bodies

    def __repr__(self) -> str:
        """Represent the part as a string."""
        return (
            f"Part(id={self.id}, "
            f"name={self.name}, "
            f"parts={[p.name for p in self.components]}, "
            f"bodies={[b.name for b in self.bodies]})"
        )


class MasterComponent:
    """
    Represents a part occurrence.

    Notes
    -----
    This class should not be accessed by users. It holds the fundamental data of
    an assembly. Master components wrap parts by adding a transform matrix.

    Parameters
    ----------
    id : str
        Unique identifier for the transformed part.
    name : str
        Name of the transformed part.
    part : Part
        Reference to the transformed part's master part.
    transform : Matrix44
        4x4 transformation matrix from the master part.
    """

    def __init__(
        self, id: str, name: str, part: Part, transform: Matrix44 = IDENTITY_MATRIX44
    ) -> None:
        """Initialize the ``MasterComponent`` class."""
        self._id: str = id
        self._name: str = name
        self._part: Part = part
        part.components.append(self)
        self._transform: Matrix44 = transform
        self._occurrences: List["Component"] = []

    @property
    def id(self) -> str:
        """ID of the transformed part."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the transformed part."""
        return self._name

    @property
    def occurrences(self) -> List["Component"]:
        """List of all occurrences of the component."""
        return self._occurrences

    @property
    def part(self) -> Part:
        """Master part of the transformed part."""
        return self._part

    @property
    def transform(self) -> Matrix44:
        """4x4 transformation matrix from the master part."""
        return self._transform

    @transform.setter
    def transform(self, matrix: Matrix44) -> None:
        self._transform = matrix

    def __repr__(self) -> str:
        """Represent the master component as a string."""
        return (
            f"MasterComponent(id={self.id}, "
            f"name={self.name}, "
            f"template={self.part}, "
            f"transform={self.transform})"
        )
