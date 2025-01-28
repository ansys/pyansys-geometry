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
""" "Testing of measurement tools."""

from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.tools.measurement_tools import Gap

from .conftest import FILES_DIR, skip_if_core_service


def test_distance_property(modeler: Modeler):
    """Test if the gap object is being constructed properly."""
    gap = Gap(distance=Distance(10))
    assert gap.distance._value == 10.0


def test_min_distance_between_objects(modeler: Modeler):
    """Test if split edge problem areas are detectable."""
    skip_if_core_service(
        modeler, test_min_distance_between_objects.__name__, "measurement_tools"
    )  # Skip test on CoreService
    design = modeler.open_file(FILES_DIR / "MixingTank.scdocx")
    gap = modeler.measurement_tools.min_distance_between_objects(design.bodies[2], design.bodies[1])
    assert abs(gap.distance._value - 0.0892) <= 0.01
