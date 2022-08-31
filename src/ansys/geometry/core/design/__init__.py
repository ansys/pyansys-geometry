"""PyGeometry design subpackage."""

from ansys.geometry.core.design.assembly import Assembly
from ansys.geometry.core.design.geometry import DesignGeometry
from ansys.geometry.core.design.solid import Solid
from ansys.geometry.core.design.surface import Surface

__all__ = ["Assembly", "DesignGeometry", "Solid", "Surface"]
