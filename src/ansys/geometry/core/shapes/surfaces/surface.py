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

from beartype.typing import Tuple

from ansys.geometry.core.math import Matrix44, Point3D
from ansys.geometry.core.shapes.parameterization import Parameterization, ParamUV
from ansys.geometry.core.shapes.surfaces.surface_evaluation import SurfaceEvaluation


class Surface(ABC):
    """Provides the abstract base class for a 3D surface."""

    @abstractmethod
    def parameterization(self) -> Tuple[Parameterization, Parameterization]:
        """Parameterize the surface as a tuple (U and V respectively)."""
        return

    @abstractmethod
    def contains_param(self, param_uv: ParamUV) -> bool:
        """Test whether a parameter is within the parametric range of the surface."""
        return

    @abstractmethod
    def contains_point(self, point: Point3D) -> bool:
        """
        Test whether the point is contained by the surface.

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
        """
        Project a point to the surface.

        This method returns the evaluation at the closest point.
        """
        return

    # TODO: Implement more surface methods
    # is_ruled
    # is_singular
    # get_length
    # intersect_curve
    # intersect_surface
    # is_coincident
