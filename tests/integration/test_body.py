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

"""Test body interaction."""

from pathlib import Path
import zipfile
from unittest.mock import Mock, patch

import matplotlib.colors as mcolors
import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core._grpc._version import GeometryApiProtos
from ansys.geometry.core.designer import DesignFileFormat, SharedTopologyType
from ansys.geometry.core.designer.body import FillStyle, MasterBody
from ansys.geometry.core.designer.part import MasterComponent, Part
from ansys.geometry.core.errors import GeometryExitedError
from ansys.geometry.core.materials import Material, MaterialProperty, MaterialPropertyType
from ansys.geometry.core.math import (
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    UNITVECTOR3D_Z,
    Frame,
    Plane,
    Point2D,
    Point3D,
    UnitVector3D,
    Vector3D,
)
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Accuracy, Angle, Distance
from ansys.geometry.core.misc.auxiliary import DEFAULT_COLOR
from ansys.geometry.core.misc.options import TessellationOptions
from ansys.geometry.core.shapes import Circle, Cone, Cylinder, Line, Sphere, Torus
from ansys.geometry.core.shapes.box_uv import BoxUV
from ansys.geometry.core.shapes.parameterization import Interval
from ansys.geometry.core.sketch import Sketch

from ..conftest import are_graphics_available
from .conftest import FILES_DIR


def _named_selection(*, backend_version=(27, 1, 0), bodies=None):
    from ansys.geometry.core.designer.selection import NamedSelection

    grpc_client = Mock()
    grpc_client.backend_version = backend_version
    grpc_client.log = Mock()
    grpc_client.services = Mock()
    grpc_client.services.named_selection = Mock()
    return NamedSelection(
        "test_ns",
        Mock(),
        grpc_client,
        bodies=bodies or [],
        preexisting_id="ns-id",
    )


def test_body_properties_and_transformations(modeler: Modeler):
    """Test body properties, setters, and transformation decorators for coverage."""
    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 10, 10)
    design = modeler.create_design("BodyPropertiesTest")
    body = design.extrude_sketch("TestBox", sketch, Quantity(10, UNITS.mm))
    master_body = body._template

    master_body.name = "RenamedBox"
    assert master_body.name == "RenamedBox"

    master_body.fill_style = FillStyle.OPAQUE
    assert master_body.fill_style == FillStyle.OPAQUE

    master_body.is_suppressed = True
    assert master_body.is_suppressed is True
    master_body.is_suppressed = False
    assert master_body.is_suppressed is False

    master_body.set_color((255, 0, 0))
    master_body._color = None
    color_value = master_body.color
    assert color_value is not None

    master_body.color = "#00ff00ff"
    assert master_body.color.lower().startswith("#00ff00")

    master_body.opacity = 0.5
    assert 0.4 < master_body.opacity < 0.6

    assert master_body.is_surface is False
    assert master_body.surface_thickness is None
    assert master_body.surface_offset is None

    faces = master_body.faces
    assert len(faces) > 0

    edges = master_body.edges
    assert len(edges) > 0

    vertices = master_body.vertices
    assert len(vertices) > 0

    volume = master_body.volume
    assert volume is not None

    master_body.translate(UnitVector3D([1, 0, 0]), Distance(5, UNITS.mm))
    master_body.scale(1.1)
    master_body.map(Frame(Point3D([0, 0, 0])))
    master_body.mirror(Plane(Point3D([0, 0, 0])))


def test_masterbody_material_and_advanced_properties(modeler: Modeler):
    """Test MasterBody material operations and advanced properties."""
    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 10, 10)
    design = modeler.create_design("MaterialTest")
    body = design.extrude_sketch("TestBody", sketch, Quantity(10, UNITS.mm))
    master_body = body._template

    density = Quantity(125, 1000 * UNITS.kg / (UNITS.m**3))
    material = Material("steel", density)
    design.add_material(material)

    material = design.materials[0]
    master_body.assign_material(material)
    retrieved_material = master_body.get_assigned_material()
    assert retrieved_material is not None

    master_body.material = material

    master_body.remove_assigned_material()

    bbox = master_body.bounding_box
    assert bbox is not None

    backend_version = master_body._grpc_client.backend_version
    if backend_version >= (27, 1, 0):
        bbox_tight = master_body.get_bounding_box(tight=True)
        assert bbox_tight is not None

    with pytest.raises(NotImplementedError):
        master_body.imprint_curves([], Sketch())

    with pytest.raises(NotImplementedError):
        master_body.project_curves(UnitVector3D([0, 0, 1]), Sketch(), True)

    with pytest.raises(NotImplementedError):
        master_body.imprint_projected_curves(UnitVector3D([0, 0, 1]), Sketch(), True)

    with pytest.raises(NotImplementedError):
        master_body.copy(design, "CopyName")

    with pytest.raises(NotImplementedError):
        master_body.get_named_selections()

    if backend_version >= (27, 1, 0):
        with pytest.raises(NotImplementedError):
            _ = master_body.centroid

        assert body.centroid is not None

    master_body._is_alive = False
    assert master_body.get_raw_tessellation() == {}
    master_body._is_alive = True

    if are_graphics_available():
        bodies_svc = master_body._grpc_client.services.bodies
        with (
            patch.object(bodies_svc, "get_tesellation", return_value={"tessellation": {}}),
            patch.object(
                bodies_svc, "get_tesellation_with_options", return_value={"tessellation": {}}
            ),
        ):
            original_version = master_body._grpc_client._backend_version
            try:
                master_body._grpc_client._backend_version = (25, 1, 0)
                master_body._tessellation = None
                master_body.tessellate(
                    tess_options=TessellationOptions(0.01, 0.01),
                    include_edges=True,
                    reset_cache=True,
                )

                master_body._grpc_client._backend_version = (25, 2, 0)
                master_body._tessellation = None
                master_body.tessellate(
                    tess_options=TessellationOptions(0.01, 0.01),
                    reset_cache=True,
                )
            finally:
                master_body._grpc_client._backend_version = original_version

        master_body.get_vtk_tessellation(
            _raw_tessellation={"f": {"vertices": [0.0, 0.0, 0.0], "faces": [4, 0, 1]}}
        )


def test_body_shell_and_remove_faces(modeler: Modeler):
    """Test shell_body and remove_faces error handling."""
    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 10, 10)
    design = modeler.create_design("ShellTest")
    body = design.extrude_sketch("TestBox", sketch, Quantity(10, UNITS.mm))
    body2 = design.extrude_sketch("TestBox2", sketch, Quantity(5, UNITS.mm))

    with pytest.raises(ValueError, match="does not belong to body"):
        body.remove_faces(body2.faces[0], Distance(1, UNITS.mm))

    bodies_svc = body._template._grpc_client.services.bodies
    with patch.object(bodies_svc, "shell", return_value={"success": False}):
        result = body.shell_body(Distance(0.1, UNITS.mm))
        assert result is False

    with patch.object(bodies_svc, "remove_faces", return_value={"success": False}):
        result = body.remove_faces(body.faces[0], Distance(0.1, UNITS.mm))
        assert result is False

    with patch.object(bodies_svc, "combine_merge", return_value={"success": False}):
        body._template.combine_merge(body2)

    with pytest.raises(NotImplementedError):
        body._template._combine_subtract(body2)

    with pytest.raises(NotImplementedError):
        body._template.plot()

    with pytest.raises(NotImplementedError):
        body._template.intersect(body2)

    with pytest.raises(NotImplementedError):
        body._template.subtract(body2)

    with pytest.raises(NotImplementedError):
        body._template.unite(body2)

    repr_str = repr(body._template)
    assert "MasterBody" in repr_str

    sketch_surf = Sketch()
    sketch_surf.box(Point2D([0, 0]), 5, 5)
    surf_body = design.create_surface("SurfaceBody", sketch_surf)
    repr_surf = repr(surf_body._template)
    assert "Surface thickness" in repr_surf

    material_result = body.get_assigned_material()
    assert material_result is None or material_result is not None

    with pytest.raises(ValueError, match="Either a sketch or edges must be provided"):
        body.imprint_curves(body.faces[:1])

    grpc_client = body._template._grpc_client
    with patch.object(grpc_client, "_backend_version", (25, 1, 0)):
        with pytest.raises(ValueError, match="A sketch must be provided for imprinting"):
            body.imprint_curves(body.faces[:1], sketch=None)

    with pytest.raises(ValueError, match="is not part of this body"):
        body.imprint_curves(body2.faces[:1], sketch=Sketch())

    with patch.object(body, "_Body__generic_boolean_op", return_value=None):
        body.intersect(body2)
        body.subtract(body2)
        body.unite(body2)


def test_body_tracker_update_paths(modeler: Modeler):
    """Test USE_TRACKER_TO_UPDATE_DESIGN=True branches and detach_faces failure path."""
    import ansys.geometry.core as pyansys_geo

    design = modeler.create_design("TrackerPaths")
    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 2, 2)
    body = design.extrude_sketch("box", sketch, 2)
    sketch2 = Sketch()
    sketch2.box(Point2D([10, 0]), 1, 1)
    body2 = design.extrude_sketch("box2", sketch2, 1)

    bodies_svc = body._grpc_client.services.bodies
    original_tracker = pyansys_geo.USE_TRACKER_TO_UPDATE_DESIGN
    try:
        pyansys_geo.USE_TRACKER_TO_UPDATE_DESIGN = True

        with patch.object(bodies_svc, "boolean", return_value={"tracker_response": {}}):
            with patch.object(design, "_update_from_tracker"):
                body.intersect(body2)

        backend_ver = body._grpc_client.backend_version
        if backend_ver >= (25, 2, 0):
            with patch.object(
                bodies_svc,
                "combine_merge",
                return_value={"success": True, "tracker_response": {}},
            ):
                with patch.object(design, "_update_from_tracker"):
                    body._template.combine_merge(body2)

        if backend_ver >= (26, 1, 0):
            with patch.object(bodies_svc, "combine", return_value={"tracker_response": {}}):
                with patch.object(design, "_update_from_tracker"):
                    body._combine_subtract(body2)

        if backend_ver >= (27, 1, 0):
            model_tools_svc = body._grpc_client.services.model_tools
            with patch.object(
                model_tools_svc,
                "detach_faces",
                return_value={"success": True, "tracked_response": {}, "created_bodies": []},
            ):
                with patch.object(design, "_update_from_tracker"):
                    body.detach_faces()

            with patch.object(
                model_tools_svc,
                "detach_faces",
                return_value={"success": False},
            ):
                result = body.detach_faces()
                assert result == []
    finally:
        pyansys_geo.USE_TRACKER_TO_UPDATE_DESIGN = original_tracker


def test_vertex_repr(modeler: Modeler):
    """Test Vertex.__repr__ coverage."""
    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 1, 1)
    design = modeler.create_design("VertexReprTest")
    body = design.extrude_sketch("box", sketch, 1)

    if len(body.vertices) > 0:
        vertex = body.vertices[0]
        repr_str = repr(vertex)
        assert "Vertex" in repr_str
        assert vertex.id in repr_str
        assert "Position" in repr_str
        assert body.id in repr_str


def test_assigning_and_getting_material(modeler: Modeler):
    """Test the assignment and retrieval of materials from a design."""
    sketch = Sketch()
    sketch.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))

    design_name = "ExtrudeProfile"
    design = modeler.create_design(design_name)

    density = Quantity(125, 1000 * UNITS.kg / (UNITS.m**3))
    poisson_ratio = Quantity(0.33, UNITS.dimensionless)
    tensile_strength = Quantity(45.0, UNITS.pascal)
    material = Material(
        "steel",
        density,
        [MaterialProperty(MaterialPropertyType.POISSON_RATIO, "myPoisson", poisson_ratio)],
    )
    material.add_property(MaterialPropertyType.TENSILE_STRENGTH, "myTensile", Quantity(45))
    design.add_material(material)

    body = design.extrude_sketch("JustACircle", sketch, Quantity(10, UNITS.mm))

    body.material = material
    mat_service = body.material

    assert mat_service.name == "steel"
    assert len(mat_service.properties) == 3
    assert mat_service.properties[MaterialPropertyType.DENSITY].type == MaterialPropertyType.DENSITY
    assert mat_service.properties[MaterialPropertyType.DENSITY].name == "Density"
    assert mat_service.properties[MaterialPropertyType.DENSITY].quantity == density
    assert (
        mat_service.properties[MaterialPropertyType.POISSON_RATIO].type
        == MaterialPropertyType.POISSON_RATIO
    )
    assert mat_service.properties[MaterialPropertyType.POISSON_RATIO].name == "myPoisson"
    assert mat_service.properties[MaterialPropertyType.POISSON_RATIO].quantity == poisson_ratio
    assert (
        mat_service.properties[MaterialPropertyType.TENSILE_STRENGTH].type
        == MaterialPropertyType.TENSILE_STRENGTH
    )
    assert mat_service.properties[MaterialPropertyType.TENSILE_STRENGTH].name == "myTensile"
    assert (
        mat_service.properties[MaterialPropertyType.TENSILE_STRENGTH].quantity == tensile_strength
    )


def test_get_empty_material(modeler: Modeler):
    """Check that the material service returns an empty material."""
    sketch = Sketch()
    sketch.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))

    design_name = "ExtrudeProfile"
    design = modeler.create_design(design_name)

    body = design.extrude_sketch("JustACircle", sketch, Quantity(10, UNITS.mm))

    mat_service = body.material
    assert mat_service.name == ""
    assert mat_service.properties[MaterialPropertyType.DENSITY].quantity == Quantity(
        0, UNITS.kg / (UNITS.m**3)
    )
    assert len(mat_service.properties) == 1


def test_remove_material_from_body(modeler: Modeler):
    """Test removing a material from a body."""
    design = modeler.create_design("RemoveMaterialTest")
    sketch = Sketch()
    sketch.circle(Point2D([0, 0], UNITS.mm), Quantity(10, UNITS.mm))

    body = design.extrude_sketch("CircleBody", sketch, Quantity(10, UNITS.mm))

    density = Quantity(7850, UNITS.kg / (UNITS.m**3))
    material = Material(
        "Steel",
        density,
        [MaterialProperty(MaterialPropertyType.POISSON_RATIO, "Poisson", Quantity(0.3))],
    )
    design.add_material(material)
    body.assign_material(material)
    assert body.material.name == "Steel"

    body.remove_assigned_material()

    assert body.material.name == ""
    assert len(body.material.properties) == 1
    assert body.material.properties[MaterialPropertyType.DENSITY].quantity == Quantity(
        0, UNITS.kg / (UNITS.m**3)
    )


def test_face_to_body_creation(modeler: Modeler):
    """Test in charge of validating the extrusion of an existing face."""
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(10, UNITS.mm))

    design_name = "BoxExtrusions"
    design = modeler.create_design(design_name)

    box_body = design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.mm))

    assert len(design.components) == 0
    assert len(design.bodies) == 1

    longer_body = design.extrude_face(
        "LongerBoxFromFace", box_body.faces[0], Quantity(20, UNITS.mm)
    )

    assert len(design.components) == 0
    assert len(design.bodies) == 2
    assert longer_body.volume.m == pytest.approx(Quantity(2e-6, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    longest_body = design.extrude_face(
        "LongestBoxFromFace", box_body.faces[0], Distance(30, UNITS.mm)
    )

    assert len(design.components) == 0
    assert len(design.bodies) == 3
    assert longest_body.volume.m == pytest.approx(Quantity(3e-6, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    nested_component = design.add_component("NestedComponent")
    surface_body = nested_component.create_surface_from_face(
        "SurfaceFromFace", longer_body.faces[2]
    )

    assert len(design.components) == 1
    assert len(design.bodies) == 3
    assert len(nested_component.components) == 0
    assert len(nested_component.bodies) == 1
    assert surface_body.volume.m == Quantity(0, UNITS.m**3).m
    assert surface_body.faces[0].area.m == pytest.approx(
        Quantity(2e-4, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )


def test_create_surface_from_copy_faces(modeler: Modeler):
    """Test creating a surface body from copied faces."""
    design = modeler.create_design("CopyFacesTest")

    cylinder = design.extrude_sketch("Cylinder", Sketch().circle(Point2D([0, 0]), 5), 20)

    face = cylinder.faces[1]
    square_surface = design.create_surface_from_face("square", face)
    assert square_surface.is_surface
    assert square_surface.faces[0].area.m == pytest.approx(102.41439999, rel=1e-6, abs=1e-8)

    circular_surface = design.copy_faces("circular", [face])
    assert circular_surface.is_surface
    assert circular_surface.faces[0].area.m == pytest.approx(78.53981633974483, rel=1e-6, abs=1e-8)


def test_component_body(modeler: Modeler):
    """Test the different ``Component`` and ``Body`` creation methods."""
    design_name = "ComponentBody_Test"
    design = modeler.create_design(design_name)
    assert design.name == design_name
    assert design.design_id is not None
    assert design.id is not None
    assert design.parent_component is None
    assert len(design.components) == 0
    assert len(design.bodies) == 0
    assert len(design.materials) == 0
    assert len(design.named_selections) == 0
    assert len(design.coordinate_systems) == 0

    sketch = Sketch()
    sketch.polygon(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), sides=5)

    name_extruded_body = "ExtrudedPolygon"
    distance_extruded_body = Quantity(50, UNITS.mm)
    body = design.extrude_sketch(
        name=name_extruded_body, sketch=sketch, distance=distance_extruded_body
    )

    assert body.name == name_extruded_body
    assert body.id is not None
    assert body.is_surface is False
    assert len(body.faces) == 7
    expected_vol = sketch.faces[0].area.m * distance_extruded_body.m * 1e-9
    assert body.volume.m == pytest.approx(expected_vol)
    assert len(design.components) == 0
    assert len(design.bodies) == 1
    assert len(body.edges) == 15
    assert len(body.vertices) == 10

    planar_component_name = "PlanarBody_Component"
    planar_component = design.add_component(planar_component_name)
    assert planar_component.id is not None
    assert planar_component.name == planar_component_name

    planar_sketch = Sketch()
    planar_sketch.ellipse(
        Point2D([50, 50], UNITS.mm), Quantity(30, UNITS.mm), Quantity(10, UNITS.mm)
    )
    planar_component_surface_name = "PlanarBody_Component_Surface"
    planar_body = planar_component.create_surface(planar_component_surface_name, planar_sketch)

    assert planar_body.name == planar_component_surface_name
    assert planar_body.id is not None
    assert planar_body.is_surface is True
    assert len(planar_body.faces) == 1
    assert planar_body.volume == 0.0
    assert len(planar_component.components) == 0
    assert len(planar_component.bodies) == 1
    assert len(design.components) == 1
    assert len(design.bodies) == 1
    assert len(planar_body.edges) == 1

    assert planar_component.parent_component.id == design.id

    comp_str = repr(planar_component)
    assert "ansys.geometry.core.designer.Component" in comp_str
    assert "Exists               : True" in comp_str
    assert "N Bodies             : 1" in comp_str
    assert "N Components         : 0" in comp_str
    assert "N Coordinate Systems : 0" in comp_str


def test_design_part(modeler: Modeler):
    """Test to validate the designer part id, name, and setter for components and bodies."""
    body1 = MasterBody(id="body1", name="First Only Body", grpc_client=modeler.client)
    body2 = MasterBody(id="body2", name="Second Body in Component", grpc_client=modeler.client)
    bodies = [body1]
    part = Part(id="IDPart", name="NamePart", components=[], bodies=bodies)
    masterpart = MasterComponent(id="PartMaster", name="Part Master", part=part)
    assert masterpart.id == "PartMaster"
    assert masterpart.name == "Part Master"
    assert masterpart.__repr__()[0:50] == "MasterComponent(id=PartMaster, name=Part Master, t"
    assert part.id == "IDPart"
    assert part.name == "NamePart"
    part.components = [body2]
    assert part.components[0].name == "Second Body in Component"
    part.bodies = body1
    assert part.bodies.name == "First Only Body"


def test_body_get_named_selections(modeler: Modeler):
    """Test getting named selections associated with bodies."""
    design = modeler.create_design("body_named_selections")
    box1 = design.extrude_sketch("box1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    box2 = design.extrude_sketch("box2", Sketch().box(Point2D([2, 2]), 1, 1), 1)

    design.create_named_selection("body_ns_1", bodies=[box1])
    design.create_named_selection("body_ns_2", bodies=[box2])

    for body in design.bodies:
        ns_list = body.get_named_selections()
        if body.id == box1.id:
            assert len(ns_list) == 1
            assert any(ns.name == "body_ns_1" for ns in ns_list)
        elif body.id == box2.id:
            assert len(ns_list) == 1
            assert any(ns.name == "body_ns_2" for ns in ns_list)
        else:
            assert len(ns_list) == 0

def test_clear_body_cache_for_part(modeler: Modeler):
    """Test _clear_body_cache_for_part() clears cached bodies for part and matching components."""
    design = modeler.create_design("clear_body_cache")

    part = design._master_component.part
    matching_component = Mock()
    matching_component._master_component = Mock()
    matching_component._master_component.part = part
    matching_component._clear_cached_bodies = Mock()

    with (
        patch.object(design, "_clear_cached_bodies") as clear_spy,
        patch.object(design, "_get_all_components", return_value=[matching_component]),
    ):
        design._clear_body_cache_for_part(part)

        clear_spy.assert_called_once()
        matching_component._clear_cached_bodies.assert_called_once()

def test_find_and_add_body_matching_part_id(modeler: Modeler):
    """Test _find_and_add_body() adds new body when parent part is found."""
    design = modeler.create_design("add_body_part")
    comp = design.add_component("BodyComponent")
    part = comp._master_component.part

    body_info = {
        "id": "new_body_1",
        "name": "NewBody",
        "parent_id": part.id,
        "is_surface": False,
    }

    with (
        patch.object(design._grpc_client.log, "debug") as debug_spy,
        patch.object(design, "_clear_body_cache_for_part"),
    ):
        result = design._find_and_add_body(body_info, design.components, None, None)

        assert result is not None
        assert result.id == "new_body_1"
        debug_spy.assert_called()
        assert any("Added new body" in str(call) for call in debug_spy.call_args_list)

def test_find_and_add_body_recursive_search(modeler: Modeler):
    """Test _find_and_add_body() recursively searches nested components for parent part."""
    design = modeler.create_design("add_body_recursive")
    parent_comp = design.add_component("ParentComp")
    nested_comp = parent_comp.add_component("NestedComp")
    part = nested_comp._master_component.part

    body_info = {
        "id": "nested_body_1",
        "name": "NestedBody",
        "parent_id": part.id,
        "is_surface": True,
    }

    with (
        patch.object(design._grpc_client.log, "debug") as debug_spy,
        patch.object(design, "_clear_body_cache_for_part"),
    ):
        result = design._find_and_add_body(body_info, design.components, None, None)

        assert result is not None
        assert result.id == "nested_body_1"
        debug_spy.assert_called()

def test_find_and_add_body_not_found_returns_none(modeler: Modeler):
    """Test _find_and_add_body() returns None when parent part cannot be found."""
    design = modeler.create_design("add_body_notfound")

    body_info = {
        "id": "orphan_body_1",
        "name": "OrphanBody",
        "parent_id": "nonexistent_part",
        "is_surface": False,
    }

    result = design._find_and_add_body(body_info, design.components, None, None)

    assert result is None

def test_find_and_add_body_empty_components(modeler: Modeler):
    """Test _find_and_add_body() returns None when component list is empty."""
    design = modeler.create_design("add_body_empty")

    body_info = {
        "id": "body_1",
        "name": "Body1",
        "parent_id": "any_part",
        "is_surface": False,
    }

    result = design._find_and_add_body(body_info, [], None, None)

    assert result is None

def test_update_body_sets_properties(modeler: Modeler):
    """Test _update_body() sets body properties from tracker response."""
    design = modeler.create_design("update_body_props")

    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 1, 1)
    body = design.extrude_sketch("body1", sketch, 1)

    body_info = {"id": body.id, "name": "UpdatedBodyName", "is_surface": True}

    with patch.object(design._grpc_client.log, "debug") as debug_spy:
        design._update_body(body, body_info)

        debug_spy.assert_called()


def test_delete_body_component(modeler: Modeler):
    """Test for verifying the deletion of ``Component`` and ``Body`` objects.

    Notes
    -----
    Requires storing scdocx file and checking manually (for now).
    """
    # Create your design on the server side
    design = modeler.create_design("Deletion_Test")

    # Create a Sketch object and draw a circle (all client side)
    sketch = Sketch()
    sketch.circle(Point2D([-30, -30], UNITS.mm), Quantity(10, UNITS.mm))
    distance = Quantity(30, UNITS.mm)

    #  The following component hierarchy is made
    #
    #           |---> comp_1 ---|---> nested_1_comp_1 ---> nested_1_nested_1_comp_1
    #           |               |
    #           |               |---> nested_2_comp_1
    #           |
    # DESIGN ---|---> comp_2 -------> nested_1_comp_2
    #           |
    #           |
    #           |---> comp_3
    #
    #
    # Now, only "comp_3", "nested_2_comp_1" and "nested_1_nested_1_comp_1"
    # will have a body associated...
    #
    #

    # Create the components
    comp_1 = design.add_component("Component_1")
    comp_2 = design.add_component("Component_2")
    comp_3 = design.add_component("Component_3")
    nested_1_comp_1 = comp_1.add_component("Nested_1_Component_1")
    nested_1_nested_1_comp_1 = nested_1_comp_1.add_component("Nested_1_Nested_1_Component_1")
    nested_2_comp_1 = comp_1.add_component("Nested_2_Component_1")
    _ = comp_2.add_component("Nested_1_Component_2")

    # Create the bodies
    body_1 = comp_3.extrude_sketch(name="comp_3_circle", sketch=sketch, distance=distance)
    body_2 = nested_2_comp_1.extrude_sketch(
        name="nested_2_comp_1_circle", sketch=sketch, distance=distance
    )
    _ = nested_1_nested_1_comp_1.extrude_sketch(
        name="nested_1_nested_1_comp_1_circle", sketch=sketch, distance=distance
    )

    # Let's start by doing something impossible - trying to delete body_1 from comp_1
    comp_1.delete_body(body_1)

    # Check that all the underlying objects are still alive
    assert comp_1.is_alive
    assert comp_1.components[0].is_alive
    assert comp_1.components[0].components[0].is_alive
    assert comp_1.components[0].components[0].bodies[0].is_alive
    assert comp_1.components[1].is_alive
    assert comp_1.components[1].bodies[0].is_alive
    assert comp_2.is_alive
    assert comp_2.components[0].is_alive
    assert comp_3.is_alive
    assert comp_3.bodies[0].is_alive

    # Do the same checks but calling them from the design object
    assert design.is_alive
    assert design.components[0].is_alive
    assert design.components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].bodies[0].is_alive
    assert design.components[0].components[1].is_alive
    assert design.components[0].components[1].bodies[0].is_alive
    assert design.components[1].is_alive
    assert design.components[1].components[0].is_alive
    assert design.components[2].is_alive
    assert design.components[2].bodies[0].is_alive

    # Let's do another impossible thing - trying to delete comp_3 from comp_1
    comp_1.delete_component(comp_3)

    # Check that all the underlying objects are still alive
    assert comp_1.is_alive
    assert comp_1.components[0].is_alive
    assert comp_1.components[0].components[0].is_alive
    assert comp_1.components[0].components[0].bodies[0].is_alive
    assert comp_1.components[1].is_alive
    assert comp_1.components[1].bodies[0].is_alive
    assert comp_2.is_alive
    assert comp_2.components[0].is_alive
    assert comp_3.is_alive
    assert comp_3.bodies[0].is_alive

    # Do the same checks but calling them from the design object
    assert design.is_alive
    assert design.components[0].is_alive
    assert design.components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].bodies[0].is_alive
    assert design.components[0].components[1].is_alive
    assert design.components[0].components[1].bodies[0].is_alive
    assert design.components[1].is_alive
    assert design.components[1].components[0].is_alive
    assert design.components[2].is_alive
    assert design.components[2].bodies[0].is_alive

    # Let's delete now the entire comp_2 component
    comp_2.delete_component(comp_2)

    # Check that all the underlying objects are still alive except for comp_2
    assert comp_1.is_alive
    assert comp_1.components[0].is_alive
    assert comp_1.components[0].components[0].is_alive
    assert comp_1.components[0].components[0].bodies[0].is_alive
    assert comp_1.components[1].is_alive
    assert comp_1.components[1].bodies[0].is_alive
    assert not comp_2.is_alive
    assert comp_3.is_alive
    assert comp_3.bodies[0].is_alive

    # Do the same checks but calling them from the design object
    assert design.is_alive
    assert len(design.components) == 2
    assert design.components[0].is_alive
    assert design.components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].bodies[0].is_alive
    assert design.components[0].components[1].is_alive
    assert design.components[0].components[1].bodies[0].is_alive
    assert design.components[1].is_alive
    assert design.components[1].bodies[0].is_alive

    # Let's delete now the body_2 object
    design.delete_body(body_2)

    # Check that all the underlying objects are still alive except for comp_2 and body_2
    assert comp_1.is_alive
    assert comp_1.components[0].is_alive
    assert comp_1.components[0].components[0].is_alive
    assert comp_1.components[0].components[0].bodies[0].is_alive
    assert comp_1.components[1].is_alive
    assert not body_2.is_alive
    assert not comp_2.is_alive
    assert comp_3.is_alive

    # Do the same checks but calling them from the design object
    assert design.is_alive
    assert design.components[0].is_alive
    assert design.components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].bodies[0].is_alive
    assert design.components[0].components[1].is_alive
    assert design.components[1].is_alive
    assert design.components[1].bodies[0].is_alive

    # Finally, let's delete the most complex one - comp_1
    design.delete_component(comp_1)

    # Check that all the underlying objects are still alive except for comp_2, body_2 and comp_1
    assert not comp_1.is_alive
    assert not comp_2.is_alive
    assert comp_3.is_alive
    assert comp_3.bodies[0].is_alive

    # Do the same checks but calling them from the design object
    assert design.is_alive
    assert len(design.components) == 1
    assert design.components[0].is_alive
    assert design.components[0].bodies[0].is_alive

    # Finally, let's delete the entire design
    design.delete_component(comp_3)

    # Check everything is dead
    assert design.is_alive
    assert len(design.components) == 0

    # Try deleting the Design object itself - this is forbidden
    with pytest.raises(ValueError, match="The design itself cannot be deleted."):
        design.delete_component(design)

    # Let's try out the representation methods
    design_str = str(design)
    assert "ansys.geometry.core.designer.Design" in design_str
    assert "Name                 : Deletion_Test" in design_str
    assert "N Bodies             : 0" in design_str
    assert "N Components         : 0" in design_str
    assert "N Coordinate Systems : 0" in design_str
    assert "N Named Selections   : 0" in design_str
    assert "N Materials          : 0" in design_str
    assert "N Beam Profiles      : 0" in design_str
    assert "N Design Points      : 0" in design_str

    comp_1_str = str(comp_1)
    assert "ansys.geometry.core.designer.Component" in comp_1_str
    assert "Name                 : Component_1" in comp_1_str
    assert "Exists               : False" in comp_1_str
    assert "Parent component     : Deletion_Test" in comp_1_str
    assert "N Bodies             : 0" in comp_1_str
    assert "N Beams              : 0" in comp_1_str
    assert "N Components         : 0" in comp_1_str
    assert "N Design Points      : 0" in comp_1_str
    assert "N Coordinate Systems : 0" in comp_1_str

    body_1_str = str(body_1)
    assert "ansys.geometry.core.designer.Body" in body_1_str
    assert "Name                 : comp_3_circle" in body_1_str
    assert "Exists               : False" in body_1_str
    assert "Surface body         : False" in body_1_str
    assert "Parent component     : Component_3" in body_1_str
    assert "Color                : None" in body_1_str

def test_single_body_translation(modeler: Modeler):
    """Test for verifying the correct translation of a ``Body``.

    Notes
    -----
    Requires storing scdocx file and checking manually (for now).
    """
    # Create your design on the server side
    design = modeler.create_design("SingleBodyTranslation_Test")

    # Create 2 Sketch objects and draw a circle and a polygon (all client side)
    sketch_1 = Sketch()
    sketch_1.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))
    sketch_2 = Sketch()
    sketch_2.polygon(Point2D([-30, -30], UNITS.mm), Quantity(10, UNITS.mm), sides=5)

    # Build 2 independent components and bodies
    circle_comp = design.add_component("CircleComponent")
    body_circle_comp = circle_comp.extrude_sketch("Circle", sketch_1, Quantity(50, UNITS.mm))
    polygon_comp = design.add_component("PolygonComponent")
    body_polygon_comp = polygon_comp.extrude_sketch("Polygon", sketch_2, Quantity(30, UNITS.mm))

    body_circle_comp.translate(UnitVector3D([1, 0, 0]), Distance(50, UNITS.mm))
    body_polygon_comp.translate(UnitVector3D([-1, 1, -1]), Quantity(88, UNITS.mm))
    body_polygon_comp.translate(UnitVector3D([-1, 1, -1]), 101)

def test_body_rotation(modeler: Modeler):
    """Test for verifying the correct rotation of a ``Body``."""
    # Create your design on the server side
    design = modeler.create_design("BodyRotation_Test")

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    original_vertices = []
    for edge in body.edges:
        original_vertices.extend([edge.shape.start, edge.shape.end])

    body.rotate(Point3D([0, 0, 0]), UnitVector3D([0, 0, 1]), np.pi / 4)

    new_vertices = []
    for edge in body.edges:
        new_vertices.extend([edge.shape.start, edge.shape.end])

    # Make sure no vertices are in the same position as in before rotation
    for old_vertex, new_vertex in zip(original_vertices, new_vertices):
        assert not np.allclose(old_vertex, new_vertex)

def test_copy_body(modeler: Modeler):
    """Test copying a body."""
    # Create your design on the server side
    design = modeler.create_design("Design")

    sketch_1 = Sketch().circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))
    body = design.extrude_sketch("Original", sketch_1, Distance(1, UNITS.mm))

    # Copy body at same design level
    copy = body.copy(design, "Copy")
    assert len(design.bodies) == 2
    assert design.bodies[-1].id == copy.id

    # Bodies should be distinct
    assert body.id != copy.id
    assert body != copy

    # Copy body into sub-component
    comp1 = design.add_component("comp1")
    copy2 = body.copy(comp1, "Subcopy")
    assert len(comp1.bodies) == 1
    assert comp1.bodies[-1].id == copy2.id

    # Bodies should be distinct
    assert body.id != copy2.id
    assert body != copy2

    # Copy a copy
    comp2 = comp1.add_component("comp2")
    copy3 = copy2.copy(comp2, "Copy3")
    assert len(comp2.bodies) == 1
    assert comp2.bodies[-1].id == copy3.id

    # Bodies should be distinct
    assert copy2.id != copy3.id
    assert copy2 != copy3

    # Ensure deleting original doesn't affect the copies
    design.delete_body(body)
    assert not body.is_alive
    assert copy.is_alive

def test_boolean_body_operations(modeler: Modeler):
    """
    Test cases:

    1) master/master
        a) intersect
            i) normal
                x) identity
                y) transform
            ii) empty failure
        b) subtract
            i) normal
                x) identity
                y) transform
            ii) empty failure
            iii) disjoint
        c) unite
            i) normal
                x) identity
                y) transform
            ii) disjoint
    2) instance/instance
        a) intersect
            i) normal
                x) identity
                y) transform
            ii) empty failure
        b) subtract
            i) normal
                x) identity
                y) transform
            ii) empty failure
        c) unite
            i) normal
                x) identity
                y) transform
    """
    design = modeler.create_design("TestBooleanOperations")

    comp1 = design.add_component("Comp1")
    comp2 = design.add_component("Comp2")
    comp3 = design.add_component("Comp3")

    body1 = comp1.extrude_sketch("Body1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    body2 = comp2.extrude_sketch("Body2", Sketch().box(Point2D([0.5, 0]), 1, 1), 1)
    body3 = comp3.extrude_sketch("Body3", Sketch().box(Point2D([5, 0]), 1, 1), 1)

    # 1.a.i.x
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy1.intersect(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

    # 1.a.i.y
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.intersect(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.25)

    # 1.a.ii
    copy1 = body1.copy(comp1, "Copy1")
    copy3 = body3.copy(comp3, "Copy3")
    with pytest.raises(ValueError, match="bodies do not intersect"):
        copy1.intersect(copy3)

    assert copy1.is_alive
    assert copy3.is_alive

    # 1.b.i.x
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy1.subtract(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

    # 1.b.i.y
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.subtract(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.75)

    # 1.b.ii
    copy1 = body1.copy(comp1, "Copy1")
    copy1a = body1.copy(comp1, "Copy1a")
    with pytest.raises(ValueError):
        copy1.subtract(copy1a)

    assert copy1.is_alive
    assert copy1a.is_alive

    # 1.b.iii
    copy1 = body1.copy(comp1, "Copy1")
    copy3 = body3.copy(comp3, "Copy3")
    copy1.subtract(copy3)

    assert Accuracy.length_is_equal(copy1.volume.m, 1)
    assert copy1.volume
    assert not copy3.is_alive

    # 1.c.i.x
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy1.unite(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1.5)

    # 1.c.i.y
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.unite(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1.75)

    # 1.c.ii
    copy1 = body1.copy(comp1, "Copy1")
    copy3 = body3.copy(comp3, "Copy3")
    copy1.unite(copy3)

    assert not copy3.is_alive
    assert body3.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1)

    # Test instance/instance
    comp1_i = design.add_component("Comp1_i", comp1)
    comp2_i = design.add_component("Comp2_i", comp2)
    comp3_i = design.add_component("Comp3_i", comp3)

    comp1_i.modify_placement(
        Vector3D([52, 61, -43]), Point3D([-4, 26, 66]), UnitVector3D([-21, 20, 87]), np.pi / 4
    )
    comp2_i.modify_placement(
        Vector3D([52, 61, -43]), Point3D([-4, 26, 66]), UnitVector3D([-21, 20, 87]), np.pi / 4
    )
    comp3_i.modify_placement(
        Vector3D([52, 61, -43]), Point3D([-4, 26, 66]), UnitVector3D([-21, 20, 87]), np.pi / 4
    )

    body1 = comp1_i.bodies[0]
    body2 = comp2_i.bodies[0]
    body3 = comp3_i.bodies[0]

    # 2.a.i.x
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy1.intersect(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

    # 2.a.i.y
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.intersect(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.25)

    # 2.a.ii
    copy1 = body1.copy(comp1_i, "Copy1")
    copy3 = body3.copy(comp3_i, "Copy3")
    with pytest.raises(ValueError, match="bodies do not intersect"):
        copy1.intersect(copy3)

    assert copy1.is_alive
    assert copy3.is_alive

    # 2.b.i.x
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy1.subtract(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

    # 2.b.i.y
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.subtract(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.75)

    # 2.b.ii
    copy1 = body1.copy(comp1_i, "Copy1")
    copy1a = body1.copy(comp1_i, "Copy1a")
    with pytest.raises(ValueError):
        copy1.subtract(copy1a)

    assert copy1.is_alive
    assert copy1a.is_alive

    # 2.b.iii
    copy1 = body1.copy(comp1_i, "Copy1")
    copy3 = body3.copy(comp3_i, "Copy3")
    copy1.subtract(copy3)

    assert Accuracy.length_is_equal(copy1.volume.m, 1)
    assert copy1.volume
    assert not copy3.is_alive

    # 2.c.i.x
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy1.unite(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1.5)

    # 2.c.i.y
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.unite(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1.75)

    # 2.c.ii
    copy1 = body1.copy(comp1_i, "Copy1")
    copy3 = body3.copy(comp3_i, "Copy3")
    copy1.unite(copy3)

    assert not copy3.is_alive
    assert body3.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1)

def test_set_body_name(modeler: Modeler):
    """Test the setting the name of a body."""
    design = modeler.create_design("simple_cube")
    unit = DEFAULT_UNITS.LENGTH
    plane = Plane(
        Point3D([1 / 2, 1 / 2, 0.0], unit=unit),
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )
    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0]), width=1 * unit, height=1 * unit)
    box = design.extrude_sketch("first_name", box_plane, 1 * unit)
    assert box.name == "first_name"
    box.set_name("updated_name")
    assert box.name == "updated_name"
    box.name = "updated_name2"
    assert box.name == "updated_name2"

def test_body_suppression(modeler: Modeler):
    """Test the suppression of a body."""

    design = modeler.create_design("RVE")
    unit = DEFAULT_UNITS.LENGTH

    plane = Plane(
        Point3D([1 / 2, 1 / 2, 0.0], unit=unit),
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )

    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0]), width=1 * unit, height=1 * unit)
    box = design.extrude_sketch("Matrix", box_plane, 1 * unit)

    assert box.is_suppressed is False
    box.set_suppressed(True)
    assert box.is_suppressed is True
    box.is_suppressed = False
    assert box.is_suppressed is False

def test_set_body_color(modeler: Modeler):
    """Test the getting and setting of body color."""

    design = modeler.create_design("RVE2")
    unit = DEFAULT_UNITS.LENGTH

    plane = Plane(
        Point3D([1 / 2, 1 / 2, 0.0], unit=unit),
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )
    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0]), width=1 * unit, height=1 * unit)
    box = design.extrude_sketch("Block", box_plane, 1 * unit)

    # Default body color is if it is not set on server side.
    assert box.color == DEFAULT_COLOR

    # Set the color of the body using hex code.
    box.color = "#0000ff"
    assert box.color[0:7] == "#0000ff"

    box.color = "#ffc000"
    assert box.color[0:7] == "#ffc000"

    # Set the color of the body using color name.
    box.set_color("green")
    box.color[0:7] == "#008000"

    # Set the color of the body using RGB values between (0,1) as floats.
    box.set_color((1.0, 0.0, 0.0))
    box.color[0:7] == "#ff0000"

    # Set the color of the body using RGB values between (0,255) as integers).
    box.set_color((0, 255, 0))
    box.color[0:7] == "#00ff00"

    # Assigning color object directly
    blue_color = mcolors.to_rgba("#0000FF")
    box.color = blue_color
    assert box.color[0:7] == "#0000ff"

    # Test an RGBA color
    box.color = "#ff00003c"
    assert box.color == "#ff00003c"

    # Test setting the opacity separately
    box.opacity = 0.8
    assert box.color == "#ff0000cc"

    # Try setting the opacity to an invalid value
    with pytest.raises(
        ValueError, match="Invalid color value: Opacity value must be between 0 and 1."
    ):
        box.opacity = 255

def test_body_scale(modeler: Modeler):
    """Verify the correct scaling of a body."""
    design = modeler.create_design("BodyScale_Test")

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert Accuracy.length_is_equal(body.volume.m, 1)

    body.scale(2)
    assert Accuracy.length_is_equal(body.volume.m, 8)

    body.scale(0.25)
    assert Accuracy.length_is_equal(body.volume.m, 1 / 8)

def test_body_mapping(modeler: Modeler):
    """Verify the correct mapping of a body."""
    design = modeler.create_design("BodyMap_Test")

    # non-symmetric shape to allow determination of mirroring
    body = design.extrude_sketch(
        "box",
        Sketch()
        .segment(Point2D([1, 1]), Point2D([-1, 1]))
        .segment_to_point(Point2D([0, 0.5]))
        .segment_to_point(Point2D([-1, -1]))
        .segment_to_point(Point2D([1, -1]))
        .segment_to_point(Point2D([1, 1])),
        1,
    )

    # Test 1: identity mapping - everything should be the same
    copy = body.copy(body.parent_component, "copy")
    copy.map(Frame(Point3D([0, 0, 0]), UnitVector3D([1, 0, 0]), UnitVector3D([0, 1, 0])))

    vertices = []
    for edge in body.edges:
        vertices.extend([edge.shape.start, edge.shape.end])

    copy_vertices = []
    for edge in copy.edges:
        copy_vertices.extend([edge.shape.start, edge.shape.end])

    assert np.allclose(vertices, copy_vertices)

    # Test 2: mirror the body - flips only the x direction
    copy = body.copy(body.parent_component, "copy")
    copy.map(Frame(Point3D([-4, 0, 1]), UnitVector3D([-1, 0, 0]), UnitVector3D([0, 1, 0])))

    copy_vertices = []
    for edge in copy.edges:
        copy_vertices.extend([edge.shape.start, edge.shape.end])

    # expected vertices from confirmed mirror
    expected_vertices = [
        Point3D([-3.0, -1.0, 0.0]),
        Point3D([-5.0, -1.0, 0.0]),
        Point3D([-3.0, -1.0, 1.0]),
        Point3D([-3.0, -1.0, 0.0]),
        Point3D([-4.0, 0.5, 0.0]),
        Point3D([-3.0, -1.0, 0.0]),
        Point3D([-4.0, 0.5, 1.0]),
        Point3D([-4.0, 0.5, 0.0]),
        Point3D([-3.0, 1.0, 0.0]),
        Point3D([-4.0, 0.5, 0.0]),
        Point3D([-3.0, 1.0, 1.0]),
        Point3D([-3.0, 1.0, 0.0]),
        Point3D([-5.0, 1.0, 0.0]),
        Point3D([-3.0, 1.0, 0.0]),
        Point3D([-5.0, 1.0, 1.0]),
        Point3D([-5.0, 1.0, 0.0]),
        Point3D([-5.0, -1.0, 0.0]),
        Point3D([-5.0, 1.0, 0.0]),
        Point3D([-5.0, -1.0, 1.0]),
        Point3D([-5.0, -1.0, 0.0]),
        Point3D([-3.0, -1.0, 1.0]),
        Point3D([-5.0, -1.0, 1.0]),
        Point3D([-4.0, 0.5, 1.0]),
        Point3D([-3.0, -1.0, 1.0]),
        Point3D([-3.0, 1.0, 1.0]),
        Point3D([-4.0, 0.5, 1.0]),
        Point3D([-5.0, 1.0, 1.0]),
        Point3D([-3.0, 1.0, 1.0]),
        Point3D([-5.0, -1.0, 1.0]),
        Point3D([-5.0, 1.0, 1.0]),
    ]

    assert np.allclose(expected_vertices, copy_vertices)

    # Test 3: rotate body 180 degrees - flip x and y direction
    map_copy = body.copy(body.parent_component, "copy")
    map_copy.map(Frame(Point3D([0, 0, 0]), UnitVector3D([-1, 0, 0]), UnitVector3D([0, -1, 0])))

    rotate_copy = body.copy(body.parent_component, "copy")
    rotate_copy.rotate(Point3D([0, 0, 0]), UnitVector3D([0, 0, 1]), np.pi)

    map_vertices = []
    for edge in map_copy.edges:
        map_vertices.extend([edge.shape.start, edge.shape.end])

    rotate_vertices = []
    for edge in rotate_copy.edges:
        rotate_vertices.extend([edge.shape.start, edge.shape.end])

    assert np.allclose(map_vertices, rotate_vertices)

def test_create_block_body(modeler: Modeler):
    """Test the creation of a block body given two opposite corner points."""
    design = modeler.create_design("BlockTest")
    block = design.create_block("testblockbody", Point3D([0, 0, 0]), Point3D([1, 2, 3]))

    assert len(block.faces) == 6
    assert block.volume.m == 6.0
    assert block.parent_component.id == design.id

    # Create a nested block body and verify that it reports the correct parent component.
    nested = design.add_component("NestedBlockComp")
    nested_block = nested.create_block("nestedblockbody", Point3D([2, 3, 4]), Point3D([5, 6, 7]))

    assert len(nested_block.faces) == 6
    assert nested_block.volume.m == 27.0
    assert nested_block.parent_component.id == nested.id

def test_body_mirror(modeler: Modeler):
    """Test the mirroring of a body."""
    design = modeler.create_design("Design1")

    # Create shape with no lines of symmetry in any axis
    body = design.extrude_sketch(
        "box",
        Sketch()
        .segment(Point2D([1, 1]), Point2D([-1, 1]))
        .segment_to_point(Point2D([0, 0.5]))
        .segment_to_point(Point2D([-1, -1]))
        .segment_to_point(Point2D([1, -1]))
        .segment_to_point(Point2D([1, 1])),
        1,
    )
    top = design.extrude_sketch(
        "top", Sketch(Plane(Point3D([0, 0, 1]))).box(Point2D([0.5, 0.5]), 0.1, 0.1), 0.1
    )
    body.unite(top)

    # Mirror across YZ plane
    copy1 = body.copy(body.parent_component, "box2")
    copy1.mirror(Plane(Point3D([2, 0, 0]), UnitVector3D([0, 0, 1]), UnitVector3D([0, 1, 0])))

    # results from SpaceClaim
    expected_vertices = [
        Point3D([5.0, -1.0, 1.0]),
        Point3D([5.0, -1.0, 0.0]),
        Point3D([4.0, 0.5, 1.0]),
        Point3D([4.0, 0.5, 0.0]),
        Point3D([5.0, 1.0, 1.0]),
        Point3D([5.0, 1.0, 0.0]),
        Point3D([3.0, 1.0, 1.0]),
        Point3D([3.0, 1.0, 0.0]),
        Point3D([3.0, -1.0, 1.0]),
        Point3D([3.0, -1.0, 0.0]),
        Point3D([3.55, 0.45, 1.1]),
        Point3D([3.55, 0.45, 1.0]),
        Point3D([3.55, 0.55, 1.1]),
        Point3D([3.55, 0.55, 1.0]),
        Point3D([3.45, 0.55, 1.1]),
        Point3D([3.45, 0.55, 1.0]),
        Point3D([3.45, 0.45, 1.1]),
        Point3D([3.45, 0.45, 1.0]),
    ]

    copy_vertices = []
    for edge in copy1.edges:
        if edge.shape.start not in copy_vertices:
            copy_vertices.append(edge.shape.start)
    assert np.allclose(expected_vertices, copy_vertices)

    # Mirror across XY plane
    copy2 = body.copy(body.parent_component, "box3")
    copy2.mirror(Plane(Point3D([0, 0, -5]), UnitVector3D([1, 0, 0]), UnitVector3D([0, 1, 0])))

    # results from SpaceClaim
    expected_vertices = [
        Point3D([-1.0, -1.0, -11.0]),
        Point3D([-1.0, -1.0, -10.0]),
        Point3D([0.0, 0.5, -11.0]),
        Point3D([0.0, 0.5, -10.0]),
        Point3D([-1.0, 1.0, -11.0]),
        Point3D([-1.0, 1.0, -10.0]),
        Point3D([1.0, 1.0, -11.0]),
        Point3D([1.0, 1.0, -10.0]),
        Point3D([1.0, -1.0, -11.0]),
        Point3D([1.0, -1.0, -10.0]),
        Point3D([0.45, 0.45, -11.1]),
        Point3D([0.45, 0.45, -11.0]),
        Point3D([0.45, 0.55, -11.1]),
        Point3D([0.45, 0.55, -11.0]),
        Point3D([0.55, 0.55, -11.1]),
        Point3D([0.55, 0.55, -11.0]),
        Point3D([0.55, 0.45, -11.1]),
        Point3D([0.55, 0.45, -11.0]),
    ]

    copy_vertices = []
    for edge in copy2.edges:
        if edge.shape.start not in copy_vertices:
            copy_vertices.append(edge.shape.start)
    assert np.allclose(expected_vertices, copy_vertices)

    # Mirror across XZ plane
    copy3 = body.copy(body.parent_component, "box4")
    copy3.mirror(Plane(Point3D([0, 3, 0]), UnitVector3D([1, 0, 0]), UnitVector3D([0, 0, 1])))

    # results from SpaceClaim
    expected_vertices = [
        Point3D([-1.0, 7.0, 1.0]),
        Point3D([-1.0, 7.0, 0.0]),
        Point3D([0.0, 5.5, 1.0]),
        Point3D([0.0, 5.5, 0.0]),
        Point3D([-1.0, 5.0, 1.0]),
        Point3D([-1.0, 5.0, 0.0]),
        Point3D([1.0, 5.0, 1.0]),
        Point3D([1.0, 5.0, 0.0]),
        Point3D([1.0, 7.0, 1.0]),
        Point3D([1.0, 7.0, 0.0]),
        Point3D([0.45, 5.55, 1.1]),
        Point3D([0.45, 5.55, 1.0]),
        Point3D([0.45, 5.45, 1.1]),
        Point3D([0.45, 5.45, 1.0]),
        Point3D([0.55, 5.45, 1.1]),
        Point3D([0.55, 5.45, 1.0]),
        Point3D([0.55, 5.55, 1.1]),
        Point3D([0.55, 5.55, 1.0]),
    ]

    copy_vertices = []
    for edge in copy3.edges:
        if edge.shape.start not in copy_vertices:
            copy_vertices.append(edge.shape.start)
    assert np.allclose(expected_vertices, copy_vertices)

def test_create_body_from_loft_profile(modeler: Modeler):
    """Test the ``create_body_from_loft_profile()`` method to create a vase
    shape.
    """
    design_sketch = modeler.create_design("loftprofile")

    profile1 = Circle(origin=[0, 0, 0], radius=8).trim(Interval(0, 2 * np.pi))
    profile2 = Circle(origin=[0, 0, 10], radius=10).trim(Interval(0, 2 * np.pi))
    profile3 = Circle(origin=[0, 0, 20], radius=5).trim(Interval(0, 2 * np.pi))

    # Call the method
    result = design_sketch.create_body_from_loft_profile(
        "vase", [[profile1], [profile2], [profile3]], False, False
    )

    # Assert that the resulting body has only one face.
    assert len(result.faces) == 1

    # check volume of body
    # expected is 0 since it's not a closed surface
    assert result.volume.m == 0

def test_surface_body_creation(modeler: Modeler):
    """Test surface body creation from trimmed surfaces."""
    design = modeler.create_design("Design1")

    # half sphere
    surface = Sphere([0, 0, 0], 1)
    trimmed_surface = surface.trim(BoxUV(Interval(0, np.pi * 2), Interval(0, np.pi / 2)))
    body = design.create_body_from_surface("sphere", trimmed_surface)
    assert len(design.bodies) == 1
    assert body.is_surface
    assert body.faces[0].area.m == pytest.approx(np.pi * 2)

    # cylinder
    surface = Cylinder([0, 0, 0], 1)
    trimmed_surface = surface.trim(BoxUV(Interval(0, np.pi * 2), Interval(0, 1)))
    body = design.create_body_from_surface("cylinder", trimmed_surface)

    assert len(design.bodies) == 2
    assert body.is_surface
    assert body.faces[0].area.m == pytest.approx(np.pi * 2)

    # cone
    surface = Cone([0, 0, 0], 1, np.pi / 4)
    trimmed_surface = surface.trim(BoxUV(Interval(0, np.pi * 2), Interval(surface.apex.z.m, 0)))
    body = design.create_body_from_surface("cone", trimmed_surface)

    assert len(design.bodies) == 3
    assert body.is_surface
    assert body.faces[0].area.m == pytest.approx(4.44288293816)

    # half torus
    surface = Torus([0, 0, 0], 2, 1)
    trimmed_surface = surface.trim(BoxUV(Interval(0, np.pi), Interval(0, np.pi * 2)))
    body = design.create_body_from_surface("torus", trimmed_surface)

    assert len(design.bodies) == 4
    assert body.is_surface
    assert body.faces[0].area.m == pytest.approx(39.4784176044)

    # SOLID BODIES

    # sphere
    surface = Sphere([0, 0, 0], 1)
    trimmed_surface = surface.trim(BoxUV(Interval(0, np.pi * 2), Interval(-np.pi / 2, np.pi / 2)))
    body = design.create_body_from_surface("sphere_solid", trimmed_surface)
    assert len(design.bodies) == 5
    assert not body.is_surface
    assert body.faces[0].area.m == pytest.approx(np.pi * 4)

    # torus
    surface = Torus([0, 0, 0], 2, 1)
    trimmed_surface = surface.trim(BoxUV(Interval(0, np.pi * 2), Interval(0, np.pi * 2)))
    body = design.create_body_from_surface("torus_solid", trimmed_surface)

    assert len(design.bodies) == 6
    assert not body.is_surface
    assert body.faces[0].area.m == pytest.approx(39.4784176044 * 2)

def test_create_surface_body_from_trimmed_curves(modeler: Modeler):
    design = modeler.create_design("surface")

    # pill shape
    circle1 = Circle(Point3D([0, 0, 0]), 1).trim(Interval(0, np.pi))
    line1 = Line(Point3D([-1, 0, 0]), UnitVector3D([0, -1, 0])).trim(Interval(0, 1))
    circle2 = Circle(Point3D([0, -1, 0]), 1).trim(Interval(np.pi, np.pi * 2))
    line2 = Line(Point3D([1, 0, 0]), UnitVector3D([0, -1, 0])).trim(Interval(0, 1))

    body = design.create_surface_from_trimmed_curves("body", [circle1, line1, line2, circle2])
    assert body.is_surface
    assert body.faces[0].area.m == pytest.approx(
        Quantity(2 + np.pi, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )

    # create from edges (by getting their trimmed curves)
    trimmed_curves_from_edges = [edge.shape for edge in body.edges]
    body = design.create_surface_from_trimmed_curves("body2", trimmed_curves_from_edges)
    assert body.is_surface
    assert body.faces[0].area.m == pytest.approx(
        Quantity(2 + np.pi, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )

def test_shell_body(modeler: Modeler):
    """Test shell command."""
    design = modeler.create_design("shell")
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    assert base.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 6

    # shell
    success = base.shell_body(0.1)
    assert success
    assert base.volume.m == pytest.approx(Quantity(0.728, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 12

    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    success = base.shell_body(-0.1)
    assert success
    assert base.volume.m == pytest.approx(Quantity(0.488, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 12

def test_named_selection_build_faces_from_metadata_returns_none_when_body_missing():
    """Test face metadata build returns None when a referenced body is unavailable."""
    import ansys.geometry.core.designer.selection as selection_module

    ns = _named_selection()
    ns._faces_meta_cached = [
        {
            "id": "face-1",
            "surface_type": 1,
            "is_reversed": False,
            "body_id": "missing-body",
        }
    ]

    with patch.object(selection_module, "get_all_bodies_from_design", return_value=[]):
        assert ns._NamedSelection__build_faces_from_metadata() is None

def test_tracker_response_delete_body_from_root(
    modeler: Modeler, unit_box_sketch: Sketch, tracker_payload_factory
):
    """Test _update_from_tracker deleting body from root level."""
    design = modeler.create_design("delete_body_root")

    body = design.extrude_sketch("body_to_delete", unit_box_sketch, 1)
    body_id = body.id

    tracker_response = tracker_payload_factory(
        deleted_bodies=[{"id": body_id, "name": "body_to_delete"}],
    )

    assert body.is_alive is True
    with (
        patch.object(design, "_clear_cached_bodies") as clear_cache_spy,
        patch.object(design._grpc_client.log, "info") as info_spy,
    ):
        design._update_from_tracker(tracker_response)

    assert body.is_alive is False
    clear_cache_spy.assert_called_once()
    assert any("Deleted body" in str(call) for call in info_spy.call_args_list)

def test_update_from_tracker_modified_body_in_nested_component(
    modeler: Modeler, unit_box_sketch: Sketch, tracker_payload_factory
):
    """Test _update_from_tracker updates modified bodies found in nested components."""
    design = modeler.create_design("mod_body_nested")

    parent_comp = design.add_component("ParentComp")
    nested_comp = parent_comp.add_component("NestedComp")

    nested_body = nested_comp.extrude_sketch("NestedBody", unit_box_sketch, 1)
    body_master_id = nested_body._template.id

    tracker_response = tracker_payload_factory(
        modified_bodies=[{"id": body_master_id, "name": "NestedBodyUpdated", "is_surface": True}],
    )

    design._update_from_tracker(tracker_response)

    assert nested_body.name == "NestedBodyUpdated"
    assert nested_body._template.is_surface is True

def test_find_and_add_body_to_component(modeler: Modeler):
    """Test _find_and_add_body finds component and adds body to it."""
    design = modeler.create_design("add_body_to_comp")

    comp = design.add_component("BodyComponent")
    part = comp._master_component.part
    part_id = part.id

    body_info = {
        "id": "new_body_1",
        "name": "NewBody",
        "parent_id": part_id,
        "is_surface": False,
    }

    with patch.object(design, "_clear_body_cache_for_part") as clear_cache_spy:
        result = design._find_and_add_body(body_info, design.components, {}, {})

    assert result is not None
    assert result.id == "new_body_1"
    assert result.name == "NewBody"
    clear_cache_spy.assert_called_once_with(part)

def test_find_and_add_body_to_nested_component_recursive(modeler: Modeler):
    """Test _find_and_add_body finds body parent in nested components via recursion."""
    design = modeler.create_design("add_body_recursive_nested")

    parent = design.add_component("ParentComp")
    child = parent.add_component("ChildComp")
    child_part = child._master_component.part

    body_info = {
        "id": "nested_new_body",
        "name": "NestedNewBody",
        "parent_id": child_part.id,
        "is_surface": True,
    }

    with patch.object(design, "_clear_body_cache_for_part") as clear_cache_spy:
        result = design._find_and_add_body(body_info, design.components, {}, {})

    assert result is not None
    assert result.id == "nested_new_body"
    clear_cache_spy.assert_called_once_with(child_part)

def test_find_and_add_body_returns_none_when_not_found(modeler: Modeler):
    """Test _find_and_add_body returns None when parent part not found."""
    design = modeler.create_design("body_notfound")

    body_info = {
        "id": "orphan_body",
        "name": "OrphanBody",
        "parent_id": "nonexistent_part",
        "is_surface": False,
    }

    result = design._find_and_add_body(body_info, design.components, {}, {})

    assert result is None

def test_find_and_remove_body_from_component(modeler: Modeler, unit_box_sketch: Sketch):
    """Test _find_and_remove_body removes body from component."""
    design = modeler.create_design("remove_body_comp")

    comp = design.add_component("TestComp")
    body = comp.extrude_sketch("TestBody", unit_box_sketch, 1)
    body_master_id = body.id.split("/")[-1]

    body_info = {"id": body_master_id}

    with patch.object(design._grpc_client.log, "debug") as debug_spy:
        result = design._find_and_remove_body(body_info, comp)

    assert result is True
    assert not body.is_alive
    debug_spy.assert_called()
    assert any(
        "Removed body" in str(call) and body_master_id in str(call)
        for call in debug_spy.call_args_list
    )

def test_find_and_remove_body_returns_false_not_found(modeler: Modeler):
    """Test _find_and_remove_body returns False when body not found."""
    design = modeler.create_design("body_remove_notfound")

    comp = design.add_component("TestComp")

    body_info = {"id": "nonexistent_body"}

    result = design._find_and_remove_body(body_info, comp)

    assert result is False

def test_update_body_properties(modeler: Modeler):
    """Test _update_body updates body properties from tracker response."""
    design = modeler.create_design("update_body_props")

    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 1, 1)
    body = design.extrude_sketch("TestBody", sketch, 1)

    body_info = {
        "id": body.id,
        "name": "UpdatedBodyName",
        "is_surface": True,
    }

    design._update_body(body, body_info)

    assert body.name == "UpdatedBodyName"
    assert body._template._is_surface is True

def test_get_body_bounding_box(modeler: Modeler):
    """Test getting the bounding box of a body."""
    design = modeler.create_design("body_bounding_box")
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    bounding_box = body.bounding_box
    assert bounding_box.min_corner.x.m == bounding_box.min_corner.y.m == -0.5
    assert bounding_box.min_corner.z.m == 0
    assert bounding_box.max_corner.x.m == bounding_box.max_corner.y.m == 0.5
    assert bounding_box.max_corner.z.m == 1

    # Test center
    center = bounding_box.center
    assert center.x.m == 0
    assert center.y.m == 0
    assert center.z.m == 0.5

def test_get_body_tight_bounding_box(modeler: Modeler):
    """Test getting the bounding box of a body with tight tolerance."""
    design = modeler.open_file(Path(FILES_DIR, "yarn.scdocx"))
    yarn_body = design.bodies[0]

    # Test getting regular bounding box
    bounding_box = yarn_body.bounding_box

    assert bounding_box.min_corner.x.m == pytest.approx(0.750637531716012)
    assert bounding_box.min_corner.y.m == pytest.approx(-0.340634843063073)
    assert bounding_box.min_corner.z.m == pytest.approx(0.0134380239342444)

    assert bounding_box.max_corner.x.m == pytest.approx(1.75484840496883)
    assert bounding_box.max_corner.y.m == pytest.approx(0.663576030656712)
    assert bounding_box.max_corner.z.m == pytest.approx(0.288244080618053)

    assert bounding_box.center.x.m == pytest.approx(1.25274296834242)
    assert bounding_box.center.y.m == pytest.approx(0.161470593796819)
    assert bounding_box.center.z.m == pytest.approx(0.150841052276149)

    # Test getting tight bounding box
    tight_bounding_box = yarn_body.get_bounding_box(tight=True)

    assert tight_bounding_box.min_corner.x.m == pytest.approx(0.754595317788195)
    assert tight_bounding_box.min_corner.y.m == pytest.approx(5.2771026530260073e-17)
    assert tight_bounding_box.min_corner.z.m == pytest.approx(0.100708473482868)

    assert tight_bounding_box.max_corner.x.m == pytest.approx(1.41421356238489)
    assert tight_bounding_box.max_corner.y.m == pytest.approx(0.659618244585186)
    assert tight_bounding_box.max_corner.z.m == pytest.approx(0.196642053388603)

    assert tight_bounding_box.center.x.m == pytest.approx(1.08440444008654)
    assert tight_bounding_box.center.y.m == pytest.approx(0.329809122292593)
    assert tight_bounding_box.center.z.m == pytest.approx(0.148675263435735)


@pytest.mark.parametrize(
    "file_extension, design_format",
    [
        ("scdocx", None),  # For .scdocx files
        ("dsco", DesignFileFormat.DISCO),  # For .dsco files
    ],
)
def test_write_body_facets_on_save(
    modeler: Modeler, tmp_path_factory: pytest.TempPathFactory, file_extension: str, design_format
):
    design = modeler.open_file(Path(FILES_DIR, "cars.scdocx"))

    # First file without body facets
    filepath_no_facets = tmp_path_factory.mktemp("test_design") / f"cars_no_facets.{file_extension}"
    if design_format:
        design.download(filepath_no_facets, design_format)
    else:
        design.download(filepath_no_facets)

    # Second file with body facets
    filepath_with_facets = (
        tmp_path_factory.mktemp("test_design") / f"cars_with_facets.{file_extension}"
    )
    if design_format:
        design.download(filepath_with_facets, design_format, write_body_facets=True)
    else:
        design.download(filepath_with_facets, write_body_facets=True)

    # Compare file sizes
    size_no_facets = filepath_no_facets.stat().st_size
    size_with_facets = filepath_with_facets.stat().st_size

    assert size_with_facets > size_no_facets

    # Ensure facets.bin and renderlist.xml files exist
    with zipfile.ZipFile(filepath_with_facets, "r") as zip_ref:
        namelist = set(zip_ref.namelist())

    expected_files = {
        "SpaceClaim/Graphics/facets.bin",
        "SpaceClaim/Graphics/renderlist.xml",
    }

    missing = expected_files - namelist
    assert not missing

def test_update_from_tracker_modified_body_nested_component(
    modeler: Modeler, tracker_payload_factory
):
    """Test _update_from_tracker updates modified bodies in nested components."""
    design = modeler.create_design("cov_mod_body_nested")
    nested = design.add_component("Parent").add_component("Child")
    body = nested.extrude_sketch("NestedBody", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    tracker_response = tracker_payload_factory(
        modified_bodies=[{"id": body._template.id, "name": "NestedUpdated", "is_surface": True}]
    )

    design._update_from_tracker(tracker_response)

    assert body.name == "NestedUpdated"
    assert body._template.is_surface is True

def test_update_from_tracker_deleted_nested_body_breaks_recursion(
    modeler: Modeler, tracker_payload_factory
):
    """Test _update_from_tracker deletes nested bodies and breaks from recursion."""
    design = modeler.create_design("cov_del_body_nested")
    parent = design.add_component("Parent")
    child = parent.add_component("Child")
    nested_body = child.extrude_sketch("NestedBody", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    tracker_response = tracker_payload_factory(
        deleted_bodies=[{"id": nested_body.id.split("/")[-1]}]
    )

    design._update_from_tracker(tracker_response)

    assert nested_body.is_alive is False

def test_find_and_remove_body_recursive_success(modeler: Modeler):
    """Test _find_and_remove_body removes nested body and marks not alive."""
    design = modeler.create_design("cov_remove_body_recursive")
    parent = design.add_component("Parent")
    child = parent.add_component("Child")
    body = child.extrude_sketch("NestedBody", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    body_id = body.id.split("/")[-1]

    removed = design._find_and_remove_body({"id": body_id}, parent)

    assert removed is True
    assert body.is_alive is False

def test_clear_body_cache_nested_component_match_only(modeler: Modeler):
    """Test _clear_body_cache_for_part clears cache only for matching components."""
    design = modeler.create_design("cov_clear_cache_nested")
    target_part = design._master_component.part

    matching_component = Mock()
    matching_component._master_component = Mock()
    matching_component._master_component.part = target_part
    matching_component._clear_cached_bodies = Mock()

    non_matching_component = Mock()
    non_matching_component._master_component = Mock()
    non_matching_component._master_component.part = Part("other", "other", [], [])
    non_matching_component._clear_cached_bodies = Mock()

    with patch.object(
        design,
        "_get_all_components",
        return_value=[matching_component, non_matching_component],
    ):
        design._clear_body_cache_for_part(target_part)

    matching_component._clear_cached_bodies.assert_called_once()
    non_matching_component._clear_cached_bodies.assert_not_called()
