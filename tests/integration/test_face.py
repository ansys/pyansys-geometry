# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Tests for face-specific behaviors."""

from pathlib import Path
from unittest.mock import Mock, patch

import ansys.geometry.core as pyansys_geo
import pytest
from ansys.geometry.core import Modeler
from ansys.geometry.core.designer import SurfaceType
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.shapes.curves.trimmed_curve import TrimmedCurve
from ansys.geometry.core.sketch import Sketch

from .conftest import FILES_DIR


def _face_for_unit_tests(*, face_id: str = "face-1", backend_version=(27, 1, 0)):
    grpc_client = Mock()
    grpc_client.backend_version = backend_version
    grpc_client.log = Mock()
    grpc_client.services = Mock()
    grpc_client.services.faces = Mock()
    grpc_client.services.model_tools = Mock()

    design = Mock(spec=["_modeler", "is_closed", "_update_design_inplace", "_update_from_tracker"])
    design._modeler = Mock()
    design.is_closed = False

    component = Mock(spec=["_parent_component"])
    component._parent_component = design

    body = Mock(spec=["_parent_component"])
    body._parent_component = component

    face = Face(face_id, SurfaceType.SURFACETYPE_PLANE, body, grpc_client)
    return face, design


def test_face_create_isoparametric_curves_builds_trimmed_curves():
    """Test isoparametric response parsing into trimmed curves."""
    face, _ = _face_for_unit_tests()

    geometry_1 = Mock()
    start_1 = Mock()
    end_1 = Mock()
    interval_1 = Mock()
    length_1 = Mock()

    geometry_2 = Mock()
    start_2 = Mock()
    end_2 = Mock()
    interval_2 = Mock()
    length_2 = Mock()

    face._grpc_client.services.faces.create_iso_parametric_curve.return_value = {
        "curves": [
            {
                "geometry": geometry_1,
                "start": start_1,
                "end": end_1,
                "interval": interval_1,
                "length": length_1,
            },
            {
                "geometry": geometry_2,
                "start": start_2,
                "end": end_2,
                "interval": interval_2,
                "length": length_2,
            },
        ]
    }

    trimmed_curves = face.create_isoparametric_curves(use_u_param=True, parameter=0.25)

    assert len(trimmed_curves) == 2
    assert isinstance(trimmed_curves[0], TrimmedCurve)
    assert isinstance(trimmed_curves[1], TrimmedCurve)
    assert trimmed_curves[0].geometry is geometry_1
    assert trimmed_curves[0].start is start_1
    assert trimmed_curves[0].end is end_1
    assert trimmed_curves[0].interval is interval_1
    assert trimmed_curves[0].length is length_1
    assert trimmed_curves[1].geometry is geometry_2
    assert trimmed_curves[1].start is start_2
    assert trimmed_curves[1].end is end_2
    assert trimmed_curves[1].interval is interval_2
    assert trimmed_curves[1].length is length_2

    face._grpc_client.services.faces.create_iso_parametric_curve.assert_called_once_with(
        id=face.id,
        use_u_param=True,
        parameter=0.25,
    )


def test_face_detach_returns_none_when_success_without_created_bodies():
    """Test detach returns None when operation succeeds but no bodies are returned."""
    import ansys.geometry.core.designer.face as face_module

    face, design = _face_for_unit_tests()
    face._grpc_client.services.model_tools.detach_faces.return_value = {
        "success": True,
        "created_bodies": [],
    }

    with (
        patch.object(pyansys_geo, "USE_TRACKER_TO_UPDATE_DESIGN", False),
        patch.object(face_module, "get_design_from_face", return_value=design),
        patch.object(face_module, "get_bodies_from_ids") as get_bodies_spy,
    ):
        result = face.detach()

    assert result is None
    design._update_design_inplace.assert_called_once()
    design._update_from_tracker.assert_not_called()
    get_bodies_spy.assert_not_called()
    face._grpc_client.services.model_tools.detach_faces.assert_called_once_with(
        selections=[[face.id]]
    )


def test_face_detach_returns_created_body_when_present():
    """Test detach returns created body from ID lookup when operation succeeds."""
    import ansys.geometry.core.designer.face as face_module

    face, design = _face_for_unit_tests()
    created_body = Mock()
    face._grpc_client.services.model_tools.detach_faces.return_value = {
        "success": True,
        "created_bodies": ["body-1"],
    }

    with (
        patch.object(pyansys_geo, "USE_TRACKER_TO_UPDATE_DESIGN", False),
        patch.object(face_module, "get_design_from_face", return_value=design),
        patch.object(face_module, "get_bodies_from_ids", return_value=[created_body]),
    ):
        result = face.detach()

    assert result is created_body
    design._update_design_inplace.assert_called_once()
    design._update_from_tracker.assert_not_called()


def test_face_detach_uses_tracker_update_when_enabled():
    """Test detach updates design from tracker when tracker mode is enabled."""
    import ansys.geometry.core.designer.face as face_module

    face, design = _face_for_unit_tests()
    face._grpc_client.services.model_tools.detach_faces.return_value = {
        "success": True,
        "tracked_response": {"modified": True},
        "created_bodies": [],
    }

    with (
        patch.object(pyansys_geo, "USE_TRACKER_TO_UPDATE_DESIGN", True),
        patch.object(face_module, "get_design_from_face", return_value=design),
        patch.object(face_module, "get_bodies_from_ids") as get_bodies_spy,
    ):
        result = face.detach()

    assert result is None
    design._update_design_inplace.assert_not_called()
    design._update_from_tracker.assert_called_once_with({"modified": True})
    get_bodies_spy.assert_not_called()


def test_face_detach_logs_and_returns_none_when_failed():
    """Test detach returns None and logs info when operation fails."""
    import ansys.geometry.core.designer.face as face_module

    face, design = _face_for_unit_tests()
    face._grpc_client.services.model_tools.detach_faces.return_value = {"success": False}

    with patch.object(face_module, "get_design_from_face", return_value=design):
        result = face.detach()

    assert result is None
    face._grpc_client.log.info.assert_called_once_with("Failed to detach faces.")
    design._update_design_inplace.assert_not_called()
    design._update_from_tracker.assert_not_called()
    face._grpc_client.services.model_tools.detach_faces.assert_called_once_with(
        selections=[[face.id]]
    )


def test_get_face_bounding_box(modeler: Modeler):
    """Test getting the bounding box of a face."""
    design = modeler.create_design("face_bounding_box")
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    bounding_box = body.faces[0].bounding_box
    assert bounding_box.min_corner.x.m == bounding_box.min_corner.y.m == -0.5
    assert bounding_box.max_corner.x.m == bounding_box.max_corner.y.m == 0.5

    bounding_box = body.faces[1].bounding_box
    assert bounding_box.min_corner.x.m == bounding_box.min_corner.y.m == -0.5
    assert bounding_box.max_corner.x.m == bounding_box.max_corner.y.m == 0.5


def test_get_face_tight_bounding_box(modeler: Modeler):
    """Test getting the tight bounding box of a face."""
    design = modeler.open_file(Path(FILES_DIR, "yarn.scdocx"))
    yarn_body = design.bodies[0]

    bounding_box = yarn_body.faces[0].bounding_box

    assert bounding_box.min_corner.x.m == pytest.approx(0.750637531716012)
    assert bounding_box.min_corner.y.m == pytest.approx(-0.340634843063073)
    assert bounding_box.min_corner.z.m == pytest.approx(0.104203649881978)

    assert bounding_box.max_corner.x.m == pytest.approx(1.75484840496883)
    assert bounding_box.max_corner.y.m == pytest.approx(0.663576030656712)
    assert bounding_box.max_corner.z.m == pytest.approx(0.196642153592138)

    assert bounding_box.center.x.m == pytest.approx(1.25274296834242)
    assert bounding_box.center.y.m == pytest.approx(0.161470593796819)
    assert bounding_box.center.z.m == pytest.approx(0.150422901737058)

    bounding_box = yarn_body.faces[0].get_bounding_box(tight=True)

    assert bounding_box.min_corner.x.m == pytest.approx(0.754595317788195)
    assert bounding_box.min_corner.y.m == pytest.approx(5.2771026530260073e-17)
    assert bounding_box.min_corner.z.m == pytest.approx(0.105040051163695)

    assert bounding_box.max_corner.x.m == pytest.approx(1.41421356238489)
    assert bounding_box.max_corner.y.m == pytest.approx(0.659618244585186)
    assert bounding_box.max_corner.z.m == pytest.approx(0.196642053388603)

    assert bounding_box.center.x.m == pytest.approx(1.08440444008654)
    assert bounding_box.center.y.m == pytest.approx(0.329809122292593)
    assert bounding_box.center.z.m == pytest.approx(0.150841052276149)
