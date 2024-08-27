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
"""Provides the ``Surface`` class."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.shapes.box_uv import BoxUV
from ansys.geometry.core.shapes.parameterization import Parameterization, ParamUV
from ansys.geometry.core.shapes.surfaces.surface_evaluation import SurfaceEvaluation

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.shapes.surfaces.trimmed_surface import TrimmedSurface


class Surface(ABC):
    """Provides the abstract base class for a 3D surface."""

    @abstractmethod
    def parameterization(self) -> tuple[Parameterization, Parameterization]:
        """Parameterize the surface as a tuple (U and V respectively)."""
        return

    @abstractmethod
    def contains_param(self, param_uv: ParamUV) -> bool:
        """Check a parameter is within the parametric range of the surface."""
        return

    @abstractmethod
    def contains_point(self, point: Point3D) -> bool:
        """Check a point is contained by the surface.

        The point can either lie within the surface or on its boundary.
        """
        return

    @abstractmethod
    def transformed_copy(self, matrix: Matrix44) -> "Surface":
        """Create a transformed copy of the surface."""
        return

    @abstractmethod
    def __eq__(self, other: "Surface") -> bool:
        """Determine if two surfaces are equal."""
        return

    @abstractmethod
    def evaluate(self, parameter: ParamUV) -> SurfaceEvaluation:
        """Evaluate the surface at the given parameter."""
        return

    @abstractmethod
    def project_point(self, point: Point3D) -> SurfaceEvaluation:
        """Project a point to the surface.

        This method returns the evaluation at the closest point.
        """
        return

    def trim(self, box_uv: BoxUV) -> "TrimmedSurface":
        """Trim this surface by bounding it with a BoxUV.

        Returns
        -------
        TrimmedSurface
            The resulting bounded surface.
        """
        from ansys.geometry.core.shapes.surfaces.trimmed_surface import TrimmedSurface

        return TrimmedSurface(self, box_uv)
