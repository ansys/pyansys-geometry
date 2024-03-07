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
"""PyAnsys Geometry designer subpackage."""

from ansys.geometry.core.designer.body import Body, MasterBody, MidSurfaceOffsetType
from ansys.geometry.core.designer.component import Component, ExtrusionDirection, SharedTopologyType
from ansys.geometry.core.designer.design import Design, DesignFileFormat
from ansys.geometry.core.designer.designpoint import DesignPoint
from ansys.geometry.core.designer.edge import CurveType, Edge
from ansys.geometry.core.designer.face import Face, SurfaceType
from ansys.geometry.core.designer.part import MasterComponent, Part
from ansys.geometry.core.designer.selection import NamedSelection
