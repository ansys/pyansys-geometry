from ansys.geometry.core.primitives.direction import Direction
from ansys.geometry.core.primitives.point3D import Point3D
from ansys.geometry.core.sketch.circle_sketch import CircleSketch
from ansys.geometry.core.sketch.line_sketch import LineSketch


class Sketch:
    """
    Provides Sketch class for building 2D sketch elements.
    """

    def __init__(self):
        """Sketch constructor"""
        self._sketch_curves = (
            []
        )  # SketchCurve[] maintaining reference to all sketch curves within the current sketch

    def circle(self, origin: Point3D, radius: float):
        """
        Add a circle sketch object to the sketch plane.
        """
        circle = CircleSketch(origin, Direction(0, 1), Direction(0, 1), radius)

        self._sketch_curves.append(circle)

        # TODO: save circle creation to history tracking object

        # return self to enable fluent-style api
        return self

    def line(self, point1: Point3D, point2: Point3D):
        """
        Add a line segment sketch object to the sketch plane.
        """
        line = LineSketch(point1, point2)

        self._sketch_curves.append(line)

        # TODO: save line creation to history tracking object

        # return self to enable fluent-style api
        return self
