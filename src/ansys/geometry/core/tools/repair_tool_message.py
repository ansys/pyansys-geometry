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
"""Module for repair tool message."""


class RepairToolMessage:
    """Provides return message for the repair tool methods."""

    def __init__(self, success: bool, created_bodies: list[str], modified_bodies: list[str]):
        """Initialize a new instance of the extra edge problem area class.

        Parameters
        ----------
        success: bool
            True if the repair operation was effective, false if it is not.
        created_bodies: list[str]
            List of bodies created after the repair operation.
        modified_bodies: list[str]
            List of bodies modified after the repair operation.
        """
        self._success = success
        self._created_bodies = created_bodies
        self._modified_bodies = modified_bodies

    @property
    def success(self) -> bool:
        """The success of the repair operation."""
        return self._success

    @property
    def created_bodies(self) -> list[str]:
        """The list of the created bodies after the repair operation."""
        return self._created_bodies

    @property
    def modified_bodies(self) -> list[str]:
        """The list of the modified bodies after the repair operation."""
        return self._modified_bodies
