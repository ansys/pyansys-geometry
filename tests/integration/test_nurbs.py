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
"""Test NURBS interaction in designs."""

import numpy as np
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.designer.component import SweepWithGuideData
from ansys.geometry.core.errors import GeometryRuntimeError
from ansys.geometry.core.math import (
    Plane,
    Point2D,
    Point3D,
)
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.shapes.box_uv import BoxUV
from ansys.geometry.core.shapes.curves.circle import Circle
from ansys.geometry.core.shapes.curves.line import Line
from ansys.geometry.core.shapes.curves.nurbs import NURBSCurve
from ansys.geometry.core.shapes.parameterization import Interval
from ansys.geometry.core.shapes.surfaces.nurbs import NURBSSurface
from ansys.geometry.core.sketch import Sketch


def test_sweep_sketch_along_nurbs(modeler: Modeler):
    """Test sweeping a sketch along a NURBS curve."""
    design = modeler.create_design("sweep_nurbs")

    # Create a NURBS curve as the path
    path_points = [
        Point3D([0, 0, 0]),
        Point3D([5, 5, 0]),
        Point3D([0, 10, 0]),
        Point3D([-5, 15, 0]),
        Point3D([0, 20, 0]),
    ]
    nurbs_path = NURBSCurve.fit_curve_from_points(path_points, degree=3).trim(Interval(0, 1))

    # create a circle on the XZ-plane centered at (0, 0, 0) with radius 2
    profile = Sketch(plane=Plane(direction_x=[1, 0, 0], direction_y=[0, 0, 1])).circle(
        Point2D([0, 0]), 2
    )

    # Sweep the profile along the NURBS path
    body = design.sweep_sketch("swept_body", profile, [nurbs_path])

    assert body is not None
    assert body.name == "swept_body"
    assert not body.is_surface
    assert len(body.faces) > 0
    assert len(body.edges) == 2


def test_sweep_with_guide(modeler: Modeler):
    """Test creating a body by sweeping a profile with a NURBS guide curve."""
    design = modeler.create_design("SweepWithGuide")

    # Create path points for the sweep path
    path_points = [
        Point3D([0.0, 0.0, 0.15]),
        Point3D([0.05, 0.0, 0.1]),
        Point3D([0.1, 0.0, 0.05]),
        Point3D([0.15, 0.0, 0.1]),
        Point3D([0.2, 0.0, 0.15]),
    ]
    nurbs_path = NURBSCurve.fit_curve_from_points(path_points, degree=3)
    n_l_points = len(path_points)
    path_interval = Interval(1.0 / (n_l_points - 1), (n_l_points - 2.0) / (n_l_points - 1))
    trimmed_path = nurbs_path.trim(path_interval)

    # Create a simple circular profile sketch
    profile_plane = Plane(origin=path_points[1])
    profile_sketch = Sketch(profile_plane)
    profile_sketch.circle(Point2D([0, 0]), 0.01)  # 0.01 radius

    # Create guide curve points (offset from path)
    guide_points = [Point3D([p.x.m, p.y.m + 0.01, p.z.m]) for p in path_points]
    guide_curve = NURBSCurve.fit_curve_from_points(guide_points, degree=3)
    guide_interval = Interval(1.0 / (n_l_points - 1), (n_l_points - 2.0) / (n_l_points - 1))
    trimmed_guide = guide_curve.trim(guide_interval)

    # Sweep the profile along the path with the guide curve
    sweep_data = [
        SweepWithGuideData(
            name="SweptBody",
            parent_id=design.id,
            sketch=profile_sketch,
            path=trimmed_path,
            guide=trimmed_guide,
            tight_tolerance=True,
        )
    ]
    sweep_body = design.sweep_with_guide(sweep_data=sweep_data)[0]

    assert sweep_body is not None
    assert sweep_body.name == "SweptBody"
    assert sweep_body.is_surface
    assert len(sweep_body.faces) == 1
    assert len(sweep_body.edges) == 2
    assert len(sweep_body.vertices) == 0


def test_create_body_from_loft_profile_with_guides(modeler: Modeler):
    """Test the ``create_body_from_loft_profile_with_guides()`` method to create a vase
    shape.
    """
    design_sketch = modeler.create_design("LoftProfileWithGuides")

    circle1 = Circle(origin=[0, 0, 0], radius=8)
    circle2 = Circle(origin=[0, 0, 10], radius=10)

    profile1 = circle1.trim(Interval(0, 2 * np.pi))
    profile2 = circle2.trim(Interval(0, 2 * np.pi))

    def circle_point(center, radius, angle_deg):
        # Returns a point on the circle at the given angle
        angle_rad = np.deg2rad(angle_deg)
        return Point3D(
            [
                center[0] + radius.m * np.cos(angle_rad),
                center[1] + radius.m * np.sin(angle_rad),
                center[2],
            ]
        )

    angles = [0, 90, 180, 270]
    guide_curves = []

    for angle in angles:
        pt1 = circle_point(circle1.origin, circle1.radius, angle)
        pt2 = circle_point(circle2.origin, circle2.radius, angle)

        # Create a guide curve (e.g., a line or spline) between pt1 and pt2
        guide_curve = NURBSCurve.fit_curve_from_points([pt1, pt2], 1).trim(Interval(0, 1))
        guide_curves.append(guide_curve)

    # Call the method
    result = design_sketch.create_body_from_loft_profiles_with_guides(
        "vase", [[profile1], [profile2]], guide_curves
    )

    # Assert that the resulting body has only one face.
    assert len(result.faces) == 1

    # check volume of body
    # expected is 0 since it's not a closed surface
    assert result.volume.m == 0
    assert result.is_surface is True


def test_nurbs_operations_with_old_backend(fake_modeler_old_backend_252: Modeler):
    """Test doing NURBS operations using an old backend."""
    design = fake_modeler_old_backend_252.create_design("ExtrudeNURBSSketchOldBackend")

    # Create the NURBS sketch, path, and surface needed for testing
    sketch = Sketch()
    sketch.nurbs_from_2d_points(
        points=[
            Point2D([0, 0]),
            Point2D([1, 0]),
            Point2D([1, 1]),
            Point2D([0, 1]),
            Point2D([0, 0]),
        ],
        tag="nurbs_sketch",
    )

    line_sketch = Sketch().segment(Point2D([0, -1]), Point2D([0, 2]), tag="line_segment")

    path = NURBSCurve.fit_curve_from_points(
        points=[
            Point3D([0, 0, 0]),
            Point3D([0, 5, 0]),
            Point3D([5, 5, 0]),
            Point3D([5, 0, 0]),
            Point3D([0, 0, 0]),
        ],
        degree=3,
    ).trim(Interval(0, 1))

    chain = Line(Point3D([0, 0, 0]), Vector3D([0, 0, 1])).trim(Interval(0, 10))

    points = [
        Point3D([0, 0, 0]),
        Point3D([0, 1, 1]),
        Point3D([0, 2, 0]),
        Point3D([1, 0, 1]),
        Point3D([1, 1, 2]),
        Point3D([1, 2, 1]),
        Point3D([2, 0, 0]),
        Point3D([2, 1, 1]),
        Point3D([2, 2, 0]),
    ]
    degree_u = 2
    degree_v = 2
    surface = NURBSSurface.fit_surface_from_points(
        points=points, size_u=3, size_v=3, degree_u=degree_u, degree_v=degree_v
    ).trim(BoxUV(Interval(0, 1), Interval(0, 1)))

    # Extrude the NURBS sketch
    with pytest.raises(
        GeometryRuntimeError,
        match="NURBS functionality requires a minimum Ansys release version of 26R1",
    ):
        design.extrude_sketch("extruded_body", sketch, distance=5)

    with pytest.raises(
        GeometryRuntimeError,
        match="NURBS functionality requires a minimum Ansys release version of 26R1",
    ):
        design.revolve_sketch("revolved_body", sketch, Vector3D([0, 0, 1]), 90, Point3D([0, 0, 0]))

    with pytest.raises(
        GeometryRuntimeError,
        match="NURBS functionality requires a minimum Ansys release version of 26R1",
    ):
        design.sweep_sketch("swept_body", sketch, [path])

    with pytest.raises(
        GeometryRuntimeError,
        match="NURBS functionality requires a minimum Ansys release version of 26R1",
    ):
        design.sweep_sketch("swept_body", line_sketch, [path])

    with pytest.raises(
        GeometryRuntimeError,
        match="NURBS functionality requires a minimum Ansys release version of 26R1",
    ):
        design.sweep_chain("swept_chain_body", [path], [chain])

    with pytest.raises(
        GeometryRuntimeError,
        match="NURBS functionality requires a minimum Ansys release version of 26R1",
    ):
        design.create_body_from_loft_profile("lofted_body", [[path]])

    with pytest.raises(
        GeometryRuntimeError,
        match="NURBS functionality requires a minimum Ansys release version of 26R1",
    ):
        design.create_surface("nurbs_surface", sketch)

    with pytest.raises(
        GeometryRuntimeError,
        match="NURBS functionality requires a minimum Ansys release version of 26R1",
    ):
        design.create_body_from_surface("nurbs_surface", surface)

    with pytest.raises(
        GeometryRuntimeError,
        match="NURBS functionality requires a minimum Ansys release version of 26R1",
    ):
        design.create_surface_from_trimmed_curves("nurbs_surface", [path])


def test_imprint_project_nurbs_old_backend(fake_modeler_old_backend_252: Modeler):
    """Test imprinting and projecting NURBS curves using an old backend."""
    design = fake_modeler_old_backend_252.create_design("ImprintNURBSCurvesOldBackend")

    # Create a body to imprint onto
    box_body = design.extrude_sketch("box_body", Sketch().box(Point2D([0, 0]), 5, 5), 5)

    # Create NURBS sketch and curves to imprint
    sketch = Sketch()
    sketch.nurbs_from_2d_points(
        points=[
            Point2D([0, 0]),
            Point2D([1, 0]),
            Point2D([1, 1]),
            Point2D([0, 1]),
            Point2D([0, 0]),
        ],
        tag="nurbs_sketch",
    )

    nurbs_curve1 = NURBSCurve.fit_curve_from_points(
        points=[
            Point3D([2, 2, 0]),
            Point3D([5, 8, 0]),
            Point3D([8, 2, 0]),
        ],
        degree=2,
    ).trim(Interval(0, 1))

    nurbs_curve2 = NURBSCurve.fit_curve_from_points(
        points=[
            Point3D([2, 8, 0]),
            Point3D([5, 2, 0]),
            Point3D([8, 8, 0]),
        ],
        degree=2,
    ).trim(Interval(0, 1))

    with pytest.raises(
        GeometryRuntimeError,
        match="NURBS functionality requires a minimum Ansys release version of 26R1",
    ):
        box_body.imprint_curves(
            faces=[box_body.faces[0]],
            trimmed_curves=[nurbs_curve1, nurbs_curve2],
        )

    with pytest.raises(
        GeometryRuntimeError,
        match="NURBS functionality requires a minimum Ansys release version of 26R1",
    ):
        box_body.imprint_curves(
            faces=[box_body.faces[0]],
            sketch=sketch,
        )

    with pytest.raises(
        GeometryRuntimeError,
        match="NURBS functionality requires a minimum Ansys release version of 26R1",
    ):
        box_body.project_curves(UnitVector3D([0, 0, 1]), sketch, True)


def test_nurbs_surface_body_creation(modeler: Modeler):
    """Test surface body creation from NURBS surfaces."""
    design = modeler.create_design("Design1")

    points = [
        Point3D([0, 0, 0]),
        Point3D([0, 1, 1]),
        Point3D([0, 2, 0]),
        Point3D([1, 0, 1]),
        Point3D([1, 1, 2]),
        Point3D([1, 2, 1]),
        Point3D([2, 0, 0]),
        Point3D([2, 1, 1]),
        Point3D([2, 2, 0]),
    ]
    degree_u = 2
    degree_v = 2
    surface = NURBSSurface.fit_surface_from_points(
        points=points, size_u=3, size_v=3, degree_u=degree_u, degree_v=degree_v
    )

    trimmed_surface = surface.trim(BoxUV(Interval(0, 1), Interval(0, 1)))
    body = design.create_body_from_surface("nurbs_surface", trimmed_surface)
    assert len(design.bodies) == 1
    assert body.is_surface
    assert body.faces[0].area.m == pytest.approx(7.44626609)

    assert surface.origin.x == 0
    assert surface.origin.y == 0
    assert surface.origin.z == 0

    assert surface.dir_x.x == 1
    assert surface.dir_x.y == 0
    assert surface.dir_x.z == 0

    assert surface.dir_z.x == 0
    assert surface.dir_z.y == 0
    assert surface.dir_z.z == 1


def test_nurbs_surface_body_creation_using_old_backend(fake_modeler_old_backend_251: Modeler):
    """Test not implemented surface body creation from NURBS surfaces using an old backend"""
    design = fake_modeler_old_backend_251.create_design("Design1")

    points = [
        Point3D([0, 0, 0]),
        Point3D([0, 1, 1]),
        Point3D([0, 2, 0]),
        Point3D([1, 0, 1]),
        Point3D([1, 1, 2]),
        Point3D([1, 2, 1]),
        Point3D([2, 0, 0]),
        Point3D([2, 1, 1]),
        Point3D([2, 2, 0]),
    ]
    degree_u = 2
    degree_v = 2
    surface = NURBSSurface.fit_surface_from_points(
        points=points, size_u=3, size_v=3, degree_u=degree_u, degree_v=degree_v
    )

    trimmed_surface = surface.trim(BoxUV(Interval(0, 1), Interval(0, 1)))
    with pytest.raises(
        GeometryRuntimeError,
        match="NURBS functionality requires a minimum Ansys release version of 26R1",
    ):
        design.create_body_from_surface("nurbs_surface", trimmed_surface)


def test_create_surface_from_nurbs_sketch(modeler: Modeler):
    """Test creating a surface from a NURBS sketch."""
    design = modeler.create_design("NURBS_Sketch_Surface")

    # Create a NURBS sketch
    sketch = Sketch()
    sketch.nurbs_from_2d_points(
        points=[
            Point2D([0, 0]),
            Point2D([1, 0]),
            Point2D([1, 1]),
            Point2D([0, 1]),
        ],
        tag="nurbs_sketch",
    )
    sketch.segment(
        start=Point2D([0, -1]),
        end=Point2D([0, 2]),
        tag="segment_1",
    )

    # Create a surface from the NURBS sketch
    surface_body = design.create_surface(
        name="nurbs_surface",
        sketch=sketch,
    )

    assert len(design.bodies) == 1
    assert surface_body.is_surface
    assert surface_body.faces[0].area.m > 0
