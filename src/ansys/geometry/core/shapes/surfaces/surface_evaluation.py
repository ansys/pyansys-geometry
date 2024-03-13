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
"""Provides for evaluating a surface."""

from functools import cached_property

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.shapes.parameterization import ParamUV
from ansys.geometry.core.typing import Real


class SurfaceEvaluation:
    """Provides for evaluating a surface."""

    def __init__(self, parameter: ParamUV) -> None:
        """Initialize the ``SurfaceEvaluation`` class."""
        self._parameter = parameter

    @property
    def parameter(self) -> ParamUV:
        """Parameter that the evaluation is based upon."""
        raise NotImplementedError("Each evaluation must provide the parameter definition.")

    @cached_property
    def position(self) -> Point3D:
        """Point on the surface, based on the evaluation."""
        raise NotImplementedError("Each evaluation must provide the position definition.")

    @cached_property
    def normal(self) -> UnitVector3D:
        """Normal to the surface."""
        raise NotImplementedError("Each evaluation must provide the position definition.")

    @cached_property
    def u_derivative(self) -> Vector3D:
        """First derivative with respect to the U parameter."""
        raise NotImplementedError("Each evaluation must provide the u-derivative definition.")

    @cached_property
    def v_derivative(self) -> Vector3D:
        """First derivative with respect to the V parameter."""
        raise NotImplementedError("Each evaluation must provide the v-derivative definition.")

    @cached_property
    def uu_derivative(self) -> Vector3D:
        """Second derivative with respect to the U parameter."""
        raise NotImplementedError("Each evaluation must provide the uu-derivative definition.")

    @cached_property
    def uv_derivative(self) -> Vector3D:
        """The second derivative with respect to the U and V parameters."""
        raise NotImplementedError("Each evaluation must provide the uv-derivative definition.")

    @cached_property
    def vv_derivative(self) -> Vector3D:
        """The second derivative with respect to v."""
        raise NotImplementedError("Each evaluation must provide the vv-derivative definition.")

    @cached_property
    def min_curvature(self) -> Real:
        """Minimum curvature."""
        raise NotImplementedError("Each evaluation must provide the minimum curvature definition.")

    @cached_property
    def min_curvature_direction(self) -> UnitVector3D:
        """Minimum curvature direction."""
        raise NotImplementedError(
            "Each evaluation must provide the minimum curvature direction definition."
        )

    @cached_property
    def max_curvature(self) -> Real:
        """Maximum curvature."""
        raise NotImplementedError("Each evaluation must provide the maximum curvature definition.")

    @cached_property
    def max_curvature_direction(self) -> UnitVector3D:
        """Maximum curvature direction."""
        raise NotImplementedError(
            "Each evaluation must provide the maximum curvature direction definition."
        )
