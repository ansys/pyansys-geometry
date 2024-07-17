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
"""Provides for creating and managing a curve."""

from functools import cached_property

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import Vector3D
from ansys.geometry.core.typing import Real


class CurveEvaluation:
    """Provides for evaluating a curve."""

    def __init__(self, parameter: Real = None) -> None:
        """Initialize the ``CurveEvaluation`` class."""
        self._parameter = parameter

    def is_set(self) -> bool:
        """Determine if the parameter for the evaluation has been set."""
        return self._parameter is not None

    @property
    def parameter(self) -> Real:
        """Parameter that the evaluation is based upon."""
        raise NotImplementedError("Each evaluation must provide the parameter definition.")

    @cached_property
    def position(self) -> Point3D:
        """Position of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the position definition.")

    @cached_property
    def first_derivative(self) -> Vector3D:
        """First derivative of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the first_derivative definition.")

    @cached_property
    def second_derivative(self) -> Vector3D:
        """Second derivative of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the second_derivative definition.")

    @cached_property
    def curvature(self) -> Real:
        """Curvature of the evaluation."""
        raise NotImplementedError("Each evaluation must provide the curvature definition.")
