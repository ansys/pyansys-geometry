"""PyGeometry design subpackage."""

from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.designer.component import Component
from ansys.geometry.core.designer.design import Design
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.designer.selection import NamedSelection

__all__ = ["Body", "Component", "Design", "Edge", "Face", "NamedSelection"]
