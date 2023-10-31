# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.

from beartype.roar import BeartypeCallHintParamViolation
import numpy as np
import pytest

from ansys.geometry.core.misc.accuracy import Accuracy
from ansys.geometry.core.primitives.parameterization import (
    Interval,
    Parameterization,
    ParamForm,
    ParamType,
    ParamUV,
)


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
    open_interval = Interval(np.NINF, np.inf)
    closed_interval = Interval(-1, 1)
    open_start = Interval(np.NINF, 1)
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


def test_param_TYPE():
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
