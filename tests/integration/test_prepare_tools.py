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
"""Testing of prepare tools."""

from ansys.geometry.core.modeler import Modeler

from .conftest import FILES_DIR


def test_volume_extract_from_faces(modeler: Modeler):
    """Test a volume is created from the provided faces."""
    design = modeler.open_file(FILES_DIR / "hollowCylinder.scdocx")

    body = design.bodies[0]
    inside_faces = [body.faces[0]]
    sealing_faces = [body.faces[1], body.faces[2]]
    created_bodies = modeler.prepare_tools.extract_volume_from_faces(sealing_faces, inside_faces)

    assert len(created_bodies) == 1


def test_volume_extract_from_edge_loops(modeler: Modeler):
    """Test a volume is created from the provided edges."""
    design = modeler.open_file(FILES_DIR / "hollowCylinder.scdocx")

    body = design.bodies[0]
    sealing_edges = [body.edges[2], body.edges[3]]
    created_bodies = modeler.prepare_tools.extract_volume_from_edge_loops(
        sealing_edges,
    )

    assert len(created_bodies) == 1


def test_share_topology(modeler: Modeler):
    """Test share topology operation is between two bodies."""
    design = modeler.open_file(FILES_DIR / "MixingTank.scdocx")

    assert modeler.prepare_tools.share_topology(design.bodies)
