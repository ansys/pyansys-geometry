# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Integration tests for the DesignCurve class."""

import numpy as np
import pytest

from ansys.geometry.core.designer.designcurve import DesignCurve
from ansys.geometry.core.math.constants import UNITVECTOR3D_Z
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.misc import UNITS, Angle
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.shapes.curves.line import Line
from ansys.geometry.core.shapes.curves.trimmed_curve import TrimmedCurve


def _create_curves(modeler: Modeler) -> tuple[DesignCurve, DesignCurve]:
    """Create two reusable design curves for testing.

    - curve1: quarter-circle arc at r=1 m around the Z-axis
              (length = pi/2 m, start = [1, 0, 0] m, end = [0, 1, 0] m)
    - curve2: semicircle arc at r=2 m around the Z-axis
              (length = 2*pi m, start = [2, 0, 0] m, end = [-2, 0, 0] m)
    """
    design = modeler.create_design("design_curve_tests")
    axis = Line(Point3D([0, 0, 0]), UNITVECTOR3D_Z)

    dp1 = design.add_design_point("curve_point1", Point3D([1, 0, 0], UNITS.m))
    curve1 = modeler.geometry_commands.revolve_points(dp1, axis, Angle(np.pi / 2, UNITS.rad))[0]

    dp2 = design.add_design_point("curve_point2", Point3D([2, 0, 0], UNITS.m))
    curve2 = modeler.geometry_commands.revolve_points(dp2, axis, Angle(np.pi, UNITS.rad))[0]

    return curve1, curve2


def test_design_curve_basic_properties(modeler: Modeler):
    """Test id, name, is_alive, and parent_component on newly created design curves."""
    curve1, curve2 = _create_curves(modeler)

    # IDs are non-empty strings assigned by the server; each curve gets a unique ID
    assert isinstance(curve1.id, str)
    assert len(curve1.id) > 0
    assert isinstance(curve2.id, str)
    assert len(curve2.id) > 0
    assert curve1.id != curve2.id

    # Names are non-empty strings
    assert isinstance(curve1.name, str)
    assert len(curve1.name) > 0
    assert isinstance(curve2.name, str)
    assert len(curve2.name) > 0

    # Both curves are alive immediately after creation
    assert curve1.is_alive is True
    assert curve2.is_alive is True

    # Curves created under the root design share the same parent component (the design itself)
    assert curve1.parent_component is modeler.design
    assert curve2.parent_component is modeler.design


def test_design_curve_length_start_end(modeler: Modeler):
    """Test the length, start, and end properties for both test curves."""
    curve1, curve2 = _create_curves(modeler)

    # curve1: quarter-circle at r=1 m → arc length = pi/2 m
    assert curve1.length.value.m == pytest.approx(np.pi / 2, rel=1e-5)
    assert np.allclose(curve1.start, Point3D([1, 0, 0]), atol=1e-6)
    assert np.allclose(curve1.end, Point3D([0, 1, 0]), atol=1e-6)

    # curve2: semicircle at r=2 m → arc length = 2*pi m
    assert curve2.length.value.m == pytest.approx(2 * np.pi, rel=1e-5)
    assert np.allclose(curve2.start, Point3D([2, 0, 0]), atol=1e-6)
    assert np.allclose(curve2.end, Point3D([-2, 0, 0]), atol=1e-6)


def test_design_curve_shape(modeler: Modeler):
    """Test that shape returns a TrimmedCurve with correct geometry and is cached on re-access."""
    curve1, curve2 = _create_curves(modeler)

    # shape is a TrimmedCurve whose start, end, length, and interval match the curve
    shape1 = curve1.shape
    assert isinstance(shape1, TrimmedCurve)
    assert np.allclose(shape1.start, Point3D([1, 0, 0]), atol=1e-6)
    assert np.allclose(shape1.end, Point3D([0, 1, 0]), atol=1e-6)
    assert shape1.length.m == pytest.approx(np.pi / 2, rel=1e-5)
    assert shape1.interval is not None
    assert shape1.geometry is not None

    # Repeated access returns the same cached object (no additional server round-trip)
    assert curve1.shape is shape1

    # Verify the second curve's shape independently
    shape2 = curve2.shape
    assert isinstance(shape2, TrimmedCurve)
    assert np.allclose(shape2.start, Point3D([2, 0, 0]), atol=1e-6)
    assert np.allclose(shape2.end, Point3D([-2, 0, 0]), atol=1e-6)
    assert shape2.length.m == pytest.approx(2 * np.pi, rel=1e-5)
    assert curve2.shape is shape2


def test_design_curve_repr(modeler: Modeler):
    """Test that __repr__ includes all expected section headers and the curve's own data."""
    curve1, _ = _create_curves(modeler)

    text = repr(curve1)
    assert "ansys.geometry.core.designer.DesignCurve" in text
    assert "ID" in text
    assert curve1.id in text
    assert "Name" in text
    assert curve1.name in text
    assert "Length" in text
    assert "Start" in text
    assert "End" in text
