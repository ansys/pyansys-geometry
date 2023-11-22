# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
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
"""Test material assignment."""

from pint import Quantity

from ansys.geometry.core import Modeler
from ansys.geometry.core.materials import Material, MaterialProperty, MaterialPropertyType
from ansys.geometry.core.misc import UNITS


def test_material_creation(modeler: Modeler, skip_not_on_linux_service):
    """Test the creation of a material on a design."""
    design = modeler.create_design("my_design")

    mat_name = "mat_1"
    density = 1000 * UNITS.kg / (UNITS.m * UNITS.m * UNITS.m)
    material = Material(mat_name, density)

    assert material.name == mat_name
    assert len(material.properties) == 1
    assert material.properties[MaterialPropertyType.DENSITY].type == MaterialPropertyType.DENSITY
    assert material.properties[MaterialPropertyType.DENSITY].name == "Density"
    assert material.properties[MaterialPropertyType.DENSITY].quantity == density

    mat_prop_name = "ratio_2"
    mat_prop_quantity = Quantity(142.2, UNITS.dimensionless)
    material_property_2 = MaterialProperty(
        MaterialPropertyType.POISSON_RATIO, mat_prop_name, mat_prop_quantity
    )
    material.add_property(
        type=material_property_2.type,
        name=material_property_2.name,
        quantity=material_property_2.quantity,
    )

    assert material.name == mat_name
    assert len(material.properties) == 2
    assert material.properties[MaterialPropertyType.DENSITY].type == MaterialPropertyType.DENSITY
    assert material.properties[MaterialPropertyType.DENSITY].name == "Density"
    assert material.properties[MaterialPropertyType.DENSITY].quantity == density
    assert (
        material.properties[MaterialPropertyType.POISSON_RATIO].type
        == MaterialPropertyType.POISSON_RATIO
    )
    assert material.properties[MaterialPropertyType.POISSON_RATIO].name == mat_prop_name
    assert material.properties[MaterialPropertyType.POISSON_RATIO].quantity == mat_prop_quantity

    design.add_material(material)

    assert design.materials[0].name == mat_name
    assert len(design.materials[0].properties) == 2
    assert (
        design.materials[0].properties[MaterialPropertyType.DENSITY].type
        == MaterialPropertyType.DENSITY
    )
    assert design.materials[0].properties[MaterialPropertyType.DENSITY].name == "Density"
    assert design.materials[0].properties[MaterialPropertyType.DENSITY].quantity == density
    assert (
        design.materials[0].properties[MaterialPropertyType.POISSON_RATIO].type
        == MaterialPropertyType.POISSON_RATIO
    )
    assert design.materials[0].properties[MaterialPropertyType.POISSON_RATIO].name == mat_prop_name
    assert (
        design.materials[0].properties[MaterialPropertyType.POISSON_RATIO].quantity
        == mat_prop_quantity
    )
