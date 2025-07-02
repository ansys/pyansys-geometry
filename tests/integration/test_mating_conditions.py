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

from pathlib import Path

import numpy as np

from ansys.geometry.core import Modeler

from .conftest import FILES_DIR


def test_align_condition(modeler: Modeler):
    """Test the creation of an align condition."""
    design = modeler.open_file(Path(FILES_DIR, "mating-conditions.scdocx"))
    face1 = next((ns for ns in design.named_selections if ns.name == "face1"), None).faces[0]
    face2 = next((ns for ns in design.named_selections if ns.name == "face2"), None).faces[0]

    old_center = face1.body.bounding_box.center

    modeler.geometry_commands.create_align_condition(design, face1, face2)

    new_center = face1.body.bounding_box.center

    assert not np.allclose(old_center, new_center)


def test_tangent_condition(modeler: Modeler):
    """Test the creation of a tangent condition."""
    design = modeler.open_file(Path(FILES_DIR, "mating-conditions.scdocx"))
    face1 = next((ns for ns in design.named_selections if ns.name == "face1"), None).faces[0]
    face2 = next((ns for ns in design.named_selections if ns.name == "face2"), None).faces[0]

    old_center = face1.body.bounding_box.center

    modeler.geometry_commands.create_tangent_condition(design, face1, face2)

    new_center = face1.body.bounding_box.center

    assert not np.allclose(old_center, new_center)


def test_orient_condition(modeler: Modeler):
    """Test the creation of an orient condition."""
    design = modeler.open_file(Path(FILES_DIR, "mating-conditions.scdocx"))
    face1 = next((ns for ns in design.named_selections if ns.name == "face3"), None).faces[0]
    face2 = next((ns for ns in design.named_selections if ns.name == "face2"), None).faces[0]

    old_center = face1.body.bounding_box.center

    modeler.geometry_commands.create_orient_condition(design, face1, face2)

    new_center = face1.body.bounding_box.center

    assert not np.allclose(old_center, new_center)
