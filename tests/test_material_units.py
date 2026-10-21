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

from unittest.mock import MagicMock

from pint import DefinitionSyntaxError, Quantity, UndefinedUnitError
import pytest

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.designer.design import Design
from ansys.geometry.core.materials.property import MaterialPropertyType
from ansys.geometry.core.modeler import Modeler


@pytest.fixture
def existing_design_modeler():
    """Provide an empty assembly through mocked gRPC services without a server."""
    client = MagicMock(spec=GrpcClient)
    client.backend_version = (26, 1, 0)
    client.services.designs.get_active.return_value = {
        "design_id": "design-id",
        "main_part_id": "part-id",
        "name": "Existing design",
    }
    client.services.designs.get_assembly.return_value = {
        "parts": [{"id": "part-id", "name": "Main part"}],
        "transformed_parts": [],
        "components": [],
        "bodies": [],
        "materials": [],
        "beams": [],
        "named_selections": [],
        "component_coordinate_systems": [],
        "design_points": [],
        "datum_points": [],
        "component_shared_topologies": [],
    }
    client.services.planes.get_all.return_value = {"planes": []}
    client.services.curves.get_all.return_value = {"curves": []}
    modeler = MagicMock(spec=Modeler)
    modeler.client = client
    return modeler


@pytest.mark.parametrize(
    "property_id, property_type, display_name, value, valid_units",
    [
        (
            "Heat.Iso.Conduction",
            MaterialPropertyType.THERMAL_CONDUCTIVITY,
            "Thermal conductivity",
            45.5,
            "W/(m*K)",
        ),
        (
            "General.Density.Mass",
            MaterialPropertyType.DENSITY,
            "Density",
            7850.0,
            "kg/m**3",
        ),
    ],
    ids=["thermal-conductivity", "density"],
)
@pytest.mark.parametrize("unit_case", ["malformed", "syntax-error", "undefined", "valid"])
def test_read_existing_design_material_units(
    existing_design_modeler,
    monkeypatch,
    property_id,
    property_type,
    display_name,
    value,
    valid_units,
    unit_case,
):
    """Read material quantities and preserve values when backend units cannot be parsed."""
    units = {
        "malformed": "W/m-K",
        "syntax-error": "W/m-K",
        "undefined": "undefined_backend_unit",
        "valid": valid_units,
    }[unit_case]
    quantity_constructor = Quantity
    if unit_case == "syntax-error":
        # Guarantee coverage of the new handler even on Pint versions raising TypeError.
        class SyntaxErrorQuantity(Quantity):
            def __new__(cls, magnitude, unit=None):
                if unit == "W/m-K":
                    raise DefinitionSyntaxError("Invalid additive unit expression: W/m-K")
                return Quantity(magnitude, unit)

        quantity_constructor = SyntaxErrorQuantity
        monkeypatch.setattr("ansys.geometry.core.designer.design.Quantity", quantity_constructor)

    client = existing_design_modeler.client
    active_design = client.services.designs.get_active.return_value
    assembly = client.services.designs.get_assembly.return_value
    assembly["materials"] = [
        {
            "name": "Test material",
            "material_properties": [
                {
                    "id": property_id,
                    "display_name": display_name,
                    "value": value,
                    "units": units,
                }
            ],
        }
    ]

    design = Design("Ignored name", existing_design_modeler, read_existing_design=True)

    client.services.designs.get_active.assert_called_once_with()
    client.services.designs.get_assembly.assert_called_once_with(active_design=active_design)
    client.services.designs.new.assert_not_called()
    assert design.design_id == "design-id"
    assert design.id == "part-id"
    assert design.name == "Existing design"
    assert len(design.materials) == 1
    material = design.materials[0]
    assert material.name == "Test material"
    assert set(material.properties) == {property_type, MaterialPropertyType.DENSITY}
    material_property = material.properties[property_type]
    assert material_property.type == property_type
    assert material_property.name == display_name

    if unit_case == "valid":
        # Valid units must remain dimensional quantities, not fall back to floats.
        assert isinstance(material_property.quantity, Quantity)
        assert material_property.quantity.magnitude == value
        assert material_property.quantity.units == Quantity(1, valid_units).units
        client.log.warning.assert_not_called()
    else:
        # Keep real backend parsing: Pint 0.26.1 raises TypeError, 0.26.2 a syntax error.
        error_type = {
            "malformed": (DefinitionSyntaxError, TypeError),
            "syntax-error": DefinitionSyntaxError,
            "undefined": UndefinedUnitError,
        }[unit_case]
        with pytest.raises(error_type) as exc_info:
            quantity_constructor(value, units)
        assert client.log.warning.call_count == 2
        client.log.warning.assert_any_call(
            f"Material property {display_name} with units {units} is not fully supported."
            " Storing value only as float."
        )
        client.log.warning.assert_any_call(f"Root cause: {exc_info.value}")
        if property_type == MaterialPropertyType.DENSITY:
            # Material reconstructs density as a dimensionless Quantity after fallback.
            assert isinstance(material_property.quantity, Quantity)
            assert material_property.quantity.magnitude == value
            assert material_property.quantity.units == Quantity(1).units
        else:
            assert isinstance(material_property.quantity, float)
            assert material_property.quantity == value

    if property_type != MaterialPropertyType.DENSITY:
        density = material.properties[MaterialPropertyType.DENSITY].quantity
        assert isinstance(density, Quantity)
        assert density.magnitude == 0
        assert density.units == Quantity(1).units
