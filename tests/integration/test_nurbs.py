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

"""Test NURBS interaction in designs."""

from pathlib import Path

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
from ansys.geometry.core.sketch.nurbs import SketchNurbs

JSON_NURBS_SAMPLES_DIR = Path(__file__).parent / "files" / "json_nurbs_samples"


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


def test_from_json_invalid_nurbs():
    """Test that invalid NURBS JSON payloads raise appropriate errors."""

    # Passing NURBSketch JSON to NURBSCurve.from_json should raise a ValueError
    with pytest.raises(ValueError, match="looks like a 2D NURBS sketch curve"):
        NURBSCurve.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "valid_sketch_curve_2d.json"), elements=["sketch_arc"]
        )

    with pytest.raises(ValueError, match="looks like a 2D NURBS sketch curve"):
        NURBSCurve.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "valid_sketch_curve_2d.json"), elements=["sketch_arc"]
        )

    # Passing NURBSurface JSON to NURBSCurve.from_json should raise a ValueError
    with pytest.raises(ValueError, match="looks like a 3D NURBS surface"):
        NURBSCurve.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "valid_surface.json"), elements=["sample_surface"]
        )

    # Test raise on invalid payload for SketchNurbs with NURBSSurface JSON
    with pytest.raises(
        ValueError,
        match="looks like a 3D NURBS surface",
    ):
        SketchNurbs.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "valid_surface.json"),
            elements=["sample_surface"],
        )

    # Test raise on invalid payload for SketchNurbs
    with pytest.raises(ValueError, match="looks like a 3D NURBS curve"):
        SketchNurbs.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "valid_curve_3d.json"),
            elements=["curve_main"],
        )


def test_nurbs_check_consistency():
    """Test that NURBS consistency checks work as expected."""

    # Test that missing knot vectors raise ValueError
    with pytest.raises(ValueError, match="Knot vector length mismatch: expected"):
        SketchNurbs.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_sketch_nurbs_cases.json"),
            elements=["missing_knot"],
        )

    # Test that extra knot vectors raise ValueError
    with pytest.raises(ValueError, match="Knot vector length mismatch: expected"):
        SketchNurbs.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_sketch_nurbs_cases.json"), elements=["extra_knot"]
        )

    # Test that invalid knot vector lengths raise ValueError
    with pytest.raises(ValueError, match="Knot vector length mismatch: expected"):
        NURBSCurve.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_curve_nurbs_cases.json"),
            elements=["missing_knot"],
        )

    # Test that extra knot vectors raise ValueError
    with pytest.raises(ValueError, match="Knot vector length mismatch: expected"):
        NURBSCurve.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_curve_nurbs_cases.json"), elements=["extra_knot"]
        )

    # Test missing list entry on json
    with pytest.raises(ValueError, match="were not found in JSON payload"):
        NURBSCurve.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_curve_nurbs_cases.json"),
            elements=["missing-list-entry"],
        )

    # Check that missing knot vectors raise ValueError
    with pytest.raises(ValueError, match="Value error, Number of"):
        NURBSSurface.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_surface_nurbs_cases.json"),
            elements=["missing_knot"],
        )

    # Check that extra knot vectors raise ValueError
    with pytest.raises(ValueError, match="Value error, Number of"):
        NURBSSurface.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_surface_nurbs_cases.json"),
            elements=["extra_knot"],
        )


def test_nurbs_non_decreasing_knot_vector():
    """Test that NURBS objects with decreasing order knot vectors raise ValueError."""

    with pytest.raises(ValueError, match="knots must be a non-decreasing sequence"):
        SketchNurbs.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_sketch_nurbs_cases.json"),
            elements=["decreasing-order"],
        )

    with pytest.raises(ValueError, match="knots must be a non-decreasing sequence"):
        NURBSCurve.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_curve_nurbs_cases.json"),
            elements=["decreasing-order"],
        )

    with pytest.raises(ValueError, match="Knot vector for U direction must be non-decreasing"):
        NURBSSurface.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_surface_nurbs_cases.json"),
            elements=["decreasing-order-u"],
        )

    with pytest.raises(ValueError, match="Knot vector for V direction must be non-decreasing"):
        NURBSSurface.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_surface_nurbs_cases.json"),
            elements=["decreasing-order-v"],
        )


def test_nurbs_knots_length_mismatch():
    """Test that NURBS objects with mismatched knots length raise ValueError."""

    with pytest.raises(ValueError):
        SketchNurbs.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_sketch_nurbs_cases.json"),
            elements=["invalid-knot-vector"],
        )

    with pytest.raises(ValueError):
        NURBSCurve.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_curve_nurbs_cases.json"),
            elements=["invalid-knot-vector"],
        )

    with pytest.raises(ValueError):
        NURBSSurface.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_surface_nurbs_cases.json"),
            elements=["invalid-knot-vector"],
        )


def test_nurbs_mismatch_weights_length():
    """Test that NURBS objects with mismatched weights length raise ValueError."""

    with pytest.raises(ValueError):
        SketchNurbs.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_sketch_nurbs_cases.json"),
            elements=["mismatch-weights"],
        )

    with pytest.raises(ValueError):
        NURBSCurve.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_curve_nurbs_cases.json"),
            elements=["mismatch-weights"],
        )

    with pytest.raises(ValueError):
        NURBSSurface.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_surface_nurbs_cases.json"),
            elements=["mismatch-weights"],
        )


def test_nurbs_to_json():
    """Test that NURBS objects can be serialized to JSON and deserialized back."""
    # Create a NURBSCurve
    curve = NURBSCurve.fit_curve_from_points(
        points=[
            Point3D([0, 0, 0]),
            Point3D([1, 1, 0]),
            Point3D([2, 0, 0]),
        ],
        degree=2,
    )

    # Serialize to JSON
    curve_json = curve.to_json()

    # Deserialize back to a NURBSCurve
    new_curve = NURBSCurve.from_json(curve_json)

    # Check that the properties match
    assert new_curve.degree == curve.degree
    assert len(new_curve.control_points) == len(curve.control_points)
    assert len(new_curve.knots) == len(curve.knots)
    assert len(new_curve.weights) == len(curve.weights)


def test_successful_nurbs_creation_from_json():
    """Test that valid NURBS JSON payloads create NURBS objects successfully."""
    # Test creating a NURBSCurve from valid JSON
    curve = NURBSCurve.from_json(
        str(JSON_NURBS_SAMPLES_DIR / "valid_curve_3d.json"), elements=["curve_main"]
    )
    assert isinstance(curve, NURBSCurve)
    assert curve.degree == 3
    assert len(curve.control_points) == 4
    assert len(curve.knots) == 8
    assert len(curve.weights) == 4

    # Test creating a SketchNurbs from valid JSON
    sketch_nurbs = SketchNurbs.from_json(
        str(JSON_NURBS_SAMPLES_DIR / "valid_sketch_curve_2d.json"), elements=["sketch_arc"]
    )
    assert isinstance(sketch_nurbs, SketchNurbs)
    assert sketch_nurbs.degree == 2
    assert len(sketch_nurbs.control_points) == 3
    assert len(sketch_nurbs.knots) == 6
    assert len(sketch_nurbs.weights) == 3

    # Test creating a NURBSSurface from valid JSON
    surface = NURBSSurface.from_json(
        str(JSON_NURBS_SAMPLES_DIR / "valid_surface.json"), elements=["sample_surface"]
    )
    assert isinstance(surface, NURBSSurface)
    assert surface.degree_u == 2
    assert surface.degree_v == 1
    assert len(surface.control_points) == 18
    assert len(surface.knotvector_u) == 12
    assert len(surface.knotvector_v) == 4


def test_nurbs_surface_from_json_element_name_not_found_raises():
    """Test that a missing element name raises a clear error."""

    # Test for surface element name not found in JSON payload
    with pytest.raises(ValueError):
        NURBSSurface.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "valid_surface.json"),
            elements=["does_not_exist"],
        )

    # Test for sketch element name not found in JSON payload
    with pytest.raises(ValueError):
        NURBSCurve.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_surface_nurbs_cases.json"),
            elements=["missing-list-entry"],
        )

    # Test for curve element name not found in JSON payload
    with pytest.raises(ValueError):
        NURBSCurve.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_sketch_nurbs_cases.json"),
            elements=["missing-list-entry"],
        )


def test_nurbs_surface_from_control_points_invalid_knot_vector_raises():
    """Test that invalid surface knot vectors raise errors with real inputs."""
    with pytest.raises(ValueError, match="valid knot vector for the u-direction"):
        NURBSSurface.from_control_points(
            degree_u=1,
            degree_v=1,
            knots_u=[0.0, 0.5, 0.4, 1.0],
            knots_v=[0.0, 0.0, 1.0, 1.0],
            control_points=[
                Point3D([0.0, 0.0, 0.0]),
                Point3D([1.0, 0.0, 0.0]),
                Point3D([0.0, 1.0, 0.0]),
                Point3D([1.0, 1.0, 0.0]),
            ],
        )


def test_nurbs_curve_from_json_path_and_auto_selection():
    """Test NURBSCurve.from_json using file path and auto-selected named element."""
    curve = NURBSCurve.from_json(str(JSON_NURBS_SAMPLES_DIR / "valid_curve_3d.json"))

    assert curve.degree == 3
    assert len(curve.control_points) == 4
    assert len(curve.knots) == 8
    assert len(curve.weights) == 4


def test_nurbs_curve_from_json_element_name_not_found_raises():
    """Test that a missing element name raises a Value Error."""

    # Test missing list entry on json
    with pytest.raises(ValueError):
        SketchNurbs.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_sketch_nurbs_cases.json"),
            elements=["missing-list-entry"],
        )

    # Test missing "elements"
    with pytest.raises(ValueError):
        SketchNurbs.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_sketch_nurbs_cases.json"),
            elements=["non-existent-element"],
        )

    # Test mismatched weights length raises ValueError
    with pytest.raises(ValueError):
        SketchNurbs.from_json(
            str(JSON_NURBS_SAMPLES_DIR / "invalid_sketch_nurbs_cases.json"),
            elements=["mismatch-weights"],
        )


def test_nurbs_surface_from_json_defaults_weights_when_missing():
    """Test that NURBSSurface.from_json defaults weights to 1.0 when not provided."""

    surface = NURBSSurface.from_json(
        str(JSON_NURBS_SAMPLES_DIR / "valid_surface_no_weights.json"),
        elements=["surface-no-weights"],
    )

    assert len(surface.weights) == 18
    assert surface.weights == [1.0] * len(surface.control_points)


def test_nurbs_curve_from_control_points_invalid_knot_vector_raises():
    """Test that invalid curve knot vectors raise errors with real inputs."""
    with pytest.raises(ValueError, match="valid knot vector"):
        NURBSCurve.from_control_points(
            control_points=[
                Point3D([0.0, 0.0, 0.0]),
                Point3D([1.0, 1.0, 0.0]),
                Point3D([2.0, 0.0, 0.0]),
            ],
            degree=2,
            knots=[0.0, 0.0, 0.0, 1.0, 1.0],
        )


def test_nurbs_curve_fit_curve_from_points_degenerate_input_raises():
    """Test fitting a degenerate 3D point set raises an error."""
    with pytest.raises(ZeroDivisionError):
        NURBSCurve.fit_curve_from_points(
            points=[
                Point3D([0.0, 0.0, 0.0]),
                Point3D([0.0, 0.0, 0.0]),
                Point3D([0.0, 0.0, 0.0]),
            ],
            degree=2,
        )


def test_sketch_nurbs_fit_curve_from_points_degree_too_high_raises():
    """Test SketchNurbs.fit_curve_from_points degree validation."""
    with pytest.raises(ValueError, match="is too high for the number of points provided"):
        SketchNurbs.fit_curve_from_points(
            points=[
                Point2D([0.0, 0.0]),
                Point2D([1.0, 1.0]),
                Point2D([2.0, 0.0]),
                Point2D([3.0, -1.0]),
            ],
            degree=4,
        )


def test_sketch_nurbs_fit_curve_from_points_degenerate_input_raises():
    """Test fitting a degenerate 2D point set raises an error."""
    with pytest.raises(ZeroDivisionError):
        SketchNurbs.fit_curve_from_points(
            points=[
                Point2D([0.0, 0.0]),
                Point2D([0.0, 0.0]),
                Point2D([0.0, 0.0]),
            ],
            degree=2,
        )


def test_sketch_nurbs_from_control_points_invalid_knot_vector_raises():
    """Test that invalid sketch knot vectors raise errors with real inputs."""
    with pytest.raises(ValueError, match="valid knot vector"):
        SketchNurbs.from_control_points(
            control_points=[Point2D([0.0, 0.0]), Point2D([1.0, 1.0]), Point2D([2.0, 0.0])],
            degree=2,
            knots=[0.0, 0.0, 0.0, 1.0, 1.0],
        )


def test_nurbs_from_control_points_wraps_check_variables_error(
    monkeypatch: pytest.MonkeyPatch,
):
    """Ensure from_control_points methods wrap low-level NURBS validation errors."""
    import geomdl.NURBS as GEOMDL_NURBS

    def _raise_check_error(self):
        raise ValueError("forced check failure")

    monkeypatch.setattr(GEOMDL_NURBS.Curve, "_check_variables", _raise_check_error)
    monkeypatch.setattr(GEOMDL_NURBS.Surface, "_check_variables", _raise_check_error)

    with pytest.raises(ValueError, match="Invalid NURBS curve"):
        SketchNurbs.from_control_points(
            control_points=[Point2D([0.0, 0.0]), Point2D([1.0, 1.0]), Point2D([2.0, 0.0])],
            degree=2,
            knots=[0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
        )

    with pytest.raises(ValueError, match="Invalid NURBS curve"):
        NURBSCurve.from_control_points(
            control_points=[
                Point3D([0.0, 0.0, 0.0]),
                Point3D([1.0, 1.0, 0.0]),
                Point3D([2.0, 0.0, 0.0]),
            ],
            degree=2,
            knots=[0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
        )

    with pytest.raises(ValueError, match="Invalid NURBS surface"):
        NURBSSurface.from_control_points(
            degree_u=1,
            degree_v=1,
            knots_u=[0.0, 0.0, 1.0, 1.0],
            knots_v=[0.0, 0.0, 1.0, 1.0],
            control_points=[
                Point3D([0.0, 0.0, 0.0]),
                Point3D([1.0, 0.0, 0.0]),
                Point3D([0.0, 1.0, 0.0]),
                Point3D([1.0, 1.0, 0.0]),
            ],
        )


def test_nurbs_fit_curve_wraps_check_variables_error(monkeypatch: pytest.MonkeyPatch):
    """Ensure fit_curve_from_points methods wrap low-level NURBS validation errors."""
    import geomdl.NURBS as GEOMDL_NURBS

    def _raise_check_error(self):
        raise ValueError("forced check failure")

    monkeypatch.setattr(GEOMDL_NURBS.Curve, "_check_variables", _raise_check_error)

    with pytest.raises(ValueError, match="Invalid NURBS curve"):
        SketchNurbs.fit_curve_from_points(
            points=[Point2D([0.0, 0.0]), Point2D([1.0, 0.5]), Point2D([2.0, 0.0])],
            degree=2,
        )

    with pytest.raises(ValueError, match="Invalid NURBS curve"):
        NURBSCurve.fit_curve_from_points(
            points=[
                Point3D([0.0, 0.0, 0.0]),
                Point3D([1.0, 1.0, 0.0]),
                Point3D([2.0, 0.0, 0.0]),
            ],
            degree=2,
        )
