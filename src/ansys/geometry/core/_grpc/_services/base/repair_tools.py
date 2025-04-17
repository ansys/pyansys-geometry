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


class GRPCRepairToolsService(ABC):
    """Abstract base class for gRPC-based repair tools service.

    This class defines a set of abstract methods that must be implemented
    by any concrete subclass. These methods are used to identify and repair
    various geometry issues in a CAD model.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the gRPC repair tools service.

        Parameters:
            channel (grpc.Channel): The gRPC channel used to communicate with the service.
        """
        pass  # pragma: no cover

    @abstractmethod
    def find_split_edges(self, **kwargs):
        """Identify split edges in the geometry."""
        pass  # pragma: no cover


    @abstractmethod
    def find_extra_edges(self, **kwargs):
        """Identify extra edges in the geometry."""
        pass  # pragma: no cover

    @abstractmethod
    def find_inexact_edges(self, **kwargs):
        """Identify inexact edges in the geometry."""
        pass  # pragma: no cover

    @abstractmethod
    def find_short_edges(self, **kwargs):
        """Identify short edges in the geometry."""
        pass  # pragma: no cover

    @abstractmethod
    def find_duplicate_faces(self, **kwargs):
        """Identify duplicate faces in the geometry."""
        pass  # pragma: no cover

    @abstractmethod
    def find_missing_faces(self, **kwargs):
        """Identify missing faces in the geometry."""
        pass  # pragma: no cover

    @abstractmethod
    def find_small_faces(self, **kwargs):
        """Identify small faces in the geometry."""
        pass  # pragma: no cover

    @abstractmethod
    def find_stitch_faces(self, **kwargs):
        """Identify faces that can be stitched together in the geometry."""
        pass  # pragma: no cover

    @abstractmethod
    def find_simplify(self, **kwargs):
        """Identify areas in the geometry that can be simplified."""
        pass  # pragma: no cover

    @abstractmethod
    def find_interferences(self, **kwargs):
        """Identify interferences in the geometry."""
        pass  # pragma: no cover

    @abstractmethod
    def find_and_fix_short_edges(self, **kwargs):
        """Identify and fix short edges in the geometry."""
        pass  # pragma: no cover

    @abstractmethod
    def find_and_fix_extra_edges(self, **kwargs):
        """Identify and fix extra edges in the geometry."""
        pass  # pragma: no cover

    @abstractmethod
    def find_and_fix_split_edges(self, **kwargs):
        """Identify and fix split edges in the geometry."""
        pass  # pragma: no cover

    @abstractmethod
    def find_and_fix_simplify(self, **kwargs):
        """Identify and simplify areas in the geometry."""
        pass  # pragma: no cover

    @abstractmethod
    def inspect_geometry(self, **kwargs):
        """Inspect the geometry for issues."""
        pass  # pragma: no cover

    @abstractmethod
    def repair_geometry(self, **kwargs):
        """Repair the geometry by addressing identified issues."""
        pass  # pragma: no cover
