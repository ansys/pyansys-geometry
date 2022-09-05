"""PyGeometry design subpackage."""

from ansys.geometry.core.design_assembly.assembly import Assembly
from ansys.geometry.core.design_assembly.design import Design
from ansys.geometry.core.design_assembly.geometry import DesignGeometry
from ansys.geometry.core.design_assembly.solid import Solid
from ansys.geometry.core.design_assembly.surface import Surface

__all__ = ["Assembly", "Design", "DesignGeometry", "Solid", "Surface"]
