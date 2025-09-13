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
"""Module containing the designs service implementation (abstraction layer)."""

from abc import ABC, abstractmethod

import grpc


class GRPCDesignsService(ABC):  # pragma: no cover
    """Designs service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the GRPCDesignsService class."""
        pass

    @abstractmethod
    def open(self, **kwargs) -> dict:
        """Open a design on the service."""
        pass

    @abstractmethod
    def new(self, **kwargs) -> dict:
        """Create a new design."""
        pass

    @abstractmethod
    def close(self, **kwargs) -> dict:
        """Close the currently open design."""
        pass

    @abstractmethod
    def put_active(self, **kwargs) -> dict:
        """Activate an already opened design on the service."""
        pass

    @abstractmethod
    def save_as(self, **kwargs) -> dict:
        """Create a new design."""
        pass

    @abstractmethod
    def download_export(self, **kwargs) -> dict:
        """Download and export a design into a certain format."""
        pass

    @abstractmethod
    def stream_download_export(self, **kwargs) -> dict:
        """Download and export a design into a certain format."""
        pass

    @abstractmethod
    def insert(self, **kwargs) -> dict:
        """Insert a part/component/design into an existing design."""
        pass

    @abstractmethod
    def get_active(self, **kwargs) -> dict:
        """Get the active design on the service."""
        pass

    @abstractmethod
    def _serialize_tracker_command_response(self, **kwargs) -> dict:
        """Get a serialized response from the tracker."""
        pass
    
