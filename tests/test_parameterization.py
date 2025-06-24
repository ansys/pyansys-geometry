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

from beartype.roar import BeartypeCallHintParamViolation
import numpy as np
import pytest

from ansys.geometry.core.misc.accuracy import Accuracy
from ansys.geometry.core.shapes import Interval, Parameterization, ParamForm, ParamType, ParamUV


def test_param_uv():
    p = ParamUV(1, 1)
    p2 = ParamUV(1, 2)

    assert p.u == 1
    assert p.v == 1

    sum = p + p2
    assert sum.u == 2
    assert sum.v == 3

    diff = p - p2
    assert diff.u == 0
    assert diff.v == -1

    prod = p * p2
    assert prod.u == 1
    assert prod.v == 2

    quot = p / p2
    assert Accuracy.length_is_equal(quot.u, 1)
    assert Accuracy.length_is_equal(quot.v, 0.5)


def test_interval():
    open_interval = Interval(-np.inf, np.inf)
    closed_interval = Interval(-1, 1)
    open_start = Interval(-np.inf, 1)
    open_end = Interval(-1, np.inf)

    assert np.isneginf(open_interval.start)
    assert np.isinf(open_interval.end)

    assert open_interval.is_open()
    assert not closed_interval.is_open()
    assert not open_start.is_open()
    assert not open_end.is_open()

    assert not open_interval.is_closed()
    assert closed_interval.is_closed()
    assert not open_start.is_closed()
    assert not open_end.is_closed()

    with pytest.raises(ValueError):
        open_interval.get_span()
    with pytest.raises(ValueError):
        open_start.get_span()
    with pytest.raises(ValueError):
        open_end.get_span()

    assert closed_interval.get_span() == 2


def test_param_form():
    open = ParamForm.OPEN
    closed = ParamForm.CLOSED
    periodic = ParamForm.PERIODIC
    other = ParamForm.OTHER

    assert open.name == "OPEN"
    assert open.value == 1

    assert closed.name == "CLOSED"
    assert closed.value == 2

    assert periodic.name == "PERIODIC"
    assert periodic.value == 3

    assert other.name == "OTHER"
    assert other.value == 4


def test_param_type():
    linear = ParamType.LINEAR
    circular = ParamType.CIRCULAR
    other = ParamType.OTHER

    assert linear.name == "LINEAR"
    assert linear.value == 1

    assert circular.name == "CIRCULAR"
    assert circular.value == 2

    assert other.name == "OTHER"
    assert other.value == 3


def test_parameterization():
    p = Parameterization(ParamForm.PERIODIC, ParamType.CIRCULAR, Interval(0, 2 * np.pi))
    assert p.form == ParamForm.PERIODIC
    assert p.type == ParamType.CIRCULAR
    assert p.interval.start == 0
    assert Accuracy.length_is_equal(p.interval.end, 2 * np.pi)
    assert p.interval.is_closed()

    with pytest.raises(BeartypeCallHintParamViolation):
        Parameterization(ParamType.CIRCULAR, ParamType.OTHER, Interval(-1, 1))

    with pytest.raises(BeartypeCallHintParamViolation):
        Parameterization(ParamForm.CLOSED, ParamForm.CLOSED, Interval(-1, 1))

    with pytest.raises(BeartypeCallHintParamViolation):
        Parameterization(ParamForm.CLOSED, ParamType.OTHER, [-1, 1])


def test_param_uv_iter():
    """Test the __iter__ method of ParamUV."""
    param = ParamUV(3.5, 7.2)
    u, v = param  # Unpack using the __iter__ method
    assert u == 3.5
    assert v == 7.2


def test_param_uv_repr():
    """Test the __repr__ method of ParamUV."""
    param = ParamUV(3.5, 7.2)
    assert repr(param) == "ParamUV(u=3.5, v=7.2)"


def test_parameterization_repr():
    """Test the __repr__ method of the Parameterization class."""
    # Create a sample Parameterization object
    interval = Interval(0, 10)
    parameterization = Parameterization(ParamForm.CLOSED, ParamType.LINEAR, interval)
    # Expected string representation
    expected_repr = (
        "Parameterization(form=ParamForm.CLOSED, type=ParamType.LINEAR, "
        "interval=Interval(start=0, end=10))"
    )
    # Assert the __repr__ output matches the expected string
    assert repr(parameterization) == expected_repr
