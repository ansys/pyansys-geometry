# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

import json
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

import numpy as np
from pint import Quantity

from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.misc.checks import check_input_types, graphics_required
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Angle, Distance
from ansys.geometry.core.sketch.edge import SketchEdge
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    import geomdl.NURBS as geomdl_nurbs  # noqa: N811
    import pyvista as pv


class SketchNurbs(SketchEdge):
    """Represents a NURBS sketch curve.

    Warnings
    --------
    NURBS sketching is only supported in 26R1 and later versions of Ansys.

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

    def contains_point(self, point: Point2D, tol: float = 1e-6) -> bool:
        """Check if the curve contains a given point within a specified tolerance.

        Parameters
        ----------
        point : Point2D
            The point to check.
        tol : float, optional
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
        return any(np.linalg.norm(np.array(pt) - np.array(point)) < tol for pt in sampled)

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

    @classmethod
    @check_input_types
    def from_control_points(
        cls,
        control_points: list[Point2D],
        degree: int,
        knots: list[Real],
        weights: list[Real] = None,
    ) -> "SketchNurbs":
        """Create a NURBS curve from control points.

        Parameters
        ----------
        control_points : list[Point2D]
            Control points of the curve.
        degree : int
            Degree of the curve.
        knots : list[Real]
            Knot vector of the curve.
        weights : list[Real], optional
            Weights of the control points.

        Returns
        -------
        SketchNurbs
            NURBS curve.
        """
        curve = cls()
        curve._nurbs_curve.degree = degree
        curve._nurbs_curve.ctrlpts = control_points
        curve._nurbs_curve.knotvector = knots
        if weights:
            curve._nurbs_curve.weights = weights

        # Verify the curve is valid
        try:
            curve._nurbs_curve._check_variables()
        except ValueError as e:
            raise ValueError(f"Invalid NURBS curve: {e}")

        return curve

    @classmethod
    @check_input_types
    def from_json(
        cls, source: Union[dict, str, Path], element_name: Optional[str] = None
    ) -> "SketchNurbs":
        """Create a NURBS sketch curve from a JSON file.

        Parameters
        ----------
        source : Union[dict, str, Path]
            JSON file path or dictionary containing the NURBS sketch curve data.
        element_name : str, optional
            Name of the element to load when the JSON payload contains
            multiple top-level named elements.

        Returns
        -------
        SketchNurbs
            NURBS sketch curve created exactly from the given data.
        """
        if not isinstance(source, dict):
            source = json.loads(Path(source).read_text(encoding="utf-8"))

        required_keys = {"control_points", "degree", "knots"}
        if not required_keys.issubset(source):
            if element_name is not None:
                if element_name not in source:
                    raise ValueError(f"Element '{element_name}' was not found in JSON payload.")
                source = source[element_name]
                if not isinstance(source, dict) or not required_keys.issubset(source):
                    raise ValueError(
                        f"Element '{element_name}' is not a valid sketch NURBS payload."
                    )
            else:
                selected = None
                for _, element in source.items():
                    if isinstance(element, dict) and required_keys.issubset(element):
                        selected = element
                        break
                if selected is None:
                    raise ValueError("No valid sketch NURBS element was found in JSON payload.")
                source = selected

        # If weights are not provided, set all weights to 1.0.
        weights = source.get("weights")
        if weights is None:
            weights = [1.0] * len(source["control_points"])

        return cls.from_control_points(
            control_points=[Point2D(cp) for cp in source["control_points"]],
            degree=source["degree"],
            knots=source["knots"],
            weights=weights,
        )

    @classmethod
    @check_input_types
    def partial_ellipse(
        cls,
        center: Point2D,
        major_radius: Quantity | Distance | Real,
        minor_radius: Quantity | Distance | Real,
        start_angle: Quantity | Angle | Real,
        end_angle: Quantity | Angle | Real,
        angle: Quantity | Angle | Real = 0,
    ) -> "SketchNurbs":
        """Create an exact rational NURBS for a partial ellipse arc.

        Parameters
        ----------
        center : Point2D
            Center of the ellipse.
        major_radius : ~pint.Quantity | Distance | Real
            Semi-major axis length (x-direction before rotation).
        minor_radius : ~pint.Quantity | Distance | Real
            Semi-minor axis length (y-direction before rotation).
        start_angle : ~pint.Quantity | Angle | Real
            Parametric start angle. Defaults to radians when given as a ``Real``.
        end_angle : ~pint.Quantity | Angle | Real
            Parametric end angle. Defaults to radians when given as a ``Real``.
            The arc sweeps counter-clockwise when ``end_angle > start_angle``.
        angle : ~pint.Quantity | Angle | Real, default: 0
            Rotation of the ellipse about its center (radians when ``Real``).

        Returns
        -------
        SketchNurbs
            Exact rational quadratic NURBS (degree 2) for the requested arc.
            The arc is split into segments of at most 90° for numerical stability.

        Raises
        ------
        ValueError
            If either radius is non-positive.
        ValueError
            If ``start_angle`` equals ``end_angle`` (zero-length arc).
        """
        # ------------------------------------------------------------------
        # Extract SI float values
        # ------------------------------------------------------------------
        a = (
            major_radius if isinstance(major_radius, Distance) else Distance(major_radius)
        ).value.m_as(DEFAULT_UNITS.LENGTH)

        b = (
            minor_radius if isinstance(minor_radius, Distance) else Distance(minor_radius)
        ).value.m_as(DEFAULT_UNITS.LENGTH)

        # Angles are stored in base unit (radians) inside Angle._value
        theta0 = (start_angle if isinstance(start_angle, Angle) else Angle(start_angle))._value
        theta1 = (end_angle if isinstance(end_angle, Angle) else Angle(end_angle))._value
        phi = (angle if isinstance(angle, Angle) else Angle(angle))._value

        # Center coordinates are already in base units (metres)
        cx, cy = float(center[0]), float(center[1])

        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------
        if a <= 0:
            raise ValueError("Semi-major axis must be a real positive value.")
        if b <= 0:
            raise ValueError("Semi-minor axis must be a real positive value.")

        delta = theta1 - theta0
        if np.isclose(delta, 0.0):
            raise ValueError("Start angle and end angle must be different.")
        elif delta < 0:
            raise ValueError("Start angle must be less than end angle.")

        # ------------------------------------------------------------------
        # Split into segments of at most π/2 (90°) for numerical stability
        # ------------------------------------------------------------------
        n_segs = max(1, int(np.ceil(abs(delta) / (np.pi / 2))))
        d_theta = delta / n_segs
        w_mid = float(np.cos(abs(d_theta) / 2.0))  # conic weight for each segment

        cos_phi, sin_phi = np.cos(phi), np.sin(phi)

        def _on_ellipse(theta: Real) -> np.ndarray:
            """Unrotated, unshifted point on the ellipse."""
            return np.array([a * np.cos(theta), b * np.sin(theta)])

        def _tangent(theta: Real) -> np.ndarray:
            """Unrotated tangent direction (CCW sense) at parametric angle theta."""
            return np.array([-a * np.sin(theta), b * np.cos(theta)])

        def _shoulder(theta_a: Real, theta_b: Real) -> np.ndarray:
            """Tangent-intersection shoulder control point for one conic segment."""
            p0, p2 = _on_ellipse(theta_a), _on_ellipse(theta_b)
            d0, d2 = _tangent(theta_a), _tangent(theta_b)
            # Solve p0 + t*d0 = p2 + s*d2  →  [d0 | -d2][t,s]^T = p2-p0
            det = d0[0] * (-d2[1]) - (-d2[0]) * d0[1]
            rhs = p2 - p0
            t = ((-d2[1]) * rhs[0] - (-d2[0]) * rhs[1]) / det
            return p0 + t * d0

        def _to_global(pt: np.ndarray) -> list:
            """Rotate by phi then translate to center."""
            return [
                cos_phi * pt[0] - sin_phi * pt[1] + cx,
                sin_phi * pt[0] + cos_phi * pt[1] + cy,
            ]

        # ------------------------------------------------------------------
        # Accumulate control points, weights and knot vector
        # ------------------------------------------------------------------
        ctrl_pts: list[list[float]] = []
        weights: list[float] = []

        # Start point (on ellipse)
        ctrl_pts.append(_to_global(_on_ellipse(theta0)))
        weights.append(1.0)

        for i in range(n_segs):
            t_a = theta0 + i * d_theta
            t_b = theta0 + (i + 1) * d_theta

            # Shoulder (off-ellipse) control point for this segment
            ctrl_pts.append(_to_global(_shoulder(t_a, t_b)))
            weights.append(w_mid)

            # End point of this segment (on ellipse); shared with next segment
            ctrl_pts.append(_to_global(_on_ellipse(t_b)))
            weights.append(1.0)

        # Interior knots are repeated (multiplicity = degree = 2) at each join
        knot_vector = [0.0, 0.0, 0.0]
        for i in range(1, n_segs):
            t = i / n_segs
            knot_vector.extend([t, t])
        knot_vector.extend([1.0, 1.0, 1.0])

        # ------------------------------------------------------------------
        # Assemble and return the SketchNurbs
        # ------------------------------------------------------------------
        nurbs = cls()
        nurbs._nurbs_curve.degree = 2
        nurbs._nurbs_curve.ctrlpts = ctrl_pts
        nurbs._nurbs_curve.knotvector = knot_vector
        nurbs._nurbs_curve.weights = weights

        return nurbs
