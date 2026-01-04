# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
"""Tests trimmed geometry."""

import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core.connection import BackendType
from ansys.geometry.core.designer.face import SurfaceType
from ansys.geometry.core.math import Point3D, UnitVector3D
from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.shapes import Circle, Line
from ansys.geometry.core.shapes.box_uv import LocationUV
from ansys.geometry.core.shapes.curves.trimmed_curve import ReversedTrimmedCurve, TrimmedCurve
from ansys.geometry.core.shapes.parameterization import Interval
from ansys.geometry.core.shapes.surfaces.trimmed_surface import (
    ReversedTrimmedSurface,
    TrimmedSurface,
)
from ansys.geometry.core.sketch.sketch import Sketch


def create_hedgehog(modeler: Modeler):
    """A helper function that creates the Hedgehog model."""
    design = modeler.create_design("Hedgehog")
    sketch = Sketch().arc_from_three_points(
        Point2D([0.01, 0.01]), Point2D([0, -0.005]), Point2D([-0.01, 0.01])
    )
    sketch.arc_from_three_points(
        Point2D([0.01, 0.01]), Point2D([0, 0]), Point2D([-0.01, 0.01])
    ).circle(Point2D([0, 0]), 0.02)
    body = design.extrude_sketch("Cylinder", sketch, 0.02)
    # Add points to edges and corners - no missing corners
    points_between_corners = 4
    for edge in body.edges:
        total_point_gaps = np.floor(edge.length.m * 1000 / points_between_corners)
        current_gap = 0
        while current_gap < total_point_gaps:
            design.add_design_point(
                f"Point_{current_gap}",
                edge.shape.evaluate_proportion(current_gap / total_point_gaps).position,
            )
            current_gap += 1
    # Add hedgehog hairs (face-normals) to these points
    for face in body.faces:
        for edge in face.edges:
            total_point_gaps = np.floor(edge.length.m * 1000 / points_between_corners)
            current_gap = 0
            while current_gap < total_point_gaps + 1:
                p1 = edge.shape.evaluate_proportion(current_gap / total_point_gaps).position
                uv = face.shape.project_point(p1).parameter
                u, v = face.shape.get_proportional_parameters(uv)
                normal = face.normal(u, v)
                p2 = design.add_design_point("hair", p1 + normal / 800).value
                design._create_sketch_line(p1, p2)
                current_gap += 1
    # Add isoparametric curves, not on linux
    if not BackendType.is_core_service(modeler.client.backend_type):
        param = 0.20
        while param <= 1:
            for face in body.faces:
                face.create_isoparametric_curves(True, param)  # u
                face.create_isoparametric_curves(False, param)  # v
            param += 0.20
    return design


@pytest.fixture(scope="function")
def hedgehog_design(modeler: Modeler):
    """A fixture of the hedgehog design to test the surface and curve properties individually."""
    h = create_hedgehog(modeler)
    yield h


def test_trimmed_surface_properties(hedgehog_design):
    """Tests the surface properties for the hedgehog design."""
    hedgehog_body = hedgehog_design.bodies[0]
    faces = hedgehog_body.faces

    expected_surface_properties = [
        (
            SurfaceType.SURFACETYPE_CYLINDER,
            False,
            TrimmedSurface,
            (0.0, 6.283185307179586),
            (0.0, 0.02),
        ),
        (
            SurfaceType.SURFACETYPE_PLANE,
            True,
            ReversedTrimmedSurface,
            (-0.02024, 0.02024),
            (-0.02024, 0.02024),
        ),
        (
            SurfaceType.SURFACETYPE_PLANE,
            False,
            TrimmedSurface,
            (-0.02024, 0.02024),
            (-0.02024, 0.02024),
        ),
        (
            SurfaceType.SURFACETYPE_CYLINDER,
            False,
            TrimmedSurface,
            (3.141592653589793, 6.283185307179586),
            (0.0, 0.02),
        ),
        (
            SurfaceType.SURFACETYPE_CYLINDER,
            True,
            ReversedTrimmedSurface,
            (2.746801533890032, 6.677976426879348),
            (0.0, 0.02),
        ),
    ]

    for i, (surface_type, is_reversed, shape_type, interval_u, interval_v) in enumerate(
        expected_surface_properties
    ):
        assert faces[i].surface_type == surface_type
        assert faces[i]._is_reversed == is_reversed
        assert isinstance(faces[i].shape, shape_type)
        assert faces[i].shape.box_uv.interval_u == Interval(start=interval_u[0], end=interval_u[1])
        assert faces[i].shape.box_uv.interval_v == Interval(start=interval_v[0], end=interval_v[1])


def test_trimmed_surface_normals(hedgehog_design):
    """Tests the normal vectors for the hedgehog design using the BoxUV coordinates."""
    hedgehog_body = hedgehog_design.bodies[0]
    faces = hedgehog_body.faces
    # corners to consider
    corners = [
        LocationUV.TopLeft,
        LocationUV.BottomLeft,
        LocationUV.TopRight,
        LocationUV.BottomRight,
    ]

    expected_normals = [
        (
            UnitVector3D([1.0, 0.0, 0.0]),
            UnitVector3D([1.0, 0.0, 0.0]),
            UnitVector3D([-0.20700185, 0.97834055, 0.0]),
            UnitVector3D([-0.20700185, 0.97834055, 0.0]),
        ),
        (
            UnitVector3D([-0.0, -0.0, -1.0]),
            UnitVector3D([-0.0, -0.0, -1.0]),
            UnitVector3D([-0.0, -0.0, -1.0]),
            UnitVector3D([-0.0, -0.0, -1.0]),
        ),
        (
            UnitVector3D([0.0, 0.0, 1.0]),
            UnitVector3D([0.0, 0.0, 1.0]),
            UnitVector3D([0.0, 0.0, 1.0]),
            UnitVector3D([0.0, 0.0, 1.0]),
        ),
        (
            UnitVector3D([0.90268536, 0.43030122, 0.0]),
            UnitVector3D([0.90268536, 0.43030122, 0.0]),
            UnitVector3D([-0.62968173, -0.77685322, -0.0]),
            UnitVector3D([-0.62968173, -0.77685322, -0.0]),
        ),
        (
            UnitVector3D([-0.55819453, -0.82971011, -0.0]),
            UnitVector3D([-0.55819453, -0.82971011, -0.0]),
            UnitVector3D([0.74865795, 0.66295647, 0.0]),
            UnitVector3D([0.74865795, 0.66295647, 0.0]),
        ),
    ]

    for i, (top_left, bottom_left, top_right, bottom_right) in enumerate(expected_normals):
        corner_param = faces[i].shape.box_uv.get_corner(corners[0])
        assert np.allclose(faces[i].shape.normal(corner_param.u, corner_param.v), top_left)
        corner_param = faces[i].shape.box_uv.get_corner(corners[1])
        assert np.allclose(faces[i].shape.normal(corner_param.u, corner_param.v), bottom_left)
        corner_param = faces[i].shape.box_uv.get_corner(corners[2])
        assert np.allclose(faces[i].shape.normal(corner_param.u, corner_param.v), top_right)
        corner_param = faces[i].shape.box_uv.get_corner(corners[3])
        assert np.allclose(faces[i].shape.normal(corner_param.u, corner_param.v), bottom_right)


def test_trimmed_curve_properties(hedgehog_design):
    """Tests the curve properties for the hedgehog design."""
    hedgehog_body = hedgehog_design.bodies[0]
    edges = hedgehog_body.edges

    expected_curve_properties = [
        (False, TrimmedCurve, Circle, [0.01, 0.01, 0.02], [-0.01, 0.01, 0.02]),
        (False, TrimmedCurve, Line, [0.01, 0.01, 0.0], [0.01, 0.01, 0.02]),
        (True, ReversedTrimmedCurve, Circle, [-0.01, 0.01, 0.02], [0.01, 0.01, 0.02]),
        (False, TrimmedCurve, Line, [-0.01, 0.01, 0.0], [-0.01, 0.01, 0.02]),
        (False, TrimmedCurve, Circle, [0.01, 0.01, 0.0], [-0.01, 0.01, 0.0]),
        (True, ReversedTrimmedCurve, Circle, [-0.01, 0.01, 0.0], [0.01, 0.01, 0.0]),
        (False, TrimmedCurve, Circle, [0.02, 0.0, 0.02], [0.02, 0.0, 0.02]),
        (False, TrimmedCurve, Circle, [0.02, 0.0, 0.0], [0.02, 0.0, 0.0]),
    ]

    for i, (is_reversed, shape_type, geometry_type, start, end) in enumerate(
        expected_curve_properties
    ):
        assert edges[i]._is_reversed == is_reversed
        assert isinstance(edges[i].shape, shape_type)
        assert isinstance(edges[i].shape.geometry, geometry_type)
        assert np.allclose(edges[i].shape.start, Point3D(start))
        assert np.allclose(edges[i].shape.end, Point3D(end))


def test_trimmed_curve_line_translate(hedgehog_design):
    """Tests the translation of a trimmed curve with line geometry."""
    hedgehog_body = hedgehog_design.bodies[0]
    edges = hedgehog_body.edges
    edge = edges[1]
    trimmed_curve = edge.shape

    assert isinstance(trimmed_curve, TrimmedCurve)
    assert trimmed_curve.start == Point3D([0.01, 0.01, 0.0])
    assert trimmed_curve.end == Point3D([0.01, 0.01, 0.02])

    trimmed_curve.translate(UnitVector3D([1, 0, 0]), 0.01)

    assert trimmed_curve.start == Point3D([0.02, 0.01, 0.0])
    assert trimmed_curve.end == Point3D([0.02, 0.01, 0.02])


def test_trimmed_curve_line_rotate(hedgehog_design):
    """Tests the rotation of a trimmed curve with line geometry."""
    hedgehog_body = hedgehog_design.bodies[0]
    edges = hedgehog_body.edges
    edge = edges[1]
    trimmed_curve = edge.shape

    assert isinstance(trimmed_curve, TrimmedCurve)
    assert trimmed_curve.start == Point3D([0.01, 0.01, 0.0])
    assert trimmed_curve.end == Point3D([0.01, 0.01, 0.02])

    # Rotate the curve in the x-direction by 90 degrees about the point (0.01, 0.01, 0.0)
    trimmed_curve.rotate(Point3D([0.01, 0.01, 0.0]), UnitVector3D([1, 0, 0]), np.pi / 2)

    assert np.allclose(trimmed_curve.start, Point3D([0.01, 0.01, 0.0]))
    assert np.allclose(trimmed_curve.end, Point3D([0.01, -0.01, 0.0]))


def test_trimmed_curve_circle_translate(hedgehog_design):
    """Tests the rotation of a trimmed curve with circle geometry."""
    hedgehog_body = hedgehog_design.bodies[0]
    edges = hedgehog_body.edges
    edge = edges[0]
    trimmed_curve = edge.shape

    assert isinstance(trimmed_curve, TrimmedCurve)
    assert np.allclose(trimmed_curve.start, Point3D([0.01, 0.01, 0.02]))
    assert np.allclose(trimmed_curve.end, Point3D([-0.01, 0.01, 0.02]))

    trimmed_curve.translate(UnitVector3D([1, 0, 0]), 0.01)

    assert np.allclose(trimmed_curve.start, Point3D([0.02, 0.01, 0.02]))
    assert np.allclose(trimmed_curve.end, Point3D([0.0, 0.01, 0.02]))


def test_trimmed_curve_circle_rotate(hedgehog_design):
    """Tests the rotation of a trimmed curve with circle geometry."""
    hedgehog_body = hedgehog_design.bodies[0]
    edges = hedgehog_body.edges
    edge = edges[0]
    trimmed_curve = edge.shape

    assert isinstance(trimmed_curve, TrimmedCurve)
    assert np.allclose(trimmed_curve.start, Point3D([0.01, 0.01, 0.02]))
    assert np.allclose(trimmed_curve.end, Point3D([-0.01, 0.01, 0.02]))

    # Rotate the curve in the x-direction by 90 degrees about the point (0.01, 0.01, 0.02)
    trimmed_curve.rotate(Point3D([0.01, 0.01, 0.02]), UnitVector3D([0, 1, 0]), np.pi / 2)

    assert np.allclose(trimmed_curve.start, Point3D([0.01, 0.01, 0.02]))
    assert np.allclose(trimmed_curve.end, Point3D([0.01, 0.01, 0.04]))


def test_trimmed_curve(modeler: Modeler):
    """Test Trimmed Curve class"""
    design = modeler.create_design("trimmed_curve_edges")
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    with pytest.raises(ValueError):
        design.bodies[0].edges[0].shape.intersect_curve(design.bodies[0].edges[1].shape)
    # Retrieve edges and initialize TrimmedCurve objects with the gRPC client
    edge0 = TrimmedCurve(
        geometry=body.edges[0].shape.geometry,
        start=body.edges[0].shape.start,
        end=body.edges[0].shape.end,
        interval=body.edges[0].shape.interval,
        length=body.edges[0].shape.length,
        grpc_client=modeler.client,  # Pass the gRPC client here
    )
    edge1 = TrimmedCurve(
        geometry=body.edges[1].shape.geometry,
        start=body.edges[1].shape.start,
        end=body.edges[1].shape.end,
        interval=body.edges[1].shape.interval,
        length=body.edges[1].shape.length,
        grpc_client=modeler.client,  # Pass the gRPC client here
    )

    edge2 = TrimmedCurve(
        geometry=body.edges[4].shape.geometry,
        start=body.edges[4].shape.start,
        end=body.edges[4].shape.end,
        interval=body.edges[4].shape.interval,
        length=body.edges[4].shape.length,
        grpc_client=modeler.client,  # Pass the gRPC client here
    )

    # Perform assertions and call intersect_curve
    assert (
        edge0.__repr__()
        == "TrimmedCurve(geometry: <class 'ansys.geometry.core.shapes.curves.line.Line'>, "
        "start: [-0.5 -0.5  1. ], end: [ 0.5 -0.5  1. ], "
        "interval: Interval(start=0.0, end=1.0), length: 1.0 meter)"
    )
    assert edge0.length == Quantity(1, UNITS.m)
    assert edge0.intersect_curve(edge1) == [Point3D([-0.5, -0.5, 1.0])]
    assert edge0.intersect_curve(edge2) == []
