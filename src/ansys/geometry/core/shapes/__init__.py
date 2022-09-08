"""PyGeometry shapes subpackage."""

from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.shapes.circle import Circle
from ansys.geometry.core.shapes.ellipse import Ellipse
from ansys.geometry.core.shapes.line import Line, Segment
from ansys.geometry.core.shapes.polygon import Polygon

__all__ = ["BaseShape", "Circle", "Ellipse", "Line", "Segment", "Polygon"]
