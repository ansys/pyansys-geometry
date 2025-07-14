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
"""Test shapes."""

import re

import numpy as np
import pytest

from ansys.geometry.core.math import (
    IDENTITY_MATRIX44,
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    Point3D,
    Vector3D,
)
from ansys.geometry.core.shapes import (
    ParamUV,
    PlaneSurface,
    SurfaceEvaluation,
)
from ansys.geometry.core.shapes.box_uv import BoxUV, LocationUV
from ansys.geometry.core.shapes.curves import CurveEvaluation
from ansys.geometry.core.shapes.parameterization import Interval


def test_box_uv():
    """Test BoxUV class"""
    box_uv1 = BoxUV(Interval(0, np.pi * 2), Interval(0, np.pi / 2))
    box_uv2 = BoxUV(Interval(0, np.pi * 2), Interval(0, np.pi / 2))
    param_uv1 = ParamUV(0, 0.03)
    assert BoxUV.__eq__(box_uv1, box_uv2)
    assert BoxUV.__eq__(box_uv1, param_uv1)
    assert not BoxUV.__ne__(box_uv1, box_uv2)
    assert BoxUV.__ne__(box_uv1, param_uv1)
    assert BoxUV.is_negative(box_uv1, 0, 0)
    assert BoxUV.is_negative(BoxUV(Interval(-1, -0.5), Interval(-2, -1)), 0, 0)
    assert BoxUV.contains(box_uv2, param_uv1)
    BoxUV.inflate(box_uv1, 2, 1.5)
    assert round(box_uv1.interval_u.end, 5) == 6.28319
    assert round(box_uv1.interval_v.end, 5) == 1.57080
    assert round(box_uv1.proportion(0.1, 0.5).u, 5) == 0.62832
    assert round(box_uv1.proportion(0.2, 0.35).v, 5) == 0.54978
    assert round(box_uv1.get_center().u, 5) == 3.14159
    assert round(box_uv1.get_center().v, 5) == 0.78540
    assert round(box_uv1.get_corner(LocationUV.TopLeft).u, 5) == 0.0
    assert round(box_uv1.get_corner(LocationUV.BottomLeft).u, 5) == 0.0
    assert round(box_uv1.get_corner(LocationUV.LeftCenter).u, 5) == 0.0
    assert round(box_uv1.get_corner(LocationUV.TopRight).u, 5) == 6.28319
    assert round(box_uv1.get_corner(LocationUV.BottomRight).u, 5) == 6.28319
    assert round(box_uv1.get_corner(LocationUV.RightCenter).u, 5) == 6.28319
    assert round(box_uv1.get_corner(LocationUV.BottomCenter).u, 5) == 3.14159
    assert round(box_uv1.get_corner(LocationUV.TopCenter).u, 5) == 3.14159


def test_unite_interval():
    """Test unite interval functionality."""
    with pytest.raises(ValueError, match="Start value must be less than end value"):
        Interval(5, 0)
    interval1 = Interval(0, 5)
    interval2 = Interval(1, 3)

    assert interval1.__eq__(4) == NotImplemented
    assert not interval1.__eq__(interval2)
    assert interval2.__eq__(interval2)

    # Test unite
    united_interval = Interval.unite(interval1, interval2)
    assert united_interval.start == 0
    assert united_interval.end == 5

    united_interval = Interval.unite(interval2, interval1)
    assert united_interval.start == 0
    assert united_interval.end == 5

    united_interval = Interval.unite(interval1, Interval(1, 10))
    assert united_interval.start == 0
    assert united_interval.end == 10

    # Test self_unite
    interval1.self_unite(interval2)
    assert interval1.start == 0
    assert interval1.end == 5


def test_intersect_interval():
    """Test intersect interval functionality."""

    interval1 = Interval(0, 50)
    interval2 = Interval(5, 20)
    tolerance = 0.1

    # Test intersection
    intersection = Interval.intersect(interval1, interval2, tolerance)
    assert intersection is not None
    assert intersection.start == 5
    assert intersection.end == 20
    # Test intersection with no overlap
    interval2 = Interval(60, 80)
    with pytest.raises(ValueError, match="Start value must be less than end value"):
        Interval.intersect(interval1, interval2, tolerance)
    # Test intersection with negative intervals
    interval1 = Interval(-10, -1)
    interval2 = Interval(-12, -3)
    intersection = Interval.intersect(interval1, interval2, tolerance)
    assert intersection is not None
    assert intersection.start == -10
    assert intersection.end == -3

    interval1.self_intersect(interval2, tolerance)
    assert interval1.start == -10
    assert interval1.end == -1


def test_contains_value():
    """Test the contains_value method of the Interval class."""
    # Case 1: Value within the interval
    interval = Interval(0, 10)
    assert interval.contains_value(5, 0.1) is True
    # Case 2: Value outside the interval
    assert interval.contains_value(15, 0.1) is False
    # Case 3: Value near the start boundary within accuracy
    assert interval.contains_value(0.05, 0.1) is True
    # Case 4: Value near the end boundary within accuracy
    assert interval.contains_value(9.95, 0.1) is True
    # Case 5: Value near the start boundary outside accuracy
    assert interval.contains_value(-0.2, 0.1) is False
    # Case 6: Value near the end boundary outside accuracy
    assert interval.contains_value(10.2, 0.1) is False
    # Case 8: Reversed interval (start > end)
    reversed_interval = Interval(0, 10)  # Simulate reversed interval
    reversed_interval._start = 10  # Manually override to simulate invalid state
    reversed_interval._end = 0
    assert reversed_interval.contains_value(5, 0.1) is True
    # Case 9: Value exactly at the start
    assert interval.contains_value(0, 0.1) is True
    # Case 10: Value exactly at the end
    assert interval.contains_value(10, 0.1) is True
    # Case 11: Value less than start with tolerance
    assert reversed_interval.contains_value(-2, 1) is False
    # Case 12: Value greater than end with tolerance
    assert reversed_interval.contains_value(11, 0.5) is False


def test_planar_surface():
    """Test the planar surface functionality."""
    with pytest.raises(
        ValueError, match="Plane reference (dir_x) and axis (dir_z) must be perpendicular."
    ):
        PlaneSurface(Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_X)
    plane0 = PlaneSurface(Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_Y)
    plane1 = PlaneSurface(Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_Y)
    assert plane0.__eq__(plane1) is True
    with pytest.raises(
        NotImplementedError, match=re.escape("contains_param() is not implemented.")
    ):
        plane0.contains_param(ParamUV(0.5, 0.5))
    with pytest.raises(
        NotImplementedError, match=re.escape("contains_point() is not implemented.")
    ):
        plane0.contains_point(Point3D([0, 0, 0]))
    u, v = plane0.parameterization()
    assert u
    assert v
    plane3 = plane0.transformed_copy(IDENTITY_MATRIX44)
    assert plane3.__eq__(plane0) is True
    plane_evaluation = plane0.evaluate(ParamUV(0.5, 0.5))
    assert plane_evaluation.u_derivative == UNITVECTOR3D_Y
    assert plane_evaluation.v_derivative == Vector3D([0.0, 0.0, -1.0])
    assert plane_evaluation.uu_derivative == Vector3D([0, 0, 0])
    assert plane_evaluation.uv_derivative == Vector3D([0, 0, 0])
    assert plane_evaluation.vv_derivative == Vector3D([0, 0, 0])
    assert plane_evaluation.min_curvature == 0
    assert plane_evaluation.min_curvature_direction == UNITVECTOR3D_X
    assert plane_evaluation.max_curvature == 0
    assert plane_evaluation.max_curvature_direction == Vector3D([0.0, 0.0, -1.0])


def test_surface_evaluation():
    """Test the surface evaluation functionality."""
    plane0 = SurfaceEvaluation(ParamUV(0.5, 0.5))
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the parameter definition."
    ):
        plane0.parameter()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the position definition."
    ):
        plane0.position()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the position definition."
    ):
        plane0.normal()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the u-derivative definition."
    ):
        plane0.u_derivative()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the v-derivative definition."
    ):
        plane0.v_derivative()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the uu-derivative definition."
    ):
        plane0.uu_derivative()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the uv-derivative definition."
    ):
        plane0.uv_derivative()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the vv-derivative definition."
    ):
        plane0.vv_derivative()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the minimum curvature definition."
    ):
        plane0.min_curvature()
    with pytest.raises(
        NotImplementedError,
        match="Each evaluation must provide the minimum curvature direction definition.",
    ):
        plane0.min_curvature_direction()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the maximum curvature definition."
    ):
        plane0.max_curvature()
    with pytest.raises(
        NotImplementedError,
        match="Each evaluation must provide the maximum curvature direction definition.",
    ):
        plane0.max_curvature_direction()


def test_curve_evaluation():
    """Test the curve evaluation functionality."""
    curve0 = CurveEvaluation(3)
    assert curve0.is_set()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the parameter definition."
    ):
        curve0.parameter()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the position definition."
    ):
        curve0.position()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the first_derivative definition."
    ):
        curve0.first_derivative()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the second_derivative definition."
    ):
        curve0.second_derivative()
    with pytest.raises(
        NotImplementedError, match="Each evaluation must provide the curvature definition."
    ):
        curve0.curvature()
