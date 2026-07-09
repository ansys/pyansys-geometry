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

"""Provides for creating a custom selection."""

from enum import Enum, unique
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.geometry.core.connection.client import GrpcClient
    from ansys.geometry.core.designer.design import Design
    from ansys.geometry.core.selection_builder.body_selection import (
        BodySelection,
    )


@unique
class StringFilterType(Enum):
    """Provides values for the string filter types supported."""

    STRINGFILTERTYPE_TEXT = 0
    STRINGFILTERTYPE_WILDCARD = 1
    STRINGFILTERTYPE_REGULAREXPRESSION = 2


@unique
class InvertScope(Enum):
    """Provides values for the scope of selection inversion."""

    INVERTSCOPE_VISIBLE = 0
    INVERTSCOPE_ALL = 1


@unique
class ExtendScope(Enum):
    """Provides values for the scope of selection extension."""

    EXTENDSCOPE_ALL = 0
    EXTENDSCOPE_BODY = 1
    EXTENDSCOPE_VISIBLE = 2


@unique
class RangeType(Enum):
    """Provides values for the range of location-based selection."""

    RANGETYPE_INTERSECT = 0
    RANGETYPE_CONTAIN = 1


class SelectionBuilder:
    """A builder for creating a custom selection."""

    def __init__(self, design: "Design", grpc_client: "GrpcClient"):
        """Initialize the selection builder.

        Parameters
        ----------
        design : Design
            The active design used to resolve body IDs into ``Body`` objects.
        """
        from ansys.geometry.core.selection_builder.body_selection import (
            BodySelection,
        )
        from ansys.geometry.core.selection_builder.face_selection import (
            FaceSelection,
        )

        self._grpc_client = grpc_client
        self._design = design

        self._bodies = BodySelection(design, self._grpc_client)
        self._faces = FaceSelection(design, self._grpc_client)

    @property
    def bodies(self) -> "BodySelection":
        """Get the body selection."""
        return self._bodies

    @property
    def faces(self) -> "FaceSelection":
        """Get the face selection."""
        return self._faces
