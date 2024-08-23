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
"""Provides the data structure for material and material properties."""

from collections.abc import Sequence

from beartype import beartype as check_input_types
from pint import Quantity

from ansys.geometry.core.materials.property import MaterialProperty, MaterialPropertyType


class Material:
    """Provides the data structure for a material.

    Parameters
    ----------
    name: str
        Material name.
    density: ~pint.Quantity
        Material density.
    additional_properties: Sequence[MaterialProperty], default: None
        Additional material properties.
    """

    @check_input_types
    def __init__(
        self,
        name: str,
        density: Quantity,
        additional_properties: Sequence[MaterialProperty] | None = None,
    ):
        """Initialize the ``Material`` class."""
        self._name = name
        self._density = MaterialProperty(MaterialPropertyType.DENSITY, "Density", density)
        if not additional_properties:
            additional_properties = []

        # Add the density to the properties list
        additional_properties.append(self._density)
        self._properties = {}
        for property in additional_properties:
            self._properties[property.type] = property

    @property
    def properties(self) -> dict[MaterialPropertyType, MaterialProperty]:
        """Dictionary of the material property type and material properties."""
        return self._properties

    @property
    def name(self) -> str:
        """Material name."""
        return self._name

    @check_input_types
    def add_property(self, type: MaterialPropertyType, name: str, quantity: Quantity) -> None:
        """Add a material property to the ``Material`` class.

        Parameters
        ----------
        type : MaterialPropertyType
            Material property type.
        name: str
            Material name.
        quantity: ~pint.Quantity
            Material value and unit.
        """
        property = MaterialProperty(type, name, quantity)
        self._properties[property.type] = property
