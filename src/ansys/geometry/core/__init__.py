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
"""PyAnsys Geometry is a Python wrapper for the Ansys Geometry service."""

# Version
# ------------------------------------------------------------------------------

import importlib.metadata as importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))
"""PyAnsys Geometry version."""

# Ease import statements
# ------------------------------------------------------------------------------

import os

from ansys.geometry.core.connection.launcher import (
    launch_docker_modeler,
    launch_modeler,
    launch_modeler_with_discovery,
    launch_modeler_with_discovery_and_pimlight,
    launch_modeler_with_geometry_service,
    launch_modeler_with_geometry_service_and_pimlight,
    launch_modeler_with_spaceclaim,
    launch_modeler_with_spaceclaim_and_pimlight,
    launch_remote_modeler,
)
from ansys.geometry.core.logger import LOG
from ansys.geometry.core.modeler import Modeler

# Global config constants
# ------------------------------------------------------------------------------

USE_TRAME: bool = False
"""Global constant for checking whether to use `trame <https://kitware.github.io/trame/>`_
for visualization."""

DISABLE_MULTIPLE_DESIGN_CHECK: bool = False
"""
Global constant for disabling the ``ensure_design_is_active`` check.

Only set this to false if you are sure you want to disable this check and you will ONLY
be working with one design.
"""

DOCUMENTATION_BUILD: bool = os.environ.get("PYANSYS_GEOMETRY_DOC_BUILD", "false").lower() == "true"
"""Global flag to set when building the documentation to use the proper PyVista Jupyter
backend."""
