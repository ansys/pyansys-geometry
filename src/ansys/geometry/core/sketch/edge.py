"""``SketchEdge`` class module."""

from pint import Quantity

from ansys.geometry.core.math import Point2D


class SketchEdge:
    """Provides base class for modeling edges forming sketched shapes."""

    @property
    def start(self) -> Point2D:
        raise NotImplementedError("Each edge must provide this definition.")

    @property
    def end(self) -> Point2D:
        raise NotImplementedError("Each edge must provide this definition.")

    @property
    def length(self) -> Quantity:
        raise NotImplementedError("Each edge must provide this definition.")
