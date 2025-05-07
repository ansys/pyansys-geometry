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
"""Module containing the repair tools service implementation."""

from abc import ABC

import grpc


class GRPCRepairToolsServiceV1(ABC):
    """Repair tools service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the MeasurementToolsService class."""

    def find_split_edges(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def find_extra_edges(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def find_inexact_edges(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def find_short_edges(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def find_duplicate_faces(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def find_missing_faces(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def find_small_faces(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def find_stitch_faces(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def find_simplify(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def find_interferences(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def find_and_fix_short_edges(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def find_and_fix_extra_edges(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def find_and_fix_split_edges(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def find_and_fix_simplify(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def inspect_geometry(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    def repair_geometry(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError
