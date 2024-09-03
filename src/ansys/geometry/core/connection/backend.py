# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
"""Module providing definitions for the backend types."""

from enum import Enum, unique
from typing import Union


@unique
class BackendType(Enum):
    """Provides an enum holding the available backend types."""

    DISCOVERY = 0
    SPACECLAIM = 1
    WINDOWS_SERVICE = 2
    LINUX_SERVICE = 3


class ApiVersions(Enum):
    """Provides an enum for all the compatibles API versions."""

    V_21 = 21
    V_22 = 22
    V_231 = 231
    V_232 = 232
    V_241 = 241
    V_242 = 242
    V_251 = LATEST = 251

    @staticmethod
    def parse_input(version: Union[int, str, "ApiVersions"]) -> "ApiVersions":
        """Convert an input to an ApiVersions enum.

        Parameters
        ----------
        version : int | str | ApiVersions
            The version to convert to an ApiVersions enum.

        Returns
        -------
        ApiVersions
            The version as an ApiVersions enum.
        """
        if isinstance(version, ApiVersions):
            return version
        elif isinstance(version, str) and version.isnumeric():
            return ApiVersions(int(version))
        elif isinstance(version, int):
            return ApiVersions(version)
        else:
            raise ValueError("API version must be an integer, string or an ApiVersions enum.")
