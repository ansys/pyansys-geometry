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

"""Provides USD export utilities for PyAnsys Geometry."""

import functools
import re
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.colors as mcolors

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.component import Component
    from ansys.geometry.core.designer.design import Design
    from ansys.geometry.core.misc.options import TessellationOptions

_USD_AVAILABLE: bool | None = None
"""Cached availability flag for usd-core. ``None`` means not yet checked."""

_ERROR_USD_REQUIRED = (
    "The 'usd-core' package is required for USD export. "
    "Install it with: pip install ansys-geometry-core[usd]"
)

_VALID_USD_FORMATS = ("usda", "usdc", "usdz", "usd")


def run_if_usd_required() -> None:
    """Check that usd-core is installed, raising ImportError if not."""
    global _USD_AVAILABLE
    if _USD_AVAILABLE is None:
        try:
            from pxr import Usd  # noqa: F401

            _USD_AVAILABLE = True
        except (ModuleNotFoundError, ImportError):
            _USD_AVAILABLE = False

    if _USD_AVAILABLE is False:
        raise ImportError(_ERROR_USD_REQUIRED)


def usd_required(method):
    """Decorate a method as requiring usd-core.

    Parameters
    ----------
    method : callable
        Method to decorate.

    Returns
    -------
    callable
        Decorated method that raises ``ImportError`` if ``usd-core`` is not installed.
    """

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        run_if_usd_required()
        return method(*args, **kwargs)

    return wrapper
