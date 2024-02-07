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
"""Provides the PyAnsys Geometry miscellaneous subpackage."""

from ansys.geometry.core.misc.accuracy import ANGLE_ACCURACY, LENGTH_ACCURACY, Accuracy
from ansys.geometry.core.misc.auxiliary import (
    get_bodies_from_ids,
    get_design_from_body,
    get_design_from_component,
    get_design_from_edge,
    get_design_from_face,
    get_edges_from_ids,
    get_faces_from_ids,
)
from ansys.geometry.core.misc.checks import (
    check_is_float_int,
    check_ndarray_is_all_nan,
    check_ndarray_is_float_int,
    check_ndarray_is_non_zero,
    check_ndarray_is_not_none,
    check_pint_unit_compatibility,
    check_type,
    check_type_all_elements_in_iterable,
    check_type_equivalence,
)
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Angle, Distance
from ansys.geometry.core.misc.options import ImportOptions
from ansys.geometry.core.misc.units import UNITS, PhysicalQuantity
