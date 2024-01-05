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
"""PyAnsys Geometry math subpackage."""

from ansys.geometry.core.math.bbox import BoundingBox2D
from ansys.geometry.core.math.constants import (
    DEFAULT_POINT2D,
    DEFAULT_POINT3D,
    IDENTITY_MATRIX33,
    IDENTITY_MATRIX44,
    UNITVECTOR2D_X,
    UNITVECTOR2D_Y,
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    UNITVECTOR3D_Z,
    ZERO_POINT2D,
    ZERO_POINT3D,
    ZERO_VECTOR2D,
    ZERO_VECTOR3D,
)
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.matrix import Matrix, Matrix33, Matrix44
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.math.vector import UnitVector2D, UnitVector3D, Vector2D, Vector3D
