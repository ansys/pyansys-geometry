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
"""Provides various option classes."""

from dataclasses import asdict, dataclass
from enum import Enum, unique


@unique
class ExtrudeType(Enum):
    """Provides values for extrusion types."""

    NONE = 0
    ADD = 1
    CUT = 2
    FORCE_ADD = 3
    FORCE_CUT = 4
    FORCE_INDEPENDENT = 5
    FORCE_NEW_SURFACE = 6


@unique
class OffsetMode(Enum):
    """Provides values for offset modes during extrusions."""

    IGNORE_RELATIONSHIPS = 0
    MOVE_FACES_TOGETHER = 1
    MOVE_FACES_APART = 2


@unique
class FillPatternType(Enum):
    """Provides values for types of fill patterns."""

    GRID = 0
    OFFSET = 1
    SKEWED = 2


@dataclass
class ImportOptions:
    """Import options when opening a file.

    Parameters
    ----------
    cleanup_bodies : bool = False
        Simplify geometry and clean up topology.
    import_coordinate_systems : bool = False
        Import coordinate systems.
    import_curves : bool = False
        Import curves.
    import_hidden_components_and_geometry : bool = False
        Import hidden components and geometry.
    import_names : bool = False
        Import names of bodies and curves.
    import_planes : bool = False
        Import planes.
    import_points : bool = False
        Import points.
    """

    cleanup_bodies: bool = False
    import_coordinate_systems: bool = False
    import_curves: bool = False
    import_hidden_components_and_geometry: bool = False
    import_names: bool = False
    import_planes: bool = False
    import_points: bool = False

    def to_dict(self):
        """Provide the dictionary representation of the ImportOptions class."""
        return {k: bool(v) for k, v in asdict(self).items()}

@dataclass
class MoveOptions:
    """Options for moving geometry.

    Parameters
    ----------
    copy : bool = False
        Copy the geometry instead of moving it.
    """

    copy: bool = False

    def to_dict(self):
        """Provide the dictionary representation of the MoveOptions class."""
        return {k: bool(v) for k, v in asdict(self).items()}