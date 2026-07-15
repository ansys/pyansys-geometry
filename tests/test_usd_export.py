# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
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

"""Tests for the USD export module."""

import pytest

from ansys.geometry.core.plotting.usd_export import (
    raw_tess_to_usd_mesh_data,
    sanitize_usd_name,
    unique_name,
)


def test_usd_required_raises_when_unavailable():
    """run_if_usd_required raises ImportError when usd-core is not available."""
    import ansys.geometry.core.plotting.usd_export as usd_mod

    original = usd_mod._USD_AVAILABLE
    usd_mod._USD_AVAILABLE = False
    try:
        with pytest.raises(ImportError, match="usd-core"):
            usd_mod.run_if_usd_required()
    finally:
        usd_mod._USD_AVAILABLE = original


def test_usd_required_decorator_raises_when_unavailable():
    """@usd_required propagates ImportError when usd-core is not available."""
    import ansys.geometry.core.plotting.usd_export as usd_mod

    @usd_mod.usd_required
    def _dummy():
        return "ok"

    original = usd_mod._USD_AVAILABLE
    usd_mod._USD_AVAILABLE = False
    try:
        with pytest.raises(ImportError, match="usd-core"):
            _dummy()
    finally:
        usd_mod._USD_AVAILABLE = original


def test_usd_required_passes_when_available():
    """run_if_usd_required does not raise when _USD_AVAILABLE is True."""
    import ansys.geometry.core.plotting.usd_export as usd_mod

    original = usd_mod._USD_AVAILABLE
    usd_mod._USD_AVAILABLE = True
    try:
        usd_mod.run_if_usd_required()  # must not raise
    finally:
        usd_mod._USD_AVAILABLE = original


def test_sanitize_spaces():
    assert sanitize_usd_name("my body") == "my_body"


def test_sanitize_special_chars():
    assert sanitize_usd_name("body-1 (main)") == "body_1__main_"


def test_sanitize_digit_prefix():
    assert sanitize_usd_name("1body") == "_1body"


def test_sanitize_empty():
    assert sanitize_usd_name("") == "_unnamed"


def test_sanitize_already_valid():
    assert sanitize_usd_name("ValidName_123") == "ValidName_123"


def test_unique_name_no_collision():
    assert unique_name("body", set()) == "body"


def test_unique_name_single_collision():
    assert unique_name("body", {"body"}) == "body_1"


def test_unique_name_multiple_collisions():
    assert unique_name("body", {"body", "body_1", "body_2"}) == "body_3"


def test_raw_tess_single_triangle():
    """Single face tessellation with one triangle."""
    raw_tess = {
        "face_1": {
            "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            "faces": [3, 0, 1, 2],
            "is_edge": False,
        }
    }
    points, counts, indices = raw_tess_to_usd_mesh_data(raw_tess)
    assert points == [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
    assert counts == [3]
    assert indices == [0, 1, 2]


def test_raw_tess_two_faces_index_offset():
    """Two face tessellations are merged with correct vertex index offsets."""
    raw_tess = {
        "face_1": {
            "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            "faces": [3, 0, 1, 2],
            "is_edge": False,
        },
        "face_2": {
            "vertices": [2.0, 0.0, 0.0, 3.0, 0.0, 0.0, 2.0, 1.0, 0.0],
            "faces": [3, 0, 1, 2],
            "is_edge": False,
        },
    }
    points, counts, indices = raw_tess_to_usd_mesh_data(raw_tess)
    assert len(points) == 6
    assert counts == [3, 3]
    assert indices == [0, 1, 2, 3, 4, 5]  # face_2 indices offset by 3


def test_raw_tess_empty_dict():
    """Empty raw tessellation returns empty lists."""
    points, counts, indices = raw_tess_to_usd_mesh_data({})
    assert points == []
    assert counts == []
    assert indices == []


def test_raw_tess_skips_edges():
    """Edge entries (is_edge=True) are ignored."""
    raw_tess = {
        "edge_1": {
            "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            "faces": [],
            "is_edge": True,
        },
        "face_1": {
            "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            "faces": [3, 0, 1, 2],
            "is_edge": False,
        },
    }
    points, counts, indices = raw_tess_to_usd_mesh_data(raw_tess)
    assert len(points) == 3
    assert counts == [3]
    assert indices == [0, 1, 2]


def test_raw_tess_skips_empty_entry():
    """Face entries with no vertices/faces are skipped."""
    raw_tess = {
        "face_1": {"vertices": [], "faces": [], "is_edge": False},
        "face_2": {
            "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            "faces": [3, 0, 1, 2],
            "is_edge": False,
        },
    }
    points, counts, indices = raw_tess_to_usd_mesh_data(raw_tess)
    assert len(points) == 3

