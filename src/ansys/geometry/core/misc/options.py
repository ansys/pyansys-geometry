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
"""Provides various option classes."""

from dataclasses import asdict, dataclass

from beartype import beartype as check_input_types
from pint import Quantity

from ansys.geometry.core.misc.measurements import Angle, Distance
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
    import_named_selections : bool = True
        Import the named selections associated with the root component being inserted.
    """

    cleanup_bodies: bool = False
    import_coordinate_systems: bool = False
    import_curves: bool = False
    import_hidden_components_and_geometry: bool = False
    import_names: bool = False
    import_planes: bool = False
    import_points: bool = False
    import_named_selections: bool = True

    def to_dict(self):
        """Provide the dictionary representation of the ImportOptions class."""
        return {k: bool(v) for k, v in asdict(self).items()}


@dataclass
class ImportOptionsDefinitions:
    """Import options definitions when opening a file.

    Parameters
    ----------
    import_named_selections_keys : string = None
        Import the named selections keys associated with the root component being inserted.
    """

    import_named_selections_keys: str = None

    def to_dict(self):
        """Provide the dictionary representation of the ImportOptionsDefinitions class."""
        return {k: str(v) for k, v in asdict(self).items()}


class TessellationOptions:
    """Provides options for getting tessellation.

    Parameters
    ----------
    surface_deviation : Distance | Quantity | Real
        The maximum deviation from the true surface position.
        If a Real is provided, it is assumed to be in the default length unit.
    angle_deviation : Angle | Quantity | Real
        The maximum deviation from the true surface normal.
        If a Real is provided, it is assumed to be in radians.
    max_aspect_ratio : Real, default=0.0
        The maximum aspect ratio of facets.
    max_edge_length : Distance | Quantity | Real, default=0.0
        The maximum facet edge length.
    watertight : bool, default=False
        Whether triangles on opposite sides of an edge should match.
    """

    @check_input_types
    def __init__(
        self,
        surface_deviation: Distance | Quantity | Real,
        angle_deviation: Angle | Quantity | Real,
        max_aspect_ratio: Real = 0.0,
        max_edge_length: Distance | Quantity | Real = 0.0,
        watertight: bool = False,
    ):
        """Initialize ``TessellationOptions`` class."""
        # Convert inputs to Distance and Angle objects
        self._surface_deviation = (
            surface_deviation
            if isinstance(surface_deviation, Distance)
            else Distance(surface_deviation)
        )
        self._angle_deviation = (
            angle_deviation if isinstance(angle_deviation, Angle) else Angle(angle_deviation)
        )
        self._max_aspect_ratio = max_aspect_ratio
        self._max_edge_length = (
            max_edge_length if isinstance(max_edge_length, Distance) else Distance(max_edge_length)
        )
        self._watertight = watertight

    @property
    def surface_deviation(self) -> Distance:
        """Surface Deviation.

        The maximum deviation from the true surface position.
        """
        return self._surface_deviation

    @property
    def angle_deviation(self) -> Angle:
        """Angle deviation.

        The maximum deviation from the true surface normal.
        """
        return self._angle_deviation

    @property
    def max_aspect_ratio(self) -> Real:
        """Maximum aspect ratio.

        The maximum aspect ratio of facets.
        """
        return self._max_aspect_ratio

    @property
    def max_edge_length(self) -> Distance:
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


class FMDExportOptions:
    """Provides options for FMD export.

    Parameters
    ----------
    deviation : Distance | Quantity | Real, default=0.00075
        The maximum deviation from the true surface position.
        If a Real is provided, it is assumed to be in the default length unit.
        Must be between 0.00003 m and 0.002 m.
    angle : Angle | Quantity | Real, default=0.13962634016
        The maximum deviation from the true surface normal.
        If a Real is provided, it is assumed to be in radians.
        Must be between 0.05 degrees (≈ 8.727e-4 rad) and 30 degrees (≈ 0.5236 rad).
    aspect_ratio: int, default=-3
        The maximum aspect ratio of facets.
    max_edge_length: Distance | Quantity | Real, default=0.0
        The maximum facet edge length.
    """

    def __init__(
        self,
        deviation: Distance | Quantity | Real = 0.00075,
        angle: Angle | Quantity | Real = 0.13962634016,
        aspect_ratio: int = -3,
        max_edge_length: Distance | Quantity | Real = 0.0,
    ):
        """Initialize ``FMDExportOptions`` class."""
        self._deviation = (
            deviation if isinstance(deviation, Distance) else Distance(deviation)
        )
        _dev_m = self._deviation.value.m_as("m")
        if not (0.00003 <= _dev_m <= 0.002):
            raise ValueError(
                f"deviation must be between 0.00003 m and 0.002 m, got {_dev_m} m."
            )

        self._angle = angle if isinstance(angle, Angle) else Angle(angle)
        _ang_deg = self._angle.value.m_as("degree")
        if not (0.05 <= _ang_deg <= 30.0):
            raise ValueError(
                f"angle must be between 0.05 degrees and 30 degrees, got {_ang_deg:.6f} degrees."
            )

        self._aspect_ratio = int(aspect_ratio)
        self._max_edge_length = (
            max_edge_length if isinstance(max_edge_length, Distance) else Distance(max_edge_length)
        )

    @property
    def deviation(self) -> Distance:
        """Deviation.

        The maximum deviation from the true surface position.
        """
        return self._deviation

    @property
    def angle(self) -> Angle:
        """Angle.

        The maximum deviation from the true surface normal.
        """
        return self._angle

    @property
    def aspect_ratio(self) -> int:
        """Aspect ratio.

        The maximum aspect ratio of facets.
        """
        return self._aspect_ratio

    @property
    def max_edge_length(self) -> Distance:
        """Maximum edge length.

        The maximum facet edge length.
        """
        return self._max_edge_length

    