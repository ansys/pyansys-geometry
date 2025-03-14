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

from beartype import beartype as check_input_types

from ansys.geometry.core.typing import Real


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


class TessellationOptions:
    """Provides options for getting tessellation.

    Parameters
    ----------
    surface_deviation : Real
        The maximum deviation from the true surface position.
    angle_deviation : Real
        The maximum deviation from the true surface normal, in radians.
    max_aspect_ratio : Real, default=0.0
        The maximum aspect ratio of facets.
    max_edge_length : Real, default=0.0
        The maximum facet edge length.
    watertight : bool, default=False
        Whether triangles on opposite sides of an edge should match.
    """

    @check_input_types
    def __init__(
        self,
        surface_deviation: Real,
        angle_deviation: Real,
        max_aspect_ratio: Real = 0.0,
        max_edge_length: Real = 0.0,
        watertight: bool = False,
    ):
        """Initialize ``TessellationOptions`` class."""
        self._surface_deviation = surface_deviation
        self._angle_deviation = angle_deviation
        self._max_aspect_ratio = max_aspect_ratio
        self._max_edge_length = max_edge_length
        self._watertight = watertight

    @property
    def surface_deviation(self) -> Real:
        """Surface Deviation.

        The maximum deviation from the true surface position.
        """
        return self._surface_deviation

    @property
    def angle_deviation(self) -> Real:
        """Angle deviation.

        The maximum deviation from the true surface normal, in radians.
        """
        return self._angle_deviation

    @property
    def max_aspect_ratio(self) -> Real:
        """Maximum aspect ratio.

        The maximum aspect ratio of facets.
        """
        return self._max_aspect_ratio

    @property
    def max_edge_length(self) -> Real:
        """Maximum edge length.

        The maximum facet edge length.
        """
        return self._max_edge_length

    @property
    def watertight(self) -> bool:
        """Watertight.

        Whether triangles on opposite sides of an edge should match.
        """
        return self._watertight
