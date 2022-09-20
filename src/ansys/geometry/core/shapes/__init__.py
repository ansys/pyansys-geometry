"""PyGeometry shapes subpackage."""

from ansys.geometry.core.shapes.arc import Arc
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.shapes.box import Box
from ansys.geometry.core.shapes.circle import Circle
from ansys.geometry.core.shapes.ellipse import Ellipse
from ansys.geometry.core.shapes.line import Line, Segment
from ansys.geometry.core.shapes.polygon import Polygon
from ansys.geometry.core.shapes.slot import Slot

__all__ = [
    "Arc",
    "BaseShape",
    "Box",
    "Circle",
    "Ellipse",
    "Line",
    "Polygon",
    "Segment",
    "Slot",
]
