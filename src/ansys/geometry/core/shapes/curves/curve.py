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
"""Provides the ``Curve`` class."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ansys.geometry.core.math.matrix import Matrix44
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.shapes.curves.curve_evaluation import CurveEvaluation
from ansys.geometry.core.shapes.parameterization import Interval, Parameterization
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.shapes.curves.trimmed_curve import TrimmedCurve


class Curve(ABC):
    """Provides the abstract base class representing a 3D curve."""

    @abstractmethod
    def parameterization(self) -> Parameterization:
        """Parameterize the curve."""
        return

    @abstractmethod
    def contains_param(self, param: Real) -> bool:
        """Check a parameter is within the parametric range of the curve."""
        return

    @abstractmethod
    def contains_point(self, point: Point3D) -> bool:
        """Check a point is contained by the curve.

        The point can either lie within the curve or on its boundary.
        """
        return

    @abstractmethod
    def transformed_copy(self, matrix: Matrix44) -> "Curve":
        """Create a transformed copy of the curve."""
        return

    @abstractmethod
    def __eq__(self, other: "Curve") -> bool:
        """Determine if two curves are equal."""
        return

    @abstractmethod
    def evaluate(self, parameter: Real) -> CurveEvaluation:
        """Evaluate the curve at the given parameter."""
        return

    @abstractmethod
    def project_point(self, point: Point3D) -> CurveEvaluation:
        """Project a point to the curve.

        This method returns the evaluation at the closest point.
        """
        return

    def trim(self, interval: Interval) -> "TrimmedCurve":
        """Trim this curve by bounding it with an interval.

        Returns
        -------
        TrimmedCurve
            The resulting bounded curve.
        """
        from ansys.geometry.core.shapes.curves.trimmed_curve import TrimmedCurve

        return TrimmedCurve(
            self,
            self.evaluate(interval.start).position,
            self.evaluate(interval.end).position,
            interval,
            None,
        )
