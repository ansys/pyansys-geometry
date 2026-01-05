# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
"""Module containing the patterns service implementation (abstraction layer)."""

from abc import ABC, abstractmethod

import grpc


class GRPCPatternsService(ABC):  # pragma: no cover
    """Patterns service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the GRPCPatternsService class."""
        pass

    @abstractmethod
    def create_linear_pattern(self, **kwargs) -> dict:
        """Create a linear pattern of entities."""
        pass

    @abstractmethod
    def modify_linear_pattern(self, **kwargs) -> dict:
        """Modify a linear pattern of entities."""
        pass

    @abstractmethod
    def create_circular_pattern(self, **kwargs) -> dict:
        """Create a circular pattern of entities."""
        pass

    @abstractmethod
    def modify_circular_pattern(self, **kwargs) -> dict:
        """Modify a circular pattern of entities."""
        pass

    @abstractmethod
    def create_fill_pattern(self, **kwargs) -> dict:
        """Create a fill pattern of entities."""
        pass

    @abstractmethod
    def update_fill_pattern(self, **kwargs) -> dict:
        """Update a fill pattern of entities."""
        pass
