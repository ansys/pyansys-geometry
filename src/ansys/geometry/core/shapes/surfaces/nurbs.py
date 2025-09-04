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
"""Provides for creating and managing a NURBS surface."""

from typing import TYPE_CHECKING

from beartype import beartype as check_input_types

from ansys.geometry.core.math import Point3D
from ansys.geometry.core.shapes.surfaces.surface import Surface
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    import geomdl.NURBS as geomdl_nurbs  # noqa: N811

class NURBSSurface(Surface):
    """Represents a NURBS surface.

    Notes
    -----
    This class is a wrapper around the NURBS surface class from the `geomdl` library.
    By leveraging the `geomdl` library, this class provides a high-level interface
    to create and manipulate NURBS surfaces. The `geomdl` library is a powerful
    library for working with NURBS curves and surfaces. For more information, see
    https://pypi.org/project/geomdl/.

    """

    def __init__(self, geomdl_object: "geomdl_nurbs.Surface" = None):
        """Initialize ``NURBSSurface`` class."""
        try:
            import geomdl.NURBS as geomdl_nurbs  # noqa: N811
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "The `geomdl` library is required to use the NURBSSurface class. "
                "Please install it using `pip install geomdl`."
            ) from e

        self._nurbs_surface = geomdl_object if geomdl_object else geomdl_nurbs.Surface()

    @property
    def geomdl_nurbs_surface(self) -> "geomdl_nurbs.Surface":
        """Get the underlying `geomdl` NURBS surface object.
        
        Notes
        -----
        This property gives access to the full functionality of the NURBS surface
        coming from the `geomdl` library. Use with caution.
        """
        return self._nurbs_surface
    
    @property
    def control_points(self) -> list[Point3D]:
        """Get the control points of the NURBS surface."""
        return [Point3D(pt) for pt in self._nurbs_surface.ctrlpts]
    
    @property
    def degree_u(self) -> int:
        """Get the degree of the surface in the U direction."""
        return self._nurbs_surface.degree_u
    
    @property
    def degree_v(self) -> int:
        """Get the degree of the surface in the V direction."""
        return self._nurbs_surface.degree_v

    @property
    def knotvector_u(self) -> list[Real]:
        """Get the knot vector for the u-direction of the surface."""
        return self._nurbs_surface.knotvector_u

    @property
    def knotvector_v(self) -> list[Real]:
        """Get the knot vector for the v-direction of the surface."""
        return self._nurbs_surface.knotvector_v

    @property
    def weights(self) -> list[Real]:
        """Get the weights of the control points."""
        return self._nurbs_surface.weights
    
    @classmethod
    @check_input_types
    def fit_curve_from_points(
        cls,
        points: list[Point3D],
        size_u: int,
        size_v: int,
        degree_u: int,
        degree_v: int,
    ) -> "NURBSSurface":
        """Fit a NURBS surface to a set of points.

        Parameters
        ----------
        points : list[Point3D]
            Points to fit the surface to.
        size_u : int
            Number of control points in the U direction.
        size_v : int
            Number of control points in the V direction.
        degree_u : int
            Degree of the surface in the U direction.
        degree_v : int
            Degree of the surface in the V direction.

        Returns
        -------
        NURBSSurface
            Fitted NURBS surface.
        """
        from geomdl import fitting

        converted_pts = [[*pt] for pt in points]

        surface = fitting.interpolate_surface(
            converted_pts,
            size_u=size_u,
            size_v=size_v,
            degree_u=degree_u,
            degree_v=degree_v,
        )

        nurbs_surface = cls()
        nurbs_surface._nurbs_surface.degree_u = degree_u
        nurbs_surface._nurbs_surface.degree_v = degree_v
        nurbs_surface._nurbs_surface.ctrlpts = surface.ctrlpts
        nurbs_surface._nurbs_surface.knotvector = surface.knotvector
        nurbs_surface._nurbs_surface.weights = surface.weights

        return nurbs_surface