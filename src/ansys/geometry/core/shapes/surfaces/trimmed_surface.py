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
"""Provides the ``TrimmedSurface`` class."""

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.shapes.box_uv import BoxUV
from ansys.geometry.core.shapes.parameterization import ParamUV
from ansys.geometry.core.shapes.surfaces.surface import Surface
from ansys.geometry.core.shapes.surfaces.surface_evaluation import SurfaceEvaluation
from ansys.geometry.core.typing import Real


class TrimmedSurface:
    """Represents a trimmed surface.

    A trimmed surface is a surface that has a boundary. This boundary comes in the form of a
    bounding BoxUV.

    Parameters
    ----------
    face : Face
        Face that the trimmed surface belongs to.
    geometry : Surface
        Underlying mathematical representation of the surface.
    """

    def __init__(self, geometry: Surface, box_uv: BoxUV):
        """Initialize an instance of a trimmed surface."""
        self._geometry = geometry
        self._box_uv = box_uv

    @property
    def geometry(self) -> Surface:
        """Underlying mathematical surface."""
        return self._geometry

    @property
    def box_uv(self) -> BoxUV:
        """Bounding BoxUV of the surface."""
        return self._box_uv

    def get_proportional_parameters(self, param_uv: ParamUV) -> ParamUV:
        """Convert non-proportional parameters into proportional parameters.

        Parameters
        ----------
        param_uv : ParamUV
            Non-proportional UV parameters.

        Returns
        -------
        ParamUV
            Proportional (from 0-1) UV parameters.
        """
        bounds_u = self.box_uv.interval_u
        bounds_v = self.box_uv.interval_v
        u = param_uv.u
        v = param_uv.v
        return (
            (u - bounds_u.start) / bounds_u.get_span(),
            (v - bounds_v.start) / bounds_v.get_span(),
        )

    def normal(self, u: Real, v: Real) -> UnitVector3D:
        """Provide the normal to the surface.

        Parameters
        ----------
        u : Real
            First coordinate of the 2D representation of a surface in UV space.
        v : Real
            Second coordinate of the 2D representation of a surface in UV space.

        Returns
        -------
        UnitVector3D
            Unit vector is normal to the surface at the given UV coordinates.
        """
        return self.evaluate_proportion(u, v).normal

    def project_point(self, point: Point3D) -> SurfaceEvaluation:
        """Project a point onto the surface and evaluate it at that location.

        Parameters
        ----------
        point : Point3D
            Point to project onto the surface.

        Returns
        -------
        SurfaceEvaluation
            Resulting evaluation.
        """
        return self.geometry.project_point(point)

    def evaluate_proportion(self, u: Real, v: Real) -> SurfaceEvaluation:
        """Evaluate the surface at proportional u and v parameters.

        Parameters
        ----------
        u : Real
            U parameter in the proportional range [0,1].
        v : Real
            V parameter in the proportional range [0,1].

        Returns
        -------
        SurfaceEvaluation
            Resulting surface evaluation.
        """
        bounds_u = self.box_uv.interval_u
        bounds_v = self.box_uv.interval_v
        return self.geometry.evaluate(
            ParamUV(
                bounds_u.start + bounds_u.get_span() * u,
                bounds_v.start + bounds_v.get_span() * v,
            )
        )

    # TODO: perimeter, area?
    # https://github.com/ansys/pyansys-geometry/issues/1319


class ReversedTrimmedSurface(TrimmedSurface):
    """Represents a reversed trimmed surface.

    When a surface is reversed, its normal vector is negated to provide the proper
    outward facing vector.

    Parameters
    ----------
    face : Face
        Face that the trimmed surface belongs to.
    geometry : Surface
        Underlying mathematical representation of the surface.
    """

    def __init__(self, geometry: Surface, box_uv: BoxUV):
        """Initialize an instance of a reversed trimmed surface."""
        super().__init__(geometry, box_uv)

    def normal(self, u: Real, v: Real) -> UnitVector3D:  # noqa: D102
        return -self.evaluate_proportion(u, v).normal

    def project_point(self, point: Point3D) -> SurfaceEvaluation:  # noqa: D102
        evaluation = self.geometry.project_point(point)
        evaluation.normal = -evaluation.normal
        return evaluation
