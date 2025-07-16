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
"""Provides for creating and managing a nurbs sketch curve."""

from typing import TYPE_CHECKING

from beartype import beartype as check_input_types
import numpy as np

from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.misc.checks import graphics_required
from ansys.geometry.core.sketch.edge import SketchEdge
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    import geomdl.NURBS as geomdl_nurbs  # noqa: N811
    import pyvista as pv


class SketchNurbs(SketchEdge):
    """Represents a NURBS sketch curve.

    Notes
    -----
    This class is a wrapper around the NURBS curve class from the `geomdl` library.
    By leveraging the `geomdl` library, this class provides a high-level interface
    to create and manipulate NURBS curves. The `geomdl` library is a powerful
    library for working with NURBS curves and surfaces. For more information, see
    https://pypi.org/project/geomdl/.

    """

    def __init__(self):
        """Initialize the NURBS sketch curve."""
        super().__init__()
        try:
            import geomdl.NURBS as geomdl_nurbs  # noqa: N811
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "The `geomdl` library is required to use the NURBSCurve class. "
                "Please install it using `pip install geomdl`."
            ) from e

        self._nurbs_curve = geomdl_nurbs.Curve()

    @property
    def geomdl_nurbs_curve(self) -> "geomdl_nurbs.Curve":
        """Get the underlying NURBS curve.

        Notes
        -----
        This property gives access to the full functionality of the NURBS curve
        coming from the `geomdl` library. Use with caution.
        """
        return self._nurbs_curve

    @property
    def control_points(self) -> list[Point2D]:
        """Get the control points of the curve."""
        return [Point2D(point) for point in self._nurbs_curve.ctrlpts]

    @property
    def degree(self) -> int:
        """Get the degree of the curve."""
        return self._nurbs_curve.degree

    @property
    def knots(self) -> list[Real]:
        """Get the knot vector of the curve."""
        return self._nurbs_curve.knotvector

    @property
    def weights(self) -> list[Real]:
        """Get the weights of the control points."""
        return self._nurbs_curve.weights

    @property
    def start(self) -> Point2D:
        """Get the start point of the curve."""
        return Point2D(self._nurbs_curve.evaluate_single(0.0))

    @property
    def end(self) -> Point2D:
        """Get the end point of the curve."""
        return Point2D(self._nurbs_curve.evaluate_single(1.0))

    @property
    @graphics_required
    def visualization_polydata(self) -> "pv.PolyData":
        """Get the VTK polydata representation for PyVista visualization.

        Returns
        -------
        pyvista.PolyData
            VTK pyvista.Polydata configuration.

        Notes
        -----
        The representation lies in the X/Y plane within
        the standard global Cartesian coordinate system.
        """
        import numpy as np
        import pyvista as pv

        # Sample points along the curve
        params = np.linspace(0, 1, 100)
        points = [self._nurbs_curve.evaluate_single(u) for u in params]  # For 2D: [x, y]

        # Add a zero z-coordinate for PyVista (only supports 3D points)
        points = [(*pt, 0.0) for pt in points]

        # Create PolyData and add the line
        polydata = pv.PolyData(points)
        polydata.lines = [len(points)] + list(range(len(points)))

        return polydata

    def contains_point(self, point: Point2D, tolerance: Real = 1e-6) -> bool:
        """Check if the curve contains a given point within a specified tolerance.

        Parameters
        ----------
        point : Point2D
            The point to check.
        tolerance : Real, optional
            The tolerance for the containment check, by default 1e-6.

        Returns
        -------
        bool
            True if the curve contains the point within the tolerance, False otherwise.
        """
        # Sample points along the curve
        params = np.linspace(0, 1, 200)
        sampled = [self._nurbs_curve.evaluate_single(u) for u in params]

        # Check if any sampled point is close to the target point
        return any(np.linalg.norm(np.array(pt) - np.array(point)) < tolerance for pt in sampled)

    @classmethod
    @check_input_types
    def fit_curve_from_points(
        cls,
        points: list[Point2D],
        degree: int = 3,
    ) -> "SketchNurbs":
        """Fit a NURBS curve to a set of points.

        Parameters
        ----------
        points : list[Point2D]
            The points to fit the curve to.
        degree : int, optional
            The degree of the NURBS curve, by default 3.

        Returns
        -------
        SketchNurbs
            A new instance of SketchNurbs fitted to the given points.
        """
        from geomdl import fitting

        # Check degree compared to number of points provided
        if degree < 1:
            raise ValueError("Degree must be at least 1.")
        if len(points) == 2:
            degree = 1  # Force linear interpolation for two points
        if len(points) == 3:
            degree = 2  # Force quadratic interpolation for three points
        if degree >= len(points):
            raise ValueError(
                f"Degree {degree} is too high for the number of points provided: {len(points)}."
            )

        curve = fitting.interpolate_curve(
            [[*pt] for pt in points],  # Convert Point2D to list of coordinates
            degree=degree,
        )

        # Construct the NURBSCurve object
        nurbs_curve = cls()
        nurbs_curve._nurbs_curve.degree = curve.degree
        nurbs_curve._nurbs_curve.ctrlpts = [Point2D(entry) for entry in curve.ctrlpts]
        nurbs_curve._nurbs_curve.knotvector = curve.knotvector
        nurbs_curve._nurbs_curve.weights = curve.weights

        # Verify the curve is valid
        try:
            nurbs_curve._nurbs_curve._check_variables()
        except ValueError as e:
            raise ValueError(f"Invalid NURBS curve: {e}")

        return nurbs_curve
