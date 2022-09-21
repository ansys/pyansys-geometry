"""PyGeometry design subpackage."""

from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.designer.component import Component
from ansys.geometry.core.designer.design import Design
from ansys.geometry.core.designer.edge import CurveType, Edge
from ansys.geometry.core.designer.face import Face, SurfaceType
from ansys.geometry.core.designer.selection import NamedSelection

__all__ = [
    "Body",
    "Component",
    "CurveType",
    "Design",
    "Edge",
    "Face",
    "NamedSelection",
    "SurfaceType",
]
