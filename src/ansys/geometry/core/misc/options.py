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
"""Provides various option classes."""
from dataclasses import asdict, dataclass


@dataclass
class ImportOptions:
    """
    Import options when opening a file.

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
