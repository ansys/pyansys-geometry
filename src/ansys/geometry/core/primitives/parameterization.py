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
"""Provides the parametrization-related classes."""

from enum import Enum, unique

from beartype import beartype as check_input_types
import numpy as np

from ansys.geometry.core.typing import Real


class ParamUV:
    """
    Parameter class containing 2 parameters: (u, v).

    Notes
    -----
    Likened to a 2D point in UV space Used as an argument in parametric
    surface evaluations. This matches the service implementation for the
    Geometry service.

    Parameters
    ----------
    u : Real
        u-parameter.
    v : Real
        v-parameter.
    """

    def __init__(self, u: Real, v: Real) -> None:
        """Initialize ``ParamUV`` class."""
        self._u = u
        self._v = v

    @property
    def u(self) -> Real:
        """u-parameter."""
        return self._u

    @property
    def v(self) -> Real:
        """v-parameter."""
        return self._v

    @check_input_types
    def __add__(self, other: "ParamUV") -> "ParamUV":
        """
        Add the u and v components of the other ParamUV to this ParamUV.

        Parameters
        ----------
        other : ParamUV
            The parameters to add these parameters.

        Returns
        -------
        ParamUV
            The sum of the parameters.
        """
        return ParamUV(self._u + other._u, self._v + other._v)

    @check_input_types
    def __sub__(self, other: "ParamUV") -> "ParamUV":
        """
        Subtract the u and v components of the other ParamUV from this ParamUV.

        Parameters
        ----------
        other : ParamUV
            The parameters to subtract from these parameters.

        Returns
        -------
        ParamUV
            The difference of the parameters.
        """
        return ParamUV(self._u - other._u, self._v - other._v)

    @check_input_types
    def __mul__(self, other: "ParamUV") -> "ParamUV":
        """
        Multiplies the u and v components of this ParamUV by the other ParamUV.

        Parameters
        ----------
        other : ParamUV
            The parameters to multiply by these parameters.

        Returns
        -------
        ParamUV
            The product of the parameters.
        """
        return ParamUV(self._u * other._u, self._v * other._v)

    @check_input_types
    def __truediv__(self, other: "ParamUV") -> "ParamUV":
        """
        Divides the u and v components of this ParamUV by the other ParamUV.

        Parameters
        ----------
        other : ParamUV
            The parameters to divide these parameters by.

        Returns
        -------
        ParamUV
            The quotient of the parameters.
        """
        return ParamUV(self._u / other._u, self._v / other._v)

    def __repr__(self) -> str:
        """Represent the ``ParamUV`` as a string."""
        return f"ParamUV(u={self.u}, v={self.v})"


class Interval:
    """
    Interval class that defines a range of values.

    Parameters
    ----------
    start : Real
        Start value of the interval.
    end : Real
        End value of the interval.
    """

    @check_input_types
    def __init__(self, start: Real, end: Real) -> None:
        """Initialize ``Interval`` class."""
        if end < start:
            raise ValueError("Start value must be less than end value")

        self._start = start
        self._end = end

    @property
    def start(self) -> Real:
        """Start value of the interval."""
        return self._start

    @property
    def end(self) -> Real:
        """End value of the interval."""
        return self._end

    def is_open(self) -> bool:
        """
        If the interval is open (-inf, inf).

        Returns
        -------
        bool
            True if both ends of the interval are negative and positive infinity respectively.
        """
        return np.isneginf(self.start) and np.isinf(self.end)

    def is_closed(self) -> bool:
        """
        If the interval is closed. Neither value is inf or -inf.

        Returns
        -------
        bool
            True if neither bound of the interval is infinite.
        """
        return self.start > np.NINF and self.end < np.inf

    def get_span(self) -> Real:
        """
        Return the quantity contained by the interval. Interval must be closed.

        Returns
        -------
        Real
            The difference between the end and start of the interval.
        """
        if not self.is_closed():
            raise ValueError("Interval must be closed to get the span.")

        return self.end - self.start

    def __repr__(self) -> str:
        """Represent the ``Interval`` as a string."""
        return f"Interval(start={self.start}, end={self.end})"


@unique
class ParamForm(Enum):
    """ParamForm enum class that defines the form of a Parameterization."""

    OPEN = 1
    CLOSED = 2
    PERIODIC = 3
    OTHER = 4


@unique
class ParamType(Enum):
    """ParamType enum class that defines the type of a Parameterization."""

    LINEAR = 1
    CIRCULAR = 2
    OTHER = 3


class Parameterization:
    """
    Parameterization class describes the parameters of a specific geometry.

    Parameters
    ----------
    form : ParamForm
        Form of the parameterization.
    type : ParamType
        Type of the parameterization.
    interval : Interval
        Interval of the parameterization.
    """

    @check_input_types
    def __init__(self, form: ParamForm, type: ParamType, interval: Interval) -> None:
        """Initialize ``Parameterization`` class."""
        self._form = form
        self._type = type
        self._interval = interval

    @property
    def form(self) -> ParamForm:
        """The form of the parameterization."""
        return self._form

    @property
    def type(self) -> ParamType:
        """The type of the parameterization."""
        return self._type

    @property
    def interval(self) -> Interval:
        """The interval of the parameterization."""
        return self._interval

    def __repr__(self) -> str:
        """Represent the ``Parameterization`` as a string."""
        return f"Parameterization(form={self.form}, type={self.type}, interval={self.interval})"
