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
"""Provides for creating and managing a NURBS surface."""

from typing import TYPE_CHECKING

from beartype import beartype as check_input_types

from ansys.geometry.core.shapes.surfaces.surface import Surface

if TYPE_CHECKING:  # pragma: no cover
    import geomdl.NURBS as geomdl_nurbs  # noqa: N811

class NURBSSurface(Surface):
    """Represents a NURBS surface.

    Notes
    -----
    This class is a wrapper around the NURBS surface class from the `geomdl` library.
    By leveraging the `geomdl` library, this class provides a high-level interface
    to create and manipulate NURBS surfaces. The `geomdl` library is a powerful
    library for working with NURBS curves and surfaces. For more information, see
    https://pypi.org/project/geomdl/.

    """

    def __init__(self, geomdl_object: "geomdl_nurbs.Surface" = None):
        """Initialize ``NURBSCurve`` class."""
        try:
            import geomdl.NURBS as geomdl_nurbs  # noqa: N811
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "The `geomdl` library is required to use the NURBSCurve class. "
                "Please install it using `pip install geomdl`."
            ) from e

        self._nurbs_curve = geomdl_object if geomdl_object else geomdl_nurbs.Curve()