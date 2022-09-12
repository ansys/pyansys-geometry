"""PyGeometry design subpackage."""

from ansys.geometry.core.designer.assembly import Assembly
from ansys.geometry.core.designer.design import Design
from ansys.geometry.core.designer.geometry import DesignGeometry
from ansys.geometry.core.designer.solid import Solid
from ansys.geometry.core.designer.surface import Surface

__all__ = ["Assembly", "Design", "DesignGeometry", "Solid", "Surface"]
