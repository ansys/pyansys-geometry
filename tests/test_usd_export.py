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
