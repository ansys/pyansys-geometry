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
"""Module containing the repair tools service implementation (abstraction layer).

This module defines an abstract base class for a gRPC-based repair tools service.
The class provides a set of abstract methods for identifying and repairing various
geometry issues, such as split edges, extra edges, duplicate faces, and more.
"""

from abc import ABC, abstractmethod

import grpc


class GRPCRepairToolsService(ABC):  # pragma: no cover
    """Abstract base class for gRPC-based repair tools service.

    Parameters
    ----------
    channel: grpc.Channel
        The gRPC channel used to communicate with the service.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the gRPC repair tools service."""
        pass

    @abstractmethod
    def find_split_edges(self, **kwargs) -> dict:
        """Identify split edges in the geometry."""
        pass

    @abstractmethod
    def find_extra_edges(self, **kwargs) -> dict:
        """Identify extra edges in the geometry."""
        pass

    @abstractmethod
    def find_inexact_edges(self, **kwargs) -> dict:
        """Identify inexact edges in the geometry."""
        pass

    @abstractmethod
    def find_short_edges(self, **kwargs) -> dict:
        """Identify short edges in the geometry."""
        pass

    @abstractmethod
    def find_duplicate_faces(self, **kwargs) -> dict:
        """Identify duplicate faces in the geometry."""
        pass

    @abstractmethod
    def find_missing_faces(self, **kwargs) -> dict:
        """Identify missing faces in the geometry."""
        pass

    @abstractmethod
    def find_small_faces(self, **kwargs) -> dict:
        """Identify small faces in the geometry."""
        pass

    @abstractmethod
    def find_stitch_faces(self, **kwargs) -> dict:
        """Identify faces that can be stitched together in the geometry."""
        pass

    @abstractmethod
    def find_simplify(self, **kwargs) -> dict:
        """Identify areas in the geometry that can be simplified."""
        pass

    @abstractmethod
    def find_interferences(self, **kwargs) -> dict:
        """Identify interferences in the geometry."""
        pass

    @abstractmethod
    def find_and_fix_short_edges(self, **kwargs) -> dict:
        """Identify and fix short edges in the geometry."""
        pass

    @abstractmethod
    def find_and_fix_extra_edges(self, **kwargs) -> dict:
        """Identify and fix extra edges in the geometry."""
        pass

    @abstractmethod
    def find_and_fix_split_edges(self, **kwargs) -> dict:
        """Identify and fix split edges in the geometry."""
        pass

    @abstractmethod
    def find_and_fix_simplify(self, **kwargs) -> dict:
        """Identify and simplify areas in the geometry."""
        pass

    @abstractmethod
    def find_and_fix_stitch_faces(self, **kwargs) -> dict:
        """Identify and stitch faces in the geometry."""
        pass

    @abstractmethod
    def inspect_geometry(self, **kwargs) -> dict:
        """Inspect the geometry for issues."""
        pass

    @abstractmethod
    def repair_geometry(self, **kwargs) -> dict:
        """Repair the geometry by addressing identified issues."""
        pass

    @abstractmethod
    def fix_duplicate_faces(self, **kwargs) -> dict:  # noqa: D102
        """Fix duplicate faces in the geometry."""
        pass

    @abstractmethod
    def fix_missing_faces(self, **kwargs) -> dict:  # noqa: D102
        """Fix missing faces in the geometry."""
        pass

    @abstractmethod
    def fix_inexact_edges(self, **kwargs) -> dict:  # noqa: D102
        """Fix inexact edges in the geometry."""
        pass

    @abstractmethod
    def fix_extra_edges(self, **kwargs) -> dict:  # noqa: D102
        """Fix extra edges in the geometry."""
        pass

    @abstractmethod
    def fix_short_edges(self, **kwargs) -> dict:  # noqa: D102
        """Fix short edges in the geometry."""
        pass

    @abstractmethod
    def fix_small_faces(self, **kwargs) -> dict:  # noqa: D102
        """Fix small faces in the geometry."""
        pass

    @abstractmethod
    def fix_split_edges(self, **kwargs) -> dict:  # noqa: D102
        """Fix split edges in the geometry."""
        pass

    @abstractmethod
    def fix_stitch_faces(self, **kwargs) -> dict:  # noqa: D102
        """Fix stitch faces in the geometry."""
        pass

    @abstractmethod
    def fix_unsimplified_faces(self, **kwargs) -> dict:  # noqa: D102
        """Fix areas to simplify in the geometry."""
        pass

    @abstractmethod
    def fix_interference(self, **kwargs) -> dict:  # noqa: D102
        """Fix interferences in the geometry."""
        pass
