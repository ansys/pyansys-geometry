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
"""Module containing the assembly controls service implementation (abstraction layer)."""

from abc import ABC, abstractmethod

import grpc


class GRPCAssemblyControlsService(ABC):  # pragma: no cover
    """Assembly controls service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the GRPCAssemblyControls class."""
        pass

    @abstractmethod
    def create_align_condition(self, **kwargs) -> dict:
        """Create an align condition between two geometry objects."""
        pass

    @abstractmethod
    def create_tangent_condition(self, **kwargs) -> dict:
        """Create a tangent condition between two geometry objects."""
        pass

    @abstractmethod
    def create_orient_condition(self, **kwargs) -> dict:
        """Create an orient condition between two geometry objects."""
        pass
