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
"""Utility functions for plotting and visualization."""

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:  # pragma: no cover
    import pyvista as pv

    from ansys.geometry.core.math.point import Point3D
    from ansys.geometry.core.math.vector import Vector3D
    from ansys.geometry.core.typing import Real


def create_elliptical_polydata(
    origin: "Point3D",
    dir_x: "Vector3D",
    dir_y: "Vector3D",
    dir_z: "Vector3D",
    major_radius: "Real",
    minor_radius: "Real | None" = None,
    num_points: int = 100,
) -> "pv.PolyData":
    """Create PyVista PolyData for an ellipse or circle.

    This function creates a discretized representation of an ellipse (or circle)
    as a closed loop of line segments for visualization purposes.

    Parameters
    ----------
    origin : Point3D
        Center point of the ellipse/circle.
    dir_x : Vector3D
        Direction vector for the major axis (or X axis for circles).
    dir_y : Vector3D
        Direction vector for the minor axis (or Y axis for circles).
    dir_z : Vector3D
        Normal direction vector.
    major_radius : Real
        Major radius of the ellipse. For circles, this is the radius.
    minor_radius : Real, optional
        Minor radius of the ellipse. If None, defaults to major_radius
        (creating a circle).
    num_points : int, default: 100
        Number of points to use for discretization.

    Returns
    -------
    pyvista.PolyData
        VTK PolyData representation with line segments forming a closed loop.

    Notes
    -----
    For a circle, either pass the same value for both radii or only provide
    major_radius (minor_radius will default to major_radius).
    """
    import pyvista as pv

    # Default minor_radius to major_radius for circles
    if minor_radius is None:
        minor_radius = major_radius

    # Create parametric points
    # Use endpoint=False to avoid duplicating the first/last point in the closed loop
    theta = np.linspace(0, 2 * np.pi, num_points, endpoint=False)

    # Calculate points using ellipse parametric equations
    points = np.column_stack(
        [
            (
                origin[0]
                + major_radius * np.cos(theta) * dir_x[0]
                + minor_radius * np.sin(theta) * dir_y[0]
            ),
            (
                origin[1]
                + major_radius * np.cos(theta) * dir_x[1]
                + minor_radius * np.sin(theta) * dir_y[1]
            ),
            (
                origin[2]
                + major_radius * np.cos(theta) * dir_x[2]
                + minor_radius * np.sin(theta) * dir_y[2]
            ),
        ]
    )

    # Create line segments forming a closed loop
    lines = np.column_stack(
        [np.full(num_points, 2), np.arange(num_points), np.roll(np.arange(num_points), -1)]
    ).ravel()

    return pv.PolyData(points, lines=lines)
